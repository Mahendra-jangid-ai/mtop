# import time
# from collections import deque
# from typing import Any, Dict

# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output
# import plotly.graph_objs as go

# # ================= YOUR PROVIDERS =================
# from core.cpu import CPUProvider
# from core.memory import MemoryProvider
# from core.disk import DiskProvider
# from metrics.net_calc import NetworkCalcProvider
# from core.uptime import UptimeProvider

# # ================= INIT PROVIDERS =================
# cpu_p = CPUProvider()
# mem_p = MemoryProvider()
# disk_p = DiskProvider()
# net_p = NetworkCalcProvider()
# up_p = UptimeProvider()

# cpu_p.get_metrics()
# net_p.get_metrics()
# time.sleep(1)

# # ================= HISTORY =================
# MAX_POINTS = 60
# cpu_total_hist = deque(maxlen=MAX_POINTS)
# cpu_core_hist: Dict[str, deque] = {}
# net_hist: Dict[str, Dict[str, deque]] = {}

# # ================= HELPERS =================
# def format_bytes(value: int) -> str:
#     for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
#         if value < 1024:
#             return f"{value:.2f} {unit}"
#         value /= 1024
#     return f"{value:.2f} PiB"


# def dict_to_table(data: Dict[str, Any], title: str):
#     rows = []

#     def walk(prefix, value):
#         if isinstance(value, dict):
#             for k, v in value.items():
#                 walk(f"{prefix}.{k}" if prefix else k, v)
#         else:
#             display = format_bytes(value) if isinstance(value, int) else value
#             rows.append(
#                 html.Tr([
#                     html.Td(prefix, style={"fontWeight": "bold", "paddingRight": "12px"}),
#                     html.Td(display),
#                 ])
#             )

#     walk("", data)

#     return html.Div(
#         [
#             html.H4(title),
#             html.Table(
#                 rows,
#                 style={
#                     "width": "100%",
#                     "borderCollapse": "collapse",
#                     "fontFamily": "monospace",
#                 },
#             ),
#         ],
#         style={"marginTop": "10px"},
#     )

# # ================= DASH APP =================
# app = dash.Dash(__name__)
# app.title = "Linux System Monitor"

# # ================= LAYOUT =================
# app.layout = html.Div(
#     style={"fontFamily": "Arial", "padding": "12px"},
#     children=[
#         html.H2("Linux System Monitor"),

#         dcc.Interval(id="tick", interval=1000, n_intervals=0),

#         html.Div(id="header"),

#         html.Div(id="cpu_section", style={"border": "1px solid #ccc", "padding": "10px", "marginBottom": "15px"}),
#         html.Div(id="memory_section", style={"border": "1px solid #ccc", "padding": "10px", "marginBottom": "15px"}),
#         html.Div(id="disk_section", style={"border": "1px solid #ccc", "padding": "10px", "marginBottom": "15px"}),
#         html.Div(id="network_section", style={"border": "1px solid #ccc", "padding": "10px"}),
#     ],
# )

# # ================= CALLBACK =================
# @app.callback(
#     [
#         Output("header", "children"),
#         Output("cpu_section", "children"),
#         Output("memory_section", "children"),
#         Output("disk_section", "children"),
#         Output("network_section", "children"),
#     ],
#     Input("tick", "n_intervals"),
# )
# def update(_):
#     # ================= HEADER =================
#     uptime = up_p.format_uptime()
#     load = up_p.get_load_average()
#     header = html.Pre(f"Uptime: {uptime} | Load: {load['1min']} {load['5min']} {load['15min']}")

#     # ================= CPU =================
#     cpu = cpu_p.get_metrics()
#     cpu_total_hist.append(cpu["total"])

#     cpu_total_fig = go.Figure(
#         data=[go.Scatter(y=list(cpu_total_hist), mode="lines", name="CPU %")],
#         layout=go.Layout(title=f"CPU Usage — {cpu['model']}", yaxis=dict(range=[0, 100])),
#     )

#     core_traces = []
#     for core, val in cpu["cores"].items():
#         if core not in cpu_core_hist:
#             cpu_core_hist[core] = deque(maxlen=MAX_POINTS)
#         cpu_core_hist[core].append(val)
#         core_traces.append(go.Scatter(y=list(cpu_core_hist[core]), mode="lines", name=core))

