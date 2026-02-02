import os
import time
from typing import Dict, Tuple, Optional


BYTES_IN_GIB = 1024 ** 3


class DiskProvider:
    """
    Provides disk IO, partition capacity, and swap metrics using /proc.
    Linux-specific implementation.
    """

    MOUNTS_PATH = "/proc/mounts"
    DISKSTATS_PATH = "/proc/diskstats"
    MEMINFO_PATH = "/proc/meminfo"

    IGNORED_MOUNT_PREFIXES = (
        "/snap",
        "/proc",
        "/sys",
        "/dev",
        "/run",
        "/var/lib/docker",
    )

    IGNORED_DISK_PREFIXES = ("loop", "ram", "sr", "zram")

    def __init__(self) -> None:
        # { disk: (r_bytes, w_bytes, io_ticks, r_ops, w_ops, timestamp) }
        self.last_stats: Dict[str, Tuple[int, int, int, int, int, float]] = {}

    # ---------------- PARTITION CAPACITY ----------------
    def _get_partition_capacity(self) -> Dict[str, Dict[str, object]]:
        capacity: Dict[str, Dict[str, object]] = {}

        try:
            with open(self.MOUNTS_PATH, "r", encoding="utf-8") as file:
                for line in file:
                    if not line.startswith("/dev/"):
                        continue

                    dev, mount = line.split()[:2]
                    part = dev.split("/")[-1]

                    if mount.startswith(self.IGNORED_MOUNT_PREFIXES):
                        continue

                    try:
                        st = os.statvfs(mount)

                        total = (st.f_blocks * st.f_frsize) / BYTES_IN_GIB
                        free = (st.f_bavail * st.f_frsize) / BYTES_IN_GIB
                        used = total - free
                        pct = (used / total * 100) if total else 0

                        capacity[part] = {
                            "total": round(total, 2),
                            "used": round(used, 2),
                            "free": round(free, 2),
                            "pct": round(pct, 1),
                            "mount": mount,
                        }
                    except (OSError, IOError):
                        continue
        except (OSError, IOError):
            pass

        return capacity

    # ---------------- RAW DISK IO ----------------
    def _read_diskstats(self) -> Dict[str, Dict[str, int]]:
        disks: Dict[str, Dict[str, int]] = {}

        try:
            with open(self.DISKSTATS_PATH, "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.split()
                    if len(parts) < 14:
                        continue

                    dev = parts[2]

                    if dev.startswith(self.IGNORED_DISK_PREFIXES):
                        continue

                    disks[dev] = {
                        "r_ops": int(parts[3]),
                        "r_bytes": int(parts[5]) * 512,
                        "w_ops": int(parts[7]),
                        "w_bytes": int(parts[9]) * 512,
                        "io_ticks": int(parts[12]),
                    }
        except (OSError, IOError):
            pass

        return disks

    # ---------------- SWAP ----------------
    def _get_swap(self) -> Optional[Dict[str, float]]:
        mem: Dict[str, int] = {}

        try:
            with open(self.MEMINFO_PATH, "r", encoding="utf-8") as file:
                for line in file:
                    key, value = line.split(":", 1)
                    mem[key.strip()] = int(value.split()[0]) * 1024
        except (OSError, IOError):
            return None

        total = mem.get("SwapTotal", 0) / BYTES_IN_GIB
        free = mem.get("SwapFree", 0) / BYTES_IN_GIB
        used = total - free
        pct = (used / total * 100) if total else 0

        return {
            "total": round(total, 2),
            "used": round(used, 2),
            "free": round(free, 2),
            "pct": round(pct, 1),
        }

    # ---------------- PUBLIC API ----------------
    def get_metrics(self) -> Dict[str, object]:
        now = time.time()

        disks = self._read_diskstats()
        partitions = self._get_partition_capacity()
        swap = self._get_swap()

        result = {
            "disks": {},
            "partitions": partitions,
            "swap": swap,
        }

        for dev, data in disks.items():
            prev = self.last_stats.get(dev)

            if prev:
                prb, pwb, pticks, props, pwops, pt = prev
                dt = now - pt

                if dt > 0:
                    read_speed = ((data["r_bytes"] - prb) / BYTES_IN_GIB) / dt
                    write_speed = ((data["w_bytes"] - pwb) / BYTES_IN_GIB) / dt
                    iops = (
                        (data["r_ops"] - props)
                        + (data["w_ops"] - pwops)
                    ) / dt
                    util_pct = (data["io_ticks"] - pticks) / (dt * 10)
                else:
                    read_speed = write_speed = iops = util_pct = 0.0
            else:
                read_speed = write_speed = iops = util_pct = 0.0

            result["disks"][dev] = {
                "read_speed": round(max(read_speed, 0.0), 4),
                "write_speed": round(max(write_speed, 0.0), 4),
                "iops": round(max(iops, 0.0), 1),
                "util_pct": round(min(max(util_pct, 0.0), 100.0), 1),
            }

            self.last_stats[dev] = (
                data["r_bytes"],
                data["w_bytes"],
                data["io_ticks"],
                data["r_ops"],
                data["w_ops"],
                now,
            )

        return result

