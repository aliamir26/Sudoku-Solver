# gui.py
"""
==============================================================
  gui.py — Tkinter GUI for Sudoku CSP Solver
  Poora visual interface yahan hai:
  - Board drawing
  - Difficulty aur puzzle selection
  - Algorithm selection (AC-3 / Backtracking)
  - Solve, Hint, Reset buttons
  - Time display
==============================================================
"""

import tkinter as tk
from tkinter import messagebox
import copy

from datasets import get_puzzle
from csp_solver import ac3, backtracking
from hint import get_hint, is_board_correct


# ─────────────────────────────────────────────
#  COLORS — professional dark theme palette
# ─────────────────────────────────────────────

BG_COLOR        = "#1a1a2e"   # Dark navy background
PANEL_COLOR     = "#16213e"   # Slightly lighter panel
BOARD_BG        = "#0f3460"   # Board background
CELL_EMPTY      = "#1a1a2e"   # Empty cell color
CELL_GIVEN      = "#0f3460"   # Pre-filled cell
CELL_USER       = "#16213e"   # User-filled cell
CELL_HINT       = "#1b4332"   # Hint cell (green tint)
CELL_WRONG      = "#3b1219"   # Wrong cell (red tint)
CELL_SELECTED   = "#533483"   # Selected cell (purple)

TEXT_GIVEN      = "#e2e8f0"   # Pre-filled number color
TEXT_USER       = "#63b3ed"   # User typed number color
TEXT_HINT       = "#68d391"   # Hint number color
TEXT_WRONG      = "#fc8181"   # Wrong number color
TEXT_ACCENT     = "#a78bfa"   # Accent purple

GRID_LINE_THIN  = "#334155"   # Thin grid lines
GRID_LINE_THICK = "#a78bfa"   # Thick box borders (purple)

BTN_SOLVE       = "#7c3aed"   # Solve button
BTN_HINT        = "#059669"   # Hint button
BTN_RESET       = "#dc2626"   # Reset button
BTN_CHECK       = "#2563eb"   # Check button
BTN_HOVER       = "#5b21b6"   # Hover state

TITLE_COLOR     = "#a78bfa"   # Title text
LABEL_COLOR     = "#94a3b8"   # Label text
TIME_COLOR      = "#34d399"   # Time display


# ─────────────────────────────────────────────
#  MAIN APP CLASS
# ─────────────────────────────────────────────

