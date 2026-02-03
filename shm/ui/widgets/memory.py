from collections import deque
from .common import GraphBox, DataBox  


def format_bytes(v: float) -> str:
    for u in ("B", "KiB", "MiB", "GiB", "TiB"):
        if v < 1024:
            return f"{v:.2f} {u}"
        v /= 1024
    return f"{v:.2f} PiB"


class MemoryWidget:
    """
    Memory Widget
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

        self.history = deque(maxlen=60)

    # -------------------------------------------------
    def update(self, mem: dict, full: bool = False):
        """
        full=False → dashboard
        full=True  → fullscreen
        """

        total = mem.get("total", 1) or 1
        used = mem.get("used", 0)

        used_pct = (used / total) * 100
        self.history.append(used_pct)

        # -------- render table --------
        render = {}
        for k, v in mem.items():
            if isinstance(v, (int, float)):
                if k == "total":
                    render[k] = format_bytes(v)
                else:
                    pct = (v / total) * 100
                    render[k] = f"{format_bytes(v)} ({pct:.1f}%)"
            else:
                render[k] = str(v)

        # -------- Dashboard --------
        self.graph.update_graph(
            "Memory %",
            self.history,
            height=8,
        )
        self.data.update_data(
            "MEMORY",
            render,
        )

        # -------- Fullscreen --------
        if full:
            self.full_graph.update_graph(
                "Memory %",
                self.history,
                height=22,
            )
            self.full_data.update_data(
                "MEMORY",
                render,
            )
