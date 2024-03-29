"""
Traitement des requêtes.

Gère l'envoie des requêtes au serveur et le partage des données aux
autres threads.
"""

from datetime import datetime, timedelta
import threading
import logging
import re

import requests
import shared_data

MIN_DELAY = 30              # Temps minimum avant une nouvelle requête.
ATTEMPT_DELAY = 14          # Temps d'attente pour une requête non concluante.
MAX_ATTEMPT = 2             # Nb d'essai avant exit
SEC_TO_WAKEUP = 5 * 60 * 60 # Temps d'attente si plus de tram
    
URL = "https://api.cts-strasbourg.eu/v1/siri/2.0/stop-monitoring"

def seconds_left(future):
    return timedelta.total_seconds(future - datetime.now())


class InfosThr(threading.Thread):
    """Thread de récupération des données.

    Attributs:
        shared: liste de données partagées
        stop_event: objet event pour signaler l'arrêt du script
        logger: objet de log
        token: str, token d'identification
        payload: dict, arguments de la requête GET
    Argument en plus:
        station_ref: str, unique référence de la station
    """

    def __init__(self, shared, stop_event, station_ref, token):
        threading.Thread.__init__(self)
        self.shared = shared
        self.stop_event = stop_event
        self.logger = logging.getLogger(__name__)
        self.token = token
        self.payload = {'MonitoringRef': [station_ref],
                        'VehicleMode': 'tram',
                        'PreviewInterval': 'PT1H30M',
                        'MaximumStopVisits': 3}


    def run(self):
        local_list = []
        shared_list = self.shared.list
        req_try = 0
        req = None

        while True:
            try:
                req = requests.get(URL, auth=(self.token,''),
                        params=self.payload)
                if req.status_code == requests.codes.all_ok:
                    req_try = 0
                else:
                    req.raise_for_status()

            except requests.exceptions.HTTPError:
                self.logger.exception('Request error %d.', req.status_code,
                        exc_info=False)
                if self.stop_event.wait(timeout=MIN_DELAY):
                    break

            # Si erreur, alors retentative jusqu'à MAX_ATTEMPT fois.
            except requests.exceptions.ConnectionError:
                self.logger.exception('Connection error. Attempt %d.', req_try,
                        exc_info=False)

                if req_try < MAX_ATTEMPT:
                    req_try = req_try + 1
                    self.stop_event.wait(timeout=ATTEMPT_DELAY)
                    continue
                else:
                    self.logger.exception('Hanging up.', exc_info=False)
                    self.stop_event.set()
                    break

            data = req.json()

            # Remove UTC offset at the end of string.
            valid_until_str = re.sub(r"^(.*)(\+|\-).*", r"\1",
                    (data['ServiceDelivery']['StopMonitoringDelivery'][0]
                    ['ValidUntil']), flags=re.ASCII)

            # Secondes restantes pour une nouvelle requête
            valid_cntdown = seconds_left(datetime.strptime(valid_until_str,
                '%Y-%m-%dT%H:%M:%S'))

            # Tableau comprenant noms de ligne et heures d'arrivées.
            # Si une exception est levée, plus aucun tram n'est
            # attendu.
            try:
                tram_infos = (data['ServiceDelivery']['StopMonitoringDelivery']
                    [0]['MonitoredStopVisit'])
            except KeyError:
                self.logger.warning('End of arrivals. Waiting %d seconds.',
                        SEC_TO_WAKEUP)
                if self.stop_event.wait(timeout=SEC_TO_WAKEUP):
                    break
                continue

            # Remplissage tableau.
            for i, val in enumerate(tram_infos):
                # Remove UTC offset at the end of string.
                valid_until_str = re.sub(r"^(.*)(\+|\-).*", r"\1",
                        (val['MonitoredVehicleJourney']['MonitoredCall']
                            ['ExpectedArrivalTime']), flags=re.ASCII)
                arrival_time = datetime.strptime(valid_until_str , '%Y-%m-%dT%H:%M:%S')
                line_ref = val['MonitoredVehicleJourney']['LineRef']
                destination = (val['MonitoredVehicleJourney']
                        ['DestinationShortName'])
                station = (val['MonitoredVehicleJourney']['MonitoredCall']
                        ['StopPointName'])
                try:
                    local_list[i] = shared_data.TramArriv(line_ref,
                            arrival_time, destination, station)
                except IndexError:
                    local_list.append(shared_data.TramArriv(line_ref,
                        arrival_time, destination, station))

            # Transfert des données.
            with self.shared.lock:
                shared_data.copy_list(local_list, shared_list)

            # Temps minimum pour éviter la saturation.
            if self.stop_event.wait(timeout=(valid_cntdown + MIN_DELAY)):
                break
