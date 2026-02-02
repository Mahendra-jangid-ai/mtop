import time
from datetime import datetime
from typing import Dict


class UptimeProvider:
    """
    Provides system uptime, boot time, and load averages.
    Linux-specific implementation using /proc.
    """

    UPTIME_PATH = "/proc/uptime"
    LOADAVG_PATH = "/proc/loadavg"

    def __init__(self) -> None:
        pass

    def get_uptime_seconds(self) -> float:
        """
        Reads total system uptime in seconds from /proc/uptime.
        """
        try:
            with open(self.UPTIME_PATH, "r", encoding="utf-8") as file:
                return float(file.readline().split()[0])
        except (OSError, IOError, ValueError):
            return 0.0

    def get_boot_time(self) -> str:
        """
        Calculates the system boot timestamp as a formatted string.
        """
        uptime_sec = self.get_uptime_seconds()
        boot_timestamp = time.time() - uptime_sec

        return datetime.fromtimestamp(
            boot_timestamp
        ).strftime("%Y-%m-%d %H:%M:%S")

    def get_load_average(self) -> Dict[str, float]:
        """
        Reads the 1, 5, and 15 minute load averages from /proc/loadavg.
        """
        try:
            with open(self.LOADAVG_PATH, "r", encoding="utf-8") as file:
                parts = file.readline().split()
                return {
                    "1min": float(parts[0]),
                    "5min": float(parts[1]),
                    "15min": float(parts[2]),
                }
        except (OSError, IOError, ValueError, IndexError):
            return {"1min": 0.0, "5min": 0.0, "15min": 0.0}

    def format_uptime(self) -> str:
        """
        Converts uptime seconds into a human-readable format.
        """
        seconds = int(self.get_uptime_seconds())

        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)

