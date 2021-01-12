#! /usr/bin/env python3

import threading


def copy_list(src, dst):
    """Copie sans recréation."""
    for i, val in enumerate(src):
        try:
            dst[i] = val
        except IndexError:
            dst.append(val)


class SharedList:
    """Tableau partagé."""

    def __init__(self):
        self.list = []
        self.lock = threading.Lock()

    def __repr__(self):
        return repr(self.list) + ' | ' + repr(self.lock)


class TramArriv:
    """Attributs de tram en transite."""

    def __init__(self, line_ref, expected_arriv, destination, station=None):
        self.line_ref = line_ref
        self.expected_arriv = expected_arriv
        self.destination = destination
        self.station = station

    def __repr__(self):
        pass
