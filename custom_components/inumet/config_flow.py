"""Adds config flow for Blueprint."""
from __future__ import annotations

import asyncio

import voluptuous as vol
from homeassistant import config_entries

from .api import (
    IntegrationBlueprintApiClient,
    IntegrationBlueprintApiClientAuthenticationError,
    IntegrationBlueprintApiClientCommunicationError,
    IntegrationBlueprintApiClientError,
    INUMET
)
from .const import DOMAIN, LOGGER, STATION, ZONE

class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        temp_client = await self.hass.async_add_executor_job(INUMET)
        stations = await self.hass.async_add_executor_job(temp_client.estaciones)
        zones = await self.hass.async_add_executor_job(temp_client.zonas)
        if user_input is not None:
            try:
                await self._test_credentials(
                    station=user_input.get(STATION),
                    zone=user_input.get(ZONE),
                )

            except IntegrationBlueprintApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except IntegrationBlueprintApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except IntegrationBlueprintApiClientError as exception:
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
                    ): vol.In([x['NombreEstacion'] for x in stations['estaciones']]),
                    vol.Required(
                    ZONE,
                    ): vol.In([x['nombre'] for x in zones['zonas']]),
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, station: int, zone: int) -> None:
        """Validate credentials."""
        client = await self.hass.async_add_executor_job(INUMET,station,zone)
        if not await self.hass.async_add_executor_job(client._test):
            raise ValueError
