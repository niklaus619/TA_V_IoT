"""Autonome Raumklimaregelung fuer Raspberry Pi 1."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ControlConfig:
    target_temperature: float = 22.0
    temperature_deadband: float = 0.5
    daylight_threshold: float = 100.0
    passive_delay_seconds: float = 120.0


@dataclass(frozen=True)
class ControlState:
    blind: str = "open"
    heating: bool = False
    cooling: bool = False


class ClimateController:
    """Regelt Store, Heizung und Kuehlung mit einer Totzone."""

    def __init__(self, config: Optional[ControlConfig] = None):
        self.config = config or ControlConfig()
        self.state = ControlState()
        self._passive_action_started: Optional[float] = None
        self._mode = "normal"

    def update(self, temperature: float, light: float, now: float) -> ControlState:
        upper = self.config.target_temperature + self.config.temperature_deadband
        lower = self.config.target_temperature - self.config.temperature_deadband
        daylight = light >= self.config.daylight_threshold

        if temperature > upper:
            self._enter_mode("cooling", now)
            if daylight:
                active = now - self._passive_action_started >= self.config.passive_delay_seconds
                self.state = ControlState("closed", cooling=active)
            else:
                self.state = ControlState(self.state.blind, cooling=True)
        elif temperature < lower:
            self._enter_mode("heating", now)
            if daylight:
                active = now - self._passive_action_started >= self.config.passive_delay_seconds
                self.state = ControlState("open", heating=active)
            else:
                self.state = ControlState(self.state.blind, heating=True)
        else:
            self._mode = "normal"
            self._passive_action_started = None
            self.state = ControlState(self.state.blind)

        return self.state

    def set_parameters(
        self,
        target_temperature: Optional[float] = None,
        temperature_deadband: Optional[float] = None,
        daylight_threshold: Optional[float] = None,
        passive_delay_seconds: Optional[float] = None,
    ) -> None:
        values = {
            "target_temperature": self.config.target_temperature if target_temperature is None else float(target_temperature),
            "temperature_deadband": self.config.temperature_deadband if temperature_deadband is None else float(temperature_deadband),
            "daylight_threshold": self.config.daylight_threshold if daylight_threshold is None else float(daylight_threshold),
            "passive_delay_seconds": self.config.passive_delay_seconds if passive_delay_seconds is None else float(passive_delay_seconds),
        }
        if not 5.0 <= values["target_temperature"] <= 35.0:
            raise ValueError("target_temperature muss zwischen 5 und 35 Grad liegen")
        if values["temperature_deadband"] <= 0:
            raise ValueError("temperature_deadband muss groesser als 0 sein")
        if values["daylight_threshold"] < 0 or values["passive_delay_seconds"] < 0:
            raise ValueError("Schwellwert und Verzoegerung duerfen nicht negativ sein")
        self.config = ControlConfig(**values)

    def _enter_mode(self, mode: str, now: float) -> None:
        if self._mode != mode:
            self._mode = mode
            self._passive_action_started = now
