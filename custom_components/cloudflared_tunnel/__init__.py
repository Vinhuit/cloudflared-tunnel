import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .cloudflared import start_cloudflared_tunnel

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hostname = entry.data["hostname"]
    port = entry.data["port"]

    _LOGGER.info(f"Starting cloudflared tunnel for {hostname}:{port}")
    await start_cloudflared_tunnel(hass, hostname, port)
    return True