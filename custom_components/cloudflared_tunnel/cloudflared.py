"""Cloudflared tunnel management."""
import asyncio
import logging
import os
import platform
import shutil
import stat
import urllib.request
from typing import Optional, Callable
from homeassistant.core import HomeAssistant

from .const import STATUS_RUNNING, STATUS_STOPPED, STATUS_ERROR

_LOGGER = logging.getLogger(__name__)

BIN_DIR = os.path.join(os.path.dirname(__file__), "bin")
BIN_PATH = os.path.join(BIN_DIR, "cloudflared" + (".exe" if platform.system().lower() == "windows" else ""))


class CloudflaredTunnel:
    """Class to manage a Cloudflared tunnel."""

    def __init__(self, hass: HomeAssistant, hostname: str, port: int) -> None:
        """Initialize the tunnel."""
        self.hass = hass
        self.hostname = hostname
        self.port = port
        self.process: Optional[asyncio.subprocess.Process] = None
        self._status = STATUS_STOPPED
        self._listeners: list[Callable] = []

    @property
    def status(self) -> str:
        """Get the current tunnel status."""
        return self._status

    def add_status_listener(self, listener: Callable) -> None:
        """Add a callback for status updates."""
        self._listeners.append(listener)

    def remove_status_listener(self, listener: Callable) -> None:
        """Remove a status callback."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _update_status(self, new_status: str) -> None:
        """Update status and notify listeners."""
        self._status = new_status
        for listener in self._listeners:
            self.hass.async_create_task(listener())

    async def start(self) -> None:
        """Start the tunnel."""
        if self.process:
            return

        if not os.path.exists(BIN_PATH):
            _LOGGER.info("cloudflared binary not found, downloading...")
            await self.hass.async_add_executor_job(download_cloudflared)

        try:
            self.process = await asyncio.create_subprocess_exec(
                BIN_PATH,
                "tunnel",
                "--url",
                f"http://localhost:{self.port}",
                "--hostname",
                self.hostname,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self._update_status(STATUS_RUNNING)
            _LOGGER.info("Started cloudflared tunnel for %s:%s", self.hostname, self.port)

            # Monitor the process output
            self.hass.loop.create_task(self._monitor_output())

        except Exception as err:
            self._update_status(STATUS_ERROR)
            _LOGGER.error("Failed to start tunnel: %s", err)
            raise

    async def _monitor_output(self) -> None:
        """Monitor the tunnel process output."""
        assert self.process is not None
        while True:
            line = await self.process.stdout.readline()
            if not line:
                break
            _LOGGER.debug("[cloudflared] %s", line.decode().strip())

    async def stop(self) -> None:
        """Stop the tunnel."""
        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
            finally:
                self.process = None
                self._update_status(STATUS_STOPPED)
                _LOGGER.info("Stopped cloudflared tunnel for %s:%s", self.hostname, self.port)


def download_cloudflared() -> None:
    """Download the cloudflared binary."""
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

    _LOGGER.info("Downloading cloudflared from %s", url)
    dest = BIN_PATH
    urllib.request.urlretrieve(url, dest)

    if system != "windows":
        os.chmod(dest, os.stat(dest).st_mode | stat.S_IEXEC)

    _LOGGER.info("cloudflared downloaded to: %s", BIN_PATH)