# 🚇 Cloudflared Tunnel Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

> Create secure tunnels to expose your Home Assistant services using Cloudflare Zero Trust

![Cloudflared Tunnel Logo](custom_components/cloudflared_tunnel/brands/icon.png)

This custom integration provides a seamless way to expose local Home Assistant services securely over the internet using Cloudflare's TCP access tunnels. Unlike traditional Cloudflared tunnels, this integration uses the `cloudflared access tcp` command for quick, configuration-free tunnel creation.

[Getting Started](#getting-started) • [Installation](#installation) • [Configuration](#configuration) • [Features](#features) • [Troubleshooting](#troubleshooting)

## ✨ Features

🔄 **Dynamic Tunnels**
- Create multiple TCP access tunnels on demand
- Perfect for temporary or dynamic service exposure
- No permanent tunnel configuration needed

🔒 **Security**
- JWT token support for protected services
- Cloudflare Zero Trust integration
- Real-time tunnel status monitoring

🤖 **Automation Ready**
- Start/Stop controls via service calls
- Status sensors for automation triggers
- Protection status tracking

🛠️ **Easy Management**
- Automatic download of the correct `cloudflared` binary
- User-friendly configuration through Home Assistant UI
- Real-time status updates and error reporting

📊 **Monitoring**
- Dedicated sensor entities for each tunnel
- Status, hostname, and port monitoring
- Protection status tracking

## 🚀 Getting Started

### Prerequisites

- Home Assistant 2023.8.0 or newer
- A Cloudflare account with a registered domain
- [HACS](https://hacs.xyz/) installed (for easy installation)
- (Optional) Cloudflare Zero Trust account for protected tunnels

### Installation

#### Option 1: HACS (Recommended)

1. Open HACS in Home Assistant
2. Click ⋮ > Custom Repositories
3. Add this repository:
   ```
   URL: https://github.com/Vinhuit/cloudflared_tunnel
   Category: Integration
   ```
4. Click "Download"
5. Restart Home Assistant
6. Go to Settings > Devices & Services
7. Click "+ ADD INTEGRATION"
8. Search for "Cloudflared Tunnel"

#### Option 2: Manual Installation

1. Download the [latest release](https://github.com/Vinhuit/cloudflared_tunnel/releases)
2. Extract and copy `cloudflared_tunnel` folder to:
   ```
   config/custom_components/cloudflared_tunnel/
   ```
3. Restart Home Assistant
4. Go to Settings > Devices & Services
5. Click "+ ADD INTEGRATION"
6. Search for "Cloudflared Tunnel"

## ⚙️ Configuration

### Basic Setup

Each tunnel requires just two pieces of information:
1. **Hostname** - Your Cloudflare domain or subdomain
   ```
   Example: assistant.yourdomain.com
   ```
2. **Local Port** - The port of your service
   ```
   Examples:
   - 8123 (Home Assistant)
   - 10300 (Wyoming Protocol)
   - 1883 (MQTT)
   ```

### Protected Tunnels (Optional)

To add authentication to your tunnel:

1. Visit [Cloudflare Zero Trust](https://one.dash.cloudflare.com)
2. Go to **Access > Service Auth**
3. Click **Create Service Token**
4. Configure your token:
   - Name: `HA Tunnel Token`
   - Duration: Choose expiration (or leave blank)
   - Restrictions: Add IP limits if desired
5. Click **Generate Token**
6. Copy & paste the token during tunnel setup

### Advanced Usage

You can create multiple tunnels with different configurations:

```yaml
# Example Configurations

Home Assistant UI:
  hostname: home.example.com
  port: 8123
  token: [optional]

Voice Assistant:
  hostname: voice.example.com
  port: 10300
  token: required_for_protection

MQTT Broker:
  hostname: mqtt.example.com
  port: 1883
  token: required_for_security
```

The token will be used to authenticate the tunnel connection. When a token is used:
- The tunnel becomes protected, requiring authentication
- A "Protection" sensor will show "Protected" status
- The tunnel logs will indicate it's running in protected mode

## Entities Created

For each tunnel, the following entities are created:

- **Hostname Sensor**: Shows the configured hostname
- **Port Sensor**: Shows the configured local port
- **Status Sensor**: Shows the current tunnel status (running/stopped/error)
- **Stop Button**: Allows stopping the tunnel

## 🔧 Integration Details

### Available Entities

Each tunnel creates several entities:

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.cloudflared_[hostname]_status` | Sensor | Tunnel status (running/stopped/error) |
| `sensor.cloudflared_[hostname]_protection` | Sensor | Protection status (protected/public) |
| `button.cloudflared_[hostname]_stop` | Button | Stop tunnel control |
| `sensor.cloudflared_[hostname]_port` | Sensor | Local port number |

### Common Use Cases

#### 1. Voice Assistant Access
```yaml
hostname: voice.example.com
port: 10300  # Wyoming Protocol
token: optional_for_protection
```

#### 2. Remote UI Access
```yaml
hostname: ha.example.com
port: 8123    # Home Assistant
# No token for public access
```

#### 3. Secure MQTT
```yaml
hostname: mqtt.example.com
port: 1883
token: recommended_for_security
```

## 🔍 Troubleshooting

### Common Issues

#### Tunnel Won't Start
- Verify hostname DNS configuration in Cloudflare
- Check if port is available and service is running
- Review Home Assistant logs for error messages

#### Binary Download Issues
1. Check internet connectivity
2. Verify write permissions
3. Try downloading `cloudflared` manually
4. Check system architecture compatibility

#### Protection Issues
1. Verify token format
2. Ensure token hasn't expired
3. Check IP restrictions if configured
4. Verify Zero Trust settings

### Advanced Debugging

Enable debug logging by adding to `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.cloudflared_tunnel: debug
```

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ❤️ Support

- 🐛 Found a bug? [Open an issue](https://github.com/Vinhuit/cloudflared_tunnel/issues)
- 💡 Have an idea? Start a [Discussion](https://github.com/Vinhuit/cloudflared_tunnel/discussions)
- ⭐ Like this project? Star it on GitHub!

---

<sub>[releases]: https://github.com/Vinhuit/cloudflared_tunnel/releases
[releases-shield]: https://img.shields.io/github/release/Vinhuit/cloudflared_tunnel.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/Vinhuit/cloudflared_tunnel.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40Vinhuit-blue.svg?style=for-the-badge
[user_profile]: https://github.com/Vinhuit
[buymecoffee]: https://www.buymeacoffee.com/Vinhuit
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge</sub>
