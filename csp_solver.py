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
