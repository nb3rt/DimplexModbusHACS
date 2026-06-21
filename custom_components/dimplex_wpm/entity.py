"""Shared base for Dimplex WPM coordinator entities."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry

from .device import build_device_info


class DimplexEntityMixin:
    """Common device-info, unique-id and availability for all entities.

    Use as the first base, e.g. ``class DimplexSensor(DimplexEntityMixin,
    CoordinatorEntity, SensorEntity)``. The platform __init__ must call
    :meth:`_apply_common` after ``CoordinatorEntity.__init__``.
    """

    _attr_has_entity_name = True
    _dimplex_key: str = ""

    def _apply_common(
        self,
        entry: ConfigEntry,
        *,
        key: str,
        module: str,
        name: str | None,
        host: str | None = None,
        software_version: str | None = None,
        model: str | None = None,
    ) -> None:
        self._dimplex_key = key
        self._attr_unique_id = f"{entry.entry_id}_{module}_{key}"
        if name is not None:
            self._attr_name = name
        configuration_url = f"http://{host}" if host else None
        self._attr_device_info = build_device_info(
            entry,
            module,
            host=host,
            configuration_url=configuration_url,
            software_version=software_version,
            model=model,
        )

    @property
    def available(self) -> bool:
        """Entity is available when its value is present in coordinator data."""
        coordinator = self.coordinator  # type: ignore[attr-defined]
        if not coordinator.last_update_success:
            return False
        data = coordinator.data or {}
        return self._dimplex_key in data.get("values", {})