class SudokuApp:
    """
    Main GUI class — poori app yahan manage hoti hai.
    Tkinter window banata hai aur sab components attach karta hai.
    """

    def __init__(self, root):
        """App initialize karo — window setup karo."""
        self.root = root
        self.root.title("Sudoku CSP Solver — AL-2002")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # ── State variables ──
        self.current_grid   = None   # Jo abhi board par hai
        self.original_grid  = None   # Original puzzle (reset ke liye)
        self.solution       = None   # Solved grid
        self.selected_cell  = None   # Currently selected cell (r, c)
        self.hint_cells     = set()  # Cells jo hint se fill hue
        self.user_cells     = set()  # Cells jo user ne fill kiye
        self.wrong_cells    = set()  # Cells jo galat hain

        self.difficulty_var  = tk.StringVar(value="easy")
        self.puzzle_var      = tk.StringVar(value="1")
        self.algorithm_var   = tk.StringVar(value="backtracking")

        # ── Build UI ──
        self._build_title()
        self._build_controls()
        self._build_board()
        self._build_info_panel()
        self._build_buttons()

        # ── Load first puzzle by default ──
        self.load_puzzle()


    # ─────────────────────────────────────────
    #  UI BUILDERS
    # ─────────────────────────────────────────

    def _build_title(self):
        """Title bar banao — top mein."""
        title_frame = tk.Frame(self.root, bg=BG_COLOR, pady=12)
        title_frame.pack(fill="x")

        tk.Label(
            title_frame,
            text="✦  SUDOKU CSP SOLVER  ✦",
            font=("Courier New", 20, "bold"),
            bg=BG_COLOR,
            fg=TITLE_COLOR
        ).pack()

        tk.Label(
            title_frame,
            text="Arc-Consistency 3  ·  Backtracking Search",
            font=("Courier New", 9),
            bg=BG_COLOR,
            fg=LABEL_COLOR
        ).pack()


    def _build_controls(self):
        """
        Top controls — difficulty, puzzle number, algorithm selection.
        Teen rows of dropdowns/radio buttons.
        """
        ctrl_frame = tk.Frame(self.root, bg=PANEL_COLOR, padx=20, pady=12)
        ctrl_frame.pack(fill="x", padx=20, pady=(0, 10))

        # ── Row 1: Difficulty ──
        row1 = tk.Frame(ctrl_frame, bg=PANEL_COLOR)
        row1.pack(fill="x", pady=3)

        tk.Label(
            row1, text="DIFFICULTY", font=("Courier New", 8, "bold"),
            bg=PANEL_COLOR, fg=LABEL_COLOR, width=12, anchor="w"
        ).pack(side="left")

        for diff in ["easy", "medium", "hard"]:
            tk.Radiobutton(
                row1, text=diff.capitalize(),
                variable=self.difficulty_var, value=diff,
                font=("Courier New", 9),
                bg=PANEL_COLOR, fg=TEXT_GIVEN,
                selectcolor=BG_COLOR,
                activebackground=PANEL_COLOR,
                activeforeground=TEXT_ACCENT,
                command=self._on_difficulty_change
            ).pack(side="left", padx=8)

        # ── Row 2: Puzzle Number ──
        row2 = tk.Frame(ctrl_frame, bg=PANEL_COLOR)
        row2.pack(fill="x", pady=3)

        tk.Label(
            row2, text="PUZZLE #", font=("Courier New", 8, "bold"),
            bg=PANEL_COLOR, fg=LABEL_COLOR, width=12, anchor="w"
        ).pack(side="left")

        for p in ["1", "2", "3", "4"]:
            tk.Radiobutton(
                row2, text=f"Puzzle {p}",
                variable=self.puzzle_var, value=p,
                font=("Courier New", 9),
                bg=PANEL_COLOR, fg=TEXT_GIVEN,
                selectcolor=BG_COLOR,
                activebackground=PANEL_COLOR,
                activeforeground=TEXT_ACCENT,
            ).pack(side="left", padx=8)

        # ── Row 3: Algorithm ──
        row3 = tk.Frame(ctrl_frame, bg=PANEL_COLOR)
        row3.pack(fill="x", pady=3)

        tk.Label(
            row3, text="ALGORITHM", font=("Courier New", 8, "bold"),
            bg=PANEL_COLOR, fg=LABEL_COLOR, width=12, anchor="w"
        ).pack(side="left")

        for algo, label in [("backtracking", "Backtracking"), ("ac3", "AC-3")]:
            tk.Radiobutton(
                row3, text=label,
                variable=self.algorithm_var, value=algo,
                font=("Courier New", 9),
                bg=PANEL_COLOR, fg=TEXT_GIVEN,
                selectcolor=BG_COLOR,
                activebackground=PANEL_COLOR,
                activeforeground=TEXT_ACCENT,
            ).pack(side="left", padx=8)

        # ── Load Puzzle Button ──
        load_btn = tk.Button(
            ctrl_frame,
            text="LOAD PUZZLE",
            font=("Courier New", 9, "bold"),
            bg=TEXT_ACCENT, fg=BG_COLOR,
            relief="flat", padx=12, pady=4,
            cursor="hand2",
            command=self.load_puzzle
        )
        load_btn.pack(pady=(6, 0))


    def _build_board(self):
        """
        9x9 Sudoku board banao Canvas par.
        Har cell ek clickable area hai.
        """
        board_outer = tk.Frame(self.root, bg=GRID_LINE_THICK, padx=3, pady=3)
        board_outer.pack(padx=20, pady=5)

        self.canvas = tk.Canvas(
            board_outer,
            width=450, height=450,
            bg=BOARD_BG,
            highlightthickness=0
        )
        self.canvas.pack()

        # Mouse click event
        self.canvas.bind("<Button-1>", self._on_cell_click)
        # Keyboard input
        self.root.bind("<Key>", self._on_key_press)

        # Draw grid lines initially
        self._draw_grid_lines()


    def _build_info_panel(self):
        """
        Info panel — time display, status messages.
        Board ke neeche.
        """
        info_frame = tk.Frame(self.root, bg=PANEL_COLOR, padx=20, pady=8)
        info_frame.pack(fill="x", padx=20, pady=5)

        # Time label
        time_row = tk.Frame(info_frame, bg=PANEL_COLOR)
        time_row.pack(fill="x")

        tk.Label(
            time_row, text="SOLVE TIME:",
            font=("Courier New", 9, "bold"),
            bg=PANEL_COLOR, fg=LABEL_COLOR
        ).pack(side="left")

        self.time_label = tk.Label(
            time_row, text="—",
            font=("Courier New", 11, "bold"),
            bg=PANEL_COLOR, fg=TIME_COLOR
        )
        self.time_label.pack(side="left", padx=8)

        # Status label
        self.status_label = tk.Label(
            info_frame,
            text="Load a puzzle to begin.",
            font=("Courier New", 9),
            bg=PANEL_COLOR, fg=LABEL_COLOR,
            wraplength=400
        )
        self.status_label.pack(fill="x", pady=(4, 0))


    def _build_buttons(self):
        """
        Action buttons — Solve, Hint, Check, Reset.
        2x2 grid of buttons.
        """
        btn_frame = tk.Frame(self.root, bg=BG_COLOR, pady=10)
        btn_frame.pack(padx=20, pady=(0, 15))

        buttons = [
            ("⚡  SOLVE",  BTN_SOLVE, self.solve_puzzle),
            ("💡  HINT",   BTN_HINT,  self.give_hint),
            ("✓  CHECK",  BTN_CHECK, self.check_board),
            ("↺  RESET",  BTN_RESET, self.reset_puzzle),
        ]

        for i, (text, color, cmd) in enumerate(buttons):
            btn = tk.Button(
                btn_frame,
                text=text,
                font=("Courier New", 10, "bold"),
                bg=color, fg="white",
                relief="flat",
                padx=18, pady=8,
                cursor="hand2",
                command=cmd
            )
            btn.grid(row=i // 2, column=i % 2, padx=6, pady=5, sticky="ew")

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)


    # ─────────────────────────────────────────
    #  DRAWING FUNCTIONS
    # ─────────────────────────────────────────

    def _draw_grid_lines(self):
        """Grid lines draw karo — thin aur thick dono."""
        cell_size = 50

        for i in range(10):
            # Thick lines har 3rd line par (box borders)
            if i % 3 == 0:
                width = 3
                color = GRID_LINE_THICK
            else:
                width = 1
                color = GRID_LINE_THIN

            # Vertical lines
            self.canvas.create_line(
                i * cell_size, 0,
                i * cell_size, 450,
                fill=color, width=width
            )
            # Horizontal lines
            self.canvas.create_line(
                0, i * cell_size,
                450, i * cell_size,
                fill=color, width=width
            )


    def _draw_board(self):
        """
        Poora board redraw karo current state se.
        Har cell ki background aur number fresh draw hoti hai.
        """
        if self.current_grid is None:
            return

        self.canvas.delete("cell")  # Sirf cells delete karo, lines nahi
        cell_size = 50

        for r in range(9):
            for c in range(9):
                x1 = c * cell_size + 2
                y1 = r * cell_size + 2
                x2 = x1 + cell_size - 4
                y2 = y1 + cell_size - 4
                cx = c * cell_size + cell_size // 2
                cy = r * cell_size + cell_size // 2

                val = self.current_grid[r][c]

                # ── Cell background color decide karo ──
                if (r, c) == self.selected_cell:
                    bg = CELL_SELECTED
                elif (r, c) in self.wrong_cells:
                    bg = CELL_WRONG
                elif (r, c) in self.hint_cells:
                    bg = CELL_HINT
                elif self.original_grid and self.original_grid[r][c] != 0:
                    bg = CELL_GIVEN
                elif (r, c) in self.user_cells:
                    bg = CELL_USER
                else:
                    bg = CELL_EMPTY

                # Draw cell background
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=bg, outline="",
                    tags="cell"
                )

                # ── Number color decide karo ──
                if val != 0:
                    if (r, c) in self.wrong_cells:
                        fg = TEXT_WRONG
                    elif (r, c) in self.hint_cells:
                        fg = TEXT_HINT
                    elif self.original_grid and self.original_grid[r][c] != 0:
                        fg = TEXT_GIVEN
                    else:
                        fg = TEXT_USER

                    self.canvas.create_text(
                        cx, cy,
                        text=str(val),
                        font=("Courier New", 18, "bold"),
                        fill=fg,
                        tags="cell"
                    )

        # Grid lines dobara draw karo (cells ke upar)
        self._draw_grid_lines()