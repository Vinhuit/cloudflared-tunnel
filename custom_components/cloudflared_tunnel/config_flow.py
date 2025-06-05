from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_HOSTNAME, CONF_PORT

class CloudflaredConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Cloudflared Tunnel", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOSTNAME): str,
                vol.Required(CONF_PORT, default=10300): int
            }),
            errors=errors
        )