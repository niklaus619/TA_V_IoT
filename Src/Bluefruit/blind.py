#Zeigt den vom Raspberry Pi vorgegebenen Storenstatus mit NeoPixeln an.#

from adafruit_circuitplayground import cp


GREEN = (0, 80, 0)
OFF = (0, 0, 0)
BRIGHTNESS = 0.3

# Globale Helligkeit aller NeoPixel: 0.0 = aus, 1.0 = maximal.
cp.pixels.brightness = BRIGHTNESS

_closed = False


def set_closed(closed):
    #Store schliessen (Pixel aus) oder oeffnen (Pixel gruen).#
    global _closed
    _closed = bool(closed)
    cp.pixels.fill(OFF if _closed else GREEN)


def is_closed():
    #Den zuletzt eingestellten Storenstatus zurueckgeben.#
    return _closed

def set_neopixels(enabled):
    #NeoPixel ueber die IoT-Plattform ein- oder ausschalten.#
    cp.pixels.fill(GREEN if enabled else OFF)