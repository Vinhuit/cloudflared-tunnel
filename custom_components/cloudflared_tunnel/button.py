"""Button platform for Cloudflared Tunnel."""
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, DATA_TUNNELS


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Cloudflared Tunnel button."""
    tunnel = hass.data[DOMAIN][DATA_TUNNELS][config_entry.entry_id]
    async_add_entities([CloudflaredStopButton(config_entry, tunnel)])


class CloudflaredStopButton(ButtonEntity):
    """Button to stop the Cloudflared tunnel."""

    _attr_has_entity_name = True
    _attr_name = "Stop Tunnel"
    _attr_icon = "mdi:stop-circle"

    def __init__(self, config_entry: ConfigEntry, tunnel) -> None:
        """Initialize the button."""
        self._config_entry = config_entry
        self._tunnel = tunnel
        self._attr_unique_id = f"{config_entry.entry_id}_stop_button"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"Cloudflared Tunnel ({tunnel.hostname})",
            manufacturer="Cloudflare",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._tunnel.stop()
