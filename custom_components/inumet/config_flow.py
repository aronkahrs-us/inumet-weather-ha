"""Adds config flow for Blueprint."""
from __future__ import annotations
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .api import (
    InumetApiClientAuthenticationError,
    InumetApiClientNoDataError,
    InumetApiClientError,
)
from .const import DOMAIN, LOGGER, UPDATE_INTERVAL

from inumet_api import INUMET

class InumetFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Inumet."""

    VERSION = 2

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    lat=user_input.get(CONF_LATITUDE),
                    long=user_input.get(CONF_LONGITUDE)
                )

            except InumetApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except InumetApiClientNoDataError as exception:
                LOGGER.error(exception)
                _errors["base"] = "no_data"
            except InumetApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f'{self.client.stationName}',
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LATITUDE, default=self.hass.config.latitude
                    ): cv.latitude,
                    vol.Required(
                        CONF_LONGITUDE, default=self.hass.config.longitude
                    ): cv.longitude,
                    vol.Required(
                        "UPDATE_INTERVAL", default=UPDATE_INTERVAL
                    ): int,
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, lat: float, long: float) -> None:
        """Validate credentials."""
        self.client = await self.hass.async_add_executor_job(INUMET,lat,long)
        if not await self.hass.async_add_executor_job(self.client._test):
            raise InumetApiClientNoDataError

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Inumet."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            if CONF_LATITUDE in self.config_entry.data:
                user_input[CONF_LATITUDE] = self.config_entry.data[CONF_LATITUDE]
            if CONF_LONGITUDE in self.config_entry.data:
                user_input[CONF_LONGITUDE] = self.config_entry.data[CONF_LONGITUDE]
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input
            )
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "UPDATE_INTERVAL", default=self.config_entry.data.get("UPDATE_INTERVAL")
                    ): int,
                }
            ),
        )
