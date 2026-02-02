import os
from typing import Dict


class MemoryProvider:
    """
    Provides system memory statistics using /proc/meminfo.
    Linux-specific implementation.
    """

    MEMINFO_PATH = "/proc/meminfo"

    def __init__(self) -> None:
        pass

    # ---------------- SYSTEM MEMORY ----------------
    def get_system_memory(self) -> Dict[str, int]:
        """
        Returns system-wide memory stats based on /proc/meminfo.

        All values are in bytes.
        """
        mem: Dict[str, int] = {}

        try:
            with open(self.MEMINFO_PATH, "r", encoding="utf-8") as file:
                for line in file:
                    key, value = line.split(":", 1)
                    mem[key.strip()] = int(value.strip().split()[0]) * 1024
        except (OSError, IOError):
            return {}

        total = mem.get("MemTotal", 0)
        free = mem.get("MemFree", 0)
        buffers = mem.get("Buffers", 0)
        cached = mem.get("Cached", 0) + mem.get("SReclaimable", 0)
        shared = mem.get("Shmem", 0)
        available = mem.get("MemAvailable", 0)

        # Linux-preferred logic: Total - Available
        used = (
            total - available
            if available
            else (total - free - buffers - cached)
        )

        swap_total = mem.get("SwapTotal", 0)
        swap_free = mem.get("SwapFree", 0)
        swap_used = swap_total - swap_free

        return {
            "total": total,
            "used": used,
            "free": free,
            "available": available,
            "buffers": buffers,
            "cached": cached,
            "shared": shared,
            "swap_total": swap_total,
            "swap_used": swap_used,
            "swap_free": swap_free,
        }

    # ---------------- UTILITY ----------------
    @staticmethod
    def format_bytes(size: float) -> str:
        """
        Formats a byte value into a human-readable string.
        """
        for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

        return f"{size:.2f} EiB"

