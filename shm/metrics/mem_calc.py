import os

class MemoryCalcProvider:
    def __init__(self):
        pass

    # ---------------- PROCESS MEMORY ----------------
    def get_process_memory(self, pid):
        """
        Returns RSS memory (bytes) for a process from /proc/[pid]/status
        """
        try:
            with open(f"/proc/{pid}/status", "r") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        # VmRSS is the Resident Set Size (Actual physical RAM used)
                        return int(line.split()[1]) * 1024
        except Exception:
            pass
        return 0

    def get_top_memory_processes(self, limit=10):
        """
        Returns a sorted list of top memory-consuming processes
        """
        processes = []

        # Filter for numeric PID directories in /proc
        for pid in filter(str.isdigit, os.listdir("/proc")):
            mem = self.get_process_memory(pid)
            if mem <= 0:
                continue

            try:
                with open(f"/proc/{pid}/comm", "r") as f:
                    name = f.read().strip()
            except Exception:
                name = "unknown"

            processes.append({
                "pid": pid,
                "name": name,
                "mem": mem
            })

        # Sort by memory usage descending
        processes.sort(key=lambda x: x["mem"], reverse=True)
        return processes[:limit]
