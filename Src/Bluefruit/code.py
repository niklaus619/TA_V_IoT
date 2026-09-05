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
    # Befehle fuer die Store und die NeoPixel werden verarbeitet.
    command_type = message.get("type")

    if command_type == "set_blind":
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
        return

    # Befehl zum Ein- oder Ausschalten der NeoPixel verarbeiten.
    if command_type == "set_neopixel":
        on = message.get("on")

        # Der Zustand muss eindeutig als true oder false uebertragen werden.
        if not isinstance(on, bool):
            server.send({"type": "error", "message": "on_must_be_boolean"})
            return

        # NeoPixel ein- oder ausschalten.
        blind.set_neopixels(on)

        # Den neuen NeoPixel-Zustand an den Raspberry Pi zurueckmelden.
        server.send({
            "type": "neopixel_state",
            "on": on,
        })
        return

    server.send({"type": "error", "message": "unknown_command"})


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
