"""Device helpers for Dimplex WPM."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry

from .const import (
    DEVICE_MANUFACTURER,
    DEVICE_NAME,
    DOMAIN,
    MODULE_NAME_MAP,
    MODULE_ROOT,
)


def build_device_info(
    entry: ConfigEntry,
    module: str,
    *,
    host: str | None = None,
    configuration_url: str | None = None,
    software_version: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Return device info for the requested module (medium device tree)."""
    base_identifier = (DOMAIN, entry.entry_id)
    if module == MODULE_ROOT:
        identifiers = {base_identifier}
    else:
        identifiers = {(DOMAIN, f"{entry.entry_id}_{module}")}

    if module == MODULE_ROOT:
        name = f"{DEVICE_NAME} ({host})" if host else DEVICE_NAME
    else:
        name = MODULE_NAME_MAP.get(module, module)

    device_info: dict[str, Any] = {
        "identifiers": identifiers,
        "manufacturer": DEVICE_MANUFACTURER,
        "name": name,
    }
    if configuration_url:
        device_info["configuration_url"] = configuration_url

    if module == MODULE_ROOT:
        if software_version:
            device_info["sw_version"] = software_version
        if model:
            device_info["model"] = model
    else:
        device_info["via_device"] = base_identifier

    return device_info
