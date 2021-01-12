#! /usr/bin/env python3

import sys
import threading
import signal
import argparse
import logging
import infos_tram
import shared_data
import lcd_display

TOKEN = ''
STATION_REF = ''
I2C_ADDR = 0x3f
I2C_BUS = 1
SEC_PER_FRAM = 5
LOGS = sys.argv[0] + '.log'

stop_event = threading.Event()


def int16(string):
    """Conversion de type pour parser."""
    return int(string, 16)


def sig_handler(signum, frame):
    stop_event.set()


def main():
    parser = argparse.ArgumentParser(
            description='Tram station monitoring on I2C LCD.')
    parser.add_argument('--station', help='station reference (ex: 275A)',
            required=True)
    parser.add_argument('token', help='authentification token')
    parser.add_argument('-i', dest='i2c', type=int16, default=I2C_ADDR,
            help='I2C module address (in hexadecimal)')
    parser.add_argument('-b', dest='bus', type=int, default=I2C_BUS,
            help='I2C bus (0 -- original Pi, 1 -- above versions)')
    parser.add_argument('-r', dest='refresh', type=int, default=SEC_PER_FRAM,
            help='screen refresh delay (in seconds)')
    parser.add_argument('-l', dest='log', default=LOGS,
            help='log specified location')

    args = parser.parse_args()

    logging.basicConfig(filename=args.log, level=logging.INFO,
            format='[%(asctime)s]%(levelname)s:%(name)s:%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
    shared_list = shared_data.SharedList()
    infos = infos_tram.InfosThr(shared_list, stop_event, args.station,
            args.token)
    display = lcd_display.DisplayThr(shared_list, stop_event, args.refresh,
            args.i2c, args.bus)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGHUP, sig_handler)

    logging.info('Server start.')
    infos.start()
    display.start()

    infos.join()
    display.join()
    logging.info('Server shutdown.')
    logging.shutdown()

    sys.exit(0)


if __name__ == "__main__":
    main()
