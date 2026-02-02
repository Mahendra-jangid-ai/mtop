from typing import Dict, List

from shm.core.uptime import UptimeProvider


class UptimeWidget:
    """
    Dynamic uptime + load widget.

    - Pure UI layer
    - No sys.path hacks
    - No provider dependency
    - Future-proof (new fields auto-render)
    - Works on all Linux systems
    """

    def __init__(self) -> None:
        self.colors = {
            "time": "\033[1;33m",      # Yellow
            "load": "\033[38;5;214m",  # Orange
            "label": "\033[1;37m",     # White
            "reset": "\033[0m",
            "critical": "\033[1;31m",  # Red
        }

        # Priority keys (others auto-append)
        self.priority = [
            "uptime",
            "boot_time",
            "load_1m",
            "load_5m",
            "load_15m",
        ]

    # ---------------- FORMAT ----------------
    def _format(self, key: str, value) -> str:
        label = key.replace("_", " ").title()

        if key == "uptime":
            return (
                f"{self.colors['label']}Up:{self.colors['reset']} "
                f"{self.colors['time']}{value}{self.colors['reset']}"
            )

        if key.startswith("load"):
            color = self.colors["load"]
            try:
                if float(value) > 2.0:
                    color = self.colors["critical"]
            except Exception:
                pass

            return (
                f"{self.colors['label']}{label}:{self.colors['reset']} "
                f"{color}{value}{self.colors['reset']}"
            )

        return (
            f"{self.colors['label']}{label}:{self.colors['reset']} {value}"
        )

    # ---------------- RENDER ----------------
    def render(self, data: Dict[str, object]) -> List[str]:
        """
        Expected input (example):
        {
            "uptime": "3d 4h 21m",
            "boot_time": "2026-02-01 09:12:00",
            "load_1m": 0.42,
            "load_5m": 0.38,
            "load_15m": 0.31
        }
        """
        parts: List[str] = []

        # priority first
        for key in self.priority:
            if key in data:
                parts.append(self._format(key, data[key]))

        # future / extra fields
        for key, value in data.items():
            if key not in self.priority:
                parts.append(self._format(key, value))

        sep = f" {self.colors['label']}│{self.colors['reset']} "
        return [sep.join(parts)]

if __name__ == "__main__":
    up_provider = UptimeProvider()
    up_stats = {
        "uptime": up_provider.format_uptime(),
        "boot_time": up_provider.get_boot_time(),
        **{
            f"load_{key}": value
            for key, value in up_provider.get_load_average().items()
        },
    }

    widget = UptimeWidget()
    rendered_output = widget.render(up_stats)

    for line in rendered_output:
        print(line)