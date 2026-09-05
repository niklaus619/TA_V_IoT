"""Adapter fuer Bluefruit und Sense HAT V2."""

import json
import logging
from typing import Any, Dict, List, Optional


LOG = logging.getLogger(__name__)


class BluefruitSerial:
    """Zeilenweises JSON ueber den USB-CDC-Datenkanal des Bluefruit."""

    def __init__(self, port: str, baudrate: int = 115200):
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("Fuer Bluefruit wird das Paket pyserial benoetigt") from exc
        self._serial = serial.Serial(port=port, baudrate=baudrate, timeout=0)
        self._buffer = bytearray()

    def receive(self) -> List[Dict[str, Any]]:
        waiting = self._serial.in_waiting
        if waiting:
            self._buffer.extend(self._serial.read(waiting))
        messages = []
        while b"\n" in self._buffer:
            raw, _, remainder = self._buffer.partition(b"\n")
            self._buffer[:] = remainder
            try:
                message = json.loads(raw.decode("utf-8"))
                if isinstance(message, dict):
                    print("BLUEFRUIT RX:", json.dumps(message, separators=(",", ":")))
                    messages.append(message)
            except (UnicodeError, ValueError):
                LOG.warning("Ungueltige JSON-Nachricht vom Bluefruit verworfen")
        return messages

    def send(self, message: Dict[str, Any]) -> None:
        payload = (json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8")
        self._serial.write(payload)

    def close(self) -> None:
        self._serial.close()


class SenseHatAdapter:
    COLORS = {"off": (0, 0, 0), "heating": (255, 0, 0), "cooling": (0, 0, 255)}

    def __init__(self, simulate: bool = False, simulated_humidity: float = 45.0):
        self._simulated_humidity = simulated_humidity
        self._sense: Optional[Any] = None
        if not simulate:
            try:
                from sense_hat import SenseHat
                self._sense = SenseHat()
            except (ImportError, OSError) as exc:
                LOG.warning("Sense HAT nicht verfuegbar; Simulationsmodus aktiv: %s", exc)

    def humidity(self) -> float:
        if self._sense is None:
            return round(self._simulated_humidity, 1)
        return round(float(self._sense.get_humidity()), 1)

    def display(self, heating: bool, cooling: bool) -> None:
        if self._sense is None:
            return
        mode = "heating" if heating else "cooling" if cooling else "off"
        self._sense.clear(*self.COLORS[mode])
