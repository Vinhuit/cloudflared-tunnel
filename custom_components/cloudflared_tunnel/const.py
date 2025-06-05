"""Constants for the Cloudflared Tunnel integration."""

DOMAIN = "cloudflared_tunnel"

# Configuration
CONF_HOSTNAME = "hostname"
CONF_PORT = "port"
CONF_TOKEN = "token"  # JWT token

# Platform names
PLATFORM_SENSOR = "sensor"
PLATFORM_BUTTON = "button"

# Tunnel status
STATUS_RUNNING = "running"
STATUS_STOPPED = "stopped"
STATUS_ERROR = "error"

# Data storage keys
DATA_TUNNELS = "tunnels"

# URLs
TOKEN_DOCS_URL = "https://developers.cloudflare.com/cloudflare-one/identity/users/service-tokens/"