#     cpu_core_fig = go.Figure(
#         data=core_traces,
#         layout=go.Layout(title="CPU Per Core", yaxis=dict(range=[0, 100])),
#     )

#     cpu_section = [
#         html.H3("CPU"),
#         dcc.Graph(figure=cpu_total_fig),
#         dcc.Graph(figure=cpu_core_fig),
#         dict_to_table(cpu, "CPU RAW DATA"),
#     ]

#     # ================= MEMORY =================
#     mem = mem_p.get_system_memory()
#     ram_pct = (mem["used"] / mem["total"]) * 100 if mem["total"] else 0
#     swap_pct = (mem["swap_used"] / mem["swap_total"]) * 100 if mem["swap_total"] else 0

#     mem_fig = go.Figure(
#         data=[
#             go.Bar(name="RAM %", x=["RAM"], y=[ram_pct]),
#             go.Bar(name="SWAP %", x=["SWAP"], y=[swap_pct]),
#         ],
#         layout=go.Layout(title="Memory Usage", yaxis=dict(range=[0, 100]), barmode="group"),
#     )

#     memory_section = [
#         html.H3("Memory"),
#         dcc.Graph(figure=mem_fig),
#         dict_to_table(mem, "MEMORY RAW DATA"),
#     ]

#     # ================= DISK =================
#     disk = disk_p.get_metrics()

#     part_fig = go.Figure(
#         data=[
#             go.Bar(
#                 x=list(disk["partitions"].keys()),
#                 y=[v["pct"] for v in disk["partitions"].values()],
#             )
#         ],
#         layout=go.Layout(title="Disk Partition Usage %", yaxis=dict(range=[0, 100])),
#     )

#     io_traces = []
#     for dev, stats in disk["disks"].items():
#         io_traces.append(go.Bar(name=f"{dev} R", x=[dev], y=[stats["read_speed"]]))
#         io_traces.append(go.Bar(name=f"{dev} W", x=[dev], y=[stats["write_speed"]]))

#     io_fig = go.Figure(
#         data=io_traces,
#         layout=go.Layout(title="Disk I/O (GiB/s)", barmode="group"),
#     )

#     disk_section = [
#         html.H3("Disk"),
#         dcc.Graph(figure=part_fig),
#         dcc.Graph(figure=io_fig),
#         dict_to_table(disk, "DISK RAW DATA"),
#     ]

#     # ================= NETWORK =================
#     net = net_p.get_metrics()
#     net_traces = []

#     for iface, stats in net.items():
#         if iface not in net_hist:
#             net_hist[iface] = {"down": deque(maxlen=MAX_POINTS), "up": deque(maxlen=MAX_POINTS)}
#         net_hist[iface]["down"].append(stats["down_speed"])
#         net_hist[iface]["up"].append(stats["up_speed"])

#         net_traces.append(go.Scatter(y=list(net_hist[iface]["down"]), mode="lines", name=f"{iface} ↓"))
#         net_traces.append(go.Scatter(y=list(net_hist[iface]["up"]), mode="lines", name=f"{iface} ↑"))

#     net_fig = go.Figure(
#         data=net_traces,
#         layout=go.Layout(title="Network Throughput"),
#     )

#     network_section = [
#         html.H3("Network"),
#         dcc.Graph(figure=net_fig),
#         dict_to_table(net, "NETWORK RAW DATA"),
#     ]

#     return header, cpu_section, memory_section, disk_section, network_section


# # ================= MAIN =================
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8050, debug=False)








# -------------------------------------------------------------------------------------------------------------------------------------------






















# from __future__ import annotations

# from collections import deque
# from typing import Dict, Any

# import asciichartpy

# from textual.app import App, ComposeResult
# from textual.containers import Horizontal, Vertical
# from textual.widgets import Static, Header, Footer
# from textual.reactive import reactive

# # ================= PROVIDERS (UNCHANGED) =================
# from core.cpu import CPUProvider
# from core.memory import MemoryProvider
# from core.disk import DiskProvider
# from metrics.net_calc import NetworkCalcProvider
# from core.uptime import UptimeProvider


