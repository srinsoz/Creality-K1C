import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
        CrealitySensor(ci, "printFileName", "Filename", icon="mdi:file"),
        CrealitySensor(ci, "TotalLayer", "Total layers", icon="mdi:layers"),
        CrealitySensor(ci, "layer", "Current layer", icon="mdi:layers"),
        CrealitySensor(
            ci,
            "printJobTime",
            "Total time",
            SensorDeviceClass.DURATION,
            unit_of_measurement="s",
            icon="mdi:timer-sand-complete",
        ),
        CrealitySensor(
            ci,
            "printLeftTime",
            "Remaing time",
            SensorDeviceClass.DURATION,
            unit_of_measurement="s",
            icon="mdi:timer-sand",
        ),
        CrealitySensor(
            ci,
            "printProgress",
            "Progress",
            unit_of_measurement="%",
            icon="mdi:progress-helper",
        ),
        CrealitySensor(ci, "model", "Model", icon="mdi:format-color-text"),
        CrealitySensor(ci, "hostname", "Hostname", icon="mdi:format-color-text"),
        CrealitySensor(ci, "state", "State", icon="mdi:format-color-text"),
        CrealitySensor(ci, "modelVersion", "Firmware", icon="mdi:format-color-text"),
        CrealitySensor(
            ci,
            "nozzleTemp",
            "Nozzle temperature",
            SensorDeviceClass.TEMPERATURE,
            unit_of_measurement="°C",
            icon="mdi:printer-3d-nozzle",
        ),
        CrealitySensor(
            ci,
            "bedTemp0",
            "Hot bed temperature",
            SensorDeviceClass.TEMPERATURE,
            unit_of_measurement="°C",
            icon="mdi:thermometer",
        ),
        # Add any additional sensors you need here
    ]
    binsensors = [
        CrealityBinarySensor(ci, "fan", "Fan", "mdi:fan"),
        CrealityBinarySensor(ci, "fanAuxiliary", "Side fan", "mdi:fan"),
        CrealityBinarySensor(ci, "fanCase", "Back fan", "mdi:fan"),
        CrealityBinarySensor(ci, "lightSw", "Light", "mdi:lightbulb"),
        CrealityBinarySensor(
            ci, "materialDetect", "Material detected", "mdi:toy-brick"
        ),
    ]

    async_add_entities(sensors + binsensors)


class CrealityBaseSensor:
    """Base class for Creality sensors."""

    _attr_should_poll = False

    def __init__(
        self, ci: CrealityInterface, data_key: str, name_suffix: str, icon: str
    ):
        self._ci = ci
        self._value = None
        self._available = True  # fixme implement this corretl
        self._data_key = data_key
        self._icon = icon
        self._attr_name = name_suffix
        self._attr_unique_id = f"{ci._host}_{data_key}"
        ci.registerSensor(self)

    @property
    def name(self):
        return self._attr_name

    @property
    def available(self):
        return self._available

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def icon(self):
        return self._icon

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._ci._host)},
            "name": "Creality K1C Printer",
            "manufacturer": "Creality",
            "model": "K1C",
        }


class CrealitySensor(CrealityBaseSensor, SensorEntity):
    """Defines a single Creality sensor."""

    _attr_should_poll = False

    def __init__(
        self,
        ci: CrealityInterface,
        data_key: str,
        name_suffix: str,
        device_class=None,
        unit_of_measurement=None,
        icon=None,
    ):
        super().__init__(ci, data_key, name_suffix, icon)
        self._unit_of_measurement = unit_of_measurement
        self._device_class = device_class

    def update_state(self, value):
        if value != self._value:
            self._value = value
            self.async_schedule_update_ha_state()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._value

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement if defined."""
        return self._unit_of_measurement


class CrealityBinarySensor(CrealityBaseSensor, BinarySensorEntity):
    """Defines a single Creality binary sensor."""

    def update_state(self, new_value: str):
        if new_value != self._value:
            self._value = new_value
            self.async_schedule_update_ha_state()

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._value is not None and self._value > 0
