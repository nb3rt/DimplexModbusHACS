"""Dimplex WPM integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .const import (
    CAPABILITY_CONF_MAP,
    CONF_ENABLE_WRITE_ENTITIES,
    CONF_ENABLED_MODULES,
    CONF_FLOW_SENSOR_ENTITY,
    CONF_INCLUDE_RE_REGISTERS,
    CONF_PROFILE,
    CONF_SCAN_INTERVAL,
    CONF_SOFTWARE_VERSION,
    CONF_TIMEOUT,
    CONF_UNIT_ID,
    DEFAULT_ENABLE_WRITE,
    DEFAULT_PROFILE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SOFTWARE_VERSION,
    DEFAULT_TIMEOUT,
    DEFAULT_UNIT_ID,
    DOMAIN,
    resolve_capabilities,
    resolve_enabled_modules,
)
from .coordinator import DimplexDataUpdateCoordinator
from .modbus_client import DimplexModbusClient
from .profiles import get_profile
from .registers import CAP_INVERTER_FREQ, CORE_MODULES

LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.CLIMATE,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dimplex WPM from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    source = {**entry.data, **entry.options}
    host = source[CONF_HOST]
    port = source.get(CONF_PORT, 502)
    unit_id = source.get(CONF_UNIT_ID, DEFAULT_UNIT_ID)
    timeout = source.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
    scan_interval = source.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    software_version = source.get(CONF_SOFTWARE_VERSION, DEFAULT_SOFTWARE_VERSION)

    profile = get_profile(source.get(CONF_PROFILE, DEFAULT_PROFILE))

    if CONF_ENABLED_MODULES in source:
        enabled_modules = resolve_enabled_modules(source)
    else:
        enabled_modules = frozenset(CORE_MODULES) | profile.default_modules

    if any(key in source for key in CAPABILITY_CONF_MAP):
        capabilities = resolve_capabilities(source)
    else:
        capabilities = profile.default_capabilities

    include_re = source.get(
        CONF_INCLUDE_RE_REGISTERS, CAP_INVERTER_FREQ in capabilities
    )
    enable_control = entry.options.get(CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE)

    client = DimplexModbusClient(host, port, unit_id, timeout)
    coordinator = DimplexDataUpdateCoordinator(
        hass,
        client,
        scan_interval=scan_interval,
        software_version=software_version,
        enabled_modules=enabled_modules,
        capabilities=capabilities,
        include_re=include_re,
        profile=profile,
        flow_sensor_entity=source.get(CONF_FLOW_SENSOR_ENTITY) or None,
        enable_control=enable_control,
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
        "software_version": software_version,
        "profile": profile.key,
        "model": profile.name,
        CONF_ENABLE_WRITE_ENTITIES: entry.options.get(
            CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE
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
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
