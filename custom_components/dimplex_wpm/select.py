"""Select entity for SG Ready mode."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pymodbus.exceptions import ModbusException

from .const import (
    CONF_ENABLE_WRITE_ENTITIES,
    DEFAULT_ENABLE_WRITE,
    DOMAIN,
    MODULE_ROOT,
    REG_SG_READY_MODE,
    SG_READY_REVERSE,
)
from .device import build_device_info
from .entity import DimplexEntityMixin
from .registers import KIND_SELECT, WriteSpec

PARALLEL_UPDATES = 1  # serialize writes to the controller


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entity."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    allow_write = data.get(CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE)

    if not allow_write:
        return

    host = data.get("host")
    version = data.get("software_version")
    model = data.get("model")

    entities: list[SelectEntity] = [
        DimplexSGReadySelect(
            coordinator, entry, allow_write, host=host, software_version=version, model=model
        )
    ]
    entities.extend(
        DimplexWriteSelect(coordinator, entry, ws, host=host, version=version, model=model)
        for ws in coordinator.write_specs
        if ws.kind == KIND_SELECT
    )
    async_add_entities(entities)


class DimplexSGReadySelect(CoordinatorEntity, SelectEntity):
    """Representation of the SG Ready mode select."""

    _attr_has_entity_name = True
    _attr_translation_key = "sg_ready_mode"

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        allow_write: bool,
        *,
        host: str | None = None,
        software_version: str | None = None,
        model: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._allow_write = allow_write
        self._attr_unique_id = f"{entry.entry_id}_{MODULE_ROOT}_sg_ready_mode"
        configuration_url = f"http://{host}" if host else None
        self._attr_device_info = build_device_info(
            entry,
            MODULE_ROOT,
            host=host,
            configuration_url=configuration_url,
            software_version=software_version,
            model=model,
        )

    @property
    def current_option(self) -> str | None:
        if not self.coordinator.data:
            return None
        value = self.coordinator.data.get("values", {}).get("sg_ready_text")
        # Guard against unmapped device codes ("Unknown (x)") not in options.
        return value if value in SG_READY_REVERSE else None

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


class DimplexWriteSelect(DimplexEntityMixin, CoordinatorEntity, SelectEntity):
    """A holding-register select backed by a WriteSpec options_map (gated)."""

    def __init__(self, coordinator, entry: ConfigEntry, ws: WriteSpec, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._ws = ws
        self._reverse = {label: code for code, label in (ws.options_map or {}).items()}
        self._apply_common(
            entry, key=ws.key, module=ws.module, name=ws.name,
            host=host, software_version=version, model=model,
        )
        self._attr_options = list((ws.options_map or {}).values())
        if ws.icon:
            self._attr_icon = ws.icon

    @property
    def available(self) -> bool:
        # Writable: keep operable even if the read-back register is missing.
        return self.coordinator.last_update_success

    @property
    def current_option(self) -> str | None:
        raw = (self.coordinator.data or {}).get("values", {}).get(self._ws.key)
        if raw is None:
            return None
        return (self._ws.options_map or {}).get(raw)

    async def async_select_option(self, option: str) -> None:
        if option not in self._reverse:
            raise HomeAssistantError(f"Invalid option {option}")
        try:
            await self.coordinator.write_register(self._ws.address, self._reverse[option])
        except ModbusException as err:
            raise HomeAssistantError(f"Failed to write {self._ws.name}: {err}") from err
        await self.coordinator.async_request_refresh()
