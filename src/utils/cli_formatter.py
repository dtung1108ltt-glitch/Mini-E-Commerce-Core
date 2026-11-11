"""
CLI Formatter Utilities
Provides ANSI color codes, box drawing tables, and defensive input prompts.
"""
from typing import List, Dict, Any, Optional

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_banner():
    banner = f"""{CYAN}{BOLD}
╔══════════════════════════════════════════════════════════════════════╗
║               MINI E-COMMERCE CORE ENGINE (DSA)                      ║
║          High-Performance Data Structures & Algorithms               ║
║                     100,000+ Items Architecture                      ║
╚══════════════════════════════════════════════════════════════════════╝{RESET}"""
    print(banner)


def print_section(title: str):
    print(f"\n{YELLOW}{BOLD}▶ {title.upper()}{RESET}")
    print(f"{DIM}{'─' * 60}{RESET}")


def prompt_int(prompt: str, default: Optional[int] = None, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    while True:
        suffix = f" [default: {default}]: " if default is not None else ": "
        raw = input(f"{BOLD}{prompt}{RESET}{suffix}").strip()
        if not raw and default is not None:
            return default
        try:
            val = int(raw)
            if min_val is not None and val < min_val:
                print(f"{RED}Value must be >= {min_val}. Try again.{RESET}")
                continue
            if max_val is not None and val > max_val:
                print(f"{RED}Value must be <= {max_val}. Try again.{RESET}")
                continue
            return val
        except ValueError:
            print(f"{RED}Invalid integer input. Please try again.{RESET}")


def prompt_float(prompt: str, default: Optional[float] = None, min_val: Optional[float] = None, max_val: Optional[float] = None) -> float:
    while True:
        suffix = f" [default: {default}]: " if default is not None else ": "
        raw = input(f"{BOLD}{prompt}{RESET}{suffix}").strip()
        if not raw and default is not None:
            return default
        try:
            val = float(raw)
            if min_val is not None and val < min_val:
                print(f"{RED}Value must be >= {min_val}. Try again.{RESET}")
                continue
            if max_val is not None and val > max_val:
                print(f"{RED}Value must be <= {max_val}. Try again.{RESET}")
                continue
            return val
        except ValueError:
            print(f"{RED}Invalid decimal input. Please try again.{RESET}")


def prompt_str(prompt: str, default: Optional[str] = None) -> str:
    suffix = f" [default: '{default}']: " if default is not None else ": "
    raw = input(f"{BOLD}{prompt}{RESET}{suffix}").strip()
    if not raw and default is not None:
        return default
    return raw


def print_table(headers: List[str], rows: List[List[Any]]):
    if not rows:
        print(f"{DIM}(No records to display){RESET}")
        return

    # Calculate max column widths
    str_rows = [[str(cell) for cell in row] for row in rows]
    col_widths = [len(h) for h in headers]
    for row in str_rows:
        for idx, cell in enumerate(row):
            if idx < len(col_widths):
                col_widths[idx] = max(col_widths[idx], len(cell))

    # Header row
    header_str = " │ ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
    separator = "─┼─".join("─" * col_widths[i] for i in range(len(headers)))
    top_border = "─┬─".join("─" * col_widths[i] for i in range(len(headers)))
    bottom_border = "─┴─".join("─" * col_widths[i] for i in range(len(headers)))

    print(f"{CYAN}┌─{top_border}─┐{RESET}")
    print(f"{CYAN}│ {BOLD}{header_str}{RESET}{CYAN} │{RESET}")
    print(f"{CYAN}├─{separator}─┤{RESET}")
    for row in str_rows:
        row_str = " │ ".join(f"{row[i]:<{col_widths[i]}}" if i < len(row) else " " * col_widths[i] for i in range(len(headers)))
        print(f"│ {row_str} │")
    print(f"{CYAN}└─{bottom_border}─┘{RESET}")
