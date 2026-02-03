# from collections import deque
# from .common import GraphBox, DataBox


# def flatten(d, prefix=""):
#     out = {}
#     for k, v in d.items():
#         key = f"{prefix}.{k}" if prefix else k
#         if isinstance(v, dict):
#             out.update(flatten(v, key))
#         else:
#             out[key] = v
#     return out


# class DiskWidget:
#     """
#     Disk Widget
#     - Dashboard graph
#     - Fullscreen graph
#     """

#     def __init__(self):
#         # -------- Dashboard widgets --------
#         self.graph = GraphBox()
#         self.data = DataBox()

#         # -------- Fullscreen widgets --------
#         self.full_graph = GraphBox()
#         self.full_data = DataBox()

#         self.hist = deque(maxlen=60)

#     # -------------------------------------------------
#     def update(self, disk: dict, full: bool = False):
#         """
#         full=False → dashboard
#         full=True  → fullscreen
#         """

#         # collect disk usage %
#         for part in disk.get("partitions", {}).values():
#             self.hist.append(part.get("pct", 0))

#         # -------- Dashboard --------
#         self.graph.update_graph(
#             "Disk %",
#             self.hist,
#             height=8,
#         )
#         self.data.update_data(
#             "DISK",
#             flatten(disk),
#         )

#         # -------- Fullscreen --------
#         if full:
#             self.full_graph.update_graph(
#                 "Disk %",
#                 self.hist,
#                 height=22,
#             )
#             self.full_data.update_data(
#                 "DISK",
#                 flatten(disk),
#             )

from collections import deque
from typing import Dict

from .common import GraphBox, DataBox


class DiskWidget:
    """
    Disk Widget
    - Works with existing DiskProvider
    - Works with existing DataBox
    - NO flatten()
    - Human readable keys
    """

    def __init__(self):
        # Dashboard
        self.graph = GraphBox()
        self.data = DataBox()

        # Fullscreen
        self.full_graph = GraphBox()
        self.full_data = DataBox()

        self.hist = deque(maxlen=60)

    # -------------------------------------------------
    def update(self, disk: Dict, full: bool = False):
        """
        disk = DiskProvider.get_metrics()
        """

        # ---------- Disk usage history ----------
        for p in disk.get("partitions", {}).values():
            self.hist.append(p.get("pct", 0.0))

        # ---------- Build FLAT + HUMAN dict ----------
        out: Dict[str, object] = {}

        # ---- Per disk IO ----
        for dev, s in disk.get("disks", {}).items():
            out[f"{dev} Read Speed (MiB/s)"] = round(s["read_speed"] * 1024, 2)
            out[f"{dev} Write Speed (MiB/s)"] = round(s["write_speed"] * 1024, 2)
            out[f"{dev} IOPS"] = s["iops"]
            out[f"{dev} Util (%)"] = s["util_pct"]

        # ---- Partitions ----
        for part, p in disk.get("partitions", {}).items():
            out[f"{part} Used (%)"] = p["pct"]
            out[f"{part} Free (GiB)"] = p["free"]

        # ---- Swap ----
        if disk.get("swap"):
            out["Swap Used (%)"] = disk["swap"]["pct"]

        # ---------- Dashboard ----------
        self.graph.update_graph(
            "Disk %",
            self.hist,
            height=8,
        )
        self.data.update_data(
            "DISK",
            out,
        )

        # ---------- Fullscreen ----------
        if full:
            self.full_graph.update_graph(
                "Disk %",
                self.hist,
                height=22,
            )
            self.full_data.update_data(
                "DISK",
                out,
            )


