"""Verbindet Sensorik, Regelung, Aktorik und IoT-Server."""

import logging
import time
from datetime import date
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

        # Manuelle Storensteuerung. Standardmaessig arbeitet die Automatik.
        self._blind_mode = "auto"
        self._manual_blind: Optional[str] = None
        self._manual_blind_date: Optional[date] = None

    def step(self, now: Optional[float] = None) -> None:
        now = time.monotonic() if now is None else now

        self._reset_manual_blind_if_needed()

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

        # Im manuellen Modus hat der Benutzer Vorrang vor der Automatik.
        if (
            self._blind_mode == "manual"
            and self._manual_blind in ("open", "closed")
        ):
            effective_blind = self._manual_blind
        else:
            effective_blind = state.blind
        closed = effective_blind == "closed"
        
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
                "blind": effective_blind,
                "blind_mode": self._blind_mode,
                "heating": state.heating,
                "cooling": state.cooling,
                "target_temperature": self.controller.config.target_temperature,
                "temperature_deadband": self.controller.config.temperature_deadband,
            })
            self._last_status_sent = now

    def _handle_server_command(self, command: Dict[str, Any]) -> None:
        command_type = command.get("type")

        # Regelparameter vom IoT-Server verarbeiten.
        if command_type == "set_parameters":
            allowed = (
                "target_temperature",
                "temperature_deadband",
                "daylight_threshold",
                "passive_delay_seconds"
            )

            parameters = {
                key: command[key]
                for key in allowed
                if key in command
            }

            try:
                self.controller.set_parameters(**parameters)
            except (TypeError, ValueError) as exc:
                LOG.warning("Ungueltige Regelparameter: %s", exc)

            return
        
        # Klimaanlagenanzeige auf dem Sense HAT freigeben oder ausschalten.
        if command_type == "set_sense_neopixel":
            on = command.get("on")

            # Der Zustand muss eindeutig als true oder false uebertragen werden.
            if not isinstance(on, bool):
                LOG.warning(
                    "Ungueltiger Sense-HAT-NeoPixel-Befehl: %r",
                    command
                )
                return

            self.sense_hat.set_neopixels(on)

            LOG.info(
                "Klimaanlagenanzeige auf %s gesetzt",
                "EIN" if on else "AUS"
            )

            return
        
        # Storensteuerung automatisch oder manuell setzen.
        if command_type == "set_blind_mode":
            mode = command.get("mode")

            if mode == "auto":
                self._blind_mode = "auto"
                self._manual_blind = None
                self._manual_blind_date = None

                LOG.info("Storensteuerung auf AUTO gesetzt")
                return

            if mode == "manual":
                blind = command.get("blind")

                if blind not in ("open", "closed"):
                    LOG.warning(
                        "Ungueltiger manueller Storenbefehl: %r",
                        command
                    )
                    return

                self._blind_mode = "manual"
                self._manual_blind = blind
                self._manual_blind_date = date.today()

                LOG.info(
                    "Storensteuerung MANUELL: %s",
                    "OFFEN" if blind == "open" else "GESCHLOSSEN"
                )
                return

            LOG.warning("Ungueltiger Storenmodus: %r", command)
            return
        
        # Unbekannte Befehle nicht ausfuehren.
        LOG.warning("Unbekannter Serverbefehl: %r", command)

        def _reset_manual_blind_if_needed(self) -> None:
            if self._blind_mode != "manual":
                return

            if self._manual_blind_date is None:
                return

            if date.today() == self._manual_blind_date:
                return

            self._blind_mode = "auto"
            self._manual_blind = None
            self._manual_blind_date = None

            LOG.info(
                "Mitternacht erreicht: Storensteuerung wieder auf AUTO"
            )
