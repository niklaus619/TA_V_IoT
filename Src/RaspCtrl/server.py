"""Modbus TCP im Hintergrund, damit Netzwerkausfaelle die Regelung nicht blockieren."""

import logging
import socket
import struct
import threading
import time

LOG = logging.getLogger(__name__)


def _read_exact(sock, size):
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Modbus-Verbindung geschlossen")
        data.extend(chunk)
    return bytes(data)


class IoTServerClient:
    def __init__(self, host, port=502, reconnect_seconds=5.0):
        self.host, self.port = host, port
        self.reconnect_seconds = reconnect_seconds
        self._socket = None
        self._transaction = 0
        self._next_connect = 0.0
        self._lock = threading.Lock()
        self._pending_status = None
        self._commands = []
        self._seen = [None] * 4
        self._stop = threading.Event()
        self._thread = None

    def _start(self):
        with self._lock:
            if self._thread is None and not self._stop.is_set():
                self._thread = threading.Thread(target=self._run, daemon=True)
                self._thread.start()

    def connect(self):
        """Nur vom Netzwerk-Thread aufrufen."""
        if self._socket is not None:
            return True
        if time.monotonic() < self._next_connect:
            return False
        try:
            self._socket = socket.create_connection((self.host, self.port), timeout=1.0)
            self._seen = [None] * 4
            LOG.info("Mit Modbus-Server %s:%s verbunden", self.host, self.port)
            return True
        except OSError as exc:
            self._next_connect = time.monotonic() + self.reconnect_seconds
            LOG.warning("Modbus-Server %s:%s nicht erreichbar: %s", self.host, self.port, exc)
            return False

    def _request(self, pdu):
        self._transaction = (self._transaction + 1) & 65535
        self._socket.sendall(struct.pack(">HHHB", self._transaction, 0, len(pdu) + 1, 1) + pdu)
        transaction, protocol, length, unit = struct.unpack(">HHHB", _read_exact(self._socket, 7))
        if (transaction, protocol, unit) != (self._transaction, 0, 1) or not 2 <= length <= 254:
            raise OSError("Ungueltiger Modbus-Header")
        response = _read_exact(self._socket, length - 1)
        if response[0] != pdu[0]:
            raise OSError("Modbus-Fehlerantwort: " + response.hex())
        return response

    def send(self, message):
        """Merkt den neuesten Status fuer den naechsten Netzwerkzyklus vor."""
        try:
            temperature = round(float(message["temperature"]) * 10)
            values = [
                temperature & 65535,
                round(float(message["humidity"]) * 10),
                round(float(message["light"])),
                int(message["blind"] == "closed") | (int(bool(message["heating"])) << 1) | (int(bool(message["cooling"])) << 2),
                round(float(message["target_temperature"]) * 10),
                round(float(message["temperature_deadband"]) * 10),
            ]
            if not -32768 <= temperature <= 32767 or not 0 <= values[1] <= 1000 or not 50 <= values[4] <= 350 or not 1 <= values[5] <= 65535:
                raise ValueError("Messwerte ausserhalb des Registerbereichs")
            payload = struct.pack(">BHHB6H", 16, 0, 6, 12, *values)
        except (KeyError, TypeError, ValueError, OverflowError, struct.error) as exc:
            LOG.warning("Status nicht uebertragbar: %s", exc)
            return False
        with self._lock:
            self._pending_status = payload
        self._start()
        return True

    def receive(self):
        self._start()
        with self._lock:
            commands, self._commands = self._commands, []
        return commands

    def _run(self):
        while not self._stop.is_set():
            if self.connect():
                try:
                    response = self._request(struct.pack(">BHH", 3, 100, 8))
                    if len(response) != 18 or response[1] != 16:
                        raise OSError("Ungueltige Registerantwort")
                    registers = struct.unpack(">8H", response[2:])
                    commands = []

                    # Alle vier Befehlspaare auswerten.
                    for index in (0, 1, 2, 3):
                        revision, value = registers[index * 2:index * 2 + 2]
                        pair = (revision, value)

                        if revision and pair != self._seen[index]:

                            if index < 2:
                                key = (
                                    "target_temperature",
                                    "temperature_deadband"
                                )[index]

                                commands.append({
                                    "type": "set_parameters",
                                    key: value / 10
                                })

                            elif index == 2:
                                # Register 104/105:
                                # 0 = AUTO
                                # 1 = MANUELL OFFEN
                                # 2 = MANUELL GESCHLOSSEN
                                if value == 0:
                                    commands.append({
                                        "type": "set_blind_mode",
                                        "mode": "auto"
                                    })

                                elif value == 1:
                                    commands.append({
                                        "type": "set_blind_mode",
                                        "mode": "manual",
                                        "blind": "open"
                                    })

                                elif value == 2:
                                    commands.append({
                                        "type": "set_blind_mode",
                                        "mode": "manual",
                                        "blind": "closed"
                                    })

                                else:
                                    LOG.warning(
                                        "Ungueltiger Storenbefehl aus Modbus: %s",
                                        value
                                    )

                            else:
                                commands.append({
                                    "type": "set_sense_neopixel",
                                    "on": bool(value)
                                })

                        self._seen[index] = pair
                    with self._lock:
                        # Begrenzt auf den neuesten Befehl pro Parameter/Aktor.
                        for command in commands:
                            self._commands = [old for old in self._commands if old.keys() != command.keys() or old["type"] != command["type"]]
                            self._commands.append(command)
                        pending = self._pending_status
                    if pending is not None:
                        if self._request(pending) != pending[:5]:
                            raise OSError("Ungueltige Schreibbestaetigung")
                        with self._lock:
                            if self._pending_status is pending:
                                self._pending_status = None
                except OSError as exc:
                    LOG.warning("Modbus-Verbindung unterbrochen: %s", exc)
                    self._disconnect()
            self._stop.wait(0.25)

    def close(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=3.0)
        self._disconnect()

    def _disconnect(self):
        if self._socket is not None:
            self._socket.close()
        self._socket = None
        self._next_connect = time.monotonic() + self.reconnect_seconds
