import os
import time
from typing import Dict, List, Optional, Tuple


class ProcessProvider:
    """
    Provides per-process CPU usage by sampling /proc/[pid]/stat.
    Linux-specific implementation.
    """

    PROC_PATH = "/proc"

    def __init__(self) -> None:
        # { pid: (ticks, timestamp) }
        self.last: Dict[str, Tuple[int, float]] = {}

        # System clock ticks per second (typically 100)
        self.clk: int = os.sysconf(os.sysconf_names["SC_CLK_TCK"])

    def _ticks(self, pid: str) -> Optional[int]:
        """
        Returns total CPU ticks (utime + stime) for a process.
        """
        try:
            with open(f"{self.PROC_PATH}/{pid}/stat", "r", encoding="utf-8") as file:
                data = file.read().split()
                # utime (14) + stime (15)
                return int(data[13]) + int(data[14])
        except (OSError, IOError, IndexError, ValueError):
            return None

    def _name(self, pid: str) -> str:
        """
        Returns process name from /proc/[pid]/comm.
        """
        try:
            with open(f"{self.PROC_PATH}/{pid}/comm", "r", encoding="utf-8") as file:
                return file.read().strip()
        except (OSError, IOError):
            return "unknown"

    def get_top(self, limit: int = 10) -> List[Dict[str, object]]:
        """
        Returns a list of top processes sorted by CPU usage.

        Each entry:
            { pid, name, cpu }
        """
        now = time.time()
        result: List[Dict[str, object]] = []

        # Iterate numeric PIDs in /proc
        for pid in filter(str.isdigit, os.listdir(self.PROC_PATH)):
            ticks = self._ticks(pid)
            if ticks is None:
                continue

            prev_ticks, prev_time = self.last.get(pid, (ticks, now))

            tick_diff = ticks - prev_ticks
            time_diff = now - prev_time

            if tick_diff > 0 and time_diff > 0:
                # CPU % = (delta_ticks / clock_ticks_per_sec) / delta_time * 100
                cpu = (tick_diff / self.clk) / time_diff * 100

                result.append({
                    "pid": pid,
                    "name": self._name(pid),
                    "cpu": round(cpu, 1),
                })

            self.last[pid] = (ticks, now)

        # Highest CPU usage first
        result.sort(key=lambda item: item["cpu"], reverse=True)
        return result[:limit]
