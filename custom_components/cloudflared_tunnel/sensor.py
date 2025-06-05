"""Sensor platform for Cloudflared Tunnel."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    CONF_HOSTNAME,
    CONF_PORT,
    DATA_TUNNELS,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Cloudflared Tunnel sensors."""
    tunnel = hass.data[DOMAIN][DATA_TUNNELS][config_entry.entry_id]
    
    entities = [
        CloudflaredHostnameSensor(config_entry, tunnel),
        CloudflaredPortSensor(config_entry, tunnel),
        CloudflaredStatusSensor(config_entry, tunnel),
    ]
    async_add_entities(entities)


class CloudflaredBaseSensor(SensorEntity):
    """Base class for Cloudflared sensors."""

    _attr_has_entity_name = True

    def __init__(self, config_entry: ConfigEntry, tunnel) -> None:
        """Initialize the sensor."""
        self._config_entry = config_entry
        self._tunnel = tunnel
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"Cloudflared Tunnel ({tunnel.hostname})",
            manufacturer="Cloudflare",
        )


class CloudflaredHostnameSensor(CloudflaredBaseSensor):
    """Sensor for Cloudflared hostname."""

    _attr_name = "Hostname"
    _attr_icon = "mdi:web"

    def __init__(self, config_entry: ConfigEntry, tunnel) -> None:
        """Initialize the sensor."""
        super().__init__(config_entry, tunnel)
        self._attr_unique_id = f"{config_entry.entry_id}_hostname"
        self._attr_native_value = tunnel.hostname


class CloudflaredPortSensor(CloudflaredBaseSensor):
    """Sensor for Cloudflared local port."""

    _attr_name = "Local Port"
    _attr_icon = "mdi:port"

    def __init__(self, config_entry: ConfigEntry, tunnel) -> None:
        """Initialize the sensor."""
        super().__init__(config_entry, tunnel)
        self._attr_unique_id = f"{config_entry.entry_id}_port"
        self._attr_native_value = tunnel.port


class CloudflaredStatusSensor(CloudflaredBaseSensor):
    """Sensor for Cloudflared tunnel status."""

    _attr_name = "Status"
    _attr_icon = "mdi:tunnel"

    def __init__(self, config_entry: ConfigEntry, tunnel) -> None:
        """Initialize the sensor."""
        super().__init__(config_entry, tunnel)
        self._attr_unique_id = f"{config_entry.entry_id}_status"
        self._attr_native_value = tunnel.status
        tunnel.add_status_listener(self._handle_status_update)

    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        self._tunnel.remove_status_listener(self._handle_status_update)

    @callback
    async def _handle_status_update(self):
        """Handle status updates."""
        self._attr_native_value = self._tunnel.status
        self.async_write_ha_state()
