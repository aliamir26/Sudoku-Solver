# hint.py
"""
==============================================================
  hint.py — Hint Assistance System
  Yeh file user ko ek correct value suggest karti hai.
  Jab user Hint button dabata hai, ek empty cell fill hoti hai.
  Solution backtracking se milta hai aur compare hota hai.
==============================================================
"""

from csp_solver import backtracking


def get_hint(current_grid, original_grid):
    """
    Ek hint return karo — pehli empty cell ki correct value.
    current_grid: jo abhi board par hai (user entries bhi)
    original_grid: original puzzle (unmodified)
    Returns: (row, col, correct_value) ya None agar board complete hai
    """
    # Solution nikalo original puzzle se
    solution, _ = backtracking(original_grid)

    if solution is None:
        return None

    # Pehli empty cell dhundo aur uski correct value return karo
    for r in range(9):
        for c in range(9):
            if current_grid[r][c] == 0:
                return (r, c, solution[r][c])

    return None  # Koi empty cell nahi = already complete


def is_board_correct(current_grid, original_grid):
    """
    User ki filled values check karo solution ke against.
    Sirf woh cells check hoti hain jo original mein empty theen.
    Returns: (all_correct: bool, wrong_cells: list of (r,c))
    """
    solution, _ = backtracking(original_grid)

    if solution is None:
        return False, []

    wrong_cells = []
    for r in range(9):
        for c in range(9):
            # Sirf user-filled cells check karo
            if original_grid[r][c] == 0 and current_grid[r][c] != 0:
                if current_grid[r][c] != solution[r][c]:
                    wrong_cells.append((r, c))

    return (len(wrong_cells) == 0), wrong_cells