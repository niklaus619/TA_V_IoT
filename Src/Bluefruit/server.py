#Sendet und empfaengt zeilenweise JSON-Nachrichten ueber USB CDC.#

import json
import usb_cdc


# Der separate Datenkanal wird in boot.py aktiviert.
_serial = usb_cdc.data
# Unvollstaendige USB-Nachrichten werden bis zum Zeilenende gesammelt.
_receive_buffer = bytearray()


def send(message):
    #Ein Dictionary als abgeschlossene JSON-Zeile an den Raspberry Pi senden.#
    if _serial is None:
        return
    payload = json.dumps(message) + "\n"
    # Die exakt gesendete Nachricht auf der separaten Konsole anzeigen.
    _serial.write(payload.encode("utf-8"))


def receive():
    #Alle vollstaendigen und gueltigen JSON-Nachrichten zurueckgeben.#
    if _serial is None:
        return []

    available = _serial.in_waiting
    if available:
        _receive_buffer.extend(_serial.read(available))

    messages = []
    # Jede Nachricht endet mit einem Zeilenumbruch und kann einzeln dekodiert werden.
    while b"\n" in _receive_buffer:
        raw_line, _, remainder = _receive_buffer.partition(b"\n")
        _receive_buffer[:] = remainder
        if not raw_line:
            continue
        try:
            messages.append(json.loads(raw_line.decode("utf-8")))
        except (ValueError, UnicodeError):
            # Fehlerhafte Daten nicht ausfuehren, sondern dem Raspberry Pi melden.
            send({"type": "error", "message": "invalid_json"})

    return messages
