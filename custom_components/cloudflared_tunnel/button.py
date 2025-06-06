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
    """Set up the Cloudflared Tunnel buttons."""
    tunnel = hass.data[DOMAIN][DATA_TUNNELS][config_entry.entry_id]
    async_add_entities([
        CloudflaredStopButton(config_entry, tunnel),
        CloudflaredStartButton(config_entry, tunnel)
    ])


class CloudflaredBaseButton(ButtonEntity):
    """Base button class for Cloudflared tunnel controls."""

    _attr_has_entity_name = True

    def __init__(self, config_entry: ConfigEntry, tunnel) -> None:
        """Initialize the button."""
        self._config_entry = config_entry
        self._tunnel = tunnel
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"Cloudflared Tunnel ({tunnel.hostname})",
            manufacturer="Cloudflare",
        )

class CloudflaredStopButton(CloudflaredBaseButton):
    """Button to stop the Cloudflared tunnel."""

    _attr_name = "Stop Tunnel"
    _attr_icon = "mdi:stop-circle"

    def __init__(self, config_entry: ConfigEntry, tunnel) -> None:
        """Initialize the button."""
        super().__init__(config_entry, tunnel)
        self._attr_unique_id = f"{config_entry.entry_id}_stop_button"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._tunnel.stop()

class CloudflaredStartButton(CloudflaredBaseButton):
    """Button to start the Cloudflared tunnel."""

    _attr_name = "Start Tunnel"
    _attr_icon = "mdi:play-circle"

    def __init__(self, config_entry: ConfigEntry, tunnel) -> None:
        """Initialize the button."""
        super().__init__(config_entry, tunnel)
        self._attr_unique_id = f"{config_entry.entry_id}_start_button"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._tunnel.start()
