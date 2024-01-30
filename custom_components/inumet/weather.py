"""Weather platform for Inumet."""
from __future__ import annotations

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import STATE_UNAVAILABLE

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_TIME,
    Forecast,
    WeatherEntityFeature,
    WeatherEntity,
)

from homeassistant.const import (
    UnitOfLength,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)

from .const import DOMAIN
from .coordinator import InumetDataUpdateCoordinator
from .entity import InumetEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([InumetWeather(coordinator)])


class InumetWeather(InumetEntity, WeatherEntity):
    """integration_blueprint Sensor class."""

    def __init__(
        self,
        coordinator: InumetDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.name = "INUMET"
        self._attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
        self._attr_native_pressure_unit = UnitOfPressure.HPA
        self._attr_native_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_native_visibility_unit = UnitOfLength.KILOMETERS
        self._attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
        self._attr_unique_id = f"WeatherInumet_{self.coordinator.data['estado'].get('id')}"
        self._attr_attribution = "Data provided by INUMET"
        if self.coordinator.data['pronostico'] != None:
            self._attr_supported_features = WeatherEntityFeature.FORECAST_DAILY

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        try:
            estado = self.coordinator.data['estado'].get('iconoTiempoPresente')
            if estado == 4 or estado == 13 or estado == 24:
                condition = 'cloudy'
            elif estado == 12 or estado == 19:
                condition = 'windy'
            elif estado == 9 or estado == 2 or estado == 21 or estado == 22:
                condition = 'partlycloudy'
            elif estado == 1:
                condition = 'sunny'
            elif estado == 20:
                condition = 'clear-night'
            elif estado == 10:
                condition = 'lightning'
            elif estado == 11:
                condition = 'lightning-rainy'
            elif estado == 23 or estado == 3 or estado == 5 or estado == 6 or estado == 7:
                condition = 'rainy'
            elif estado == 16 or estado == 14 or estado == 15 or estado == 8:
                condition = 'fog'
            elif estado == 17:
                condition = 'snowy'
            elif estado == 18:
                condition = 'exceptional'
            return condition
        except:
            return STATE_UNAVAILABLE

    @property
    def cloud_coverage(self) -> float:
        """Return the Cloud coverage in %."""
        try:
            data = self.coordinator.data['estado'].get('cielo')
            if data == "Claro":
                coverage = 0
            elif data == "Algo Nuboso":
                coverage = 50
            elif data == "Cubierto":
                coverage = 100
            return coverage
        except:
            return STATE_UNAVAILABLE

    @property
    def native_temperature(self) -> float:
        """Return the temperature."""
        try:
            return float(self.coordinator.data['estado'].get('temperatura'))
        except:
            return STATE_UNAVAILABLE
    @property
    def native_pressure(self) -> float:
        """Return the pressure."""
        try:
            return float(self.coordinator.data['estado'].get('presion'))
        except:
            return STATE_UNAVAILABLE

    @property
    def native_dew_point(self) -> float:
        """Return the dew point."""
        try:
            return float(self.coordinator.data['estado'].get('temperaturaPuntoRocio'))
        except:
            return STATE_UNAVAILABLE

    @property
    def humidity(self) -> int:
        """Return the humidity."""
        try:
            return float(self.coordinator.data['estado'].get('humedad'))
        except:
            return STATE_UNAVAILABLE

    @property
    def native_wind_gust_speed(self) -> float:
        """Return the wind gust speed."""
        try:
            return float(self.coordinator.data['estado'].get('intRafaga').replace('-','0'))
        except:
            return STATE_UNAVAILABLE

    @property
    def native_wind_speed(self) -> float:
        """Return the wind speed."""
        try:
            return float(self.coordinator.data['estado'].get('intViento').replace('-','0'))
        except:
            return STATE_UNAVAILABLE

    @property
    def wind_bearing(self) -> int:
        """Return the wind bearing."""
        try:
            return float(self.coordinator.data['estado'].get('dirViento').replace('-','0'))
        except:
            return STATE_UNAVAILABLE

    @property
    def native_visibility(self) -> float:
        """Return the visibility."""
        try:
            return float(self.coordinator.data['estado'].get('visibilidad').replace('-','0'))
        except:
            return STATE_UNAVAILABLE

    def _forecast(self) -> list[Forecast] | None:
        """Return the forecast array."""
        try:
            if len(self.coordinator.data['pronostico']) <= 0:
                return None
            # remap keys from library to keys understood by the weather component
            return [
                {
                    ATTR_FORECAST_TIME: item["fecha"],
                    ATTR_FORECAST_NATIVE_TEMP: float(item["tempMax"]),
                    ATTR_FORECAST_NATIVE_TEMP_LOW: float(item["tempMin"]),
                    ATTR_FORECAST_CONDITION: item["condition"],
                }
                for item in self.coordinator.data['pronostico']
            ]
        except:
            return STATE_UNAVAILABLE

    @callback
    def _async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units."""
        return self._forecast