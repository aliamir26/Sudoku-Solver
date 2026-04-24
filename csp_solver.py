# csp_solver.py
"""
==============================================================
  csp_solver.py — AC-3 aur Backtracking Algorithms
  Yeh file Sudoku ko solve karti hai do tareeqon se:
  1. AC-3 (Arc Consistency 3) — domain reduction
  2. Backtracking Search — recursive trial and error
  Dono ka time bhi measure hota hai yahan
==============================================================
"""

import copy
import time
from collections import deque


# ─────────────────────────────────────────────
#  HELPER FUNCTIONS — dono algorithms use karte hain
# ─────────────────────────────────────────────

def get_peers(row, col):
    """
    Ek cell ke saare peers return karo.
    Peers = same row + same col + same 3x3 box wale cells.
    """
    peers = set()

    # Same row ke saare cells
    for c in range(9):
        if c != col:
            peers.add((row, c))

    # Same column ke saare cells
    for r in range(9):
        if r != row:
            peers.add((r, col))

    # Same 3x3 box ke saare cells
    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if (r, c) != (row, col):
                peers.add((r, c))

    return peers


def build_domains(grid):
    """
    Har cell ka domain banao.
    Agar cell filled hai: domain = {us value}
    Agar empty hai (0): domain = {1,2,3,4,5,6,7,8,9}
    """
    domains = {}
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                domains[(r, c)] = {grid[r][c]}
            else:
                domains[(r, c)] = set(range(1, 10))
    return domains


def is_valid(grid, row, col, num):
    """
    Check karo ke num ko (row, col) mein rakh sakte hain ya nahi.
    Backtracking ke liye use hota hai.
    """
    # Row check
    if num in grid[row]:
        return False

    # Column check
    if num in [grid[r][col] for r in range(9)]:
        return False

    # 3x3 box check
    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if grid[r][c] == num:
                return False

    return True


def find_empty(grid):
    """
    Pehli empty cell (value=0) dhundo aur return karo.
    Agar koi empty nahi: None return karo (puzzle solved!).
    """
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return (r, c)
    return None


# ─────────────────────────────────────────────
#  AC-3 ALGORITHM
# ─────────────────────────────────────────────

def revise(domains, xi, xj):
    """
    REVISE function — AIMA book se liya gaya.
    Xi ka domain revise karo Xj ke against.
    Agar koi value x in Di ke liye koi valid y Di mein nahi:
    toh x ko Di se hata do.
    Returns True agar domain change hua.
    """
    revised = False

    # Xi ke domain ki har value check karo
    for x in set(domains[xi]):
        # Kya Xj mein koi y hai jo x se alag ho?
        # Sudoku constraint: xi != xj
        if domains[xj] == {x}:
            # Sirf ek value hai Xj mein aur woh x ke barabar hai
            # Toh x Xi ke liye invalid hai
            domains[xi].discard(x)
            revised = True

    return revised


def ac3(grid):
    """
    AC-3 Algorithm — AIMA book se liya gaya.
    Saare arcs ko queue mein daalo aur process karo.
    Returns: (solved_grid or None, time_taken)
    """
    start_time = time.time()

    # Deep copy taake original grid safe rahe
    grid = copy.deepcopy(grid)

    # Domains banao
    domains = build_domains(grid)

    # Queue mein saare arcs daalo (Xi, Xj) jahan Xi aur Xj peers hain
    queue = deque()
    for r in range(9):
        for c in range(9):
            for (pr, pc) in get_peers(r, c):
                queue.append(((r, c), (pr, pc)))

    # AC-3 main loop
    while queue:
        (xi, xj) = queue.popleft()

        if revise(domains, xi, xj):
            # Agar domain empty ho gaya: inconsistency!
            if len(domains[xi]) == 0:
                end_time = time.time()
                return None, round(end_time - start_time, 6)

            # Xi ke saare neighbors ko dobara queue mein daalo (Xj ko chod ke)
            for neighbor in get_peers(xi[0], xi[1]):
                if neighbor != xj:
                    queue.append((neighbor, xi))

    # Domains se grid banao
    result_grid = [[0] * 9 for _ in range(9)]
    for r in range(9):
        for c in range(9):
            if len(domains[(r, c)]) == 1:
                result_grid[r][c] = list(domains[(r, c)])[0]
            else:
                # AC-3 akela solve nahi kar saka
                # Backtracking se complete karo
                result_grid[r][c] = grid[r][c]

    # Agar abhi bhi empty cells hain toh backtracking se finish karo
    if any(result_grid[r][c] == 0 for r in range(9) for c in range(9)):
        result_grid = _backtrack(result_grid)

    end_time = time.time()
    time_taken = round(end_time - start_time, 6)

    if result_grid:
        return result_grid, time_taken
    return None, time_taken


# ─────────────────────────────────────────────
#  BACKTRACKING ALGORITHM
# ─────────────────────────────────────────────

def _backtrack(grid):
    """
    Internal recursive backtracking function.
    AIMA BACKTRACK function ka Python version.
    """
    # Base case: koi empty cell nahi = solution mil gaya
    empty = find_empty(grid)
    if empty is None:
        return grid

    row, col = empty

    # 1 se 9 tak har value try karo
    for num in range(1, 10):
        if is_valid(grid, row, col, num):
            grid[row][col] = num  # Value assign karo

            result = _backtrack(grid)  # Recursion

            if result is not None:
                return result  # Solution mil gaya!

            grid[row][col] = 0  # Backtrack — galat tha

    return None  # Koi solution nahi mila is path mein


def backtracking(grid):
    """
    Public Backtracking function — GUI yahi call karegi.
    Returns: (solved_grid or None, time_taken)
    """
    start_time = time.time()

    grid_copy = copy.deepcopy(grid)
    result = _backtrack(grid_copy)

    end_time = time.time()
    time_taken = round(end_time - start_time, 6)

    return result, time_taken


# ─────────────────────────────────────────────
#  QUICK TEST — direct run karo check ke liye
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Simple test puzzle
    test_grid = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    print("Testing Backtracking...")
    sol, t = backtracking(test_grid)
    print(f"Solved in {t} seconds")
    for row in sol:
        print(row)

    print("\nTesting AC-3...")
    sol2, t2 = ac3(test_grid)
    print(f"Solved in {t2} seconds")
    for row in sol2:
        print(row)