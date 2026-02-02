import os
import sys

class Colors:
    """
    Production-level Color Engine for Terminal UI.
    Supports ANSI 256 and TrueColor (RGB).
    """
    
    # Core ANSI
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"

    # Semantic Theme Palette (btop-inspired)
    # Using 256-color palette for maximum compatibility
    MAIN_FG = "\033[38;5;253m"      # Near white
    MAIN_BG = "\033[48;5;234m"      # Deep grey/black
    
    # Component Colors
    CPU_GRAPH = "\033[38;5;39m"     # Blue
    MEM_GRAPH = "\033[38;5;121m"    # Spring Green
    NET_DOWN  = "\033[38;5;39m"     # Cyan
    NET_UP    = "\033[38;5;161m"    # Magenta
    DISK_BAR  = "\033[38;5;214m"    # Amber/Orange
    PROC_USER = "\033[38;5;147m"    # Soft Purple
    
    # Status Levels
    OK    = "\033[38;5;76m"         # Green
    WARN  = "\033[38;5;220m"        # Yellow
    CRIT  = "\033[38;5;196m"        # Red
    
    # Border & UI
    BORDER_ACTIVE = "\033[38;5;39m"
    BORDER_DIM    = "\033[38;5;238m"
    HEADER_BG     = "\033[48;5;236m"

    @staticmethod
    def true_color(r: int, g: int, b: int, is_bg: bool = False) -> str:
        """Returns TrueColor (RGB) escape sequence."""
        code = "48" if is_bg else "38"
        return f"\033[{code};2;{r};{g};{b}m"

    @staticmethod
    def color_256(code: int, is_bg: bool = False) -> str:
        """Returns ANSI 256-color escape sequence."""
        prefix = "48" if is_bg else "38"
        return f"\033[{prefix};5;{code}m"

    @classmethod
    def get_gradient(cls, ratio: float):
        """
        Returns a color based on usage ratio (0.0 to 1.0).
        Green -> Yellow -> Red
        """
        if ratio < 0.5: return cls.OK
        if ratio < 0.8: return cls.WARN
        return cls.CRIT

    @classmethod
    def strip_colors(cls, text: str) -> str:
        """Removes all ANSI escape codes from string (useful for length calc)."""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    @classmethod
    def print_test_card(cls):
        """Prints a diagnostic color card to the terminal."""
        print(f"\n{cls.BOLD}SHM Dashboard - Production Color Palette{cls.RESET}\n")
        
        test_labels = [
            ("CPU", cls.CPU_GRAPH), ("MEM", cls.MEM_GRAPH), 
            ("NET DOWN", cls.NET_DOWN), ("NET UP", cls.NET_UP),
            ("OK", cls.OK), ("WARN", cls.WARN), ("CRIT", cls.CRIT)
        ]
        
        for label, color in test_labels:
            bar = f"{color}█" * 20 + cls.RESET
            print(f"{label:<10} {bar}")

        # RGB Gradient Test
        print(f"\n{cls.DIM}TrueColor Support Test:{cls.RESET}")
        gradient = ""
        for i in range(0, 255, 10):
            gradient += cls.true_color(i, 255-i, 150) + "█"
        print(gradient + cls.RESET + "\n")

# --- Initialize on Import ---
# Check if terminal supports color
if not sys.stdout.isatty():
    # Disable colors if output is piped to a file/tool
    for attr in dir(Colors):
        if not attr.startswith("__") and isinstance(getattr(Colors, attr), str):
            setattr(Colors, attr, "")

if __name__ == "__main__":
    Colors.print_test_card()