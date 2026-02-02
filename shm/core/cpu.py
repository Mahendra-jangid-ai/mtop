import os
from typing import Dict, Tuple


class CPUProvider:
    """
    Provides CPU utilization metrics using /proc filesystem (Linux only).

    Tracks total CPU usage and per-core usage by computing deltas
    between consecutive reads of /proc/stat.
    """

    CPUINFO_PATH = "/proc/cpuinfo"
    STAT_PATH = "/proc/stat"

    def __init__(self) -> None:
        self.history: Dict[str, Tuple[int, int]] = {}
        self.cpu_count: int = os.cpu_count() or 1
        self.cpu_model: str = self._get_cpu_model()

    def _get_cpu_model(self) -> str:
        """
        Reads CPU model name from /proc/cpuinfo.
        """
        try:
            with open(self.CPUINFO_PATH, "r", encoding="utf-8") as file:
                for line in file:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except (OSError, IOError):
            pass

        return "Unknown CPU"

    def _read_stats(self) -> Dict[str, Tuple[int, int]]:
        """
        Reads total and idle CPU ticks from /proc/stat.

        Returns:
            Dict mapping cpu id -> (total_ticks, idle_ticks)
        """
        stats: Dict[str, Tuple[int, int]] = {}

        try:
            with open(self.STAT_PATH, "r", encoding="utf-8") as file:
                for line in file:
                    if not line.startswith("cpu"):
                        continue

                    parts = line.split()
                    if len(parts) < 8:
                        continue

                    ticks = list(map(int, parts[1:8]))
                    idle = ticks[3] + ticks[4]
                    total = sum(ticks)

                    stats[parts[0]] = (total, idle)
        except (OSError, IOError):
            pass

        return stats

    def get_metrics(self) -> Dict[str, object]:
        """
        Computes CPU utilization percentages.

        Returns:
            {
                "model": str,
                "total": float,
                "cores": { "cpu0": float, "cpu1": float, ... }
            }
        """
        current = self._read_stats()

        result = {
            "model": self.cpu_model,
            "total": 0.0,
            "cores": {},
        }

        for cpu, (total, idle) in current.items():
            prev_total, prev_idle = self.history.get(cpu, (total, idle))

            diff_total = total - prev_total
            diff_idle = idle - prev_idle

            usage = (
                ((diff_total - diff_idle) / diff_total * 100)
                if diff_total > 0
                else 0.0
            )
            usage = round(usage, 1)

            if cpu == "cpu":
                result["total"] = usage
            else:
                result["cores"][cpu] = usage

            self.history[cpu] = (total, idle)

        return result