# # ================= HELPERS =================
# def format_bytes(v: float) -> str:
#     for u in ("B", "KiB", "MiB", "GiB", "TiB"):
#         if v < 1024:
#             return f"{v:.2f} {u}"
#         v /= 1024
#     return f"{v:.2f} PiB"


# def flatten(d: Dict[str, Any], prefix="") -> Dict[str, Any]:
#     out = {}
#     for k, v in d.items():
#         key = f"{prefix}.{k}" if prefix else k
#         if isinstance(v, dict):
#             out.update(flatten(v, key))
#         else:
#             out[key] = v
#     return out


# def ascii_line(data, height=8):
#     if not data:
#         return ""
#     return asciichartpy.plot(
#         list(data),
#         {"height": height},
#     )


# # ================= DATA BOX =================
# class DataBox(Static):
#     def update_data(self, title: str, data: Dict[str, Any]):
#         lines = [f"[b]{title}[/b]\n"]
#         for k, v in data.items():
#             lines.append(f"{k:<24} {v}")
#         self.update("\n".join(lines))


# # ================= GRAPH BOX =================
# class GraphBox(Static):
#     def update_graph(self, title: str, data: deque):
#         graph = ascii_line(data)
#         self.update(f"[b]{title}[/b]\n\n{graph}")


# # ================= MAIN APP =================
# class SystemMonitor(App):
#     CSS = """
#     Screen { background: black; }

#     .box {
#         border: round green;
#         padding: 1;
#     }

#     .mem { border: round blue; }
#     .disk { border: round yellow; }
#     .net { border: round magenta; }
#     """

#     BINDINGS = [("q", "quit", "Quit")]

#     cpu_hist = deque(maxlen=60)
#     mem_hist = deque(maxlen=60)
#     disk_hist = deque(maxlen=60)
#     rx_hist = deque(maxlen=60)
#     tx_hist = deque(maxlen=60)

#     show_graphs = reactive(True)

#     def __init__(self):
#         super().__init__()
#         self.cpu_p = CPUProvider()
#         self.mem_p = MemoryProvider()
#         self.disk_p = DiskProvider()
#         self.net_p = NetworkCalcProvider()
#         self.up_p = UptimeProvider()

#     # ---------------- COMPOSE ----------------
#     def compose(self) -> ComposeResult:
#         yield Header(show_clock=True)

#         with Vertical():
#             with Horizontal():
#                 with Vertical(classes="box"):
#                     self.cpu_graph = GraphBox()
#                     self.cpu_data = DataBox()
#                     yield self.cpu_graph
#                     yield self.cpu_data

#                 with Vertical(classes="box mem"):
#                     self.mem_graph = GraphBox()
#                     self.mem_data = DataBox()
#                     yield self.mem_graph
#                     yield self.mem_data

#             with Horizontal():
#                 with Vertical(classes="box disk"):
#                     self.disk_graph = GraphBox()
#                     self.disk_data = DataBox()
#                     yield self.disk_graph
#                     yield self.disk_data

#                 with Vertical(classes="box net"):
#                     self.net_graph = GraphBox()
#                     self.net_data = DataBox()
#                     yield self.net_graph
#                     yield self.net_data

#         yield Footer()

#     # ---------------- RESPONSIVE ----------------
#     def on_resize(self):
#         self.show_graphs = self.size.width > 100

#         self.cpu_graph.display = self.show_graphs
#         self.mem_graph.display = self.show_graphs
#         self.disk_graph.display = self.show_graphs
#         self.net_graph.display = self.show_graphs

#     # ---------------- REFRESH LOOP ----------------
#     def on_mount(self):
#         self.set_interval(1, self.refresh_data)

#     # ---------------- UPDATE ----------------
#     def refresh_data(self):
#         uptime = self.up_p.format_uptime()
#         load = self.up_p.get_load_average()
#         self.title = f"SystemMonitor — Up {uptime} | Load {load['1min']} {load['5min']} {load['15min']}"

#         # ===== CPU =====
#         cpu = self.cpu_p.get_metrics()
#         self.cpu_hist.append(cpu["total"])
#         self.cpu_graph.update_graph("CPU %", self.cpu_hist)
#         self.cpu_data.update_data("CPU", flatten(cpu))

