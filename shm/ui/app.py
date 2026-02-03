from __future__ import annotations

"""
Application entry point for System Monitor (Textual UI)

Responsibilities:
- Initialize the Textual app
- Import and run main layout
- Keep app.py minimal (no UI logic here)
"""

from shm.ui.layout import SystemMonitor



def main() -> None:
    """
    Start the System Monitor TUI application.
    """
    app = SystemMonitor()
    app.run()


if __name__ == "__main__":
    main()
