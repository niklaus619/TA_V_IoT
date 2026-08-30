#Steuert Sensorabfrage, Storenanzeige und USB-Kommunikation.#

import time

import blind
import sensor
import server


SENSOR_INTERVAL_SECONDS = 1.0


def send_status():
    #Aktuelle Sensorwerte und den Storenstatus an den Raspberry Pi senden.#
    status = sensor.read()

    # Erfolgreich gelesene Messwerte im seriellen Monitor anzeigen.
    print(
        "Temperatur: {:.1f} C | Licht: {}".format(
            status["temperature"], status["light"]
        )
    )

    status["type"] = "status"
    status["blind"] = "closed" if blind.is_closed() else "open"
    server.send(status)


def handle_message(message):
    #Einen vom Raspberry Pi empfangenen Storenbefehl verarbeiten.#
    # Nur Befehle fuer die Store werden von diesem Programm akzeptiert.
    if message.get("type") != "set_blind":
        server.send({"type": "error", "message": "unknown_command"})
        return

    closed = message.get("closed")
    # Der Zustand muss eindeutig als true oder false uebertragen werden.
    if not isinstance(closed, bool):
        server.send({"type": "error", "message": "closed_must_be_boolean"})
        return

    blind.set_closed(closed)
    server.send({
        "type": "blind_state",
        "blind": "closed" if blind.is_closed() else "open",
    })


# Beim Programmstart ist die Store offen und die NeoPixel leuchten gruen.
blind.set_closed(False)
next_sensor_update = 0.0

while True:
    # USB laufend abfragen, damit Befehle ohne lange Verzoegerung ankommen.
    for incoming_message in server.receive():
        handle_message(incoming_message)

    now = time.monotonic()
    if now >= next_sensor_update:
        send_status()
        next_sensor_update = now + SENSOR_INTERVAL_SECONDS

    # Die kurze Pause entlastet den Prozessor, ohne die USB-Reaktion zu stoeren.
    time.sleep(0.01)
