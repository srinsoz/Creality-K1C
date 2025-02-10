from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .__init__ import CrealityInterface
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Creality Control sensors from a config entry."""
    ci = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [
        CrealitySensor(ci, "printFileName", "Filename"),
        CrealitySensor(ci, "TotalLayer", "Total layers"),
        CrealitySensor(ci, "layer", "Current layer"),
        CrealitySensor(ci, "printJobTime", "Total time", SensorDeviceClass.DURATION),
        CrealitySensor(ci, "printLeftTime", "Remaing time", SensorDeviceClass.DURATION),
        CrealitySensor(ci, "printProgress", "Progress", unit_of_measurement="%"),
        CrealitySensor(ci, "fan", "Fan"),
        CrealitySensor(ci, "fanAuxiliary", "Side fan"),
        CrealitySensor(ci, "fanCase", "Back fan"),
        CrealitySensor(ci, "lightSw", "Light"),
        CrealitySensor(ci, "materialDetect", "Material detected"),
        CrealitySensor(ci, "model", "Model"),
        CrealitySensor(ci, "hostname", "Hostname"),
        CrealitySensor(ci, "modelVersion", "Firmware"),
        CrealitySensor(
            ci,
            "nozzleTemp",
            "Nozzle temperature",
            SensorDeviceClass.TEMPERATURE,
            unit_of_measurement="°C",
        ),
        CrealitySensor(
            ci,
            "bedTemp0",
            "Hot bed temperature",
            SensorDeviceClass.TEMPERATURE,
            unit_of_measurement="°C",
        ),
        # Add any additional sensors you need here
    ]
    async_add_entities(sensors)


class CrealitySensor(SensorEntity):
    """Defines a single Creality sensor."""

    _attr_should_poll = False

    def __init__(
        self,
        ci: CrealityInterface,
        data_key: str,
        name_suffix: str,
        device_class=None,
        unit_of_measurement=None,
    ):
        super().__init__()
        self._ci = ci
        self._value = None
        self._available = True
        self.data_key = data_key
        self._attr_name = f"Creality {name_suffix}"
        self._attr_unique_id = f"{ci._host}_{data_key}"
        self._unit_of_measurement = unit_of_measurement
        self._device_class = device_class
        ci.registerSensor(self)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self._available

    def update_state(self, value):
        if value != self._value:
            self._value = value
            self.async_schedule_update_ha_state()
            _LOGGER.info(
                "sensor %s update to %s", self._attr_unique_id, str(self._value)
            )

    @property
    def unique_id(self):
        """Return a unique identifier for this sensor."""
        return self._attr_unique_id

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._value

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement if defined."""
        return self._unit_of_measurement

    @property
    def device_info(self):
        """Return information about the device this sensor is part of."""
        return {
            "identifiers": {(DOMAIN, self._ci._host)},
            "name": "Creality K1C Printer",
            "manufacturer": "Creality",
            "model": "K1C",
        }
