
# # from collections import deque
# # from .common import GraphBox, DataBox


# # def format_speed(bytes_per_sec: float) -> str:
# #     bits = bytes_per_sec * 8
# #     for unit in ("bps", "Kbps", "Mbps", "Gbps"):
# #         if bits < 1000:
# #             return f"{bits:.2f} {unit}"
# #         bits /= 1000
# #     return f"{bits:.2f} Tbps"


# # def format_bytes(v: float) -> str:
# #     for u in ("B", "KiB", "MiB", "GiB", "TiB"):
# #         if v < 1024:
# #             return f"{v:.2f} {u}"
# #         v /= 1024
# #     return f"{v:.2f} PiB"


# # class NetworkWidget:
# #     """
# #     Production Network Widget
# #     - Interface name shown ONCE
# #     - Human readable values
# #     - RX + TX combined graph
# #     """

# #     def __init__(self):
# #         self.graph = GraphBox()
# #         self.data = DataBox()

# #         self.rx_hist = deque(maxlen=60)
# #         self.tx_hist = deque(maxlen=60)

# #     def update(self, net: dict):
# #         lines = []

# #         for iface, stats in net.items():
# #             down = stats.get("download_speed", 0.0)
# #             up = stats.get("upload_speed", 0.0)

# #             # graph history
# #             self.rx_hist.append(down)
# #             self.tx_hist.append(up)

# #             # ---- interface header (ONCE) ----
# #             lines.append(f"[b]{iface.upper()}[/b]")

# #             lines.append(f"  Download Speed      {format_speed(down)}")
# #             lines.append(f"  Upload Speed        {format_speed(up)}")
# #             lines.append(
# #                 f"  Total Receive       {format_bytes(stats.get('total_receive_bytes', 0))}"
# #             )
# #             lines.append(
# #                 f"  Total Transmit      {format_bytes(stats.get('total_transmit_bytes', 0))}"
# #             )
# #             lines.append(f"  Receive Packets     {stats.get('receive_packets', 0)}")
# #             lines.append(f"  Transmit Packets    {stats.get('transmit_packets', 0)}")
# #             lines.append(f"  Receive Errors      {stats.get('receive_errors', 0)}")
# #             lines.append(f"  Transmit Errors     {stats.get('transmit_errors', 0)}")
# #             lines.append(
# #                 f"  Dropped Packets     {stats.get('total_dropped_packets', 0)}"
# #             )
# #             lines.append("")

# #         # RX + TX combined graph
# #         mix = deque(
# #             [r + t for r, t in zip(self.rx_hist, self.tx_hist)],
# #             maxlen=60,
# #         )

# #         self.graph.update_graph("Network RX + TX", mix)
# #         self.data.update_data("NETWORK", lines)




# from collections import deque
# from shm.ui.widgets.common import GraphBox, DataBox


# def format_speed(bytes_per_sec: float) -> str:
#     bits = bytes_per_sec * 8
#     for unit in ("bps", "Kbps", "Mbps", "Gbps"):
#         if bits < 1000:
#             return f"{bits:.2f} {unit}"
#         bits /= 1000
#     return f"{bits:.2f} Tbps"


# def format_bytes(v: float) -> str:
#     for u in ("B", "KiB", "MiB", "GiB", "TiB"):
#         if v < 1024:
#             return f"{v:.2f} {u}"
#         v /= 1024
#     return f"{v:.2f} PiB"


# class NetworkWidget:
#     def __init__(self):
#         # dashboard widgets
#         self.graph = GraphBox()
#         self.data = DataBox()

#         # fullscreen widgets (SEPARATE)
#         self.full_graph = GraphBox()
#         self.full_data = DataBox()

#         self.rx_hist = deque(maxlen=60)
#         self.tx_hist = deque(maxlen=60)

#     def update(self, net: dict):
#         lines = []

#         for iface, stats in net.items():
#             down = stats.get("download_speed", 0.0)
#             up = stats.get("upload_speed", 0.0)

#             self.rx_hist.append(down)
#             self.tx_hist.append(up)

