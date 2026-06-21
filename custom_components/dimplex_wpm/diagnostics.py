"""Diagnostics for the Dimplex WPM integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {CONF_HOST, "host"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    return {
        "entry": {
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
        },
        "config": {
            "profile": data.get("profile"),
            "model": data.get("model"),
            "software_version": coordinator.software_version,
            "enabled_modules": sorted(coordinator.enabled_modules),
            "capabilities": sorted(coordinator.capabilities),
            "estimation_possible": coordinator.estimation_possible,
            "enable_control": coordinator.enable_control,
            "active_register_count": len(coordinator.specs),
            "energy_groups": [g.key for g in coordinator.energy_groups],
            "write_specs": [w.key for w in coordinator.write_specs],
            "tunables": coordinator.tunables,
        },
        "data": async_redact_data(coordinator.data or {}, TO_REDACT),
    }
