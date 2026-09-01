"""Nicht blockierende TCP/IP-Verbindung zum IoT-Server (JSON Lines)."""

import json
import logging
import socket
import time
from typing import Any, Dict, List, Optional


LOG = logging.getLogger(__name__)


class IoTServerClient:
    def __init__(self, host: str, port: int, reconnect_seconds: float = 5.0):
        self.host = host
        self.port = port
        self.reconnect_seconds = reconnect_seconds
        self._socket: Optional[socket.socket] = None
        self._buffer = bytearray()
        self._next_connect = 0.0

    def connect(self) -> bool:
        if self._socket is not None:
            return True
        now = time.monotonic()
        if now < self._next_connect:
            return False
        try:
            connection = socket.create_connection((self.host, self.port), timeout=1.0)
            connection.setblocking(False)
            self._socket = connection
            LOG.info("Mit IoT-Server %s:%s verbunden", self.host, self.port)
            return True
        except OSError as exc:
            self._next_connect = now + self.reconnect_seconds
            LOG.warning("IoT-Server nicht erreichbar: %s", exc)
            return False

    def send(self, message: Dict[str, Any]) -> bool:
        if not self.connect():
            return False
        try:
            payload = (json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8")
            self._socket.sendall(payload)
            return True
        except OSError:
            self._disconnect()
            return False

    def receive(self) -> List[Dict[str, Any]]:
        if not self.connect():
            return []
        try:
            while True:
                chunk = self._socket.recv(4096)
                if not chunk:
                    self._disconnect()
                    return []
                self._buffer.extend(chunk)
        except BlockingIOError:
            pass
        except OSError:
            self._disconnect()
            return []

        messages = []
        while b"\n" in self._buffer:
            raw, _, remainder = self._buffer.partition(b"\n")
            self._buffer[:] = remainder
            try:
                message = json.loads(raw.decode("utf-8"))
                if isinstance(message, dict):
                    messages.append(message)
            except (UnicodeError, ValueError):
                LOG.warning("Ungueltige Nachricht vom IoT-Server verworfen")
        return messages

    def close(self) -> None:
        self._disconnect()

    def _disconnect(self) -> None:
        if self._socket is not None:
            self._socket.close()
        self._socket = None
        self._next_connect = time.monotonic() + self.reconnect_seconds