#             lines.append(f"[b]{iface.upper()}[/b]")
#             lines.append(f"  Download Speed      {format_speed(down)}")
#             lines.append(f"  Upload Speed        {format_speed(up)}")
#             lines.append(
#                 f"  Total Receive       {format_bytes(stats.get('total_receive_bytes', 0))}"
#             )
#             lines.append(
#                 f"  Total Transmit      {format_bytes(stats.get('total_transmit_bytes', 0))}"
#             )
#             lines.append(f"  Receive Packets     {stats.get('receive_packets', 0)}")
#             lines.append(f"  Transmit Packets    {stats.get('transmit_packets', 0)}")
#             lines.append(f"  Receive Errors      {stats.get('receive_errors', 0)}")
#             lines.append(f"  Transmit Errors     {stats.get('transmit_errors', 0)}")
#             lines.append(
#                 f"  Dropped Packets     {stats.get('total_dropped_packets', 0)}"
#             )
#             lines.append("")

#         mix = deque(
#             [r + t for r, t in zip(self.rx_hist, self.tx_hist)],
#             maxlen=60,
#         )

#         # dashboard
#         self.graph.update_graph("Network RX + TX", mix, height=8)
#         self.data.update_data("NETWORK", lines)

#         # fullscreen
#         self.full_graph.update_graph("Network RX + TX", mix, height=22)
#         self.full_data.update_data("NETWORK", lines)
from collections import deque
from .common import GraphBox, DataBox


def format_speed(bytes_per_sec: float) -> str:
    bits = bytes_per_sec * 8
    for unit in ("bps", "Kbps", "Mbps", "Gbps"):
        if bits < 1000:
            return f"{bits:.2f} {unit}"
        bits /= 1000
    return f"{bits:.2f} Tbps"


def format_bytes(v: float) -> str:
    for u in ("B", "KiB", "MiB", "GiB", "TiB"):
        if v < 1024:
            return f"{v:.2f} {u}"
        v /= 1024
    return f"{v:.2f} PiB"


class NetworkWidget:
    """
    Network Widget
    - Dashboard graph (small)
    - Fullscreen graph (big)
    - Interface name shown once
    """

    def __init__(self):
        # dashboard
        self.graph = GraphBox()
        self.data = DataBox()

        # fullscreen
        self.full_graph = GraphBox()
        self.full_data = DataBox()

        self.rx_hist = deque(maxlen=60)
        self.tx_hist = deque(maxlen=60)

    def update(self, net: dict, full: bool = False):
        lines = []

        for iface, stats in net.items():
            down = stats.get("download_speed", 0.0)
            up = stats.get("upload_speed", 0.0)

            self.rx_hist.append(down)
            self.tx_hist.append(up)

            lines.append(f"[b]{iface.upper()}[/b]")
            lines.append(f"  Download Speed      {format_speed(down)}")
            lines.append(f"  Upload Speed        {format_speed(up)}")
            lines.append(
                f"  Total Receive       {format_bytes(stats.get('total_receive', 0))}"
            )
            lines.append(
                f"  Total Transmit      {format_bytes(stats.get('total_transmit', 0))}"
            )
            lines.append(f"  Receive Packets     {stats.get('receive_packets', 0)}")
            lines.append(f"  Transmit Packets    {stats.get('transmit_packets', 0)}")
            lines.append(f"  Receive Errors      {stats.get('receive_errors', 0)}")
            lines.append(f"  Transmit Errors     {stats.get('transmit_errors', 0)}")
            lines.append(
                f"  Dropped Packets     {stats.get('total_dropped_packets', 0)}"
            )
            lines.append("")

        mix = deque(
            [r + t for r, t in zip(self.rx_hist, self.tx_hist)],
            maxlen=60,
        )

        # -------- dashboard --------
        self.graph.update_graph("Network RX + TX", mix, height=8)
        self.data.update_data("NETWORK", lines)

        # -------- fullscreen --------
        if full:
            self.full_graph.update_graph(
                "Network RX + TX", mix, height=24
            )
            self.full_data.update_data("NETWORK", lines)
