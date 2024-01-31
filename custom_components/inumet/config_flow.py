"""Adds config flow for Blueprint."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .api import (
    InumetApiClientAuthenticationError,
    InumetApiClientNoDataError,
    InumetApiClientError,
    INUMET
)
from .const import DOMAIN, LOGGER, STATION, DEPTO

class InumetFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Inumet."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        temp_client = await self.hass.async_add_executor_job(INUMET)
        stations = await self.hass.async_add_executor_job(temp_client.estaciones)
        deptos = await self.hass.async_add_executor_job(temp_client.departamentos)
        if user_input is not None:
            try:
                await self._test_credentials(
                    station=user_input.get(STATION),
                    depto=user_input.get(DEPTO),
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
                    title=user_input[STATION],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                    STATION,
                    ): vol.In([x['NombreEstacion'] for x in stations]),
                    vol.Required(
                    DEPTO,
                    ): vol.In([x['nombre'] for x in deptos]),
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, station: int, depto: int) -> None:
        """Validate credentials."""
        client = await self.hass.async_add_executor_job(INUMET,station,depto)
        if not await self.hass.async_add_executor_job(client._test):
            raise InumetApiClientNoDataError
