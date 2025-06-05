# Cloudflared Tunnel Integration for Home Assistant

This custom integration allows you to run a Cloudflare TCP tunnel to expose services like Piper/Whisper over the Wyoming Protocol.

## Features

- Automatically downloads `cloudflared` binary if missing
- Allows configuration of hostname and local port
- Starts tunnel on Home Assistant startup
- HACS-compatible

## Installation

1. Copy to `custom_components/cloudflared_tunnel/`
2. Add to HACS as a custom repository
3. Restart Home Assistant
4. Add the integration and configure your hostname + port

## Example Use Case

Tunnel your remote TTS service with:

```
cloudflared access tcp --hostname wyoming.mixsmart.dev --url localhost:10300
```

## License

MIT