"""Binary sensor platform for integration_blueprint."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import DOMAIN
from .coordinator import InumetDataUpdateCoordinator
from .entity import InumetEntity

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="advertencias",
        name="Alerta",
        icon="mdi:alert-circle"
    ),
    BinarySensorEntityDescription(
        key="avisos",
        name="Aviso",
        icon="mdi:information"
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        InumetBinarySensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class InumetBinarySensor(InumetEntity, BinarySensorEntity):
    """integration_blueprint binary_sensor class."""

    def __init__(
        self,
        coordinator: InumetDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{DOMAIN}_{self.entity_description.key}_{self.coordinator.data['estado'].get('id')}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        try:
            alerts = self.coordinator.data.get(self.entity_description.key)
            _colores = ['','Amarilla','Naranja','Roja']
            riesgos = [x['riesgoFenomeno'] for x in alerts['advertencias']][0]
            descripcion = [x['descripcion'] for x in alerts['advertencias']][0]
            self.extra_state_attributes = {
                    "riesgoViento": riesgos["riesgoViento"],
                    "riesgoLluvia": riesgos["riesgoLluvia"],
                    "riesgoTormenta": riesgos["riesgoTormenta"],
                    "riesgoVisibilidad": riesgos["riesgoVisibilidad"],
                    "riesgoCalor": riesgos["riesgoCalor"],
                    "riesgoFrio": riesgos["riesgoFrio"],
                    "alertaColor": _colores[riesgos[max(riesgos, key=riesgos.get)]],
                    "descripcion": descripcion,
                }
            zones = [[i['label'] for i in x['zonasArray']] for x in alerts['advertencias']][0]
            return self.coordinator.client.depto in zones
        except:
            return False
