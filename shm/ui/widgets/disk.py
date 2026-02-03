from collections import deque
from .common import GraphBox, DataBox


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out


class DiskWidget:
    """
    Disk Widget
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
    def update(self, disk: dict, full: bool = False):
        """
        full=False → dashboard
        full=True  → fullscreen
        """

        # collect disk usage %
        for part in disk.get("partitions", {}).values():
            self.hist.append(part.get("pct", 0))

        # -------- Dashboard --------
        self.graph.update_graph(
            "Disk %",
            self.hist,
            height=8,
        )
        self.data.update_data(
            "DISK",
            flatten(disk),
        )

        # -------- Fullscreen --------
        if full:
            self.full_graph.update_graph(
                "Disk %",
                self.hist,
                height=22,
            )
            self.full_data.update_data(
                "DISK",
                flatten(disk),
            )
