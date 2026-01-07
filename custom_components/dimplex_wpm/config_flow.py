"""Config flow for Dimplex WPM."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback

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
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DEFAULT_UNIT_ID,
    DOMAIN,
    REGISTER_STRATEGY_MAP,
    REGISTER_STRATEGY_AUTO,
)


class DimplexConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dimplex WPM."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_HOST]}_{user_input[CONF_UNIT_ID]}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Dimplex WPM", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): int,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    int, vol.Range(min=5, max=300)
                ),
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(
                    int, vol.Range(min=1, max=30)
                ),
                vol.Optional(CONF_REGISTER_STRATEGY, default=REGISTER_STRATEGY_AUTO): vol.In(
                    REGISTER_STRATEGY_MAP
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DimplexOptionsFlow(config_entry)


class DimplexOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the integration."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                    ),
                ): vol.All(int, vol.Range(min=5, max=300)),
                vol.Optional(
                    CONF_ENABLE_WRITE_ENTITIES,
                    default=self.config_entry.options.get(
                        CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE
                    ),
                ): bool,
                vol.Optional(
                    CONF_ENABLE_EMS,
                    default=self.config_entry.options.get(CONF_ENABLE_EMS, False),
                ): bool,
                vol.Optional(
                    CONF_ENABLE_BMS_TEMP,
                    default=self.config_entry.options.get(CONF_ENABLE_BMS_TEMP, False),
                ): bool,
                vol.Optional(
                    CONF_ENABLE_EXTERNAL_LOCK,
                    default=self.config_entry.options.get(CONF_ENABLE_EXTERNAL_LOCK, False),
                ): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
