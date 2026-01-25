"""Image platform for Inumet."""

from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
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
        map_url = self._make_map_url()
        self._attr_image_url: str = map_url
        self._attr_image_last_updated = dt_util.utcnow()

    @property
    def image_url(self) -> str | None:
        """Return the image URL."""
        try:
            map_url = self._make_map_url()
            return map_url
        except Exception:
            return None

    @property
    def image_last_updated(self) -> datetime | None:
        """Return the last updated time."""
        return dt_util.utcnow()

    def _make_map_url(self) -> str:
        """Create the map URL."""
        adv = self.coordinator.data.get("advertencias").get("mapaMerge")  # type: ignore
        avi = self.coordinator.data.get("avisos").get("mapaMerge")  # type: ignore

        # Parse both URLs
        p1 = urlparse(adv)
        p2 = urlparse(avi)
        q1 = parse_qs(p1.query, keep_blank_values=True)
        q2 = parse_qs(p2.query, keep_blank_values=True)
        # Take base params from the first URL
        merged = {}

        for key in q1:
            if key not in ["path", "markers"]:
                # merge both paths
                merged[key] = q1[key]

        merged["path"] = q1.get("path", []) + q2.get("path", [])  # type: ignore
        merged["markers"] = q1.get("markers", []) + q2.get("markers", [])  # type: ignore

        # Rebuild final URL
        final_query = urlencode(merged, doseq=True)
        final_url = urlunparse((p1.scheme, p1.netloc, p1.path, "", final_query, ""))  # type: ignore

        return final_url
