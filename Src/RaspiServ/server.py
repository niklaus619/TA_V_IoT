"""TCP-Server fuer die Kommunikation mit RaspCtrl."""

from ast import main
from email import message
import json
import logging
import socket
import threading
from typing import Any, Dict, Optional
from database import save_measurement


LOG = logging.getLogger(__name__)


class RaspCtrlServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 9000):
        self.host = host
        self.port = port

        self._client: Optional[socket.socket] = None
        self._client_lock = threading.Lock()

        self._latest_status: Dict[str, Any] = {}
        self._status_lock = threading.Lock()

    def serve_forever(self) -> None:
        """Startet den TCP-Server und wartet auf RaspCtrl."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1,
            )

            server_socket.bind((self.host, self.port))
            server_socket.listen(1)

            LOG.info(
                "RaspServ wartet auf Verbindung auf %s:%s",
                self.host,
                self.port,
            )

            while True:
                client, address = server_socket.accept()

                LOG.info(
                    "RaspCtrl verbunden: %s:%s",
                    address[0],
                    address[1],
                )

                with self._client_lock:
                    self._client = client

                try:
                    self._handle_client(client)
                except OSError as exc:
                    LOG.warning("Verbindung zu RaspCtrl verloren: %s", exc)
                finally:
                    with self._client_lock:
                        if self._client is client:
                            self._client = None

                    client.close()

                    LOG.info("RaspCtrl getrennt")

    def _handle_client(self, client: socket.socket) -> None:
        """Empfaengt JSON-Lines von RaspCtrl."""

        buffer = bytearray()

        while True:
            data = client.recv(4096)

            if not data:
                return

            buffer.extend(data)

            while b"\n" in buffer:
                raw_message, _, remainder = buffer.partition(b"\n")
                buffer[:] = remainder

                if not raw_message:
                    continue

                try:
                    message = json.loads(raw_message.decode("utf-8"))
                except (UnicodeError, json.JSONDecodeError):
                    LOG.warning(
                        "Ungueltige Nachricht empfangen: %r",
                        raw_message,
                    )
                    continue

                if not isinstance(message, dict):
                    continue

                self._process_message(message)

    def _process_message(self, message: Dict[str, Any]) -> None:
        """Verarbeitet Nachrichten von RaspCtrl."""

        if message.get("type") == "status":
            with self._status_lock:
                self._latest_status = message.copy()

            save_measurement(message)

            LOG.info("Status von RaspCtrl: %s", message)

        else:
            LOG.info("Nachricht von RaspCtrl: %s", message)


    def get_latest_status(self) -> Dict[str, Any]:
        """Gibt den zuletzt empfangenen Status zurueck."""

        with self._status_lock:
            return self._latest_status.copy()


    def is_connected(self) -> bool:
        """Prueft, ob RaspCtrl verbunden ist."""

        with self._client_lock:
            return self._client is not None


    def send_command(self, command: Dict[str, Any]) -> None:
        """Sendet einen JSON-Befehl an RaspCtrl."""

        payload = (
            json.dumps(command, separators=(",", ":")) + "\n"
        ).encode("utf-8")

        with self._client_lock:
            if self._client is None:
                raise ConnectionError("RaspCtrl ist nicht verbunden")

            self._client.sendall(payload)

    def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    server = RaspCtrlServer()
    server.serve_forever()


if __name__ == "__main__":
    main()