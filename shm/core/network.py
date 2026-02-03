# import time
# from typing import Dict


# class NetworkProvider:
#     """
#     Reads raw network interface statistics from /proc/net/dev.
#     Linux-specific implementation.
#     """

#     NETDEV_PATH = "/proc/net/dev"

#     def __init__(self) -> None:
#         pass

#     # ---------------- RAW READ ----------------
#     def _read_network_file(self) -> Dict[str, Dict[str, int]]:
#         """
#         Parses /proc/net/dev.

#         Returns:
#             {
#                 iface: {
#                     rx_bytes, rx_packets, rx_errs, rx_drop,
#                     tx_bytes, tx_packets, tx_errs, tx_drop
#                 }
#             }
#         """
#         interfaces: Dict[str, Dict[str, int]] = {}

#         try:
#             with open(self.NETDEV_PATH, "r", encoding="utf-8") as file:
#                 lines = file.readlines()[2:]  # skip headers

#             for line in lines:
#                 if ":" not in line:
#                     continue

#                 iface, data = line.split(":", 1)
#                 iface = iface.strip()
#                 fields = data.split()

#                 interfaces[iface] = {
#                     "rx_bytes": int(fields[0]),
#                     "rx_packets": int(fields[1]),
#                     "rx_errs": int(fields[2]),
#                     "rx_drop": int(fields[3]),
#                     "tx_bytes": int(fields[8]),
#                     "tx_packets": int(fields[9]),
#                     "tx_errs": int(fields[10]),
#                     "tx_drop": int(fields[11]),
#                 }

#         except (OSError, IOError):
#             return {}

#         return interfaces

#     # ---------------- UTILITY ----------------
#     @staticmethod
#     def format_speed(bytes_per_sec: float) -> str:
#         """
#         Converts Bytes/sec → human readable bits/sec.
#         """
#         bits = bytes_per_sec * 8

#         for unit in ("bps", "Kbps", "Mbps", "Gbps", "Tbps"):
#             if bits < 1000:
#                 return f"{bits:.1f} {unit}"
#             bits /= 1000

#         return f"{bits:.1f} Pbps"


import time
from typing import Dict, List


class NetworkProvider:
    """
    Reads raw network interface statistics from /proc/net/dev
    in a future-proof way using header parsing.
    """

    NETDEV_PATH = "/proc/net/dev"

    def __init__(self) -> None:
        self._rx_fields: List[str] = []
        self._tx_fields: List[str] = []
        self._parse_headers()

    # ---------------- HEADER PARSE ----------------
    def _parse_headers(self) -> None:
        try:
            with open(self.NETDEV_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()[:2]

            rx = lines[1].split("|")[1].split()
            tx = lines[1].split("|")[2].split()

            self._rx_fields = [f"rx_{x}" for x in rx]
            self._tx_fields = [f"tx_{x}" for x in tx]

        except Exception:
            self._rx_fields = []
            self._tx_fields = []

    # ---------------- RAW READ ----------------
    def read(self) -> Dict[str, Dict[str, int]]:
        interfaces: Dict[str, Dict[str, int]] = {}

        try:
            with open(self.NETDEV_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()[2:]

            for line in lines:
                if ":" not in line:
                    continue

                iface, data = line.split(":", 1)
                iface = iface.strip()
                values = list(map(int, data.split()))

                iface_data = {}

                for name, value in zip(self._rx_fields + self._tx_fields, values):
                    iface_data[name] = value

                interfaces[iface] = iface_data

        except (OSError, IOError):
            return {}

        return interfaces

    # ---------------- UTILITY ----------------
    @staticmethod
    def format_speed(bytes_per_sec: float) -> str:
        bits = bytes_per_sec * 8
        for unit in ("bps", "Kbps", "Mbps", "Gbps", "Tbps"):
            if bits < 1000:
                return f"{bits:.1f} {unit}"
            bits /= 1000
        return f"{bits:.1f} Pbps"
