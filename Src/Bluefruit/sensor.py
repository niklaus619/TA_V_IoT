#Liest die eingebauten Temperatur- und Lichtsensoren aus.#

from adafruit_circuitplayground import cp


def read():
    #Messwerte in einem fuer die USB-Uebertragung geeigneten Dictionary liefern.#
    return {
        # Eine Nachkommastelle reicht fuer die Anzeige der Raumtemperatur aus.
        "temperature": round(cp.temperature, 1),
        # cp.light liefert den unbearbeiteten Messwert des Lichtsensors.
        "light": cp.light,
    }
