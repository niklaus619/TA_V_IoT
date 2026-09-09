#Richtet die USB-Schnittstellen vor dem Start des Hauptprogramms ein.#

import usb_cdc


# Die Konsole bleibt fuer Fehlersuche und REPL erhalten.
# Der Datenkanal uebertraegt ausschliesslich JSON-Nachrichten zum Raspberry Pi.
usb_cdc.enable(console=True, data=True)
