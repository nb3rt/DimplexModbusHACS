"""Init file for Dimplex WPM integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_ENABLE_BMS_TEMP,
    CONF_ENABLE_EMS,
    CONF_ENABLE_EXTERNAL_LOCK,
    CONF_ENABLE_WRITE_ENTITIES,
    CONF_REGISTER_STRATEGY,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_UNIT_ID,
    DEFAULT_ENABLE_WRITE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DEFAULT_UNIT_ID,
    DOMAIN,
)
from .coordinator import DimplexDataUpdateCoordinator
from .modbus_client import DimplexModbusClient

LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SELECT]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up via configuration.yaml is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dimplex WPM from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, 502)
    unit_id = entry.data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID)
    timeout = entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    register_strategy = entry.data.get(CONF_REGISTER_STRATEGY, "auto")

    client = DimplexModbusClient(host, port, unit_id, timeout)
    coordinator = DimplexDataUpdateCoordinator(
        hass,
        client,
        scan_interval=scan_interval,
        register_strategy=register_strategy,
        host=host,
        port=port,
        unit_id=unit_id,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
        "host": host,
        "port": port,
        "unit_id": unit_id,
        CONF_ENABLE_WRITE_ENTITIES: entry.options.get(
            CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE
        ),
        CONF_ENABLE_EMS: entry.options.get(CONF_ENABLE_EMS, False),
        CONF_ENABLE_BMS_TEMP: entry.options.get(CONF_ENABLE_BMS_TEMP, False),
        CONF_ENABLE_EXTERNAL_LOCK: entry.options.get(
            CONF_ENABLE_EXTERNAL_LOCK, False
        ),
    }

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["client"].close()
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update by reloading entry."""
    await hass.config_entries.async_reload(entry.entry_id)
