import os
import platform
import socket
from typing import Dict


class SysInfoProvider:
    """
    Provides system and platform metadata for display or diagnostics.
    """

    OS_RELEASE_PATH = "/etc/os-release"

    def __init__(self) -> None:
        pass

    def get_os_distro(self) -> str:
        """
        Reads /etc/os-release to get the Linux distribution name.
        Falls back to platform.system() if unavailable.
        """
        try:
            if os.path.exists(self.OS_RELEASE_PATH):
                with open(self.OS_RELEASE_PATH, "r", encoding="utf-8") as file:
                    for line in file:
                        if line.startswith("PRETTY_NAME="):
                            return (
                                line.split("=", 1)[1]
                                .strip()
                                .replace('"', "")
                            )

            return platform.system()
        except (OSError, IOError):
            return "Linux"

    def get_info(self) -> Dict[str, str]:
        """
        Returns a dictionary containing platform metadata.
        """
        return {
            "os_name": self.get_os_distro(),
            "kernel": platform.release(),
            "arch": platform.machine(),
            "hostname": socket.gethostname(),
            "python_version": platform.python_version(),
        }

    def get_banner(self) -> str:
        """
        Returns a formatted banner string for UI headers.
        """
        info = self.get_info()
        return (
            f"{info['hostname']} | "
            f"{info['os_name']} | "
            f"Kernel: {info['kernel']} | "
            f"{info['arch']}"
        )
