from collections import deque
from typing import List
from .common import GraphBox, DataBox


class CPUWidget:
    """
    CPU Widget
    - Dashboard graph
    - Fullscreen graph
    """

    def __init__(self):
        # -------- Dashboard widgets --------
        self.graph = GraphBox()
        self.data = DataBox()

        # -------- Fullscreen widgets --------
        self.full_graph = GraphBox()
        self.full_data = DataBox()

        self.hist = deque(maxlen=60)

    # -------------------------------------------------
    def format_block(self, cpu: dict, procs: list) -> List[str]:
        lines = []

        lines.append(f"Model : {cpu['model']}")
        lines.append(f"Total : {cpu['total']}%\n")

        cores = sorted(cpu["cores"].items(), key=lambda x: int(x[0][3:]))

        for i in range(0, len(cores), 3):
            row = []
            for c, v in cores[i:i + 3]:
                row.append(f"{c.upper():<5} {v:>4}%")
            lines.append("   ".join(row))

        lines.append("\nTop CPU Processes:")
        for p in procs:
            lines.append(
                f"PID {p['pid']:<6} {p['name']:<18} {p['cpu']}%"
            )

        return lines

    # -------------------------------------------------
    def update(self, cpu: dict, procs: list, full: bool = False):
        """
        full=False → dashboard
        full=True  → fullscreen
        """

        self.hist.append(cpu["total"])

        # -------- Dashboard --------
        self.graph.update_graph(
            "CPU %",
            self.hist,
            height=8,
        )
        self.data.update_data(
            "CPU",
            self.format_block(cpu, procs),
        )

        # -------- Fullscreen --------
        if full:
            self.full_graph.update_graph(
                "CPU %",
                self.hist,
                height=22,
            )
            self.full_data.update_data(
                "CPU",
                self.format_block(cpu, procs),
            )
