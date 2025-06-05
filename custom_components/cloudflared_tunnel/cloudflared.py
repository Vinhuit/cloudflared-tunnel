"""Cloudflared tunnel management."""
import asyncio
import logging
import os
import platform
import shutil
import stat
import urllib.request
import time
from typing import Optional, Callable
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers.event import async_track_time_interval
import homeassistant.util.dt as dt_util

from .const import STATUS_RUNNING, STATUS_STOPPED, STATUS_ERROR

_LOGGER = logging.getLogger(__name__)

BIN_DIR = os.path.join(os.path.dirname(__file__), "bin")
BIN_PATH = os.path.join(BIN_DIR, "cloudflared" + (".exe" if platform.system().lower() == "windows" else ""))

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

async def safe_download_cloudflared() -> None:
    """Download the cloudflared binary with retries."""
    temp_path = BIN_PATH + ".tmp"
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
    
    # Download to temporary file first
    urllib.request.urlretrieve(url, temp_path)
    
    if system != "windows":
        os.chmod(temp_path, os.stat(temp_path).st_mode | stat.S_IEXEC)
    
    # Replace the actual binary
    if os.path.exists(BIN_PATH):
        os.remove(BIN_PATH)
    os.rename(temp_path, BIN_PATH)
    
    _LOGGER.info("cloudflared downloaded to: %s", BIN_PATH)


class CloudflaredTunnel:
    """Class to manage a Cloudflared tunnel."""

    def __init__(self, hass: HomeAssistant, hostname: str, port: int, token: Optional[str] = None) -> None:
        """Initialize the tunnel."""
        self.hass = hass
        self.hostname = hostname
        self.port = port
        self.token = token
        self.process: Optional[asyncio.subprocess.Process] = None
        self._status = STATUS_STOPPED
        self._listeners: list[Callable] = []
        self._error_msg: Optional[str] = None
        self._last_restart: Optional[datetime] = None
        self._status_check_unsub = None

    async def async_init(self) -> None:
        """Initialize async components."""
        await self._start_status_monitoring()

    async def _start_status_monitoring(self) -> None:
        """Start periodic status monitoring."""
        if self._status_check_unsub is not None:
            self._status_check_unsub()
        
        self._status_check_unsub = async_track_time_interval(
            self.hass, 
            self._check_process_status,
            timedelta(seconds=30)
        )

    async def _check_process_status(self, *_) -> None:
        """Check if the process is still running and update status."""
        if not self.process:
            if self._status != STATUS_STOPPED:
                self._update_status(STATUS_STOPPED)
            return

        try:
            # Check if process is still running
            if self.process.returncode is not None:
                # Process has terminated
                self._error_msg = "Process terminated unexpectedly"
                self._update_status(STATUS_ERROR)
                self.process = None
                
                # Attempt restart if it wasn't stopped intentionally
                if (self._last_restart is None or 
                    (dt_util.utcnow() - self._last_restart).total_seconds() > 300):  # 5 minute cooldown
                    _LOGGER.info("Tunnel terminated unexpectedly, attempting restart...")
                    self._last_restart = dt_util.utcnow()
                    await self.start()
            elif self._status != STATUS_RUNNING:
                # Process is running but status doesn't reflect it
                self._update_status(STATUS_RUNNING)
                
        except Exception as err:
            _LOGGER.error("Error checking tunnel status: %s", err)
            self._error_msg = str(err)
            self._update_status(STATUS_ERROR)

    @property
    def status(self) -> str:
        """Get the current tunnel status."""
        if self._status == STATUS_ERROR and self._error_msg:
            return f"{STATUS_ERROR}: {self._error_msg}"
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
        if new_status != self._status:
            self._status = new_status
            for listener in self._listeners:
                self.hass.async_create_task(listener())

    async def start(self) -> None:
        """Start the tunnel."""
        if self.process and self.process.returncode is None:
            return

        # Ensure binary directory exists
        os.makedirs(BIN_DIR, exist_ok=True)

        # Download or update binary if needed
        if not os.path.exists(BIN_PATH):
            _LOGGER.info("cloudflared binary not found, downloading...")
            await self.hass.async_add_executor_job(safe_download_cloudflared)

        retries = MAX_RETRIES
        while retries > 0:
            try:
                cmd = [
                    BIN_PATH,
                    "access",
                    "tcp",
                    "--hostname",
                    self.hostname,
                    "--url",
                    f"localhost:{self.port}",
                ]

                if self.token:
                    cmd.extend(["--service-token-id", self.token])

                self.process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                # Check initial output for any immediate errors
                error_line = await self.process.stderr.readline()
                if error_line:
                    error_msg = error_line.decode().strip()
                    if "text file busy" in error_msg.lower():
                        if retries > 1:
                            _LOGGER.warning("Binary is busy, retrying in %s seconds...", RETRY_DELAY)
                            await asyncio.sleep(RETRY_DELAY)
                            retries -= 1
                            continue
                    if "token" in error_msg.lower():
                        raise ConfigEntryError(f"Token authentication failed: {error_msg}")
                    raise ConfigEntryError(f"Tunnel error: {error_msg}")

                self._status = STATUS_RUNNING
                self._error_msg = None
                _LOGGER.info(
                    "Started cloudflared tunnel for %s:%s%s",
                    self.hostname,
                    self.port,
                    " (Protected)" if self.token else ""
                )

                # Monitor the process output
                self.hass.loop.create_task(self._monitor_output())
                break

            except Exception as err:
                if "text file busy" in str(err).lower() and retries > 1:
                    _LOGGER.warning("Binary is busy, retrying in %s seconds...", RETRY_DELAY)
                    await asyncio.sleep(RETRY_DELAY)
                    retries -= 1
                    continue
                self._status = STATUS_ERROR
                self._error_msg = str(err)
                _LOGGER.error("Failed to start tunnel: %s", err)
                raise

        if retries == 0:
            raise ConfigEntryError("Failed to start tunnel after multiple retries")

    async def _monitor_output(self) -> None:
        """Monitor the tunnel process output."""
        assert self.process is not None

        while True:
            try:
                line = await self.process.stdout.readline()
                if not line:
                    error_line = await self.process.stderr.readline()
                    if error_line:
                        self._error_msg = error_line.decode().strip()
                        self._update_status(STATUS_ERROR)
                    break

                log_line = line.decode().strip()
                _LOGGER.debug("[cloudflared] %s", log_line)

                if "error" in log_line.lower():
                    self._error_msg = log_line
                    self._update_status(STATUS_ERROR)

            except Exception as err:
                _LOGGER.error("Error monitoring tunnel output: %s", err)
                self._error_msg = str(err)
                self._update_status(STATUS_ERROR)
                break

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

        # Stop the status monitoring
        if self._status_check_unsub:
            self._status_check_unsub()
            self._status_check_unsub = None

    async def __aenter__(self):
        """Start the tunnel when entering context."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop the tunnel when exiting context."""
        await self.stop()