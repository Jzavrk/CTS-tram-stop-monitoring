"""
Traitement le l'affichage des horaires et des lignes de tram.

Le module est adapté à un écran lcd 16x2 mais est compatible avec tout
autre taille en apportant de légères modifications.
"""

from datetime import datetime, timedelta
import sys
import logging
import threading
import rpi_i2c_lcd
import shared_data


def minutes_left(arrival_time):
    """Calcule des minutes restantes entre arrival_time et maintenant."""
    return int(timedelta.total_seconds(arrival_time - datetime.now()) // 60)


# A MODIFIER POUR ÉCRAN DIFFÉRENT
def display_idle(display):
    """Affichage d'un message d'attente."""
    display.display_string("Fetching..." + " " * 5, 1)
    display.display_string(" " * 16, 2)


# A MODIFIER POUR ÉCRAN DIFFÉRENT
def display_infos(display, station_name, info_list, valid_num):
    """Affichage des arrivées de tram à la station station_name.

    Arguments:
        display: LiquidCrystalI2C
        station_name: str
        info_list: liste de tuple (nom_de_ligne, minute_restantes)
        valid_num: nombre de cellule valide dans la liste
    """
    display.display_string("{:10.10} {:%H:%M}".format(
        station_name, datetime.now()), 1)

    if valid_num == 1:
        display.display_string("{}:{:3}m".format(
            info_list[0][0], info_list[0][1])
            + " " * 10, 2)
    else:
        display.display_string("{}:{:3}m    {}:{:3}m".format(
            info_list[0][0], info_list[0][1],
            info_list[1][0], info_list[1][1]), 2)


class DisplayThr(threading.Thread):
    """Thread du traitement de l'affichage des arrivées de tram.

    Attributs:
        display: LiquidCrystalI2C
        logger: objet de log
        shared: liste de données partagées
        stop_event: objet event pour signaler l'arrêt du script
        seconds_per_frame: délai de rafraichissement de l'écran
    Argument en plus:
        i2c_addr: adresse du module i2c
        i2c_bus: bus i2c du rpi
    """
    def __init__(self, shared, stop_event, seconds_per_frame, i2c_addr,
            i2c_bus):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.shared = shared
        self.stop_event = stop_event
        self.seconds_per_frame = seconds_per_frame
        try:
            self.display = rpi_i2c_lcd.LiquidCrystalI2C(i2c_addr, i2c_bus)
        except OSError:
            self.logger.exception('Unconnected device.', exc_info=False)
            self.stop_event.set()
            sys.exit()


    def run(self):
        local_list = []
        shared_list = self.shared.list
        filt_list = [] # Tableau de tuples (nom_de_ligne, minutes_restantes)

        while True:
            # Copie des données partagées
            with self.shared.lock:
                shared_data.copy_list(shared_list, local_list)

            # Filtrage pour ne retenir que les horaires valides (valeurs
            # positives)
            i = 0
            for itr in local_list:
                min_left = minutes_left(itr.expected_arriv)

                if min_left >= 0:
                    try:
                        filt_list[i] = (itr.line_ref, min_left)
                    except IndexError:
                        filt_list.append((itr.line_ref, min_left))
                    finally:
                        i = i + 1
            try:
                if i == 0:
                    display_idle(self.display)

                else:
                    # Tri de précaution, garantit stable
                    filt_list.sort(key=lambda tram: tram[1])
                    display_infos(self.display, local_list[0].station,
                            filt_list, i)
            except OSError:
                self.logger.exception('Connection error. Abort.',
                        exc_info=False)
                self.stop_event.set()
                break

            if self.stop_event.wait(timeout=self.seconds_per_frame):
                self.display.clear()
                break
