import time
from typing import Dict, Tuple

from shm.core.network import NetworkProvider


class NetworkCalcProvider:
    # Small epsilon to avoid division by zero
    _TIME_EPSILON = 1e-6

    def __init__(self) -> None:
        # iface -> (rx_bytes, tx_bytes)
        self._last_counters: Dict[str, Tuple[int, int]] = {}
        self._last_ts: float = time.time()

        self._provider = NetworkProvider()

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------
    def get_metrics(self) -> Dict[str, Dict[str, float]]:
        now = time.time()
        delta_time = max(now - self._last_ts, self._TIME_EPSILON)

        raw = self._provider._read_network_file()
        metrics: Dict[str, Dict[str, float]] = {}

        for iface, data in raw.items():
            # Loopback usually useless for UI / graphs
            if iface == "lo":
                continue

            metrics[iface] = self._calculate_interface(
                iface=iface,
                data=data,
                delta_time=delta_time,
            )

        self._last_ts = now
        return metrics

    # --------------------------------------------------
    # INTERNAL CALCULATION
    # --------------------------------------------------
    def _calculate_interface(
        self,
        iface: str,
        data: Dict[str, int],
        delta_time: float,
    ) -> Dict[str, float]:
        """
        Calculates metrics for a single interface.
        """

        rx_bytes = data.get("rx_bytes", 0)
        tx_bytes = data.get("tx_bytes", 0)

        prev_rx, prev_tx = self._last_counters.get(
            iface,
            (rx_bytes, tx_bytes),
        )

        download_speed = max((rx_bytes - prev_rx) / delta_time, 0.0)
        upload_speed = max((tx_bytes - prev_tx) / delta_time, 0.0)

        # Persist state
        self._last_counters[iface] = (rx_bytes, tx_bytes)

        return {
            # ---------------- SPEEDS ----------------
            "download_speed": download_speed,     # bytes/sec
            "upload_speed": upload_speed,         # bytes/sec

            # ---------------- TOTALS ----------------
            "total_receive_bytes": rx_bytes,
            "total_transmit_bytes": tx_bytes,

            # ---------------- PACKETS ----------------
            "receive_packets": data.get("rx_packets", 0),
            "transmit_packets": data.get("tx_packets", 0),

            # ---------------- ERRORS ----------------
            "receive_errors": data.get("rx_errs", 0),
            "transmit_errors": data.get("tx_errs", 0),

            # ---------------- DROPS ----------------
            "total_dropped_packets":
                data.get("rx_drop", 0) + data.get("tx_drop", 0),
        }
