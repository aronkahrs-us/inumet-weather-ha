"""InumetEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION, MANUFACTURER
from .coordinator import InumetDataUpdateCoordinator


class InumetEntity(CoordinatorEntity):
    """InumetEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: InumetDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=NAME,
            model=VERSION,
            manufacturer=MANUFACTURER,
        )
