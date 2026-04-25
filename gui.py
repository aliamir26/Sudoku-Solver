# gui.py
"""
==============================================================
  gui.py — Tkinter GUI for Sudoku CSP Solver
  - Cell-by-cell input (blocks)
  - Working hint system (visible on board)
  - Side-by-side algorithm time comparison
  - No clipping of any content
==============================================================
"""

import tkinter as tk
from tkinter import messagebox, font as tkfont
import copy
import threading
import time

from datasets import get_puzzle
from csp_solver import ac3, backtracking, format_time
from hint import get_hint, is_board_correct


# ─────────────────────────────────────────────────────────
#  THEME — Clean White + Black + Red accent
# ─────────────────────────────────────────────────────────

C_BG            = "#0d0d0d"   # Near-black background
C_SURFACE       = "#161616"   # Card/panel surface
C_SURFACE2      = "#1e1e1e"   # Elevated surface
C_BORDER        = "#2a2a2a"   # Subtle borders
C_BORDER2       = "#3a3a3a"   # Brighter border

C_WHITE         = "#f0f0f0"   # Primary text
C_GRAY          = "#888888"   # Muted text
C_LGRAY         = "#555555"   # Very muted

# Red accent — used for solving animation & highlights
C_RED           = "#e63946"
C_RED_DIM       = "#7a1e25"
C_RED_GLOW      = "#ff6b6b"

# Cell states
CELL_GIVEN_BG   = "#1a1a1a"   # Given cells — dark
CELL_EMPTY_BG   = "#111111"   # Empty cells
CELL_USER_BG    = "#161b22"   # User-filled
CELL_HINT_BG    = "#0d2818"   # Hint — dark green
CELL_WRONG_BG   = "#2a0a0a"   # Wrong — dark red
CELL_SELECT_BG  = "#1a1a2e"   # Selected — dark blue
CELL_SOLVE_BG   = "#2a0a0a"   # Being solved — red pulse

# Number colors
NUM_GIVEN       = "#e0e0e0"   # Given numbers — white
NUM_USER        = "#5b9bd5"   # User typed — blue
NUM_HINT        = "#4ade80"   # Hint — bright green
NUM_WRONG       = "#e63946"   # Wrong — red

# Grid lines
LINE_THIN       = "#2a2a2a"
LINE_THICK      = "#e63946"   # Red thick lines for 3x3 boxes

# Button colors
BTN_SOLVE       = "#e63946"
BTN_HINT        = "#166534"
BTN_CHECK       = "#1e3a5f"
BTN_RESET       = "#3a1f00"
BTN_LOAD        = "#1e1e2e"

CELL_SIZE       = 62          # Bigger cells
BOARD_SIZE      = CELL_SIZE * 9   # 558px


# ─────────────────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────────────────

