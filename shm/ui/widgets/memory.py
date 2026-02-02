from typing import Dict, List

from shm.core.memory import MemoryProvider


class MemoryWidget:
    """
    Dynamically renders ALL memory-related data provided
    by MemoryProvider (RAM + SWAP), without hardcoding keys.
    """

    def __init__(self) -> None:
        self.ram_history: List[float] = []
        self.swap_history: List[float] = []
        self.max_history: int = 40

        self.colors = {
            "ram": "\033[38;5;40m",     # Green
            "swap": "\033[38;5;208m",   # Orange
            "reset": "\033[0m",
            "bold": "\033[1m",
        }

    # ---------------- BAR ----------------
    def _get_bar(
        self,
        percentage: float,
        color: str,
        width: int = 20
    ) -> str:
        filled = int(width * percentage / 100)
        return (
            f"{color}{'█' * filled}"
            f"{self.colors['reset']}"
            f"{'░' * (width - filled)}"
        )

    # ---------------- GRAPH ----------------
    def _get_line_graph(
        self,
        history: List[float],
        current_val: float,
        color: str
    ) -> str:
        history.append(current_val)
        if len(history) > self.max_history:
            history.pop(0)

        blocks = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        graph = "".join(
            blocks[int((v / 100) * (len(blocks) - 1))]
            for v in history
        )
        return f"{color}{graph}{self.colors['reset']}"

    # ---------------- RENDER ----------------
    def render(self, mem_data: Dict[str, int]) -> List[str]:
        output: List[str] = []
        fmt = MemoryProvider.format_bytes

        # ================= RAM SUMMARY =================
        total = mem_data.get("total", 0)
        used = mem_data.get("used", 0)
        available = mem_data.get("available", 0)

        ram_pct = (used / total * 100) if total > 0 else 0

        output.append(
            f"{self.colors['bold']}MEMORY (RAM){self.colors['reset']}  "
            f"{self._get_bar(ram_pct, self.colors['ram'])} "
            f"{ram_pct:>5.1f}%"
        )

        ram_graph = self._get_line_graph(
            self.ram_history,
            ram_pct,
            self.colors["ram"]
        )
        output.append(f"History: [{ram_graph:<{self.max_history}}]")

        # ================= RAM DETAILS (DYNAMIC) =================
        for key, value in mem_data.items():
            if key.startswith("swap_"):
                continue  # handled later

            output.append(
                f"{key:<12} = {fmt(value)}"
            )

        output.append("")

        # ================= SWAP =================
        swap_total = mem_data.get("swap_total", 0)
        swap_used = mem_data.get("swap_used", 0)

        if swap_total > 0:
            swap_pct = (swap_used / swap_total * 100)

            output.append(
                f"{self.colors['bold']}SWAP{self.colors['reset']}        "
                f"{self._get_bar(swap_pct, self.colors['swap'])} "
                f"{swap_pct:>5.1f}%"
            )

            swap_graph = self._get_line_graph(
                self.swap_history,
                swap_pct,
                self.colors["swap"]
            )
            output.append(f"History: [{swap_graph:<{self.max_history}}]")

            # ================= SWAP DETAILS (DYNAMIC) =================
            for key, value in mem_data.items():
                if key.startswith("swap_"):
                    output.append(
                        f"{key:<12} = {fmt(value)}"
                    )

        return output
