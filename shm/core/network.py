from typing import Dict, List
import threading


class NetworkProvider:
    NETDEV_PATH = "/proc/net/dev"

    def __init__(self) -> None:
        self._rx_fields: List[str] = []
        self._tx_fields: List[str] = []
        self._lock = threading.Lock()
        self._parse_headers()

    # --------------------------------------------------
    # HEADER PARSING (FUTURE-PROOF)
    # --------------------------------------------------
    def _parse_headers(self) -> None:
        try:
            with open(self.NETDEV_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if len(lines) < 2 or "|" not in lines[1]:
                raise ValueError("Invalid /proc/net/dev header format")

            rx_part, tx_part = lines[1].split("|")[1:]

            self._rx_fields = [f"rx_{name}" for name in rx_part.split()]
            self._tx_fields = [f"tx_{name}" for name in tx_part.split()]

        except Exception:
            # Fallback (minimum safe set)
            self._rx_fields = ["rx_bytes"]
            self._tx_fields = ["tx_bytes"]

    def _read_network_file(self) -> Dict[str, Dict[str, int]]:
        with self._lock:
            data: Dict[str, Dict[str, int]] = {}

            try:
                with open(self.NETDEV_PATH, "r", encoding="utf-8") as f:
                    lines = f.readlines()[2:]

                fields = self._rx_fields + self._tx_fields

                for line in lines:
                    if ":" not in line:
                        continue

                    iface, values = line.split(":", 1)
                    iface = iface.strip()

                    nums = values.split()
                    if len(nums) < len(fields):
                        # Kernel mismatch → re-parse headers once
                        self._parse_headers()
                        fields = self._rx_fields + self._tx_fields

                    parsed = {
                        field: int(nums[idx])
                        for idx, field in enumerate(fields)
                        if idx < len(nums)
                    }

                    data[iface] = parsed

            except (OSError, IOError):
                # File unreadable → return last-known empty snapshot
                return {}

            except Exception:
                # Any unexpected parsing issue → fail soft
                return {}

            return data

    @staticmethod
    def format_speed(bytes_per_sec: float) -> str:
        """
        Converts Bytes/sec → human-readable bits/sec.
        """
        bits = bytes_per_sec * 8.0

        for unit in ("bps", "Kbps", "Mbps", "Gbps", "Tbps"):
            if bits < 1000:
                return f"{bits:.2f} {unit}"
            bits /= 1000

        return f"{bits:.2f} Pbps"
