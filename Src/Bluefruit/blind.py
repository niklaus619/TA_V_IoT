#Zeigt den vom Raspberry Pi vorgegebenen Storenstatus mit NeoPixeln an.#

from adafruit_circuitplayground import cp


GREEN = (0, 80, 0)
OFF = (0, 0, 0)

_closed = False


def set_closed(closed):
    #Store schliessen (Pixel aus) oder oeffnen (Pixel gruen).#
    global _closed
    _closed = bool(closed)
    cp.pixels.fill(OFF if _closed else GREEN)


def is_closed():
    #Den zuletzt eingestellten Storenstatus zurueckgeben.#
    return _closed
