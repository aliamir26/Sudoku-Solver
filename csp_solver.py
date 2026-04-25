# csp_solver.py
"""
==============================================================
  csp_solver.py — AC-3 aur Backtracking Algorithms
  Yeh file Sudoku ko solve karti hai do tareeqon se:
  1. AC-3 (Arc Consistency 3) — domain reduction + backtracking fallback
  2. Backtracking Search — recursive trial and error
  Dono ka time bhi measure hota hai yahan
  FIX: AC-3 ab properly kaam karta hai with full backtracking fallback
==============================================================
"""

import copy
import time
from collections import deque


# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────

def get_peers(row, col):
    """
    Ek cell ke saare peers return karo.
    Peers = same row + same col + same 3x3 box wale cells.
    """
    peers = set()

    # Same row
    for c in range(9):
        if c != col:
            peers.add((row, c))

    # Same column
    for r in range(9):
        if r != row:
            peers.add((r, col))

    # Same 3x3 box
    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if (r, c) != (row, col):
                peers.add((r, c))

    return peers


# Pre-compute all peers for efficiency
ALL_PEERS = {(r, c): get_peers(r, c) for r in range(9) for c in range(9)}


def build_domains(grid):
    """
    Har cell ka starting domain banao.
    Filled cell ka domain = {us value}.
    Empty cell (0) ka domain = {1..9} minus jo values peers mein hain.
    """
    domains = {}
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                domains[(r, c)] = {grid[r][c]}
            else:
                # Start with all values, remove those already used by peers
                used = set()
                for (pr, pc) in ALL_PEERS[(r, c)]:
                    if grid[pr][pc] != 0:
                        used.add(grid[pr][pc])
                domains[(r, c)] = set(range(1, 10)) - used
    return domains


