# Cloudflared Tunnel Integration for Home Assistant

This custom integration allows you to run Cloudflare TCP tunnels to expose local services securely over the internet.

## Features

- Multiple tunnel support
- Automatic download and management of the `cloudflared` binary
- User-friendly configuration through the UI
- Real-time tunnel status monitoring
- Stop/Start controls for each tunnel
- HACS-compatible

## Installation

### Method 1: HACS (Recommended)

1. Add this repository to HACS as a custom repository:
   - Repository: `https://github.com/Vinhuit/cloudflared_tunnel`
   - Category: "Integration"
2. Install the "Cloudflared Tunnel" integration
3. Restart Home Assistant
4. Go to Settings -> Devices & Services -> Add Integration
5. Search for "Cloudflared Tunnel" and configure your tunnel

### Method 2: Manual Installation

1. Download the latest release
2. Copy the `cloudflared_tunnel` directory to `custom_components/cloudflared_tunnel/`
3. Restart Home Assistant
4. Go to Settings -> Devices & Services -> Add Integration
5. Search for "Cloudflared Tunnel" and configure your tunnel

## Configuration

Each tunnel requires:
- **Hostname**: The Cloudflare hostname for your tunnel (e.g., `mytunnel.mydomain.com`)
- **Local Port**: The local port to tunnel (e.g., `10300` for Wyoming Protocol)

## Entities Created

For each tunnel, the following entities are created:

- **Hostname Sensor**: Shows the configured hostname
- **Port Sensor**: Shows the configured local port
- **Status Sensor**: Shows the current tunnel status (running/stopped/error)
- **Stop Button**: Allows stopping the tunnel

## Example Use Cases

1. Wyoming Protocol Services:
```yaml
hostname: tts.mydomain.com
port: 10300
```

2. Home Assistant Remote Access:
```yaml
hostname: home.mydomain.com
port: 8123
```

## Troubleshooting

1. If the tunnel fails to start:
   - Check that the hostname is properly configured in Cloudflare
   - Verify the local service is running on the specified port
   - Check Home Assistant logs for detailed error messages

2. If the binary fails to download:
   - Check your internet connection
   - Verify Home Assistant has write permissions to the binary directory
   - Try manual installation of cloudflared

## Support

- For bugs and feature requests, open an issue on GitHub
- For general questions, use the discussions section

## License

This project is licensed under the MIT License - see the LICENSE file for details