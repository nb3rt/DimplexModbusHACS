"""Number platform — live calibration of the estimation engine.

These write to Home Assistant only (not the heat pump), so they are NOT behind
the control/write gate. Values feed ``coordinator.tunables`` and are restored
across restarts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
    RestoreNumber,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pymodbus.exceptions import ModbusException

from .const import CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE, DOMAIN
from .entity import DimplexEntityMixin
from .registers import KIND_NUMBER, M_ENERGY, WriteSpec

NUMBER_DEVICE_CLASS_MAP = {"temperature": NumberDeviceClass.TEMPERATURE}


@dataclass(frozen=True)
class CalibrationSpec:
    key: str
    tunable: str
    name: str
    min_value: float
    max_value: float
    step: float
    unit: str | None = None
    icon: str | None = None


CALIBRATION: tuple[CalibrationSpec, ...] = (
    CalibrationSpec("cal_k_dhw", "k_dhw", "Calibration: DHW power factor", 0.90, 1.20, 0.01, icon="mdi:tune"),
    CalibrationSpec("cal_k_defrost", "k_defrost", "Calibration: defrost power factor", 0.90, 1.30, 0.01, icon="mdi:tune"),
    CalibrationSpec("cal_k_defrost_loss", "k_defrost_loss", "Calibration: defrost heat-loss factor", 0.20, 4.00, 0.05, icon="mdi:snowflake-melt"),
    CalibrationSpec("cal_heater_w", "heater_w", "Calibration: 2nd-source heater power", 0, 9000, 50, unit=UnitOfPower.WATT, icon="mdi:radiator"),
    CalibrationSpec("cal_pump_main_w", "pump_main_w", "Calibration: main pump power", 0, 400, 5, unit=UnitOfPower.WATT, icon="mdi:pump"),
    CalibrationSpec("cal_pump_floor_w", "pump_floor_w", "Calibration: floor pump power", 0, 400, 5, unit=UnitOfPower.WATT, icon="mdi:pump"),
    CalibrationSpec("cal_alpha_base", "alpha_base", "Calibration: alpha base", 0.0, 1.0, 0.01, icon="mdi:home-percent"),
    CalibrationSpec("cal_alpha_sensitivity", "alpha_sensitivity", "Calibration: alpha sensitivity", 0.0, 2.0, 0.05, icon="mdi:home-percent"),
    CalibrationSpec("cal_alpha_deadband", "alpha_deadband", "Calibration: alpha deadband", 0.0, 0.20, 0.01, icon="mdi:home-percent"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create calibration numbers (only when estimation is active)."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    host = data.get("host")
    version = coordinator.software_version
    model = data.get("model")

    entities: list[NumberEntity] = []

    # Calibration numbers (always, when estimation runs; write to HA not the pump).
    if coordinator.estimation_possible:
        entities.extend(
            DimplexCalibrationNumber(coordinator, entry, spec, host=host, version=version, model=model)
            for spec in CALIBRATION
        )

    # Writable setpoints (gated by enable_control; write to the heat pump).
    if data.get(CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE):
        entities.extend(
            DimplexWritableNumber(coordinator, entry, ws, host=host, version=version, model=model)
            for ws in coordinator.write_specs
            if ws.kind == KIND_NUMBER
        )

    async_add_entities(entities)


class DimplexCalibrationNumber(DimplexEntityMixin, CoordinatorEntity, RestoreNumber):
    """A live-tunable estimation parameter, persisted across restarts."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, entry, spec: CalibrationSpec, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._spec = spec
        self._apply_common(
            entry, key=spec.key, module=M_ENERGY, name=spec.name,
            host=host, software_version=version, model=model,
        )
        self._attr_native_min_value = spec.min_value
        self._attr_native_max_value = spec.max_value
        self._attr_native_step = spec.step
        if spec.unit:
            self._attr_native_unit_of_measurement = spec.unit
        if spec.icon:
            self._attr_icon = spec.icon
        self._attr_native_value = float(coordinator.tunables[spec.tunable])

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        if last is not None and last.native_value is not None:
            self._attr_native_value = float(last.native_value)
            self.coordinator.tunables[self._spec.tunable] = self._attr_native_value

    @property
    def available(self) -> bool:
        # Calibration is local config; always settable.
        return True

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        self.coordinator.tunables[self._spec.tunable] = value
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class DimplexWritableNumber(DimplexEntityMixin, CoordinatorEntity, NumberEntity):
    """A setpoint that writes a holding register on the heat pump (gated)."""

    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, entry, ws: WriteSpec, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._ws = ws
        self._apply_common(
            entry, key=ws.key, module=ws.module, name=ws.name,
            host=host, software_version=version, model=model,
        )
        self._attr_native_min_value = ws.min_value
        self._attr_native_max_value = ws.max_value
        self._attr_native_step = ws.step
        if ws.unit:
            self._attr_native_unit_of_measurement = ws.unit
        if ws.device_class:
            self._attr_device_class = NUMBER_DEVICE_CLASS_MAP.get(ws.device_class)
        if ws.icon:
            self._attr_icon = ws.icon

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("values", {}).get(self._ws.key)

    async def async_set_native_value(self, value: float) -> None:
        raw = self._ws.to_raw(value)
        try:
            await self.coordinator.write_register(self._ws.address, raw)
        except ModbusException as err:
            raise HomeAssistantError(
                f"Failed to write {self._ws.name}: {err}"
            ) from err
        await self.coordinator.async_request_refresh()
