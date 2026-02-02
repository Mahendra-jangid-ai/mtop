from typing import Dict, List

from ..colors import Colors


class CPUWidget:
    """
    Renders CPU usage information including:
    - Total CPU usage graph
    - Per-core usage bars
    """

    def __init__(self) -> None:
        self.history: List[float] = []   # Graph points
        self.max_history: int = 50       # Graph width

    # ---------------- BAR ----------------
    def _get_bar(self, percentage: float, width: int = 10) -> str:
        """
        Builds a dynamic usage bar based on percentage.
        """
        filled = int(width * percentage / 100)

        # Color selection logic (unchanged)
        color = (
            Colors.OK if percentage < 50
            else Colors.WARN if percentage < 80
            else Colors.CRIT
        )

        return (
            f"{color}{'█' * filled}{Colors.RESET}"
            f"{'░' * (width - filled)}"
        )

    # ---------------- GRAPH ----------------
    def _generate_graph(self, current_val: float) -> str:
        """
        Generates a line graph using Unicode blocks.
        History handling unchanged.
        """
        self.history.append(current_val)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        blocks = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        graph = ""

        for val in self.history:
            idx = int((val / 100) * (len(blocks) - 1))
            graph += blocks[idx]

        return f"{Colors.CPU_GRAPH}{graph}{Colors.RESET}"

    # ---------------- RENDER ----------------
    def render(self, cpu_data: Dict[str, object]) -> List[str]:
        """
        Renders CPU widget output.

        cpu_data:
        {
            "total": float,
            "model": str,
            "cores": { "cpu0": float, ... }
        }
        """
        output: List[str] = []

        total_usage = cpu_data.get("total", 0.0)
        model = cpu_data.get("model", "Unknown CPU")

        # 1. Title
        output.append(
            f"{Colors.BOLD}CPU: {model}{Colors.RESET}"
        )

        # 2. Usage Graph
        graph = self._generate_graph(float(total_usage))
        padded_graph = graph.ljust(self.max_history)

        output.append(
            f"Usage: [{padded_graph}] "
            f"{Colors.BOLD}{total_usage:>5}%{Colors.RESET}"
        )

        output.append(
            " " * 7 + "└" + "─" * (self.max_history - 2) + "┘"
        )

        # 3. Core Grid
        cores: Dict[str, float] = cpu_data.get("cores", {})
        sorted_cores = sorted(
            cores.keys(),
            key=lambda x: int(x[3:]) if x[3:].isdigit() else 0
        )

        num_cores = len(sorted_cores)

        # Column logic unchanged
        if num_cores <= 8:
            cols = 2
        elif num_cores <= 24:
            cols = 4
        else:
            cols = 6

        for i in range(0, num_cores, cols):
            row = []
            for j in range(cols):
                if i + j < num_cores:
                    core = sorted_cores[i + j]
                    usage = cores[core]
                    row.append(
                        f"{core.upper():<5} "
                        f"{self._get_bar(usage)} "
                        f"{usage:>5}%"
                    )
            output.append("  ".join(row))

        return output
