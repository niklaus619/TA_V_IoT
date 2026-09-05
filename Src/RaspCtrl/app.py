"""Verbindet Sensorik, Regelung, Aktorik und IoT-Server."""

import logging
import time
from typing import Any, Dict, Optional

from controller import ClimateController


LOG = logging.getLogger(__name__)


class RaspiControllerApp:
    def __init__(self, bluefruit: Any, sense_hat: Any, controller: ClimateController, server: Optional[Any] = None):
        self.bluefruit = bluefruit
        self.sense_hat = sense_hat
        self.controller = controller
        self.server = server
        self._sensor_data: Optional[Dict[str, Any]] = None
        self._last_blind_command: Optional[bool] = None
        self._last_status_sent = 0.0

    def step(self, now: Optional[float] = None) -> None:
        now = time.monotonic() if now is None else now
        for message in self.bluefruit.receive():
            if message.get("type") == "status":
                self._sensor_data = message

        if self.server is not None:
            for command in self.server.receive():
                self._handle_server_command(command)

        if self._sensor_data is None:
            return
        try:
            temperature = float(self._sensor_data["temperature"])
            light = float(self._sensor_data["light"])
        except (KeyError, TypeError, ValueError):
            LOG.warning("Unvollstaendige Sensordaten: %r", self._sensor_data)
            return

        state = self.controller.update(temperature, light, now)
        closed = state.blind == "closed"
        if closed != self._last_blind_command:
            self.bluefruit.send({"type": "set_blind", "closed": closed})
            self._last_blind_command = closed

        self.sense_hat.display(state.heating, state.cooling)
        if self.server is not None and now - self._last_status_sent >= 1.0:
            self.server.send({
                "type": "status",
                "temperature": temperature,
                "light": light,
                "humidity": self.sense_hat.humidity(),
                "blind": state.blind,
                "heating": state.heating,
                "cooling": state.cooling,
                "target_temperature": self.controller.config.target_temperature,
                "temperature_deadband": self.controller.config.temperature_deadband,
            })
            self._last_status_sent = now

    def _handle_server_command(self, command: Dict[str, Any]) -> None:
        if command.get("type") != "set_parameters":
            LOG.warning("Unbekannter Serverbefehl: %r", command)
            return
        allowed = ("target_temperature", "temperature_deadband", "daylight_threshold", "passive_delay_seconds")
        parameters = {key: command[key] for key in allowed if key in command}
        try:
            self.controller.set_parameters(**parameters)
        except (TypeError, ValueError) as exc:
            LOG.warning("Ungueltige Regelparameter: %s", exc)
