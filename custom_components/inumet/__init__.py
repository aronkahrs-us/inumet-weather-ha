"""Custom integration to integrate Inumet with Home Assistant.

For more details about this integration, please refer to
https://github.com/aronkahrs-us/inumet-weather-ha
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import  Platform, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant

from inumet_api import INUMET
from .const import DOMAIN
from .coordinator import InumetDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.WEATHER,
    Platform.IMAGE,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator = InumetDataUpdateCoordinator(
        hass=hass,
        client=await hass.async_add_executor_job(INUMET,entry.data[CONF_LATITUDE],entry.data[CONF_LONGITUDE]),
        latitude=entry.data[CONF_LATITUDE],
        longitude=entry.data[CONF_LONGITUDE],
        update_interval=entry.data['UPDATE_INTERVAL'],
    )
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
