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
import lcd_animations as anim

REFRESH_TIME = 1    # Rafraîchit l'écran toutes les secondes
ANIM_REFRESH_TIME = 0.35 # Pour l'animation

def minutes_left(arrival_time):
    """Calcule des minutes restantes entre arrival_time et maintenant."""
    return int(timedelta.total_seconds(arrival_time - datetime.now()) // 60)


# A MODIFIER POUR ÉCRAN DIFFÉRENT
def display_idle(display, animation):
    animation.play(ANIM_REFRESH_TIME)


# A MODIFIER POUR ÉCRAN DIFFÉRENT
def display_header(display, station_name):
    """Affichage nom de station et heure."""
    display.display_string("{:10.10} {:%H:%M}".format(
        station_name, datetime.now()), 1)


def display_one_tramway(display, info_list):
    """Affichage temps restant pour un tram."""
    display.display_string("{}:{:3}m".format(
        info_list[0][0], info_list[0][1])
        + " " * 10, 2)


def display_two_tramways(display, info_list):
    """Affichage temps restant pour deux trams."""
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
    Argument en plus:
        i2c_addr: adresse du module i2c
        i2c_bus: bus i2c du rpi
    """
    def __init__(self, shared, stop_event, i2c_addr, i2c_bus):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.shared = shared
        self.stop_event = stop_event
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

        idle_animation = anim.DinoAnimation(self.display)

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
                    display_idle(self.display, idle_animation)

                else:
                    # Tri de précaution, garantit stable
                    filt_list.sort(key=lambda tram: tram[1])
                    self.display.set_cursor_at(0)
                    display_header(self.display, local_list[0].station)
                    if i == 1:
                        display_one_tramway(self.display, filt_list)
                    else:
                        display_two_tramways(self.display, filt_list)

            except OSError:
                self.logger.exception('Connection error. Abort.',
                        exc_info=False)
                self.stop_event.set()
                break

            if self.stop_event.wait(timeout=REFRESH_TIME):
                break
