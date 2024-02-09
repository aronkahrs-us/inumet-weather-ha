"""Binary sensor platform for Inumet."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import DOMAIN, LOGGER, ATTRIBUTION
from .coordinator import InumetDataUpdateCoordinator
from .entity import InumetEntity
import datetime as dt

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
    """Inumet binary_sensor class."""

    def __init__(
        self,
        coordinator: InumetDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_attribution = ATTRIBUTION
        self._attr_unique_id = f"{DOMAIN}_{self.entity_description.key}_{self.coordinator.data['estado'].get('id')}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        try:
            alerts = self.coordinator.data.get(self.entity_description.key)
            if len(list(alerts['advertencias'])) > 0:
                _colores = ['','Amarilla','Naranja','Roja']
                riesgos = [x['riesgoFenomeno'] for x in alerts['advertencias']][0]
                descripcion = [x['descripcion'] for x in alerts['advertencias']][0]
                if self.entity_description.key == 'advertencias':
                    fechas = [{'inicio':dt.datetime.strptime(x['comienzo'],'%Y-%m-%d %H:%M'),'fin':(dt.datetime.strptime(x['finalizacion'],'%Y-%m-%d %H:%M'))} for x in alerts['advertencias']][0]
                else:
                    fechas = [{'inicio':dt.datetime.strptime(x['comienzo'],'%Y-%m-%d'),'fin':(dt.datetime.strptime(x['finalizacion'],'%Y-%m-%d')+ dt.timedelta(days=1))} for x in alerts['advertencias']][0]
                self.extra_state_attributes = {
                        "Fenomeno": [x['fenomeno'] for x in alerts['advertencias']][0],
                        "Riesgo Viento": riesgos["riesgoViento"],
                        "Riesgo Lluvia": riesgos["riesgoLluvia"],
                        "Riesgo Tormenta": riesgos["riesgoTormenta"],
                        "Riesgo Visibilidad": riesgos["riesgoVisibilidad"],
                        "Riesgo Calor": riesgos["riesgoCalor"],
                        "Riesgo Frio": riesgos["riesgoFrio"],
                        "Color Alerta": _colores[riesgos[max(riesgos, key=riesgos.get)]],
                        "Descripcion": descripcion,
                        "Inicio": fechas['inicio'],
                        "Fin": fechas['fin'],
                    }
                zones = [[i['label'] for i in x['zonasArray']] for x in alerts['advertencias']][0]
                if self.coordinator.client.depto in zones and fechas['inicio'] < dt.datetime.now() < fechas['fin']:
                    return True
                return False
            return False
        except Exception as e:
            LOGGER.warning(e)
            return False
