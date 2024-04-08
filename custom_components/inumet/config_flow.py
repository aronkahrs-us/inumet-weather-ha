"""Adds config flow for Blueprint."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
import homeassistant.helpers.config_validation as cv

from .api import (
    InumetApiClientAuthenticationError,
    InumetApiClientNoDataError,
    InumetApiClientError,
)
from .const import DOMAIN, LOGGER

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
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, lat: float, long: float) -> None:
        """Validate credentials."""
        self.client = await self.hass.async_add_executor_job(INUMET,lat,long)
        if not await self.hass.async_add_executor_job(self.client._test):
            raise InumetApiClientNoDataError
