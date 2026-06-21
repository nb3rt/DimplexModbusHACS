"""Sensor platform — entities generated from the register table."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODULE_ROOT
from .entity import DimplexEntityMixin
from .registers import HOLDING, RegisterSpec, EnergyGroup

DEVICE_CLASS_MAP = {
    "temperature": SensorDeviceClass.TEMPERATURE,
    "power": SensorDeviceClass.POWER,
    "energy": SensorDeviceClass.ENERGY,
    "humidity": SensorDeviceClass.HUMIDITY,
    "frequency": SensorDeviceClass.FREQUENCY,
}
STATE_CLASS_MAP = {
    "measurement": SensorStateClass.MEASUREMENT,
    "total_increasing": SensorStateClass.TOTAL_INCREASING,
    "total": SensorStateClass.TOTAL,
}
ENTITY_CATEGORY_MAP = {
    "diagnostic": EntityCategory.DIAGNOSTIC,
    "config": EntityCategory.CONFIG,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create sensor entities from the coordinator's active register set."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    host = data.get("host")
    version = coordinator.software_version
    model = data.get("model")

    entities: list[SensorEntity] = [
        DimplexControllerInfo(coordinator, entry, host=host, version=version, model=model)
    ]
    for spec in coordinator.specs:
        if spec.obj == HOLDING:
            entities.append(
                DimplexSensor(coordinator, entry, spec, host=host, version=version, model=model)
            )
    for group in coordinator.energy_groups:
        entities.append(
            DimplexEnergySensor(coordinator, entry, group, host=host, version=version, model=model)
        )

    async_add_entities(entities)


class DimplexSensor(DimplexEntityMixin, CoordinatorEntity, SensorEntity):
    """A register-backed sensor."""

    def __init__(self, coordinator, entry, spec: RegisterSpec, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._spec = spec
        self._apply_common(
            entry, key=spec.key, module=spec.module, name=spec.name,
            host=host, software_version=version, model=model,
        )
        if spec.device_class:
            self._attr_device_class = DEVICE_CLASS_MAP.get(spec.device_class)
        if spec.state_class:
            self._attr_state_class = STATE_CLASS_MAP.get(spec.state_class)
        if spec.entity_category:
            self._attr_entity_category = ENTITY_CATEGORY_MAP.get(spec.entity_category)
        if spec.unit:
            self._attr_native_unit_of_measurement = spec.unit
        if spec.icon:
            self._attr_icon = spec.icon

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("values", {}).get(self._spec.key)


class DimplexEnergySensor(DimplexEntityMixin, CoordinatorEntity, SensorEntity):
    """A combined digit-group energy counter (kWh)."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator, entry, group: EnergyGroup, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._group = group
        self._apply_common(
            entry, key=group.key, module=group.module, name=group.name,
            host=host, software_version=version, model=model,
        )
        self._attr_extra_state_attributes = {"source": "measured"}

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("values", {}).get(self._group.key)


class DimplexControllerInfo(DimplexEntityMixin, CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing connection/config metadata."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:heat-pump"

    def __init__(self, coordinator, entry, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._meta_extra = {
            "host": host,
            "software_version": version,
            "model": model,
        }
        self._apply_common(
            entry, key="controller_info", module=MODULE_ROOT, name="Controller info",
            host=host, software_version=version, model=model,
        )

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("values", {}).get("controller_info")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        meta = (self.coordinator.data or {}).get("meta", {})
        return {
            **self._meta_extra,
            "port": meta.get("port"),
            "unit_id": meta.get("unit_id"),
            "profile": meta.get("profile"),
            "last_update": meta.get("last_update"),
            "consecutive_failures": meta.get("consecutive_failures"),
            "enabled_modules": sorted(self.coordinator.enabled_modules),
            "capabilities": sorted(self.coordinator.capabilities),
        }
