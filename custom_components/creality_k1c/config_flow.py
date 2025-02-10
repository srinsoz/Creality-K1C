from aiohttp import ClientSession
import voluptuous as vol

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN


class CrealityK1CConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Creality K1c."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            valid = await self._test_connection(user_input["host"], user_input["port"])
            if valid:
                return self.async_create_entry(title="Creality K1C", data=user_input)
            errors["base"] = "cannot_connect" if valid is None else "invalid_password"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): cv.string,
                    vol.Required("port", default=9999): cv.port,
                }
            ),
            errors=errors,
        )

    async def _test_connection(self, host, port):
        """Test connection to the Creality printer."""
        uri = f"ws://{host}:{port}/"
        try:
            async with ClientSession() as session:  # noqa: SIM117
                async with session.ws_connect(uri) as ws:
                    # fixme: handle timeout
                    response = await ws.receive_json()
                    if "model" in response and response["model"] != "K1C":
                        return False  # Token is invalid
                    return True  # Assuming any response with printStatus not TOKEN_ERROR is valid
        except Exception as e:
            return None  # Unable to connect
        return None  # In case the connection could not be established or an unexpected error occurred
