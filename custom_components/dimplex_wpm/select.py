"""Select entity for SG Ready mode."""

from __future__ import annotations

from pymodbus.exceptions import ModbusException

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_ENABLE_WRITE_ENTITIES,
    DEFAULT_ENABLE_WRITE,
    DOMAIN,
    MODULE_SG,
    REG_SG_READY_MODE,
    SG_READY_MAP,
    SG_READY_REVERSE,
)
from .device import build_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entity."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    allow_write = data.get(CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE)

    async_add_entities(
        [DimplexSGReadySelect(coordinator, entry, allow_write)],
    )


class DimplexSGReadySelect(CoordinatorEntity, SelectEntity):
    """Representation of the SG Ready mode select."""

    _attr_has_entity_name = True
    _attr_translation_key = "sg_ready_mode"

    def __init__(self, coordinator, entry: ConfigEntry, allow_write: bool) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._allow_write = allow_write
        self._attr_unique_id = f"{entry.entry_id}_{MODULE_SG}_sg_ready_mode"
        self._attr_device_info = build_device_info(entry, MODULE_SG)

    @property
    def current_option(self) -> str | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data["derived"].get("sg_ready_text")

    @property
    def options(self) -> list[str]:
        return list(SG_READY_REVERSE.keys())

    @property
    def available(self) -> bool:
        return super().available and self._allow_write

    async def async_select_option(self, option: str) -> None:
        if not self._allow_write:
            raise HomeAssistantError("Write entities are disabled in options")

        if option not in SG_READY_REVERSE:
            raise HomeAssistantError(f"Invalid option {option}")
        value = SG_READY_REVERSE[option]
        try:
            await self.coordinator.write_sg_ready(REG_SG_READY_MODE, value)
            await self.coordinator.async_request_refresh()
        except ModbusException as err:
            raise HomeAssistantError(f"Failed to write SG Ready value: {err}") from err
