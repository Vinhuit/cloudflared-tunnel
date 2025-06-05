"""The Cloudflared Tunnel integration."""
import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    PLATFORM_SENSOR,
    PLATFORM_BUTTON,
    DATA_TUNNELS,
    CONF_HOSTNAME,
    CONF_PORT,
    CONF_TOKEN,
)
from .cloudflared import CloudflaredTunnel

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [PLATFORM_SENSOR, PLATFORM_BUTTON]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cloudflared Tunnel from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    
    if DATA_TUNNELS not in hass.data[DOMAIN]:
        hass.data[DOMAIN][DATA_TUNNELS] = {}

    hostname = entry.data[CONF_HOSTNAME]
    port = entry.data[CONF_PORT]
    token = entry.data.get(CONF_TOKEN)  # Optional token

    tunnel = CloudflaredTunnel(hass, hostname, port, token)
    
    try:
        # Initialize monitoring first
        await tunnel.async_init()
        # Then try to start the tunnel
        await tunnel.start()
    except Exception as err:
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][DATA_TUNNELS][entry.entry_id] = tunnel
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    tunnel = hass.data[DOMAIN][DATA_TUNNELS].get(entry.entry_id)
    if tunnel:
        await tunnel.stop()
        
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN][DATA_TUNNELS].pop(entry.entry_id)

    return unload_ok