# Cloudflared Tunnel Integration for Home Assistant

This custom integration allows you to run Cloudflare TCP access tunnels to expose local services securely over the internet. It uses the `cloudflared access tcp` command to create tunnels without requiring a permanent tunnel configuration.

## Features

- Multiple TCP access tunnel support
- Automatic download and management of the `cloudflared` binary
- User-friendly configuration through the UI
- Real-time tunnel status monitoring
- Stop/Start controls for each tunnel
- JWT token support for protected services
- Perfect for temporary or dynamic TCP tunnels
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
- **JWT Token**: (Optional) Service token for protected services

### Getting a JWT Token

If you want to protect your tunnel with authentication, you can use a JWT token. Here's how to get one:

1. Go to the [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com)
2. Navigate to **Access > Service Auth**
3. Click **Create Service Token**
4. Configure your token:
   - Give it a name (e.g., "HA Tunnel Token")
   - Set the duration (or leave blank for no expiration)
   - Add any IP restrictions if desired
5. Click **Generate Token**
6. Copy the token and paste it in the integration's configuration

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

## Example Use Cases

1. Protected Wyoming Protocol Services:
```yaml
hostname: wyoming.mydomain.com
port: 10300
token: your_jwt_token_here  # Optional
```

2. Public Home Assistant Remote Access:
```yaml
hostname: home.mydomain.com
port: 8123
# No token = public access
```

3. Protected SSH Access:
```yaml
hostname: ssh.mydomain.com
port: 22
token: your_jwt_token_here  # Recommended for SSH
```

## How It Works

This integration uses Cloudflare's TCP tunneling feature (`cloudflared access tcp`) to create instant tunnels. Each tunnel:

1. Establishes a secure connection to Cloudflare
2. Routes traffic from your chosen hostname to a local port
3. Can be optionally protected with JWT authentication
4. Can be started/stopped on demand

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