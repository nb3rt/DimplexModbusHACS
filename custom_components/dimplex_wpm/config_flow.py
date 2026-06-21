"""Config flow for Dimplex WPM."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import (
    CONF_ENABLE_WRITE_ENTITIES,
    CONF_ENABLED_MODULES,
    CONF_FLOW_SENSOR_ENTITY,
    CONF_HAS_ELECTRIC_METER,
    CONF_HAS_FLOW_SENSOR,
    CONF_HAS_HEAT_METER,
    CONF_HAS_INVERTER_FREQ,
    CONF_INCLUDE_RE_REGISTERS,
    CONF_PROFILE,
    CONF_SCAN_INTERVAL,
    CONF_SOFTWARE_VERSION,
    CONF_TIMEOUT,
    CONF_UNIT_ID,
    DEFAULT_ENABLE_WRITE,
    DEFAULT_PORT,
    DEFAULT_PROFILE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SOFTWARE_VERSION,
    DEFAULT_TIMEOUT,
    DEFAULT_UNIT_ID,
    DOMAIN,
    MODULE_NAME_MAP,
    SELECTABLE_MODULES,
    SOFTWARE_VERSIONS,
)
from .modbus_client import DimplexModbusClient
from .profiles import PROFILES, get_profile

REG_OUTDOOR = 1
PROBE_REGISTERS = {
    CONF_HAS_ELECTRIC_METER: 5170,
    CONF_HAS_HEAT_METER: 5168,
    CONF_HAS_INVERTER_FREQ: 114,
}

PROFILE_CHOICES = {key: profile.name for key, profile in PROFILES.items()}
MODULE_CHOICES = {mod: MODULE_NAME_MAP.get(mod, mod) for mod in SELECTABLE_MODULES}


async def _validate_and_probe(user_input: dict) -> dict[str, bool]:
    """Validate the connection (holding read) and probe capability hints."""
    client = DimplexModbusClient(
        user_input[CONF_HOST],
        user_input[CONF_PORT],
        user_input[CONF_UNIT_ID],
        user_input[CONF_TIMEOUT],
    )
    hints: dict[str, bool] = {}
    try:
        await client.connect()
        if await client.read_holding_registers(REG_OUTDOOR, 1) is None:
            raise ConnectionError("No response from device")
        for conf_key, reg in PROBE_REGISTERS.items():
            try:
                hints[conf_key] = await client.read_holding_registers(reg, 1) is not None
            except Exception:  # noqa: BLE001 - a probe failure just means "absent"
                hints[conf_key] = False
    finally:
        await client.close()
    return hints


class DimplexConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dimplex WPM."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._hints: dict[str, bool] = {}

    async def async_step_user(self, user_input: dict | None = None):
        """Step 1: connection + profile + firmware."""
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}_{user_input[CONF_UNIT_ID]}"
            )
            self._abort_if_unique_id_configured()
            try:
                self._hints = await _validate_and_probe(user_input)
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                self._data = dict(user_input)
                return await self.async_step_features()

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): int,
                vol.Required(CONF_PROFILE, default=DEFAULT_PROFILE): vol.In(PROFILE_CHOICES),
                vol.Optional(CONF_SOFTWARE_VERSION, default=DEFAULT_SOFTWARE_VERSION): vol.In(
                    SOFTWARE_VERSIONS
                ),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    int, vol.Range(min=5, max=300)
                ),
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(
                    int, vol.Range(min=1, max=30)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_features(self, user_input: dict | None = None):
        """Step 2: modules present + metering capabilities (auto-hinted)."""
        if user_input is not None:
            data = {**self._data, **user_input}
            return self.async_create_entry(title="Dimplex WPM", data=data)

        profile = get_profile(self._data.get(CONF_PROFILE))
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_ENABLED_MODULES,
                    default=sorted(profile.default_modules),
                ): cv.multi_select(MODULE_CHOICES),
                vol.Optional(
                    CONF_HAS_ELECTRIC_METER,
                    default=self._hints.get(CONF_HAS_ELECTRIC_METER, False),
                ): bool,
                vol.Optional(
                    CONF_HAS_HEAT_METER,
                    default=self._hints.get(CONF_HAS_HEAT_METER, False),
                ): bool,
                vol.Optional(CONF_HAS_FLOW_SENSOR, default=False): bool,
                vol.Optional(CONF_FLOW_SENSOR_ENTITY, default=""): str,
                vol.Optional(
                    CONF_HAS_INVERTER_FREQ,
                    default=self._hints.get(CONF_HAS_INVERTER_FREQ, True),
                ): bool,
                vol.Optional(CONF_INCLUDE_RE_REGISTERS, default=True): bool,
            }
        )
        return self.async_show_form(step_id="features", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DimplexOptionsFlow()


class DimplexOptionsFlow(config_entries.OptionsFlow):
    """Options: tuning, modules, capabilities, and the control gate.

    ``self.config_entry`` is provided by the base class (HA 2024.11+); do not
    assign it manually.
    """

    def _current(self, key, default):
        return self.config_entry.options.get(
            key, self.config_entry.data.get(key, default)
        )

    async def async_step_init(self, user_input: dict | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self._current(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(int, vol.Range(min=5, max=300)),
                vol.Optional(
                    CONF_ENABLED_MODULES,
                    default=self._current(CONF_ENABLED_MODULES, []),
                ): cv.multi_select(MODULE_CHOICES),
                vol.Optional(
                    CONF_HAS_ELECTRIC_METER,
                    default=self._current(CONF_HAS_ELECTRIC_METER, False),
                ): bool,
                vol.Optional(
                    CONF_HAS_HEAT_METER,
                    default=self._current(CONF_HAS_HEAT_METER, False),
                ): bool,
                vol.Optional(
                    CONF_HAS_FLOW_SENSOR,
                    default=self._current(CONF_HAS_FLOW_SENSOR, False),
                ): bool,
                vol.Optional(
                    CONF_FLOW_SENSOR_ENTITY,
                    default=self._current(CONF_FLOW_SENSOR_ENTITY, ""),
                ): str,
                vol.Optional(
                    CONF_HAS_INVERTER_FREQ,
                    default=self._current(CONF_HAS_INVERTER_FREQ, True),
                ): bool,
                vol.Optional(
                    CONF_INCLUDE_RE_REGISTERS,
                    default=self._current(CONF_INCLUDE_RE_REGISTERS, True),
                ): bool,
                vol.Optional(
                    CONF_ENABLE_WRITE_ENTITIES,
                    default=self._current(CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE),
                ): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
