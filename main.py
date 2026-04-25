# main.py
"""
==============================================================
  main.py — Entry Point
  Poori app yahan se start hoti hai.
  Imports:
    gui.py       → SudokuApp (visual interface)
    gui.py imports datasets, csp_solver, hint automatically
  Run karo: python main.py
==============================================================
"""

import tkinter as tk
from gui import SudokuApp


def main():
    """App launch karo — window banao aur center karo screen par."""
    root = tk.Tk()

    # Window dimensions — big enough for board + side panel
    W = 1020   # width
    H = 780    # height

    # Center on screen
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x  = (sw - W) // 2
    y  = (sh - H) // 2
    root.geometry(f"{W}x{H}+{x}+{y}")
    root.minsize(900, 700)

    # Launch app
    SudokuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()