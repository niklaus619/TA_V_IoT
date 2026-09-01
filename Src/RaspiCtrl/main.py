"""Startpunkt der Steuerung auf Raspberry Pi 1."""

import argparse
import logging
import time

from app import RaspiControllerApp
from controller import ClimateController, ControlConfig
from hardware import BluefruitSerial, SenseHatAdapter
from server import IoTServerClient


def parse_args():
    parser = argparse.ArgumentParser(description="IoT-Raumklimasteuerung")
    parser.add_argument("--serial-port", required=True, help="Bluefruit USB-Port, z.B. /dev/ttyACM1")
    parser.add_argument("--server-host", default="127.0.0.1", help="Adresse von Raspberry Pi 2")
    parser.add_argument("--server-port", type=int, default=9000)
    parser.add_argument("--target", type=float, default=22.0, help="Temperatur-Sollwert in Grad Celsius")
    parser.add_argument("--deadband", type=float, default=0.5, help="Temperatur-Totzone")
    parser.add_argument("--light-threshold", type=float, default=100.0)
    parser.add_argument("--passive-delay", type=float, default=120.0)
    parser.add_argument("--simulate-sense-hat", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    bluefruit = BluefruitSerial(args.serial_port)
    sense_hat = SenseHatAdapter(simulate=args.simulate_sense_hat)
    server = IoTServerClient(args.server_host, args.server_port)
    controller = ClimateController(ControlConfig(
        target_temperature=args.target,
        temperature_deadband=args.deadband,
        daylight_threshold=args.light_threshold,
        passive_delay_seconds=args.passive_delay,
    ))
    app = RaspiControllerApp(bluefruit, sense_hat, controller, server)
    try:
        while True:
            app.step()
            time.sleep(0.02)
    except KeyboardInterrupt:
        logging.info("Steuerung beendet")
    finally:
        bluefruit.close()
        server.close()


if __name__ == "__main__":
    main()
