"""Async Modbus TCP client wrapper."""

from __future__ import annotations

import asyncio
import logging
from typing import Iterable, Optional

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import REGISTER_OFFSET

LOGGER = logging.getLogger(__name__)


class DimplexModbusClient:
    """Provide async access to a Modbus TCP device."""

    def __init__(
        self,
        host: str,
        port: int,
        unit_id: int,
        timeout: int,
    ) -> None:
        self._host = host
        self._port = port
        self._unit_id = unit_id
        self._timeout = timeout
        self._client: Optional[AsyncModbusTcpClient] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        """Open the Modbus connection."""
        if self._client and self._client.connected:
            return

        self._client = AsyncModbusTcpClient(
            host=self._host,
            port=self._port,
            timeout=self._timeout,
        )
        if not await self._client.connect():
            raise ConnectionError("Unable to open Modbus connection")
        LOGGER.debug("Connected to Modbus host %s:%s", self._host, self._port)

    async def close(self) -> None:
        """Close the Modbus connection."""
        if self._client:
            await self._client.close()
            LOGGER.debug("Closed Modbus connection")
        self._client = None

    async def _ensure_connected(self) -> None:
        """Ensure that the connection is open."""
        if self._client is None or not self._client.connected:
            await self.connect()

    async def read_holding_registers(
        self, address: int, count: int
    ) -> list[int] | None:
        """Read holding registers."""
        return await self._read("read_holding_registers", address, count)

    async def read_input_registers(
        self, address: int, count: int
    ) -> list[int] | None:
        """Read input registers."""
        return await self._read("read_input_registers", address, count)

    async def write_register(self, address: int, value: int) -> None:
        """Write a single holding register."""
        address += REGISTER_OFFSET
        async with self._lock:
            await self._ensure_connected()
            try:
                assert self._client is not None
                result = await self._client.write_register(
                    address, value, unit=self._unit_id
                )
            except ModbusException as err:
                LOGGER.error("Modbus write failed: %s", err)
                raise
            if result.isError():
                raise ModbusException(f"Write error: {result}")
            LOGGER.debug("Wrote register %s=%s", address, value)

    async def _read(
        self, method: str, address: int, count: int
    ) -> list[int] | None:
        """Read registers using provided client method."""
        async with self._lock:
            await self._ensure_connected()
            try:
                assert self._client is not None
                func = getattr(self._client, method)
                result = await func(address=address, count=count, unit=self._unit_id)
            except ModbusException as err:
                LOGGER.error("Modbus read failed: %s", err)
                raise
            if result.isError():
                LOGGER.warning("Modbus read error for %s at %s: %s", method, address, result)
                return None
            LOGGER.debug(
                "Read %s registers from %s starting at %s: %s",
                count,
                method,
                address,
                result.registers,
            )
            return result.registers

    async def read_ranges(
        self,
        ranges: Iterable[tuple[int, int]],
        register_type: str,
    ) -> dict[int, int]:
        """Batch read multiple ranges and return register/value mapping."""
        values: dict[int, int] = {}
        for start, count in ranges:
            if register_type == "holding":
                data = await self.read_holding_registers(start, count)
            else:
                data = await self.read_input_registers(start, count)
            if data is None:
                continue
            for offset, value in enumerate(data):
                values[start + offset] = value
        return values
