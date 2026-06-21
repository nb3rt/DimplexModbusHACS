"""Data update coordinator — register-table driven."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DEFAULT_SCAN_INTERVAL, get_enum_map
from .modbus_client import DimplexModbusClient
from .registers import (
    COIL,
    HOLDING,
    active_energy_groups,
    active_registers,
    build_read_plan,
    decode_value,
    energy_total_kwh,
)

LOGGER = logging.getLogger(__name__)


class DimplexDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Modbus reads and decode them into a flat ``values`` map."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: DimplexModbusClient,
        *,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
        software_version: str,
        enabled_modules: frozenset[str],
        capabilities: frozenset[str],
        include_re: bool,
        host: str | None = None,
        port: int | None = None,
        unit_id: int | None = None,
        profile_name: str | None = None,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name="Dimplex WPM coordinator",
            update_interval=timedelta(seconds=scan_interval),
        )
        self._client = client
        self.software_version = software_version
        self.enabled_modules = enabled_modules
        self.capabilities = capabilities

        self.specs = active_registers(
            version=software_version,
            enabled_modules=enabled_modules,
            capabilities=capabilities,
            include_re=include_re,
        )
        self.energy_groups = active_energy_groups(
            enabled_modules=enabled_modules, capabilities=capabilities
        )
        self._plan = build_read_plan(self.specs, self.energy_groups, software_version)

        self._connection_info = {
            "host": host,
            "port": port,
            "unit_id": unit_id,
            "software_version": software_version,
            "profile": profile_name,
        }
        self._consecutive_failures = 0

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            holding, coils = await self._execute_plan()
        except Exception as err:
            self._consecutive_failures += 1
            raise UpdateFailed(f"Error communicating with Modbus device: {err}") from err
        self._consecutive_failures = 0

        values: dict[str, Any] = {"controller_info": "online"}

        for spec in self.specs:
            addr = spec.resolve_address(self.software_version)
            if addr is None:
                continue
            if spec.obj == COIL:
                if addr in coils:
                    values[spec.key] = bool(coils[addr])
                continue
            if addr not in holding:
                continue
            raw = holding[addr]
            if spec.enum:
                mapping = get_enum_map(spec.enum, self.software_version)
                values[spec.key] = mapping.get(raw, f"Unknown ({raw})")
            else:
                values[spec.key] = decode_value(spec, raw)

        for group in self.energy_groups:
            regs = [holding.get(r) for r in group.registers]
            if all(r is not None for r in regs):
                values[group.key] = energy_total_kwh(*regs)  # type: ignore[arg-type]

        # Derived problem flags from the raw codes.
        if "fault_code" in values:
            values["fault_active"] = values["fault_code"] != 0
        if "lock_code" in values:
            values["lock_active"] = values["lock_code"] != 0

        meta = {
            "last_update": dt_util.utcnow().isoformat(),
            "update_success": True,
            "consecutive_failures": self._consecutive_failures,
            **self._connection_info,
        }
        return {"values": values, "raw_holding": holding, "raw_coils": coils, "meta": meta}

    async def _execute_plan(self) -> tuple[dict[int, int], dict[int, bool]]:
        holding: dict[int, int] = {}
        coils: dict[int, bool] = {}
        for obj, start, count in self._plan:
            if obj == HOLDING:
                data = await self._client.read_holding_registers(start, count)
                if data:
                    for offset, value in enumerate(data):
                        holding[start + offset] = value
            elif obj == COIL:
                bits = await self._client.read_coils(start, count)
                if bits:
                    for offset, value in enumerate(bits):
                        coils[start + offset] = bool(value)
        return holding, coils

    @property
    def write_register(self) -> Callable[[int, int], Any]:
        """Return helper for writing a holding register (used by M2 controls)."""
        return self._client.write_register

    # Backwards-compatible alias used by the SG Ready select.
    @property
    def write_sg_ready(self) -> Callable[[int, int], Any]:
        return self._client.write_register
