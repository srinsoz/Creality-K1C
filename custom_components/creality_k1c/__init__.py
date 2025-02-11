import asyncio
from asyncio import Task
import datetime
from datetime import timedelta
import json
import logging
import traceback

import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Take a number n and return the square of n."""
    ci = CrealityInterface(hass, entry.data["host"], entry.data["port"])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = ci
    asyncio.create_task(ci.process())
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])
    return True


class CrealityInterface:
    """Creatlity Interface."""

    _port: int
    _host: str
    _ws: any
    _attr: dict
    _receive_task: Task | None
    _sensors: dict

    def __init__(self, hass: HomeAssistant, host: str, port: int):  # noqa: D107
        self._receive_task = None
        self._port = port
        self._host = host
        self._ws = None
        self._sensors = {}
        self._attr = {}
        # fixme I do not like that
        self._hass = hass

    async def connect(self):  # noqa: D102
        try:
            self._ws = await aiohttp.ClientSession().ws_connect(
                "ws://%s:%d" % (self._host, self._port)
            )
            _LOGGER.info("Connected to WebSocket server at %s", self._host)
            self._receive_task = asyncio.create_task(self._receive_handler())
        except Exception as e:
            _LOGGER.error("WebSocket connection error: %s", e)

    async def _receive_handler(self):
        async for message in self._ws:
            try:
                if message.type == aiohttp.WSMsgType.TEXT:
                    if message.data == "ok":
                        # skip ok message send after command
                        continue
                    ms = json.loads(message.data)
                    for k, v in ms.items():
                        self._attr[k] = v
                        if k in self._sensors:
                            _LOGGER.info("Update sensor %s to %s", k, v)
                            self._sensors[k].update_state(v)

            except Exception as e:
                _LOGGER.error("WebSocket invalid message: %s", e)
                error_message = traceback.format_exc()
                _LOGGER.error(error_message)

    async def send_heat_beat(self):
        # print("Sending Heat Beat")
        _LOGGER.info("Sending Heat Beat to %s", self._host)
        now = datetime.datetime.now()
        isoformat = now.isoformat()
        data = {"ModeCode": "heart_beat", "msg": isoformat}
        if self._ws is not None:
            await self._ws.send_json(data)

    async def close(self):
        if self._ws is not None:
            await self._ws.close()
            self._ws = None
            _LOGGER.info("Disconnected from WebSocket server at %s", self._host)

    async def process(self):
        await self.connect()
        while True:
            await asyncio.sleep(10)
            await self.send_heat_beat()

    def registerSensor(self, sensor: any):
        _LOGGER.info("sensor %s registred", sensor.data_key)
        self._sensors[sensor.data_key] = sensor
