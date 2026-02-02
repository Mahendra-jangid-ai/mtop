import time
from typing import Dict

from shm.core.network import NetworkProvider


class NetworkCalcProvider:
    """
    Calculates real-time network metrics by computing deltas
    between successive reads of NetworkProvider raw data.
    """

    def __init__(self) -> None:
        # { iface: (rx_bytes, tx_bytes) }
        self.last_stats: Dict[str, tuple[int, int]] = {}
        self.last_time: float = time.time()

        self.raw_reader = NetworkProvider()

    # ---------------- PUBLIC API (Calculation Logic) ----------------
    def get_metrics(self) -> Dict[str, Dict[str, float]]:
        """
        Calculates delta between two reads to derive real-time speeds.
        """
        now = time.time()
        delta_time = now - self.last_time if now > self.last_time else 0

        current = self.raw_reader._read_network_file()
        result: Dict[str, Dict[str, float]] = {}

        for iface, data in current.items():
            if iface == "lo":
                continue

            # Previous counters (defaults to current on first run)
            prev_rx, prev_tx = self.last_stats.get(
                iface,
                (data["rx_bytes"], data["tx_bytes"]),
            )

            if delta_time > 0:
                down_speed = (data["rx_bytes"] - prev_rx) / delta_time
                up_speed = (data["tx_bytes"] - prev_tx) / delta_time
            else:
                down_speed = up_speed = 0.0

            result[iface] = {
                "down_speed": max(down_speed, 0.0),
                "up_speed": max(up_speed, 0.0),
                "total_rx": data["rx_bytes"],
                "total_tx": data["tx_bytes"],
                "rx_packets": data["rx_packets"],
                "tx_packets": data["tx_packets"],
                "rx_errors": data["rx_errs"],
                "tx_errors": data["tx_errs"],
                "dropped": data["rx_drop"] + data["tx_drop"],
            }

            # Persist counters for next sampling cycle
            self.last_stats[iface] = (
                data["rx_bytes"],
                data["tx_bytes"],
            )

        self.last_time = now
        return result
