"""Sensor platform for Cloudflared Tunnel."""
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo, EntityCategory

from .cloudflared import CloudflaredTunnel
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
        CloudflaredProtectionSensor(config_entry, tunnel),
    ]
    async_add_entities(entities)


class CloudflaredBaseSensor(SensorEntity):    """Base class for Cloudflared sensors.
    
    This class provides common functionality for all Cloudflared tunnel sensors
    including device info and automatic entity naming.
    """
    _attr_has_entity_name = True
    _attr_should_poll = False  # We'll use events instead of polling
    def __init__(self, config_entry: ConfigEntry, tunnel: "CloudflaredTunnel") -> None:
        """Initialize the sensor."""
        self._config_entry = config_entry
        self._tunnel = tunnel
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"Cloudflared Tunnel ({tunnel.hostname})",
            manufacturer="Cloudflare",
            model="TCP Tunnel",
            sw_version="1.0.0",
            configuration_url=f"https://{tunnel.hostname}",
            entry_type="service",
            suggested_area="Network",
        )


class CloudflaredHostnameSensor(CloudflaredBaseSensor):
    """Sensor for Cloudflared hostname."""

    _attr_name = "Hostname"
    _attr_icon = "mdi:web"
    _attr_entity_category = EntityCategory.DIAGNOSTIC    
    def __init__(self, config_entry: ConfigEntry, tunnel: CloudflaredTunnel) -> None:
        """Initialize the sensor."""
        super().__init__(config_entry, tunnel)
        self._attr_unique_id = f"{config_entry.entry_id}_hostname"
        self.entity_id = f"sensor.cloudflared_{config_entry.entry_id}_hostname"

    @property
    def native_value(self) -> str:
        """Return the hostname."""
        return self._tunnel.hostname


class CloudflaredPortSensor(CloudflaredBaseSensor):
    """Sensor for Cloudflared local port."""
    
    _attr_name = "Local Port"
    _attr_icon = "mdi:port"
    _attr_entity_category = EntityCategory.DIAGNOSTIC    
    _attr_native_unit_of_measurement = None  # Port numbers don't have a unit

    def __init__(self, config_entry: ConfigEntry, tunnel: CloudflaredTunnel) -> None:
        """Initialize the sensor."""
        super().__init__(config_entry, tunnel)
        self._attr_unique_id = f"{config_entry.entry_id}_port"
        self.entity_id = f"sensor.cloudflared_{config_entry.entry_id}_port"

    @property
    def native_value(self) -> int:
        """Return the port number."""
        return self._tunnel.port


class CloudflaredStatusSensor(CloudflaredBaseSensor):
    """Sensor for Cloudflared tunnel status.
    
    This is a primary sensor that shows the current status of the tunnel.
    """

    _attr_name = "Status"
    _attr_icon = "mdi:tunnel"    # No entity category for this sensor as it's a primary sensor

    def __init__(self, config_entry: ConfigEntry, tunnel: CloudflaredTunnel) -> None:
        """Initialize the sensor."""
        super().__init__(config_entry, tunnel)
        self._attr_unique_id = f"{config_entry.entry_id}_status"
        self.entity_id = f"sensor.cloudflared_{config_entry.entry_id}_status"
        tunnel.add_status_listener(self._handle_status_update)

    @property
    def native_value(self) -> str:
        """Return the status."""
        return self._tunnel.status    @property
    def extra_state_attributes(self) -> dict[str, str | int | bool]:
        """Return the state attributes."""
        return {
            "last_error": self._tunnel._error_msg,
            "port": self._tunnel.port,
            "hostname": self._tunnel.hostname,
            "protected": bool(self._tunnel.token)
        }

    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        self._tunnel.remove_status_listener(self._handle_status_update)

    @callback
    def _handle_status_update(self):
        """Handle status updates."""
        self.async_write_ha_state()  # This will trigger native_value and attributes update


class CloudflaredProtectionSensor(CloudflaredBaseSensor):
    """Sensor for Cloudflared tunnel protection status."""

    _attr_name = "Protection"
    _attr_icon = "mdi:shield"    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, config_entry: ConfigEntry, tunnel: CloudflaredTunnel) -> None:
        """Initialize the sensor."""
        super().__init__(config_entry, tunnel)
        self._attr_unique_id = f"{config_entry.entry_id}_protection"
        self.entity_id = f"sensor.cloudflared_{config_entry.entry_id}_protection"
    
    @property
    def native_value(self) -> str:
        """Return the protection status."""
        return "Protected" if self._tunnel.token else "Public"
