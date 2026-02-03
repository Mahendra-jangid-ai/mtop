from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static
from textual.reactive import reactive
from textual.events import Click

# ================= PROVIDERS =================
from shm.core.cpu import CPUProvider
from shm.metrics.cpu_calc import ProcessProvider
from shm.core.memory import MemoryProvider
from shm.core.disk import DiskProvider
from shm.metrics.net_calc import NetworkCalcProvider
from shm.core.uptime import UptimeProvider

# ================= WIDGETS =================
from shm.ui.widgets.cpu import CPUWidget
from shm.ui.widgets.memory import MemoryWidget
from shm.ui.widgets.disk import DiskWidget
from shm.ui.widgets.network import NetworkWidget


class SystemMonitor(App):
    """
    System Monitor Layout
    - Dashboard view (CPU / MEM / DISK / NET)
    - Fullscreen CPU / MEMORY / DISK / NETWORK
    """

    focused_panel = reactive(None)  # None | "cpu" | "memory" | "disk" | "network"

    CSS = """
    Screen { background: black; }

    .box {
        border: round green;
        padding: 1;
    }

    .mem  { border: round blue; }
    .disk { border: round yellow; }
    .net  { border: round magenta; }
    """

    # ==================================================
    # INIT
    # ==================================================
    def __init__(self):
        super().__init__()

        # -------- Providers --------
        self.cpu_p = CPUProvider()
        self.proc_p = ProcessProvider()
        self.mem_p = MemoryProvider()
        self.disk_p = DiskProvider()
        self.net_p = NetworkCalcProvider()
        self.up_p = UptimeProvider()

        # -------- Widgets --------
        self.cpu = CPUWidget()
        self.mem = MemoryWidget()
        self.disk = DiskWidget()
        self.net = NetworkWidget()

    # ==================================================
    # COMPOSE
    # ==================================================
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # ================= DASHBOARD =================
        with Vertical(id="dashboard"):
            with Horizontal():
                with Vertical(classes="box", id="cpu-box"):
                    yield self.cpu.graph
                    yield self.cpu.data

                with Vertical(classes="box mem", id="mem-box"):
                    yield self.mem.graph
                    yield self.mem.data

            with Horizontal():
                with Vertical(classes="box disk", id="disk-box"):
                    yield self.disk.graph
                    yield self.disk.data

                with Vertical(classes="box net", id="net-box"):
                    yield self.net.graph
                    yield self.net.data

        # ================= FULLSCREEN CPU =================
        with Vertical(id="cpu-full", classes="box"):
            yield Static("[b]CPU — Full View (Esc / B to go back)[/b]\n")
            yield self.cpu.full_graph
            yield self.cpu.full_data

        # ================= FULLSCREEN MEMORY =================
        with Vertical(id="memory-full", classes="box mem"):
            yield Static("[b]MEMORY — Full View (Esc / B to go back)[/b]\n")
            yield self.mem.full_graph
            yield self.mem.full_data

        # ================= FULLSCREEN DISK =================
        with Vertical(id="disk-full", classes="box disk"):
            yield Static("[b]DISK — Full View (Esc / B to go back)[/b]\n")
            yield self.disk.full_graph
            yield self.disk.full_data

        # ================= FULLSCREEN NETWORK =================
        with Vertical(id="network-full", classes="box net"):
            yield Static("[b]NETWORK — Full View (Esc / B to go back)[/b]\n")
            yield self.net.full_graph
            yield self.net.full_data

        yield Footer()

    # ==================================================
    # LIFECYCLE
    # ==================================================
    def on_mount(self):
        self.query_one("#cpu-full").display = False
        self.query_one("#memory-full").display = False
        self.query_one("#disk-full").display = False
        self.query_one("#network-full").display = False
        self.set_interval(1, self.refresh_data)

    # ==================================================
    # EVENTS
    # ==================================================
    def on_click(self, event: Click):
        node = event.control
        while node:
            if node.id == "cpu-box":
                self.focused_panel = "cpu"
                return
            if node.id == "mem-box":
                self.focused_panel = "memory"
                return
            if node.id == "disk-box":
                self.focused_panel = "disk"
                return
            if node.id == "net-box":
                self.focused_panel = "network"
                return
            node = node.parent

    def on_key(self, event):
        if event.key in ("escape", "b"):
            self.focused_panel = None

    # ==================================================
    # VISIBILITY SWITCH
    # ==================================================
    def watch_focused_panel(self, value):
        dashboard = self.query_one("#dashboard")
        cpu_full = self.query_one("#cpu-full")
        mem_full = self.query_one("#memory-full")
        disk_full = self.query_one("#disk-full")
        net_full = self.query_one("#network-full")

        dashboard.display = value is None
        cpu_full.display = value == "cpu"
        mem_full.display = value == "memory"
        disk_full.display = value == "disk"
        net_full.display = value == "network"

    # ==================================================
    # DATA REFRESH LOOP
    # ==================================================
    def refresh_data(self):
        uptime = self.up_p.format_uptime()
        load = self.up_p.get_load_average()

        self.title = (
            f"SystemMonitor — Up {uptime} | "
            f"Load {load['1min']} {load['5min']} {load['15min']}"
        )

        self.cpu.update(
            self.cpu_p.get_metrics(),
            self.proc_p.get_top(5),
            full=(self.focused_panel == "cpu"),
        )

        self.mem.update(
            self.mem_p.get_system_memory(),
            full=(self.focused_panel == "memory"),
        )

        self.disk.update(
            self.disk_p.get_metrics(),
            full=(self.focused_panel == "disk"),
        )

        self.net.update(
            self.net_p.get_metrics(),
            full=(self.focused_panel == "network"),
        )