#         # ===== MEMORY =====
#         mem = self.mem_p.get_system_memory()
#         used_pct = (mem["used"] / mem["total"]) * 100 if mem["total"] else 0
#         self.mem_hist.append(used_pct)
#         self.mem_graph.update_graph("Memory %", self.mem_hist)
#         self.mem_data.update_data(
#             "MEMORY",
#             {k: format_bytes(v) for k, v in mem.items()},
#         )

#         # ===== DISK =====
#         disk = self.disk_p.get_metrics()
#         for part in disk.get("partitions", {}).values():
#             self.disk_hist.append(part["pct"])
#         self.disk_graph.update_graph("Disk Usage %", self.disk_hist)
#         self.disk_data.update_data("DISK", flatten(disk))

#         # ===== NETWORK =====
#         net = self.net_p.get_metrics()
#         for stats in net.values():
#             self.rx_hist.append(stats["down_speed"])
#             self.tx_hist.append(stats["up_speed"])

#         net_lines = deque(
#             [(r + t) for r, t in zip(self.rx_hist, self.tx_hist)],
#             maxlen=60,
#         )
#         self.net_graph.update_graph("Network RX+TX", net_lines)
#         self.net_data.update_data("NETWORK", flatten(net))


# # ================= ENTRY =================
# if __name__ == "__main__":
#     SystemMonitor().run()
























# -------------------------------------------------------------------------------------------------------------------------------------------

















from __future__ import annotations

import json
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import asciichartpy

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Header, Footer
from textual.reactive import reactive

# ================= PROVIDERS (UNCHANGED) =================
from shm.core.cpu import CPUProvider
from shm.core.memory import MemoryProvider
from shm.core.disk import DiskProvider
from shm.metrics.net_calc import NetworkCalcProvider
from shm.metrics.cpu_calc import ProcessProvider
from shm.core.uptime import UptimeProvider


# ================= HELPERS =================
def format_bytes(v: float) -> str:
    for u in ("B", "KiB", "MiB", "GiB", "TiB"):
        if v < 1024:
            return f"{v:.2f} {u}"
        v /= 1024
    return f"{v:.2f} PiB"


def flatten(d: Dict[str, Any], prefix="") -> Dict[str, Any]:
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out


def ascii_line(data, height=8):
    if not data:
        return ""
    return asciichartpy.plot(list(data), {"height": height})


# ================= DATA BOX (FIXED) =================
class DataBox(Static):
    """
    FIX:
    - supports list[str] (CPU custom layout)
    - supports dict (MEM / DISK / NET)
    """

    def update_data(self, title: str, data):
        lines = [f"[b]{title}[/b]\n"]

        if isinstance(data, list):
            lines.extend(data)

        elif isinstance(data, dict):
            for k, v in data.items():
                lines.append(f"{k:<28} {v}")

        self.update("\n".join(lines))


# ================= GRAPH BOX =================
class GraphBox(Static):
    def update_graph(self, title: str, data: deque):
        self.update(f"[b]{title}[/b]\n\n{ascii_line(data)}")


