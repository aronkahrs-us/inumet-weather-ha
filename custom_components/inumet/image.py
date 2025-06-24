"""Image platform for Inumet."""
from __future__ import annotations

from homeassistant.components.image import ImageEntity,ImageEntityDescription
from homeassistant.util import dt as dt_util
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import InumetDataUpdateCoordinator
from .entity import InumetEntity

ENTITY_DESCRIPTIONS = [
    ImageEntityDescription(
        key="alert_map",
        name="Mapa Alerta",
        icon="mdi:alert-circle",
    )
]


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the Image platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        InumetImage(
            hass=hass,
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class InumetImage(InumetEntity, ImageEntity):
    """Inumet Image class."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: InumetDataUpdateCoordinator,
        entity_description: ImageEntityDescription,
    ) -> None:
        """Initialize the image class."""
        super().__init__(coordinator)
        ImageEntity.__init__(self, hass)
        self.entity_description = entity_description
        self._attr_unique_id = f"{DOMAIN}_{self.entity_description.key}_{self.coordinator.data['estado'].get('id')}"
        self._attr_content_type: str = "image/png"
        map_url = self.coordinator.data.get('advertencias').get('mapaMerge') # type: ignore
        self._attr_image_url: str = map_url
        self._attr_image_last_updated = dt_util.utcnow()