def is_valid(grid, row, col, num):
    """
    Check karo ke num ko (row, col) mein rakh sakte hain ya nahi.
    Row, col, aur 3x3 box check karta hai.
    """
    # Row check
    for c in range(9):
        if grid[row][c] == num:
            return False

    # Column check
    for r in range(9):
        if grid[r][col] == num:
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
    MRV heuristic — sabse kam options wali empty cell dhundo.
    Yeh backtracking ko faster banata hai.
    """
    min_options = 10
    best_cell = None

    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                # Count how many valid numbers can go here
                count = 0
                for num in range(1, 10):
                    if is_valid(grid, r, c, num):
                        count += 1
                if count < min_options:
                    min_options = count
                    best_cell = (r, c)
                    if count == 1:
                        return best_cell  # Can't do better than 1

    return best_cell


def grid_is_complete(grid):
    """Check karo ke koi empty cell bacha hai ya nahi."""
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return False
    return True


# ─────────────────────────────────────────────
#  BACKTRACKING ALGORITHM
# ─────────────────────────────────────────────

def _backtrack(grid):
    """
    Internal recursive backtracking.
    MRV heuristic use karta hai next cell select karne ke liye.
    """
    # Koi empty cell nahi = puzzle solved!
    empty = find_empty(grid)
    if empty is None:
        return grid

    row, col = empty

    # 1-9 mein se har value try karo
    for num in range(1, 10):
        if is_valid(grid, row, col, num):
            grid[row][col] = num

            result = _backtrack(grid)

            if result is not None:
                return result

            grid[row][col] = 0  # Backtrack

    return None  # Koi solution nahi mila is path se


def backtracking(grid):
    """
    Public Backtracking function.
    Returns: (solved_grid, time_taken_seconds)
    """
    start_time = time.perf_counter()

    grid_copy = copy.deepcopy(grid)
    result = _backtrack(grid_copy)

    end_time = time.perf_counter()
    time_taken = end_time - start_time

    return result, time_taken


# ─────────────────────────────────────────────
#  AC-3 ALGORITHM
# ─────────────────────────────────────────────

def _revise(domains, xi, xj):
    """
    REVISE — Xi ka domain revise karo Xj ke according.
    Agar Xi ki koi value x ke liye Xj mein koi different value y nahi:
    toh x ko Xi ke domain se hatao.
    Returns True agar domain change hua.
    """
    revised = False

    for x in set(domains[xi]):  # copy taake iteration safe ho
        # Sudoku constraint: xi != xj
        # Agar Xj ka domain sirf {x} hai, toh x Xi ke liye invalid hai
        if domains[xj] == {x}:
            domains[xi].discard(x)
            revised = True

    return revised


def _ac3_reduce(domains):
    """
    Pure AC-3 reduction.
    Returns True agar consistent, False agar koi domain empty ho gaya.
    """
    # Saare arcs queue mein daalo
    queue = deque()
    for r in range(9):
        for c in range(9):
            for (pr, pc) in ALL_PEERS[(r, c)]:
                queue.append(((r, c), (pr, pc)))

    while queue:
        (xi, xj) = queue.popleft()

        if _revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False  # Inconsistency!

            # Xi ke saare neighbors ko re-check karo (Xj chod ke)
            for neighbor in ALL_PEERS[xi[0], xi[1]]:
                if neighbor != xj:
                    queue.append((neighbor, xi))

    return True


def _domains_to_grid(domains, original_grid):
    """
    Domains se grid banao.
    Sirf woh cells fill karo jinka domain size = 1.
    """
    grid = copy.deepcopy(original_grid)
    for r in range(9):
        for c in range(9):
            if len(domains[(r, c)]) == 1:
                grid[r][c] = list(domains[(r, c)])[0]
    return grid


def _ac3_backtrack(grid, domains):
    """
    AC-3 ke baad remaining cells ke liye backtracking.
    Domain-aware hai — sirf valid values try karta hai.
    """
    # Sabse pehle empty cell dhundo (MRV: min remaining values)
    min_len = 10
    empty = None
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                d_len = len(domains[(r, c)])
                if d_len < min_len:
                    min_len = d_len
                    empty = (r, c)
                    if d_len == 1:
                        break

    if empty is None:
        return grid  # Solved!

    row, col = empty

    # Domain ki values try karo
    for num in sorted(domains[(row, col)]):
        if is_valid(grid, row, col, num):
            grid[row][col] = num

            # Domains ka backup banao aur update karo
            new_domains = copy.deepcopy(domains)
            new_domains[(row, col)] = {num}

            # Neighbors ke domains update karo
            consistent = True
            for (nr, nc) in ALL_PEERS[(row, col)]:
                new_domains[(nr, nc)].discard(num)
                if len(new_domains[(nr, nc)]) == 0 and grid[nr][nc] == 0:
                    consistent = False
                    break

            if consistent:
                result = _ac3_backtrack(grid, new_domains)
                if result is not None:
                    return result

            grid[row][col] = 0  # Backtrack

    return None


def ac3(grid):
    """
    Public AC-3 function.
    Step 1: Domain reduction via arc consistency.
    Step 2: Backtracking on remaining empty cells using reduced domains.
    Returns: (solved_grid, time_taken_seconds)
    """
    start_time = time.perf_counter()

    grid_copy = copy.deepcopy(grid)

    # Build initial domains
    domains = build_domains(grid_copy)

    # Run AC-3 reduction
    if not _ac3_reduce(domains):
        end_time = time.perf_counter()
        return None, end_time - start_time

    # Domains se grid update karo
    for r in range(9):
        for c in range(9):
            if len(domains[(r, c)]) == 1:
                grid_copy[r][c] = list(domains[(r, c)])[0]

    # Check karo ke already solved hua ya nahi
    if grid_is_complete(grid_copy):
        end_time = time.perf_counter()
        return grid_copy, end_time - start_time

    # Agar abhi bhi empty cells hain: backtrack karo domain knowledge ke saath
    result = _ac3_backtrack(grid_copy, domains)

    end_time = time.perf_counter()
    time_taken = end_time - start_time

    return result, time_taken


# ─────────────────────────────────────────────
#  TIME FORMATTING UTILITY
# ─────────────────────────────────────────────

def format_time(seconds):
    """
    Time ko human-readable format mein convert karo.
    seconds → microseconds, milliseconds, ya seconds display karo.
    """
    if seconds < 0.001:
        # Microseconds
        return f"{seconds * 1_000_000:.1f} μs"
    elif seconds < 1.0:
        # Milliseconds
        return f"{seconds * 1000:.3f} ms"
    else:
        # Seconds
        return f"{seconds:.4f} s"


# ─────────────────────────────────────────────
#  QUICK TEST — python csp_solver.py chalao
# ─────────────────────────────────────────────

if __name__ == "__main__":
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

    print("=" * 50)
    print("BACKTRACKING TEST")
    print("=" * 50)
    sol, t = backtracking(test_grid)
    if sol:
        for row in sol:
            print(row)
        print(f"Time: {format_time(t)}")
    else:
        print("No solution found!")

    print()
    print("=" * 50)
    print("AC-3 TEST")
    print("=" * 50)
    sol2, t2 = ac3(test_grid)
    if sol2:
        for row in sol2:
            print(row)
        print(f"Time: {format_time(t2)}")
    else:
        print("No solution found!")