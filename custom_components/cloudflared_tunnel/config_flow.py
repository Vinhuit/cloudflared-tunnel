"""Config flow for Cloudflared Tunnel integration."""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from .const import DOMAIN, CONF_HOSTNAME, CONF_PORT

@config_entries.HANDLERS.register(DOMAIN)
class CloudflaredConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cloudflared Tunnel."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Check if we already have an entry with this hostname
            self._async_abort_entries_match({CONF_HOSTNAME: user_input[CONF_HOSTNAME]})

            # Create the config entry
            return self.async_create_entry(
                title=f"Cloudflared Tunnel ({user_input[CONF_HOSTNAME]})",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOSTNAME): str,
                    vol.Required(CONF_PORT, default=10300): int,
                }
            ),
            errors=errors,
        )