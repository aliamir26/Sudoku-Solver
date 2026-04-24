# main.py
"""
==============================================================
  main.py — Entry Point
  Yahan se poori app start hoti hai.
  Sab files yahan aakar milti hain:
    datasets.py  → puzzles data
    csp_solver.py → AC-3 + Backtracking
    hint.py      → hint system
    gui.py       → visual interface
  Run karo: python main.py
==============================================================
"""

import tkinter as tk
from gui import SudokuApp


def main():
    """App start karo — Tkinter window launch karo."""
    root = tk.Tk()

    # Window ko screen center mein rakh do
    window_width  = 520
    window_height = 720

    screen_width  = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width  // 2) - (window_width  // 2)
    y = (screen_height // 2) - (window_height // 2)

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # App launch karo
    app = SudokuApp(root)

    # Window loop start karo
    root.mainloop()


if __name__ == "__main__":
    main()