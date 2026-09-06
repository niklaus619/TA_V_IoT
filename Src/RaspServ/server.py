"""Modbus-TCP-Server (FC03/FC16), Registerbelegung siehe README.md."""

import logging
import socketserver
import struct
import threading
import time

from database import initialize_database, save_measurement

LOG = logging.getLogger(__name__)


def _read_exact(sock, size):
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Modbus-Verbindung geschlossen")
        data.extend(chunk)
    return bytes(data)


class _TCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class _Handler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(5.0)
        owner = self.server.owner
        try:
            while True:
                transaction, protocol, length, unit = struct.unpack(">HHHB", _read_exact(self.request, 7))
                if protocol != 0 or not 2 <= length <= 254:
                    return
                pdu = _read_exact(self.request, length - 1)
                if unit != 1:
                    response = bytes([pdu[0] | 0x80, 11])
                else:
                    response = owner._process_pdu(pdu)
                self.request.sendall(struct.pack(">HHHB", transaction, 0, len(response) + 1, unit) + response)
        except OSError:
            pass


class RaspCtrlServer:
    def __init__(self, host="0.0.0.0", port=502):
        self.host, self.port = host, port
        self._lock = threading.RLock()
        self._status = [0] * 6
        self._commands = [0] * 8
        self._latest_status = {}
        self._last_seen = None
        self._tcp = None

    def bind(self):
        """Bindet vor dem Start der Webseite; Portfehler brechen den Start ab."""
        if self._tcp is None:
            self._tcp = _TCPServer((self.host, self.port), _Handler)
            self._tcp.owner = self
            self.port = self._tcp.server_address[1]
        return self

    def serve_forever(self):
        self.bind()
        LOG.info("Modbus TCP wartet auf %s:%s (Unit-ID 1)", self.host, self.port)
        self._tcp.serve_forever()

    def close(self):
        if self._tcp is not None:
            self._tcp.shutdown()
            self._tcp.server_close()
            self._tcp = None

    def _process_pdu(self, pdu):
        function = pdu[0]
        def error(code):
            return bytes([function | 0x80, code])

        with self._lock:
            if function == 3:
                if len(pdu) != 5:
                    return error(3)
                address, count = struct.unpack(">HH", pdu[1:])
                if not 1 <= count <= 125:
                    return error(3)
                if 0 <= address and address + count <= 6:
                    values = self._status[address:address + count]
                elif 100 <= address and address + count <= 108:
                    values = self._commands[address - 100:address - 100 + count]
                    self._last_seen = time.monotonic()
                else:
                    return error(2)
                return bytes([3, count * 2]) + struct.pack(">" + "H" * count, *values)
            if function != 16:
                return error(1)
            if len(pdu) < 6:
                return error(3)
            address, count, byte_count = struct.unpack(">HHB", pdu[1:6])
            if not 1 <= count <= 123 or byte_count != count * 2 or len(pdu) != 6 + byte_count:
                return error(3)
            # Ein kompletter Status wird atomar uebertragen und gespeichert.
            if address != 0 or count != 6:
                return error(2)
            values = list(struct.unpack(">6H", pdu[6:]))
            temperature, humidity, light, flags, target, deadband = values
            if humidity > 1000 or flags > 7 or not 50 <= target <= 350 or deadband == 0:
                return error(3)
            status = {
                "type": "status",
                "temperature": (temperature if temperature < 32768 else temperature - 65536) / 10,
                "humidity": humidity / 10,
                "light": light,
                "blind": "closed" if flags & 1 else "open",
                "heating": bool(flags & 2),
                "cooling": bool(flags & 4),
                "target_temperature": target / 10,
                "temperature_deadband": deadband / 10,
            }
            try:
                save_measurement(status)
            except Exception:
                LOG.exception("Messwert konnte nicht gespeichert werden")
                return error(4)
            self._status = values
            self._latest_status = status
            self._last_seen = time.monotonic()
            return pdu[:5]

    def get_latest_status(self):
        with self._lock:
            return self._latest_status.copy()

    def is_connected(self):
        with self._lock:
            return self._last_seen is not None and time.monotonic() - self._last_seen < 5.0

    def send_command(self, command):
        """Stellt Sollwerte bereit; RaspCtrl liest sie beim naechsten Poll."""
        updates = []
        if command["type"] == "set_parameters":
            for offset, key, low, high in (
                (0, "target_temperature", 50, 350),
                (2, "temperature_deadband", 1, 65535),
            ):
                if key in command:
                    value = round(float(command[key]) * 10)
                    if not low <= value <= high:
                        raise ValueError("Parameter ausserhalb des Modbus-Bereichs")
                    updates.append((offset, value))
        elif command["type"] == "set_sense_neopixel":
            if not isinstance(command["on"], bool):
                raise ValueError("on muss bool sein")
            updates.append((6, int(command["on"])))
        else:
            raise ValueError("Unbekannter Befehl")
        with self._lock:
            if not self.is_connected():
                raise ConnectionError("RaspCtrl ist nicht verbunden")
            for offset, value in updates:
                self._commands[offset] = self._commands[offset] % 65535 + 1
                self._commands[offset + 1] = value


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    initialize_database()
    RaspCtrlServer().serve_forever()


if __name__ == "__main__":
    main()
