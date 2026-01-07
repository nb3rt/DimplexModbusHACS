"""Data update coordinator for the integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    DEFAULT_SCAN_INTERVAL,
    FAULT_MAP_BY_VERSION,
    REG_FAULT_CODE,
    LOCK_MAP_BY_VERSION,
    REG_LOCK_CODE,
    REG_DHW_TEMPERATURE,
    REG_FLOW_TEMPERATURE,
    REG_OUTDOOR_TEMPERATURE,
    REG_RETURN_SETPOINT_TEMPERATURE,
    REG_RETURN_TEMPERATURE,
    REG_SG_READY_MODE,
    SENSOR_ERROR_MAP_BY_VERSION,
    REG_SENSOR_ERROR_CODE,
    REG_STATUS_CODE,
    SENSOR_ERROR_MAP,
    SG_READY_MAP,
    STATUS_MAP_BY_VERSION,
)
from .modbus_client import DimplexModbusClient

LOGGER = logging.getLogger(__name__)


def _map_code(value: int, mapping: dict[int, str]) -> str:
    """Return a mapped string or fallback."""
    if value in mapping:
        return mapping[value]
    return f"Unknown ({value})"


def _decode_temperature(value: int) -> float:
    """Decode a signed temperature with 0.1 precision."""
    # Values are int16 with scale 0.1
    if value > 32767:
        value -= 65536
    return round(value * 0.1, 1)


class DimplexDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate data fetching from the Modbus client."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: DimplexModbusClient,
        *,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
        register_strategy: str = "holding",
        host: str | None = None,
        port: int | None = None,
        unit_id: int | None = None,
        software_version: str | None = None,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name="Dimplex WPM coordinator",
            update_interval=timedelta(seconds=scan_interval),
        )
        self._client = client
        self._register_strategy = register_strategy
        self._connection_info = {
            "host": host,
            "port": port,
            "unit_id": unit_id,
            "register_strategy": register_strategy,
            "software_version": software_version,
        }
        self._software_version = software_version
        self._consecutive_failures = 0

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Modbus and return structured payload."""
        try:
            raw = await self._read_registers()
        except Exception as err:
            self._consecutive_failures += 1
            raise UpdateFailed(f"Error communicating with Modbus device: {err}") from err
        self._consecutive_failures = 0

        derived: dict[str, Any] = {}
        if REG_OUTDOOR_TEMPERATURE in raw:
            derived["outdoor_temperature"] = _decode_temperature(
                raw[REG_OUTDOOR_TEMPERATURE]
            )
        if REG_RETURN_TEMPERATURE in raw:
            derived["return_temperature"] = _decode_temperature(raw[REG_RETURN_TEMPERATURE])
        if REG_RETURN_SETPOINT_TEMPERATURE in raw:
            derived["return_setpoint_temperature"] = _decode_temperature(
                raw[REG_RETURN_SETPOINT_TEMPERATURE]
            )
        if REG_FLOW_TEMPERATURE in raw:
            derived["flow_temperature"] = _decode_temperature(raw[REG_FLOW_TEMPERATURE])
        if REG_DHW_TEMPERATURE in raw:
            derived["dhw_temperature"] = _decode_temperature(raw[REG_DHW_TEMPERATURE])

        status_map = STATUS_MAP_BY_VERSION.get(
            self._software_version, STATUS_MAP_BY_VERSION["H"]
        )
        lock_map = LOCK_MAP_BY_VERSION.get(
            self._software_version, LOCK_MAP_BY_VERSION["H"]
        )
        fault_map = FAULT_MAP_BY_VERSION.get(
            self._software_version, FAULT_MAP_BY_VERSION["H"]
        )
        sensor_error_map = SENSOR_ERROR_MAP_BY_VERSION.get(
            self._software_version, SENSOR_ERROR_MAP_BY_VERSION["H"]
        )

        if REG_STATUS_CODE in raw:
            derived["status_text"] = _map_code(raw[REG_STATUS_CODE], status_map)
        if REG_SENSOR_ERROR_CODE in raw:
            derived["sensor_error_text"] = _map_code(
                raw[REG_SENSOR_ERROR_CODE],
                sensor_error_map,
            )
        if REG_SG_READY_MODE in raw:
            derived["sg_ready_text"] = _map_code(raw[REG_SG_READY_MODE], SG_READY_MAP)
        if REG_LOCK_CODE in raw:
            derived["lock_text"] = _map_code(raw[REG_LOCK_CODE], lock_map)
            derived["lock_active"] = raw[REG_LOCK_CODE] != 0
        if REG_FAULT_CODE in raw:
            derived["fault_text"] = _map_code(raw[REG_FAULT_CODE], fault_map)
            derived["fault_active"] = raw[REG_FAULT_CODE] != 0

        meta = {
            "last_update": dt_util.utcnow().isoformat(),
            "update_success": True,
            "consecutive_failures": self._consecutive_failures,
            **self._connection_info,
        }

        return {"raw": raw, "derived": derived, "meta": meta}

    async def _read_registers(self) -> dict[int, int]:
        """Read registers according to configured strategy."""
        # Minimal set of contiguous ranges to reduce calls.
        ranges = [
            (REG_OUTDOOR_TEMPERATURE, 6),  # 1-6 includes temperatures
            (REG_RETURN_SETPOINT_TEMPERATURE, 1),
            (REG_STATUS_CODE, 4),  # 103-106 codes
            (REG_SG_READY_MODE, 1),
        ]

        strategy = "holding" if self._register_strategy == "holding" else "input"

        if self._register_strategy == "auto":
            # Try input registers first, fall back to holding on failure.
            try:
                raw = await self._client.read_ranges(ranges, "input")
                if raw:
                    return raw
            except Exception as err:
                LOGGER.debug("Input register read failed (%s), retrying as holding", err)
            return await self._client.read_ranges(ranges, "holding")

        return await self._client.read_ranges(ranges, strategy)

    @property
    def write_sg_ready(self) -> Callable[[int, int], Any]:
        """Return helper for writing SG Ready values."""
        return self._client.write_register
