# hint.py
"""
==============================================================
  hint.py — Hint Assistance System
  Yeh file user ko ek correct value suggest karti hai
  Jab user "Hint" button dabata hai
  Solution backtracking se milta hai, phir compare hota hai
==============================================================
"""

from csp_solver import backtracking


def get_hint(current_grid, original_grid):
    """
    Ek hint return karo — ek empty cell ki correct value.
    current_grid: jo abhi board par dikh raha hai (user ne kuch fill kiya hoga)
    original_grid: original puzzle (jo pehle load hua tha)
    Returns: (row, col, correct_value) ya None agar koi hint nahi
    """

    # Pehle solution nikalo original puzzle se
    solution, _ = backtracking(original_grid)

    if solution is None:
        # Puzzle solvable hi nahi — edge case
        return None

    # Current grid mein empty cells dhundo
    # Aur pehli empty cell ka correct value solution se lo
    for r in range(9):
        for c in range(9):
            if current_grid[r][c] == 0:
                correct_value = solution[r][c]
                return (r, c, correct_value)

    # Koi empty cell nahi = puzzle already complete
    return None


def is_board_correct(current_grid, original_grid):
    """
    Check karo ke user ne jo values fill ki hain woh sahi hain ya nahi.
    Returns: (bool, list of wrong cells)
    Agar sab sahi: (True, [])
    Agar galat: (False, [(r,c), ...])
    """
    solution, _ = backtracking(original_grid)

    if solution is None:
        return False, []

    wrong_cells = []
    for r in range(9):
        for c in range(9):
            # Sirf user-filled cells check karo (original mein 0 tha)
            if original_grid[r][c] == 0 and current_grid[r][c] != 0:
                if current_grid[r][c] != solution[r][c]:
                    wrong_cells.append((r, c))

    if wrong_cells:
        return False, wrong_cells
    return True, []