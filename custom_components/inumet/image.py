"""Image platform for Inumet."""

from __future__ import annotations

from homeassistant.components.image import ImageEntity, ImageEntityDescription
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
        map_url = self.coordinator.data.get("advertencias").get("mapaMerge")  # type: ignore
        self._attr_image_url: str = map_url
        self._attr_image_last_updated = dt_util.utcnow()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator.

        Update the image URL and last-updated timestamp so HA knows the
        image changed when the coordinator fetches new data.
        """
        map_url = None
        try:
            map_url = self.coordinator.data.get("advertencias").get("mapaMerge")  # type: ignore
        except Exception:
            map_url = None

        # Update the image URL if it changed, and always bump the
        # `image_last_updated` so Home Assistant will re-fetch the image.
        if map_url is not None and map_url != getattr(self, "_attr_image_url", None):
            self._attr_image_url = map_url

        self._attr_image_last_updated = dt_util.utcnow()

        super()._handle_coordinator_update()
