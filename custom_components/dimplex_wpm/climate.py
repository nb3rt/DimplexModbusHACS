"""Climate platform — HC1 and DHW thermostats (behind the control gate).

Thin thermostats over existing pieces: current temperature from a coordinator
read value, target temperature from a writable setpoint register (reused from
the WriteSpec table, so encoding/range/read-back are shared with the number
platform). Only created when control/write entities are enabled.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pymodbus.exceptions import ModbusException

from .const import CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE, DOMAIN
from .entity import DimplexEntityMixin
from .registers import M_DHW, M_HC1


@dataclass(frozen=True)
class ClimateDef:
    key: str
    name: str
    module: str
    target_write_key: str  # WriteSpec.key providing the setpoint register
    current_keys: tuple[str, ...]  # coordinator value keys, first available wins
    icon: str | None = None


CLIMATES: tuple[ClimateDef, ...] = (
    ClimateDef(
        "thermostat", "Thermostat", M_HC1, "set_hc1_room_setpoint",
        ("room_temperature_1", "return_temperature"), icon="mdi:home-thermometer",
    ),
    ClimateDef(
        "thermostat", "Thermostat", M_DHW, "set_dhw_setpoint",
        ("dhw_temperature",), icon="mdi:water-thermometer",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create thermostats when control is enabled and the setpoint exists."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    if not data.get(CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE):
        return

    write_specs = {ws.key: ws for ws in coordinator.write_specs}
    host = data.get("host")
    version = coordinator.software_version
    model = data.get("model")

    entities = []
    for c in CLIMATES:
        ws = write_specs.get(c.target_write_key)
        if ws is None:
            continue
        entities.append(
            DimplexClimate(coordinator, entry, c, ws, host=host, version=version, model=model)
        )
    async_add_entities(entities)


class DimplexClimate(DimplexEntityMixin, CoordinatorEntity, ClimateEntity):
    """A single-mode heating thermostat backed by a setpoint register."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_hvac_mode = HVACMode.HEAT
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(self, coordinator, entry, cdef: ClimateDef, ws, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._cdef = cdef
        self._ws = ws
        self._apply_common(
            entry, key=cdef.key, module=cdef.module, name=cdef.name,
            host=host, software_version=version, model=model,
        )
        self._attr_min_temp = ws.min_value
        self._attr_max_temp = ws.max_value
        self._attr_target_temperature_step = ws.step
        if cdef.icon:
            self._attr_icon = cdef.icon

    @property
    def available(self) -> bool:
        # Writable: operable while the coordinator is updating.
        return self.coordinator.last_update_success

    @property
    def current_temperature(self) -> float | None:
        values = (self.coordinator.data or {}).get("values", {})
        for key in self._cdef.current_keys:
            val = values.get(key)
            if val is not None:
                return val
        return None

    @property
    def target_temperature(self) -> float | None:
        return (self.coordinator.data or {}).get("values", {}).get(self._ws.key)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        try:
            await self.coordinator.write_register(self._ws.address, self._ws.to_raw(temp))
        except ModbusException as err:
            raise HomeAssistantError(f"Failed to set {self._cdef.name}: {err}") from err
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        # Only HEAT is supported; nothing to switch.
        return
