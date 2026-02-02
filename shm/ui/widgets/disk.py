from typing import Dict, List

from ui.colors import Colors
from shm.core.disk import DiskProvider


class DiskWidget:
    def __init__(self) -> None:
        pass

    # ---------------- BAR ----------------
    def _get_bar(self, percentage: float, width: int = 15) -> str:
        filled = int(width * percentage / 100)
        color = Colors.OK if percentage < 80 else Colors.CRIT

        return (
            f"{color}{'█' * filled}{Colors.RESET}"
            f"{'░' * (width - filled)}"
        )

    # ---------------- RENDER ----------------
    def render(self, disk_data: Dict[str, object]) -> List[str]:
        output: List[str] = []

        # ---------------- TITLE ----------------
        output.append(
            f"{Colors.BOLD}{Colors.DISK_BAR}DISK USAGE & I/O{Colors.RESET}"
        )
        output.append("─" * 55)

        # ---------------- PARTITIONS ----------------
        output.append(
            f"{Colors.BOLD}"
            f"Mount Point      Device     Usage          Free/Total"
            f"{Colors.RESET}"
        )

        for part, info in disk_data["partitions"].items():
            bar = self._get_bar(info["pct"])
            output.append(
                f"{info['mount'][:15]:<15} "
                f"{part:<10} "
                f"{bar} {info['pct']:>5}%  "
                f"{info['free']:.2f}G/{info['total']:.2f}G"
            )

        # ---------------- SWAP ----------------
        swap = disk_data.get("swap")
        if swap:
            output.append("")
            output.append(f"{Colors.BOLD}Swap Usage{Colors.RESET}")

            bar = self._get_bar(swap["pct"])
            output.append(
                f"swap        "
                f"{bar} {swap['pct']:>5}%  "
                f"{swap['free']:.2f}G/{swap['total']:.2f}G"
            )

        output.append("")

        # ---------------- DISK I/O ----------------
        output.append(
            f"{Colors.BOLD}Disk I/O Speed (GiB/s){Colors.RESET}"
        )

        # show ALL disks (idle bhi)
        for dev, stats in disk_data["disks"].items():
            r_speed = (
                f"{Colors.NET_DOWN}R: {stats['read_speed']:.4f}{Colors.RESET}"
            )
            w_speed = (
                f"{Colors.NET_UP}W: {stats['write_speed']:.4f}{Colors.RESET}"
            )

            util_color = Colors.get_gradient(stats["util_pct"] / 100)
            util = (
                f"{util_color}Util: {stats['util_pct']}%{Colors.RESET}"
            )

            output.append(
                f"{Colors.PROC_USER}{dev:<10}{Colors.RESET} "
                f"{r_speed} | {w_speed} | {util}"
            )

        return output


# ---------------- STANDALONE TEST ----------------
if __name__ == "__main__":
    dp = DiskProvider()
    widget = DiskWidget()

    dp.get_metrics()
    import time
    time.sleep(1)

    data = dp.get_metrics()
    print("\033[H\033[J", end="")
    for line in widget.render(data):
            print(line)
    time.sleep(1)
