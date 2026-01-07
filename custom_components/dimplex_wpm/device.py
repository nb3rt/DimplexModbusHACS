"""Device helpers for Dimplex WPM."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry

from .const import DEVICE_MANUFACTURER, DOMAIN, MODULE_NAME_MAP, MODULE_ROOT


def build_device_info(
    entry: ConfigEntry,
    module: str,
    *,
    host: str | None = None,
    configuration_url: str | None = None,
) -> dict[str, Any]:
    """Return device info for the requested module."""
    base_identifier = (DOMAIN, entry.entry_id)
    identifiers = {base_identifier} if module == MODULE_ROOT else {(DOMAIN, f"{entry.entry_id}_{module}")}
    name = MODULE_NAME_MAP.get(module, MODULE_NAME_MAP[MODULE_ROOT])
    if module == MODULE_ROOT and host:
        name = f"{name} ({host})"
    device_info: dict[str, Any] = {
        "identifiers": identifiers,
        "manufacturer": DEVICE_MANUFACTURER,
        "name": name,
    }
    if configuration_url:
        device_info["configuration_url"] = configuration_url

    if module != MODULE_ROOT:
        device_info["via_device"] = base_identifier

    return device_info
