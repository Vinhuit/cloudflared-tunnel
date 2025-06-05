import asyncio
import logging
import os
import platform
import shutil
import stat
import urllib.request

_LOGGER = logging.getLogger(__name__)

BIN_DIR = "/config/cloudflared"
BIN_PATH = os.path.join(BIN_DIR, "cloudflared")

async def start_cloudflared_tunnel(hass, hostname, port):
    if not os.path.exists(BIN_PATH):
        _LOGGER.warning("cloudflared binary not found, downloading...")
        await hass.async_add_executor_job(download_cloudflared)

    cmd = [
        BIN_PATH,
        "access", "tcp",
        "--hostname", hostname,
        "--url", f"localhost:{port}"
    ]

    async def _run():
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            _LOGGER.info(f"[cloudflared] {line.decode().strip()}")

    hass.loop.create_task(_run())

def download_cloudflared():
    os.makedirs(BIN_DIR, exist_ok=True)

    system = platform.system().lower()
    arch = platform.machine().lower()

    if system == "linux":
        if "arm" in arch or "aarch64" in arch:
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
        elif "x86_64" in arch:
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        else:
            raise RuntimeError(f"Unsupported architecture: {arch}")
    elif system == "darwin":
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
    elif system == "windows":
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    else:
        raise RuntimeError(f"Unsupported OS: {system}")

    _LOGGER.info(f"Downloading cloudflared from {url}")
    dest = BIN_PATH + (".exe" if system == "windows" else "")
    urllib.request.urlretrieve(url, dest)

    os.chmod(dest, os.stat(dest).st_mode | stat.S_IEXEC)

    if not os.path.exists(BIN_PATH) and system != "windows":
        shutil.move(dest, BIN_PATH)

    _LOGGER.info(f"cloudflared downloaded to: {BIN_PATH}")