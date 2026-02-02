from typing import Dict, List

from shm.core.sys_info import SysInfoProvider


class SysInfoWidget:
    """
    Fully dynamic system information header for ALL Linux devices.

    - No static fields
    - No hardcoded widths
    - No sys.path hacks
    - Future-proof: new fields auto-render
    """

    def __init__(self) -> None:
        self.colors = {
            "host": "\033[1;32m",      # Green
            "info": "\033[38;5;39m",   # Blue
            "label": "\033[1;37m",     # White
            "reset": "\033[0m",
        }

        # Priority order (others follow automatically)
        self.priority = [
            "hostname",
            "os_name",
            "kernel",
            "arch",
            "python_version",
        ]

    # ---------------- FORMAT ----------------
    def _format(self, key: str, value: str) -> str:
        """
        Format a single key/value dynamically.
        """
        if key == "hostname":
            return (
                f"{self.colors['host']}"
                f"{value.upper()}"
                f"{self.colors['reset']}"
            )

        if key in ("os_name",):
            return (
                f"{self.colors['info']}"
                f"{value}"
                f"{self.colors['reset']}"
            )

        label = key.replace("_", " ").title()
        return (
            f"{self.colors['label']}{label}:{self.colors['reset']} {value}"
        )

    # ---------------- RENDER ----------------
    def render(self, info_data: Dict[str, str]) -> List[str]:
        """
        info_data: SysInfoProvider.get_info()
        """
        parts: List[str] = []

        # ---- priority fields first ----
        for key in self.priority:
            if key in info_data:
                parts.append(self._format(key, info_data[key]))

        # ---- remaining fields (dynamic / future-proof) ----
        for key, value in info_data.items():
            if key not in self.priority:
                parts.append(self._format(key, value))

        separator = f" {self.colors['label']}│{self.colors['reset']} "
        return [separator.join(parts)]


# ---------------- STANDALONE TEST ----------------
if __name__ == "__main__":
    provider = SysInfoProvider()
    widget = SysInfoWidget()

    data = provider.get_info()
    for line in widget.render(data):
        print(line)
