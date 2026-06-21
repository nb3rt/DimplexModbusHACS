"""Binary sensor platform — coils + derived problem flags."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODULE_ROOT
from .entity import DimplexEntityMixin
from .registers import COIL, RegisterSpec

PARALLEL_UPDATES = 0  # read-only, coordinator-driven

DEVICE_CLASS_MAP = {
    "running": BinarySensorDeviceClass.RUNNING,
    "problem": BinarySensorDeviceClass.PROBLEM,
}
ENTITY_CATEGORY_MAP = {
    "diagnostic": EntityCategory.DIAGNOSTIC,
    "config": EntityCategory.CONFIG,
}

# Derived (not register-backed) problem flags: (key, name).
DERIVED_PROBLEMS = (
    ("fault_active", "Fault active"),
    ("lock_active", "Lock active"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create binary sensors from coils and derived flags."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    host = data.get("host")
    version = coordinator.software_version
    model = data.get("model")

    entities: list[BinarySensorEntity] = []
    for spec in coordinator.specs:
        if spec.obj == COIL:
            entities.append(
                DimplexCoilBinarySensor(coordinator, entry, spec, host=host, version=version, model=model)
            )
    for key, name in DERIVED_PROBLEMS:
        entities.append(
            DimplexProblemBinarySensor(coordinator, entry, key, name, host=host, version=version, model=model)
        )

    async_add_entities(entities)


class DimplexCoilBinarySensor(DimplexEntityMixin, CoordinatorEntity, BinarySensorEntity):
    """A coil-backed binary sensor."""

    def __init__(self, coordinator, entry, spec: RegisterSpec, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._spec = spec
        self._apply_common(
            entry, key=spec.key, module=spec.module, name=spec.name,
            host=host, software_version=version, model=model,
        )
        if spec.device_class:
            self._attr_device_class = DEVICE_CLASS_MAP.get(spec.device_class)
        if spec.entity_category:
            self._attr_entity_category = ENTITY_CATEGORY_MAP.get(spec.entity_category)

    @property
    def is_on(self) -> bool | None:
        return (self.coordinator.data or {}).get("values", {}).get(self._spec.key)


class DimplexProblemBinarySensor(DimplexEntityMixin, CoordinatorEntity, BinarySensorEntity):
    """A derived problem flag (fault/lock active)."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, entry, key: str, name: str, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._key = key
        self._apply_common(
            entry, key=key, module=MODULE_ROOT, name=name,
            host=host, software_version=version, model=model,
        )

    @property
    def is_on(self) -> bool | None:
        return (self.coordinator.data or {}).get("values", {}).get(self._key)