# ================= MAIN APP =================
class SystemMonitor(App):
    CSS = """
    Screen { background: black; }

    .box {
        border: round green;
        padding: 1;
    }

    .mem { border: round blue; }
    .disk { border: round yellow; }
    .net { border: round magenta; }
    """

    BINDINGS = [("q", "quit", "Quit")]

    cpu_hist = deque(maxlen=60)
    mem_hist = deque(maxlen=60)
    disk_hist = deque(maxlen=60)
    rx_hist = deque(maxlen=60)
    tx_hist = deque(maxlen=60)

    show_graphs = reactive(True)

    def __init__(self):
        super().__init__()

        self.cpu_p = CPUProvider()
        self.proc_p = ProcessProvider()
        self.mem_p = MemoryProvider()
        self.disk_p = DiskProvider()
        self.net_p = NetworkCalcProvider()
        self.up_p = UptimeProvider()

        self.json_file = Path(__file__).parent / "system_history.json"

    # ---------------- COMPOSE ----------------
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Vertical():
            with Horizontal():
                with Vertical(classes="box"):
                    self.cpu_graph = GraphBox()
                    self.cpu_data = DataBox()
                    yield self.cpu_graph
                    yield self.cpu_data

                with Vertical(classes="box mem"):
                    self.mem_graph = GraphBox()
                    self.mem_data = DataBox()
                    yield self.mem_graph
                    yield self.mem_data

            with Horizontal():
                with Vertical(classes="box disk"):
                    self.disk_graph = GraphBox()
                    self.disk_data = DataBox()
                    yield self.disk_graph
                    yield self.disk_data

                with Vertical(classes="box net"):
                    self.net_graph = GraphBox()
                    self.net_data = DataBox()
                    yield self.net_graph
                    yield self.net_data

        yield Footer()

    # ---------------- REFRESH LOOP ----------------
    def on_mount(self):
        self.set_interval(1, self.refresh_data)

    # ---------------- CPU FORMAT ----------------
    def _format_cpu_block(self, cpu: dict, procs: list) -> List[str]:
        lines = []

        lines.append(f"Model : {cpu['model']}")
        lines.append(f"Total : {cpu['total']}%\n")

        # ---- CORE GRID (3 columns) ----
        cores = sorted(cpu["cores"].items(), key=lambda x: int(x[0][3:]))
        for i in range(0, len(cores), 3):
            row = []
            for c, v in cores[i:i+3]:
                row.append(f"{c.upper():<5} {v:>4}%")
            lines.append("   ".join(row))

        # ---- PROCESS LIST ----
        lines.append("\nTop CPU Processes:")
        for p in procs:
            lines.append(f"PID {p['pid']:<6} {p['name']:<18} {p['cpu']}%")

        return lines

    # ---------------- UPDATE ----------------
    def refresh_data(self):
        uptime = self.up_p.format_uptime()
        load = self.up_p.get_load_average()

        self.title = (
            f"SystemMonitor — Up {uptime} | "
            f"Load {load['1min']} {load['5min']} {load['15min']}"
        )

        # ===== CPU =====
        cpu = self.cpu_p.get_metrics()
        procs = self.proc_p.get_top(5)

        self.cpu_hist.append(cpu["total"])
        self.cpu_graph.update_graph("CPU %", self.cpu_hist)

        cpu_lines = self._format_cpu_block(cpu, procs)
        self.cpu_data.update_data("CPU", cpu_lines)

        # ===== MEMORY =====
        mem = self.mem_p.get_system_memory()
        total = mem.get("total", 0) or 1

        # ---- Graph logic (UNCHANGED) ----
        used = mem.get("used", 0)
        used_pct = (used / total) * 100
        self.mem_hist.append(used_pct)
        self.mem_graph.update_graph("Memory %", self.mem_hist)

        # ---- Dynamic rendering ----
        render_mem = {}

        for key, value in mem.items():
            # bytes fields only
            if isinstance(value, (int, float)):
                if key != "total":
                    pct = (value / total) * 100 if total else 0
                    render_mem[key] = f"{format_bytes(value)}  ({pct:.1f}%)"
                else:
                    render_mem[key] = format_bytes(value)

            else:
                # fallback for non-numeric fields (future safe)
                render_mem[key] = str(value)

        self.mem_data.update_data("MEMORY", render_mem)

        # ===== DISK =====
        disk = self.disk_p.get_metrics()
        for part in disk.get("partitions", {}).values():
            self.disk_hist.append(part["pct"])

        self.disk_graph.update_graph("Disk %", self.disk_hist)
        self.disk_data.update_data("DISK", flatten(disk))

        # ===== NETWORK =====
        net = self.net_p.get_metrics()
        for stats in net.values():
            self.rx_hist.append(stats["down_speed"])
            self.tx_hist.append(stats["up_speed"])

        net_mix = deque(
            [r + t for r, t in zip(self.rx_hist, self.tx_hist)],
            maxlen=60,
        )

        self.net_graph.update_graph("Network RX+TX", net_mix)
        self.net_data.update_data("NETWORK", flatten(net))

        # ===== JSON SNAPSHOT =====
        snapshot = {
            "time": datetime.now().isoformat(),
            "uptime": uptime,
            "load": load,
            "system_data": {
                "cpu": cpu,
                "memory": mem,
                "disk": disk,
                "network": net,
            },
        }

        try:
            if self.json_file.exists():
                data = json.loads(self.json_file.read_text())
            else:
                data = []
            data.append(snapshot)
            self.json_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass


# ================= ENTRY =================

