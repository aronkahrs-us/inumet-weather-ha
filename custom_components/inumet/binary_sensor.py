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
import pytz

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
            tz=hass.config.time_zone
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class InumetBinarySensor(InumetEntity, BinarySensorEntity):
    """Inumet binary_sensor class."""

    def __init__(
        self,
        coordinator: InumetDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
        tz
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_attribution = ATTRIBUTION
        self._attr_unique_id = f"{DOMAIN}_{self.entity_description.key}_{self.coordinator.data['estado'].get('id')}"
        self._tz=pytz.timezone(tz)

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        try:
            alerts = self.coordinator.data.get(self.entity_description.key)
            if len(list(alerts.get('advertencias'))) > 0:
                for alert in list(alerts.get('advertencias')):
                    _colores = ['','','Amarilla','Naranja','Roja']
                    riesgos = alert.get('riesgoFenomeno')
                    descripcion = alert.get('descripcion')
                    if self.entity_description.key == 'advertencias':
                        fechas = {'inicio':dt.datetime.strptime(alert['comienzo'],'%Y-%m-%d %H:%M'),'fin':(dt.datetime.strptime(alert['finalizacion'],'%Y-%m-%d %H:%M'))}
                    else:
                        fechas = {'inicio':dt.datetime.strptime(alert['comienzo'],'%Y-%m-%d'),'fin':(dt.datetime.strptime(alert['finalizacion'],'%Y-%m-%d')+ dt.timedelta(days=1))}
                    zones = [i['label'] for i in alert['zonasArray']]
                    if self.coordinator.client.depto in zones and fechas['inicio'].replace(tzinfo=self._tz) < pytz.utc.localize(dt.datetime.now(), is_dst=None).replace(tzinfo=self._tz) < fechas['fin'].replace(tzinfo=self._tz):
                        self.extra_state_attributes = {
                            "Fenomeno": alert['fenomeno'],
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
                        return True
                return False
            else:
                return False
        except Exception as e:
            LOGGER.warning(e)
            return False
