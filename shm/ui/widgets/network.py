import time
from typing import Dict, List

import asciichartpy as asciichart

from shm.core.network import NetworkProvider
from shm.metrics.net_calc import NetworkCalcProvider


class NetworkWidget:
    """
    Fully dynamic, production-grade Network Widget.

    - Shows ALL interfaces (including lo)
    - Shows ALL raw + calculated fields
    - Fixed-scale graphs (no jump)
    - Future-proof (new fields auto-render)
    """

    def __init__(self) -> None:
        self.calc = NetworkCalcProvider()
        self.raw = NetworkProvider()

        self.history: Dict[str, Dict[str, List[float]]] = {}
        self.scale: Dict[str, Dict[str, float]] = {}
        self.max_history: int = 30

    # ---------------- GRAPH ----------------
    def _plot(self, data: List[float], max_scale: float, color):
        if not data:
            return ""

        return asciichart.plot(
            data[-self.max_history:],
            {
                "height": 4,
                "min": 0,
                "max": max_scale,
                "colors": [color],
            },
        )

    # ---------------- RENDER ----------------
    def render(self) -> List[str]:
        output: List[str] = []

        calc_data = self.calc.get_metrics()
        raw_data = self.raw._read_network_file()

        output.append("NETWORK INTERFACE STATISTICS")
        output.append("─" * 60)

        # iterate over ALL interfaces from raw provider
        for iface, raw in raw_data.items():

            # init state
            if iface not in self.history:
                self.history[iface] = {"down": [], "up": []}
                self.scale[iface] = {"down": 1.0, "up": 1.0}

            stats = calc_data.get(iface, {})

            down = stats.get("down_speed", 0.0)
            up = stats.get("up_speed", 0.0)

            # history update
            self.history[iface]["down"].append(down)
            self.history[iface]["up"].append(up)

            if len(self.history[iface]["down"]) > self.max_history:
                self.history[iface]["down"].pop(0)
                self.history[iface]["up"].pop(0)

            # fixed scale
            self.scale[iface]["down"] = max(self.scale[iface]["down"], max(self.history[iface]["down"]))
            self.scale[iface]["up"] = max(self.scale[iface]["up"], max(self.history[iface]["up"]))

            # header
            output.append(f"{iface.upper()}")

            # speeds
            output.append(f"▼ Down: {NetworkProvider.format_speed(down)}")
            output.append(self._plot(self.history[iface]["down"], self.scale[iface]["down"], asciichart.blue))

            output.append(f"▲ Up:   {NetworkProvider.format_speed(up)}")
            output.append(self._plot(self.history[iface]["up"], self.scale[iface]["up"], asciichart.red))

            # ---------------- DETAILS (DYNAMIC) ----------------
            output.append("Details:")

            # calculated stats
            for k, v in stats.items():
                if k.endswith("_speed"):
                    continue
                output.append(f"  {k:<12} = {v}")

            # raw stats (always)
            for k, v in raw.items():
                output.append(f"  {k:<12} = {v}")

            output.append("")

        return output


# ---------------- STANDALONE RUN ----------------
if __name__ == "__main__":
    ui = NetworkWidget()

    try:
        while True:
            print("\033[H\033[J", end="")
            for line in ui.render():
                print(line)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExit")
