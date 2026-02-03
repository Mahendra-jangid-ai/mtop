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
    Fully dynamic Linux network statistics provider.
    - Header-driven parsing of /proc/net/dev
    - No static rx/tx field assumptions
    - Auto human-readable labels
    """

    NETDEV_PATH = "/proc/net/dev"

    # Kernel abbreviation expansions (stable & generic)
    _TOKEN_EXPANSIONS = {
        "rx": "Receive",
        "tx": "Transmit",
        "errs": "Errors",
        "err": "Errors",
        "drop": "Dropped",
        "bytes": "Bytes",
        "packets": "Packets",
        "fifo": "FIFO",
        "frame": "Frame",
        "compressed": "Compressed",
        "multicast": "Multicast",
        "colls": "Collisions",
        "carrier": "Carrier",
        "speed": "Speed",
        "down": "Download",
        "up": "Upload",
        "total": "Total",
    }

    def __init__(self) -> None:
        self._rx_fields: List[str] = []
        self._tx_fields: List[str] = []
        self._last_data: Dict[str, Dict[str, int]] = {}
        self._last_ts: float = time.time()
        self._parse_headers()

    # --------------------------------------------------
    # HEADER PARSING (future-proof)
    # --------------------------------------------------
    def _parse_headers(self) -> None:
        with open(self.NETDEV_PATH, "r", encoding="utf-8") as f:
            header = f.readlines()[1]

        rx, tx = header.split("|")[1:]
        self._rx_fields = [f"rx_{x}" for x in rx.split()]
        self._tx_fields = [f"tx_{x}" for x in tx.split()]

    # --------------------------------------------------
    # RAW READ
    # --------------------------------------------------
    def _read_raw(self) -> Dict[str, Dict[str, int]]:
        data: Dict[str, Dict[str, int]] = {}

        with open(self.NETDEV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()[2:]

        for line in lines:
            iface, values = line.split(":", 1)
            iface = iface.strip()
            nums = list(map(int, values.split()))

            fields = self._rx_fields + self._tx_fields
            data[iface] = dict(zip(fields, nums))

        return data

    # --------------------------------------------------
    # SPEED CALCULATION (dynamic)
    # --------------------------------------------------
    def read(self) -> Dict[str, Dict[str, float]]:
        now = time.time()
        raw = self._read_raw()

        result: Dict[str, Dict[str, float]] = {}

        for iface, stats in raw.items():
            iface_data: Dict[str, float] = {}

            prev = self._last_data.get(iface, {})
            dt = max(now - self._last_ts, 1e-6)

            # Dynamic speed detection
            if "rx_bytes" in stats:
                iface_data["down_speed"] = (
                    stats["rx_bytes"] - prev.get("rx_bytes", stats["rx_bytes"])
                ) / dt

            if "tx_bytes" in stats:
                iface_data["up_speed"] = (
                    stats["tx_bytes"] - prev.get("tx_bytes", stats["tx_bytes"])
                ) / dt

            # Copy all raw counters
            for k, v in stats.items():
                iface_data[k] = float(v)

            result[iface] = iface_data

        self._last_data = raw
        self._last_ts = now
        return result

    # --------------------------------------------------
    # HUMANIZATION (NO STATIC LABELS)
    # --------------------------------------------------
    @classmethod
    def _expand_token(cls, token: str) -> str:
        return cls._TOKEN_EXPANSIONS.get(token, token.capitalize())

    @classmethod
    def humanize_key(cls, key: str) -> str:
        """
        rx_bytes   -> Receive Bytes
        tx_packets -> Transmit Packets
        down_speed -> Download Speed
        """
        parts = key.split("_")
        return " ".join(cls._expand_token(p) for p in parts)

    @staticmethod
    def format_speed(bytes_per_sec: float) -> str:
        bits = bytes_per_sec * 8
        for unit in ("bps", "Kbps", "Mbps", "Gbps", "Tbps"):
            if bits < 1000:
                return f"{bits:.2f} {unit}"
            bits /= 1000
        return f"{bits:.2f} Pbps"

    # --------------------------------------------------
    # FINAL HUMAN OUTPUT
    # --------------------------------------------------
    def read_human(self) -> Dict[str, Dict[str, str]]:
        raw = self.read()
        out: Dict[str, Dict[str, str]] = {}

        for iface, stats in raw.items():
            iface_out: Dict[str, str] = {}

            for k, v in stats.items():
                label = self.humanize_key(k)

                if k.endswith("speed"):
                    iface_out[label] = self.format_speed(v)
                else:
                    iface_out[label] = f"{int(v)}"

            out[iface] = iface_out

        return out