class SudokuApp:
    """
    Main GUI class — poori app yahan manage hoti hai.
    Bada window, clean layout, proper cell input.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku CSP Solver  ·  AL-2002  ·  NUCES")
        self.root.configure(bg=C_BG)
        self.root.resizable(True, True)

        # ── State ──────────────────────────────────────
        self.current_grid   = None
        self.original_grid  = None
        self.selected_cell  = None
        self.hint_cells     = set()
        self.user_cells     = set()
        self.wrong_cells    = set()
        self.solving_cell   = None      # For animation
        self.is_solving     = False

        # Algorithm time results (for comparison)
        self.time_bt        = None      # Backtracking time
        self.time_ac3       = None      # AC-3 time

        # Tkinter variables
        self.difficulty_var = tk.StringVar(value="easy")
        self.puzzle_var     = tk.StringVar(value="1")
        self.algorithm_var  = tk.StringVar(value="backtracking")

        # ── Build UI ───────────────────────────────────
        self._setup_fonts()
        self._build_layout()

        # Load default puzzle
        self.load_puzzle()

        # Keyboard binding
        self.root.bind("<Key>", self._on_key_press)
        self.root.focus_set()


    def _setup_fonts(self):
        """Fonts define karo."""
        self.font_title    = tkfont.Font(family="Courier New", size=15, weight="bold")
        self.font_subtitle = tkfont.Font(family="Courier New", size=8)
        self.font_label    = tkfont.Font(family="Courier New", size=8, weight="bold")
        self.font_btn      = tkfont.Font(family="Courier New", size=9, weight="bold")
        self.font_number   = tkfont.Font(family="Courier New", size=20, weight="bold")
        self.font_given    = tkfont.Font(family="Courier New", size=20, weight="bold")
        self.font_small    = tkfont.Font(family="Courier New", size=8)
        self.font_time     = tkfont.Font(family="Courier New", size=11, weight="bold")
        self.font_time_sm  = tkfont.Font(family="Courier New", size=9)
        self.font_status   = tkfont.Font(family="Courier New", size=9)
        self.font_section  = tkfont.Font(family="Courier New", size=7, weight="bold")


    def _build_layout(self):
        """
        Main layout:
        LEFT: Controls + Board + Status
        RIGHT: Algorithm comparison panel
        """
        # Outer container — fills window
        outer = tk.Frame(self.root, bg=C_BG)
        outer.pack(fill="both", expand=True, padx=0, pady=0)

        # ── Title bar ──────────────────────────────────
        self._build_title(outer)

        # ── Content area: left + right ─────────────────
        content = tk.Frame(outer, bg=C_BG)
        content.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # LEFT column
        left = tk.Frame(content, bg=C_BG)
        left.pack(side="left", fill="both", expand=False)

        # RIGHT column — algo comparison panel
        right = tk.Frame(content, bg=C_SURFACE, width=270,
                         highlightbackground=C_BORDER2,
                         highlightthickness=1)
        right.pack(side="right", fill="y", padx=(15, 0))
        right.pack_propagate(False)

        # Build left side
        self._build_controls(left)
        self._build_board(left)
        self._build_status(left)

        # Build right side
        self._build_comparison_panel(right)


    def _build_title(self, parent):
        """Title bar at top."""
        bar = tk.Frame(parent, bg=C_SURFACE, pady=10)
        bar.pack(fill="x", padx=0, pady=(0, 10))

        # Red accent line on left
        tk.Frame(bar, bg=C_RED, width=4, height=40).pack(side="left", padx=(12, 10))

        text_frame = tk.Frame(bar, bg=C_SURFACE)
        text_frame.pack(side="left")

        tk.Label(text_frame, text="SUDOKU  CSP  SOLVER",
                 font=self.font_title, bg=C_SURFACE, fg=C_WHITE).pack(anchor="w")
        tk.Label(text_frame, text="Arc-Consistency 3  ·  Backtracking Search  ·  AL-2002",
                 font=self.font_subtitle, bg=C_SURFACE, fg=C_GRAY).pack(anchor="w")

        # Red dot indicator — top right
        tk.Label(bar, text="●", font=("Courier New", 14),
                 bg=C_SURFACE, fg=C_RED).pack(side="right", padx=15)


    def _build_controls(self, parent):
        """
        Controls panel: difficulty, puzzle, algorithm selection.
        Horizontal layout to save vertical space.
        """
        panel = tk.Frame(parent, bg=C_SURFACE,
                         highlightbackground=C_BORDER2,
                         highlightthickness=1)
        panel.pack(fill="x", pady=(0, 10))

        # ── Row 1: Difficulty + Puzzle ────────────────
        r1 = tk.Frame(panel, bg=C_SURFACE, pady=6, padx=10)
        r1.pack(fill="x")

        # Difficulty
        diff_frame = tk.Frame(r1, bg=C_SURFACE)
        diff_frame.pack(side="left", padx=(0, 20))

        tk.Label(diff_frame, text="DIFFICULTY",
                 font=self.font_section, bg=C_SURFACE, fg=C_RED).pack(anchor="w")
        rb_frame = tk.Frame(diff_frame, bg=C_SURFACE)
        rb_frame.pack()
        for d in ["easy", "medium", "hard"]:
            tk.Radiobutton(
                rb_frame, text=d.upper(),
                variable=self.difficulty_var, value=d,
                font=self.font_small,
                bg=C_SURFACE, fg=C_WHITE,
                selectcolor=C_BG,
                activebackground=C_SURFACE,
                activeforeground=C_RED,
                indicatoron=True,
                command=lambda: self.puzzle_var.set("1")
            ).pack(side="left", padx=4)

        # Puzzle number
        puz_frame = tk.Frame(r1, bg=C_SURFACE)
        puz_frame.pack(side="left", padx=(0, 20))

        tk.Label(puz_frame, text="PUZZLE #",
                 font=self.font_section, bg=C_SURFACE, fg=C_RED).pack(anchor="w")
        pb_frame = tk.Frame(puz_frame, bg=C_SURFACE)
        pb_frame.pack()
        for p in ["1", "2", "3", "4"]:
            tk.Radiobutton(
                pb_frame, text=p,
                variable=self.puzzle_var, value=p,
                font=self.font_small,
                bg=C_SURFACE, fg=C_WHITE,
                selectcolor=C_BG,
                activebackground=C_SURFACE,
                activeforeground=C_RED,
            ).pack(side="left", padx=4)

        # Algorithm
        algo_frame = tk.Frame(r1, bg=C_SURFACE)
        algo_frame.pack(side="left", padx=(0, 20))

        tk.Label(algo_frame, text="ALGORITHM",
                 font=self.font_section, bg=C_SURFACE, fg=C_RED).pack(anchor="w")
        ab_frame = tk.Frame(algo_frame, bg=C_SURFACE)
        ab_frame.pack()
        for a, label in [("backtracking", "BACKTRACK"), ("ac3", "AC-3")]:
            tk.Radiobutton(
                ab_frame, text=label,
                variable=self.algorithm_var, value=a,
                font=self.font_small,
                bg=C_SURFACE, fg=C_WHITE,
                selectcolor=C_BG,
                activebackground=C_SURFACE,
                activeforeground=C_RED,
            ).pack(side="left", padx=4)

        # ── Row 2: Load button ─────────────────────────
        r2 = tk.Frame(panel, bg=C_SURFACE, pady=6, padx=10)
        r2.pack(fill="x")

        load_btn = tk.Button(
            r2, text="  LOAD PUZZLE  ",
            font=self.font_btn,
            bg=C_RED, fg=C_WHITE,
            relief="flat", padx=8, pady=4,
            cursor="hand2",
            activebackground=C_RED_DIM,
            activeforeground=C_WHITE,
            command=self.load_puzzle
        )
        load_btn.pack(side="left")

        # Separator
        tk.Frame(r2, bg=C_BORDER, height=1).pack(fill="x", pady=(8, 0))


    def _build_board(self, parent):
        """9x9 Sudoku board using Canvas."""
        board_container = tk.Frame(parent, bg=C_BG)
        board_container.pack(pady=(0, 8))

        # Outer border with red lines (3px thick)
        outer_frame = tk.Frame(board_container,
                               bg=C_RED,
                               padx=2, pady=2)
        outer_frame.pack()

        self.canvas = tk.Canvas(
            outer_frame,
            width=BOARD_SIZE,
            height=BOARD_SIZE,
            bg=C_BG,
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self._on_cell_click)


    def _build_status(self, parent):
        """Status bar below board."""
        self.status_frame = tk.Frame(parent, bg=C_SURFACE,
                                     highlightbackground=C_BORDER,
                                     highlightthickness=1)
        self.status_frame.pack(fill="x", pady=(0, 8))

        status_inner = tk.Frame(self.status_frame, bg=C_SURFACE, padx=12, pady=6)
        status_inner.pack(fill="x")

        self.status_label = tk.Label(
            status_inner,
            text="Load a puzzle to begin.",
            font=self.font_status,
            bg=C_SURFACE, fg=C_GRAY,
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x")

        # ── Action buttons ─────────────────────────────
        btn_frame = tk.Frame(parent, bg=C_BG)
        btn_frame.pack(fill="x", pady=(0, 5))

        buttons = [
            ("⚡ SOLVE",   BTN_SOLVE, C_RED,     self.solve_puzzle),
            ("💡 HINT",    BTN_HINT,  "#4ade80",  self.give_hint),
            ("✓  CHECK",  BTN_CHECK, "#63b3ed",  self.check_board),
            ("↺  RESET",  BTN_RESET, "#f59e0b",  self.reset_puzzle),
        ]

        for text, bg, fg, cmd in buttons:
            b = tk.Button(
                btn_frame,
                text=text,
                font=self.font_btn,
                bg=bg, fg=fg,
                relief="flat",
                padx=14, pady=7,
                cursor="hand2",
                activebackground=C_SURFACE2,
                activeforeground=fg,
                command=cmd
            )
            b.pack(side="left", padx=3)

        # Keyboard hint
        tk.Label(btn_frame,
                 text="← click cell, type 1-9, Del to erase",
                 font=self.font_small, bg=C_BG, fg=C_LGRAY
                 ).pack(side="right", padx=5)


    def _build_comparison_panel(self, parent):
        """
        RIGHT PANEL — Algorithm time comparison.
        Shows timing for both algorithms on the current puzzle.
        """
        # Title
        title_bar = tk.Frame(parent, bg=C_RED, pady=6)
        title_bar.pack(fill="x")
        tk.Label(title_bar, text="ALGORITHM COMPARISON",
                 font=self.font_label, bg=C_RED, fg=C_WHITE).pack()

        inner = tk.Frame(parent, bg=C_SURFACE, padx=14, pady=10)
        inner.pack(fill="both", expand=True)

        # ── Current puzzle info ────────────────────────
        self.puzzle_info_label = tk.Label(
            inner, text="No puzzle loaded",
            font=self.font_label, bg=C_SURFACE, fg=C_GRAY,
            wraplength=240, justify="left"
        )
        self.puzzle_info_label.pack(anchor="w", pady=(0, 12))

        tk.Frame(inner, bg=C_BORDER, height=1).pack(fill="x", pady=(0, 12))

        # ── Backtracking block ─────────────────────────
        bt_block = tk.Frame(inner, bg=C_SURFACE2,
                            highlightbackground=C_BORDER2,
                            highlightthickness=1)
        bt_block.pack(fill="x", pady=(0, 8))

        bt_top = tk.Frame(bt_block, bg=C_SURFACE2, padx=10, pady=8)
        bt_top.pack(fill="x")

        tk.Label(bt_top, text="BACKTRACKING",
                 font=self.font_label, bg=C_SURFACE2, fg=C_WHITE).pack(anchor="w")

        self.bt_time_label = tk.Label(
            bt_top, text="—",
            font=self.font_time, bg=C_SURFACE2, fg=C_RED
        )
        self.bt_time_label.pack(anchor="w")

        self.bt_desc_label = tk.Label(
            bt_top,
            text="Recursive depth-first search\nwith constraint checking",
            font=self.font_small, bg=C_SURFACE2, fg=C_GRAY,
            justify="left"
        )
        self.bt_desc_label.pack(anchor="w")

        # ── AC-3 block ─────────────────────────────────
        ac3_block = tk.Frame(inner, bg=C_SURFACE2,
                             highlightbackground=C_BORDER2,
                             highlightthickness=1)
        ac3_block.pack(fill="x", pady=(0, 8))

        ac3_top = tk.Frame(ac3_block, bg=C_SURFACE2, padx=10, pady=8)
        ac3_top.pack(fill="x")

        tk.Label(ac3_top, text="AC-3",
                 font=self.font_label, bg=C_SURFACE2, fg=C_WHITE).pack(anchor="w")

        self.ac3_time_label = tk.Label(
            ac3_top, text="—",
            font=self.font_time, bg=C_SURFACE2, fg="#4ade80"
        )
        self.ac3_time_label.pack(anchor="w")

        self.ac3_desc_label = tk.Label(
            ac3_top,
            text="Arc consistency reduction\nthen backtracking fallback",
            font=self.font_small, bg=C_SURFACE2, fg=C_GRAY,
            justify="left"
        )
        self.ac3_desc_label.pack(anchor="w")

        # ── Winner banner ──────────────────────────────
        tk.Frame(inner, bg=C_BORDER, height=1).pack(fill="x", pady=(4, 8))

        self.winner_label = tk.Label(
            inner, text="",
            font=self.font_label, bg=C_SURFACE, fg=C_GRAY,
            wraplength=240, justify="left"
        )
        self.winner_label.pack(anchor="w")

        # ── Speedup display ────────────────────────────
        self.speedup_label = tk.Label(
            inner, text="",
            font=self.font_time_sm, bg=C_SURFACE, fg=C_GRAY,
            wraplength=240, justify="left"
        )
        self.speedup_label.pack(anchor="w")

        tk.Frame(inner, bg=C_BORDER, height=1).pack(fill="x", pady=(8, 8))

        # ── Run both button ────────────────────────────
        run_both_btn = tk.Button(
            inner,
            text="⚡ RUN BOTH & COMPARE",
            font=self.font_btn,
            bg=C_RED, fg=C_WHITE,
            relief="flat", padx=8, pady=6,
            cursor="hand2",
            activebackground=C_RED_DIM,
            activeforeground=C_WHITE,
            command=self.run_both_algorithms
        )
        run_both_btn.pack(fill="x", pady=(0, 8))

        # ── Complexity note ─────────────────────────────
        tk.Label(
            inner,
            text="Backtracking worst case: O(9ⁿ)\nAC-3 reduces search space first.\nBoth guarantee a correct solution.",
            font=self.font_small, bg=C_SURFACE, fg=C_LGRAY,
            justify="left", wraplength=240
        ).pack(anchor="w", pady=(4, 0))


    # ─────────────────────────────────────────────
    #  DRAWING
    # ─────────────────────────────────────────────

    def _draw_board(self):
        """Poora board redraw karo."""
        if self.current_grid is None:
            return

        self.canvas.delete("all")

        # Draw each cell
        for r in range(9):
            for c in range(9):
                self._draw_cell(r, c)

        # Draw grid lines on top
        self._draw_grid_lines()


    def _draw_cell(self, r, c):
        """Single cell draw karo — background + number."""
        x1 = c * CELL_SIZE
        y1 = r * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        cx = x1 + CELL_SIZE // 2
        cy = y1 + CELL_SIZE // 2

        val = self.current_grid[r][c] if self.current_grid else 0

        # ── Determine background ──
        if (r, c) == self.solving_cell:
            bg = CELL_SOLVE_BG
        elif (r, c) == self.selected_cell:
            bg = CELL_SELECT_BG
        elif (r, c) in self.wrong_cells:
            bg = CELL_WRONG_BG
        elif (r, c) in self.hint_cells:
            bg = CELL_HINT_BG
        elif self.original_grid and self.original_grid[r][c] != 0:
            bg = CELL_GIVEN_BG
        elif (r, c) in self.user_cells:
            bg = CELL_USER_BG
        else:
            bg = CELL_EMPTY_BG

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="")

        # ── Determine number color ──
        if val != 0:
            if (r, c) in self.wrong_cells:
                fg = NUM_WRONG
                fnt = self.font_number
            elif (r, c) in self.hint_cells:
                fg = NUM_HINT
                fnt = self.font_number
            elif self.original_grid and self.original_grid[r][c] != 0:
                fg = NUM_GIVEN
                fnt = self.font_given
            else:
                fg = NUM_USER
                fnt = self.font_number

            self.canvas.create_text(
                cx, cy,
                text=str(val),
                font=fnt,
                fill=fg
            )

        # Solving animation: pulsing red border on active cell
        if (r, c) == self.solving_cell:
            self.canvas.create_rectangle(
                x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                outline=C_RED_GLOW, width=2
            )

        # Selected cell: blue border
        if (r, c) == self.selected_cell and (r, c) != self.solving_cell:
            self.canvas.create_rectangle(
                x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                outline="#63b3ed", width=2
            )

        # Hint cell: green border
        if (r, c) in self.hint_cells and val != 0:
            self.canvas.create_rectangle(
                x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                outline=NUM_HINT, width=2
            )

        # Wrong cell: red border
        if (r, c) in self.wrong_cells:
            self.canvas.create_rectangle(
                x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                outline=C_RED, width=2
            )


    def _draw_grid_lines(self):
        """Grid lines — thin within boxes, red thick for box borders."""
        for i in range(10):
            if i % 3 == 0:
                color = LINE_THICK
                width = 3
            else:
                color = LINE_THIN
                width = 1

            # Vertical
            self.canvas.create_line(
                i * CELL_SIZE, 0,
                i * CELL_SIZE, BOARD_SIZE,
                fill=color, width=width
            )
            # Horizontal
            self.canvas.create_line(
                0, i * CELL_SIZE,
                BOARD_SIZE, i * CELL_SIZE,
                fill=color, width=width
            )


    # ─────────────────────────────────────────────
    #  EVENTS
    # ─────────────────────────────────────────────

    def _on_cell_click(self, event):
        """Mouse click — ek cell select karo."""
        if self.current_grid is None or self.is_solving:
            return

        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        if not (0 <= row < 9 and 0 <= col < 9):
            return

        # Only editable cells (original mein 0 tha)
        if self.original_grid[row][col] == 0:
            self.selected_cell = (row, col)
            self.wrong_cells.discard((row, col))
            self._draw_board()
            self.root.focus_set()


    def _on_key_press(self, event):
        """Keyboard press — selected cell mein number type karo."""
        if self.selected_cell is None or self.is_solving:
            return

        row, col = self.selected_cell

        if event.char in "123456789":
            num = int(event.char)
            self.current_grid[row][col] = num
            self.user_cells.add((row, col))
            self.hint_cells.discard((row, col))
            self.wrong_cells.discard((row, col))
            self._draw_board()

        elif event.keysym in ("Delete", "BackSpace"):
            self.current_grid[row][col] = 0
            self.user_cells.discard((row, col))
            self.wrong_cells.discard((row, col))
            self.hint_cells.discard((row, col))
            self._draw_board()

        # Arrow key navigation
        elif event.keysym == "Up" and row > 0:
            self._move_selection(row - 1, col)
        elif event.keysym == "Down" and row < 8:
            self._move_selection(row + 1, col)
        elif event.keysym == "Left" and col > 0:
            self._move_selection(row, col - 1)
        elif event.keysym == "Right" and col < 8:
            self._move_selection(row, col + 1)


    def _move_selection(self, row, col):
        """Arrow key se selection move karo — skip given cells."""
        if self.original_grid and self.original_grid[row][col] == 0:
            self.selected_cell = (row, col)
        else:
            self.selected_cell = (row, col)  # Still select, just can't edit
        self._draw_board()


    # ─────────────────────────────────────────────
    #  MAIN ACTIONS
    # ─────────────────────────────────────────────

    def load_puzzle(self):
        """Selected difficulty aur puzzle load karo."""
        diff  = self.difficulty_var.get()
        p_num = int(self.puzzle_var.get())

        self.current_grid  = get_puzzle(diff, p_num)
        self.original_grid = get_puzzle(diff, p_num)

        # Reset state
        self.selected_cell = None
        self.hint_cells    = set()
        self.user_cells    = set()
        self.wrong_cells   = set()
        self.solving_cell  = None
        self.time_bt       = None
        self.time_ac3      = None

        self._update_status(
            f"Loaded: {diff.capitalize()} — Puzzle #{p_num}  |  Click a cell and type to play",
            C_GRAY
        )

        self.puzzle_info_label.config(
            text=f"Difficulty: {diff.upper()}\nPuzzle: #{p_num}",
            fg=C_WHITE
        )

        self.bt_time_label.config(text="—", fg=C_RED)
        self.ac3_time_label.config(text="—", fg="#4ade80")
        self.winner_label.config(text="")
        self.speedup_label.config(text="")

        self._draw_board()


    def solve_puzzle(self):
        """Selected algorithm se puzzle solve karo."""
        if self.current_grid is None:
            messagebox.showwarning("No Puzzle", "Pehle puzzle load karo!")
            return
        if self.is_solving:
            return

        algo = self.algorithm_var.get()
        self._start_solve_animation(algo)


    def _start_solve_animation(self, algo):
        """Solving animation start karo in background thread."""
        self.is_solving = True
        self._update_status("Solving... ⚡", C_RED)
        self.root.update()

        def solve_thread():
            if algo == "ac3":
                solution, t = ac3(self.original_grid)
                name = "AC-3"
                self.time_ac3 = t
            else:
                solution, t = backtracking(self.original_grid)
                name = "Backtracking"
                self.time_bt = t

            # Schedule UI update on main thread
            self.root.after(0, lambda: self._on_solve_done(solution, t, name))

        thread = threading.Thread(target=solve_thread, daemon=True)
        thread.start()


    def _on_solve_done(self, solution, t, algo_name):
        """Solve ke baad UI update karo."""
        self.is_solving = False
        self.solving_cell = None

        if solution is None:
            self._update_status("✗ No solution found for this puzzle.", C_RED)
            self._draw_board()
            return

        self.current_grid = solution

        # Mark all originally empty cells as user-filled (green would be hint, these are solved)
        for r in range(9):
            for c in range(9):
                if self.original_grid[r][c] == 0:
                    self.user_cells.add((r, c))

        self.hint_cells   = set()
        self.wrong_cells  = set()
        self.selected_cell = None

        t_str = format_time(t)

        # Update comparison panel
        if algo_name == "AC-3":
            self.ac3_time_label.config(text=t_str, fg="#4ade80")
        else:
            self.bt_time_label.config(text=t_str, fg=C_RED)

        self._update_comparison()

        self._update_status(
            f"✓ Solved with {algo_name}  |  Time: {t_str}",
            "#4ade80"
        )
        self._draw_board()


    def give_hint(self):
        """Hint do — ek empty cell ki correct value reveal karo."""
        if self.current_grid is None:
            messagebox.showwarning("No Puzzle", "Pehle puzzle load karo!")
            return
        if self.is_solving:
            return

        result = get_hint(self.current_grid, self.original_grid)

        if result is None:
            self._update_status("Puzzle already complete — no hints needed!", "#4ade80")
            return

        r, c, val = result
        self.current_grid[r][c] = val
        self.hint_cells.add((r, c))
        self.user_cells.discard((r, c))
        self.wrong_cells.discard((r, c))

        self._update_status(
            f"💡 Hint revealed  →  Row {r + 1}, Col {c + 1}  =  {val}",
            NUM_HINT
        )
        self._draw_board()

        # Flash the hint cell 3 times
        self._flash_hint_cell(r, c, 3)


    def _flash_hint_cell(self, r, c, times):
        """Hint cell ko flash karo for attention."""
        if times <= 0:
            self._draw_board()
            return

        # Temporarily highlight solving_cell for flash effect
        self.solving_cell = (r, c)
        self._draw_board()

        def clear_flash():
            self.solving_cell = None
            self._draw_board()
            # Re-flash after short delay
            self.root.after(200, lambda: self._flash_hint_cell(r, c, times - 1))

        self.root.after(200, clear_flash)


    def check_board(self):
        """User ki entries check karo."""
        if self.current_grid is None:
            messagebox.showwarning("No Puzzle", "Pehle puzzle load karo!")
            return

        correct, wrong = is_board_correct(self.current_grid, self.original_grid)
        self.wrong_cells = set(wrong)

        if not wrong:
            empty_count = sum(
                1 for r in range(9) for c in range(9)
                if self.current_grid[r][c] == 0
            )
            if empty_count == 0:
                self._update_status(
                    "🎉 Perfect! Puzzle completely and correctly solved!",
                    NUM_HINT
                )
                messagebox.showinfo("Congratulations! 🎉",
                                    "Masha Allah! Aapne puzzle sahi solve kar liya!")
            else:
                self._update_status(
                    f"✓ All filled cells are correct! {empty_count} cells remaining.",
                    NUM_HINT
                )
        else:
            self._update_status(
                f"✗ {len(wrong)} incorrect cell(s) found — highlighted in red",
                C_RED
            )

        self._draw_board()


    def reset_puzzle(self):
        """Board original state par wapas le jao."""
        if self.original_grid is None:
            return

        self.current_grid  = copy.deepcopy(self.original_grid)
        self.selected_cell = None
        self.hint_cells    = set()
        self.user_cells    = set()
        self.wrong_cells   = set()
        self.solving_cell  = None

        self._update_status("Board reset. Fresh start!", C_GRAY)
        self._draw_board()


    def run_both_algorithms(self):
        """
        Dono algorithms chalao ek ke baad ek aur compare karo.
        Results comparison panel mein display hote hain.
        """
        if self.current_grid is None:
            messagebox.showwarning("No Puzzle", "Pehle puzzle load karo!")
            return
        if self.is_solving:
            return

        self.is_solving = True
        self._update_status("Running both algorithms for comparison...", C_RED)
        self.bt_time_label.config(text="Running...", fg=C_GRAY)
        self.ac3_time_label.config(text="Waiting...", fg=C_GRAY)
        self.winner_label.config(text="")
        self.speedup_label.config(text="")
        self.root.update()

        def run_thread():
            # Run backtracking
            _, t_bt = backtracking(self.original_grid)
            self.time_bt = t_bt
            self.root.after(0, lambda: self.bt_time_label.config(
                text=format_time(t_bt), fg=C_RED))
            self.root.after(0, lambda: self.ac3_time_label.config(
                text="Running...", fg=C_GRAY))

            # Run AC-3
            sol_ac3, t_ac3 = ac3(self.original_grid)
            self.time_ac3 = t_ac3

            self.root.after(0, lambda: self._on_both_done(sol_ac3, t_bt, t_ac3))

        thread = threading.Thread(target=run_thread, daemon=True)
        thread.start()


    def _on_both_done(self, sol_ac3, t_bt, t_ac3):
        """Dono algorithms complete hone ke baad UI update karo."""
        self.is_solving = False

        self.bt_time_label.config(text=format_time(t_bt), fg=C_RED)
        self.ac3_time_label.config(text=format_time(t_ac3), fg="#4ade80")

        self._update_comparison()

        self._update_status(
            f"Comparison done  |  BT: {format_time(t_bt)}  |  AC-3: {format_time(t_ac3)}",
            C_WHITE
        )

        # Show the AC-3 solution on board
        if sol_ac3:
            self.current_grid = sol_ac3
            for r in range(9):
                for c in range(9):
                    if self.original_grid[r][c] == 0:
                        self.user_cells.add((r, c))
            self.hint_cells  = set()
            self.wrong_cells = set()
            self._draw_board()


    def _update_comparison(self):
        """Comparison panel update karo — winner, speedup."""
        if self.time_bt is None or self.time_ac3 is None:
            return

        self.bt_time_label.config(text=format_time(self.time_bt), fg=C_RED)
        self.ac3_time_label.config(text=format_time(self.time_ac3), fg="#4ade80")

        if self.time_bt < self.time_ac3:
            faster = "BACKTRACKING"
            diff   = self.time_ac3 / self.time_bt if self.time_bt > 0 else 1
            self.winner_label.config(
                text=f"🏆 FASTER: {faster}",
                fg=C_RED
            )
        elif self.time_ac3 < self.time_bt:
            faster = "AC-3"
            diff   = self.time_bt / self.time_ac3 if self.time_ac3 > 0 else 1
            self.winner_label.config(
                text=f"🏆 FASTER: {faster}",
                fg="#4ade80"
            )
        else:
            diff = 1.0
            self.winner_label.config(text="⚖️ Both took equal time", fg=C_GRAY)

        if diff > 1.01:
            self.speedup_label.config(
                text=f"Speed difference: {diff:.2f}×",
                fg=C_GRAY
            )


    def _update_status(self, msg, color):
        """Status bar update karo."""
        self.status_label.config(text=msg, fg=color)