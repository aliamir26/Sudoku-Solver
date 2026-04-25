# 🧩 Sudoku CSP Solver
---

> *"The puzzle is not just in the grid — it is in the algorithm that dares to solve it."*

A Python-based Sudoku solver implementing two classic **Constraint Satisfaction Problem (CSP)** algorithms — **Arc-Consistency 3 (AC-3)** and **Backtracking Search** — wrapped in a professional **Tkinter GUI** with a dark theme, hint assistance system, difficulty selection, and real-time performance timing.

---

## 📸 Screenshots

> **Note to Student:** After running the app, take screenshots and save them in a `/screenshots` folder. Then replace the placeholder text below with actual image links like `![Board](screenshots/main_board.png)`.

| Main Board | Solving in Progress | Hint System |
|:---:|:---:|:---:|
| `[ screenshot: main_board.png ]` | `[ screenshot: solving.png ]` | `[ screenshot: hint.png ]` |
| *Default view on launch* | *Algorithm solving live* | *Hint cell glowing green* |

| Difficulty Selection | Time Display | Wrong Cell Check |
|:---:|:---:|:---:|
| `[ screenshot: difficulty.png ]` | `[ screenshot: timer.png ]` | `[ screenshot: wrong_cells.png ]` |
| *Easy / Medium / Hard radio buttons* | *Solve time to 6 decimal places* | *Red cells on wrong entries* |

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Two CSP Algorithms** | Solve with AC-3 or Backtracking — you pick the weapon |
| 🎚️ **3 Difficulty Levels** | Easy, Medium, and Hard puzzles with distinct challenge |
| 🗂️ **4 Puzzles Per Level** | 12 unique puzzles total from the provided dataset |
| 💡 **Hint System** | Reveals one correct cell at a time, highlighted in green |
| ⏱️ **Solve Time Display** | Exact algorithm runtime shown to 6 decimal places |
| ✅ **Input Validation** | Check your manual entries — wrong cells turn red instantly |
| ↺ **Reset Board** | Restore original puzzle state in one click |
| ✏️ **Manual Play Mode** | Click any empty cell, type your answer — play it yourself |
| 🎨 **Dark Theme GUI** | Professional high-contrast dark interface built with Tkinter |
| 🖱️ **Click-to-Select Cells** | Natural interaction — click, type, delete |

---

## 🧠 Algorithms — Explained Simply

### 1. Backtracking Search

Think of backtracking like walking through a maze. You move forward confidently, and the moment you hit a dead end, you step back and try a different path. Simple. Honest. Reliable.

```
For each empty cell:
    Try numbers 1 through 9
    If the number causes no conflict in its row, column, or 3x3 box:
        Place it and move to the next empty cell
    If no number from 1-9 works here:
        Undo the last placement and try the next value there
    Repeat until all 81 cells are filled correctly
```

**Advantages of Backtracking:**
- Guaranteed to find a solution if one exists
- Works on any valid Sudoku puzzle regardless of difficulty
- Straightforward to understand — classic recursive logic
- Low memory usage

**Disadvantages:**
- Can be slow on very hard puzzles — lots of wrong guesses
- Worst case time complexity: **O(9^n)** where n is the number of empty cells
- Does not use any intelligence to reduce possibilities first

---

### 2. AC-3 (Arc-Consistency 3)

Think of AC-3 like a detective eliminating suspects before making an arrest. Before guessing a single number, it scans all relationships between cells and crosses off values that are provably impossible. By the time it starts filling cells, most of the work is already done.

```
An Arc = a relationship between two peer cells (Xi, Xj)
         meaning: Xi and Xj cannot have the same value

Queue all arcs (every cell paired with every one of its peers)

While the queue is not empty:
    Take an arc (Xi, Xj) from the queue
    For each value x in Xi's possible values:
        If no value in Xj's possible values is different from x:
            Remove x from Xi's possible values (it's impossible)
    If any value was removed from Xi:
        If Xi now has zero possible values: FAILURE — no solution
        Add all of Xi's other neighbors back to the queue to re-check
```

**Advantages of AC-3:**
- Reduces domains (possible values) before any guessing begins
- Often solves Easy puzzles completely without a single guess
- Propagates constraints like dominoes — one removal triggers others
- Significantly faster than pure backtracking on simpler puzzles

**Disadvantages:**
- Cannot always fully solve Hard puzzles alone
- Falls back to backtracking when no more reductions are possible
- Slightly more memory usage (stores domains for all 81 cells)

---

### ⚖️ Algorithm Comparison Table

| Property | Backtracking | AC-3 + Backtracking |
|---|---|---|
| Core Strategy | Recursive trial and error | Constraint propagation first, then trial |
| Speed on Easy Puzzles | Fast | Very Fast |
| Speed on Hard Puzzles | Slower | Comparable or better |
| Solves Without Guessing | ❌ Never | ✅ Often (on easy/medium) |
| Guaranteed Solution | ✅ Yes | ✅ Yes |
| Memory Usage | Low | Slightly Higher |
| Complexity Class | O(9^n) | Better in practice |
| Best For | Reliable solving | Demonstrating CSP intelligence |

---

## 🗂️ Project Structure

```
sudoku-solver
│
├── main.py              ← Entry point — run this to launch the app
├── datasets.py          ← All 12 Sudoku puzzles (Easy/Medium/Hard x 4)
├── csp_solver.py        ← AC-3 and Backtracking algorithm implementations
├── hint.py              ← Hint Assistance System logic
├── gui.py               ← Complete Tkinter GUI (visuals, events, interactions)
│
├── README.md            ← This file — project documentation
├── requirements.txt     ← Python dependency list
│
└── screenshots/         ← Add your app screenshots here
    ├── main_board.png
    ├── solving.png
    └── hint.png
```

---

## 📦 Module Responsibilities (What Each File Does)

### `main.py` — The Launcher
**Purpose:** Single entry point for the entire application.
- Creates the Tkinter root window
- Calculates screen dimensions and centers the window automatically
- Instantiates `SudokuApp` from `gui.py` and hands it control
- Calls `root.mainloop()` to keep the window alive
- **You only ever run this file.** Everything else is imported by it.

---

### `datasets.py` — The Data Store
**Purpose:** Holds all puzzle data cleanly separated from logic.
- Contains three lists: `EASY_PUZZLES`, `MEDIUM_PUZZLES`, `HARD_PUZZLES`
- Each puzzle is a 9×9 Python list where `0` represents an empty cell
- Exposes one public function: `get_puzzle(difficulty, puzzle_number)`
- Uses `copy.deepcopy()` internally so the original puzzle data is **never** accidentally mutated
- Difficulty is a string (`"easy"`, `"medium"`, `"hard"`), puzzle number is 1 to 4

---

### `csp_solver.py` — The Brain
**Purpose:** Contains the two core AI algorithms.
- `backtracking(grid)` — recursive solver using validity checks and depth-first search
- `ac3(grid)` — arc consistency reducer; falls back to backtracking if needed
- Helper functions: `get_peers(r, c)`, `build_domains(grid)`, `is_valid(grid, r, c, num)`, `find_empty(grid)`
- Both public functions return a tuple: `(solved_grid, time_taken_in_seconds)`
- **Can be run standalone** (`python csp_solver.py`) to test both algorithms on a sample puzzle

---

### `hint.py` — The Guide
**Purpose:** Powers the hint button — one correct answer at a time.
- `get_hint(current_grid, original_grid)` — finds the first empty cell and returns its solution value
- `is_board_correct(current_grid, original_grid)` — checks all user-filled cells against the real solution
- Internally calls `backtracking()` on the original grid to compute the reference solution
- Returns `(row, col, correct_value)` tuple, or `None` if the board is already complete
- Returns `(True, [])` or `(False, [list of wrong (row, col) pairs])` for the check function

---

### `gui.py` — The Face
**Purpose:** Everything the user sees and interacts with.
- Builds all Tkinter widgets: title bar, control panel, canvas board, info panel, action buttons
- Manages complete application state: current grid, original grid, selected cell, hint cells, wrong cells, user cells
- Handles mouse click events (cell selection) and keyboard events (number entry, delete/backspace)
- Calls `ac3()` or `backtracking()` from `csp_solver.py` when Solve is clicked
- Calls `get_hint()` from `hint.py` when Hint is clicked
- Redraws the entire board canvas after every single interaction

---

## 🎮 UI Icons and Elements — Complete Guide 
### Buttons
 
| Button | Color | Action |
|---|---|---|
| `⚡ SOLVE` | Red | Solves the puzzle with the selected algorithm |
| `💡 HINT` | Green | Reveals one correct value in an empty cell |
| `✓ CHECK` | Blue | Validates all manually entered numbers |
| `↺ RESET` | Amber | Clears entries and restores the original puzzle |
| `LOAD PUZZLE` | Red | Loads the puzzle chosen by the controls above |
| `⚡ RUN BOTH & COMPARE` | Red (right panel) | Runs both algorithms and fills the comparison panel |
 
### Cell Colors
 
| Cell Appearance | Meaning |
|---|---|
| Dark background, white number | Given cell — provided by the puzzle, cannot be edited |
| Slightly lighter background, blue number | Number you typed manually |
| Dark green background, bright green number + green border | Hint cell — correct value just revealed |
| Dark red background, red number + red border | Wrong cell — your entry does not match the solution |
| Dark blue background + blue border | Currently selected cell — type here |
| Dark red background + glowing red border | Cell being animated during solve or hint flash |
 
### Grid Lines
 
| Line | Appearance | Meaning |
|---|---|---|
| Thick red lines | Bold, appear every 3 cells | Boundaries of the nine 3×3 boxes |
| Thin dark lines | Subtle, between individual cells | Cell dividers within each box |
| Outer red border | 2px frame around the entire board | Board boundary |
 
### Comparison Panel Elements
 
| Element | Meaning |
|---|---|
| `—` in time field | Algorithm has not been run yet this session |
| Red time value (Backtracking card) | Time taken by Backtracking on the current puzzle |
| Green time value (AC-3 card) | Time taken by AC-3 on the current puzzle |
| `🏆 FASTER: [name]` | Which algorithm finished first |
| `Speed difference: 2.4×` | How many times faster the winner was |
 
### Time Format
 
The solver uses `time.perf_counter()` for high-precision measurement and auto-formats the result:
 
| Duration | Format shown | Example |
|---|---|---|
| Under 1 millisecond | Microseconds | `445.0 μs` |
| Under 1 second | Milliseconds | `31.911 ms` |
| 1 second or more | Seconds | `4.9045 s` |
 
### Status Bar
 
The bar below the board updates after every action. Examples of what it shows:
 
- `Loaded: Easy — Puzzle #1 | Click a cell and type to play`
- `💡 Hint revealed → Row 3, Col 5 = 7`
- `✓ Solved with Backtracking | Time: 2.341 ms`
- `✗ 2 incorrect cell(s) found — highlighted in red`
- `Comparison done | BT: 6.472 ms | AC-3: 55.111 ms`

---

## 🚀 How to Run

### Step 1 — Make Sure Python Is Installed

```bash
python --version
```

You need **Python 3.8 or above**. Download from https://python.org if needed.

### Step 2 — Verify Tkinter Is Available

```bash
python -c "import tkinter; print('Tkinter is ready!')"
```

If you see `Tkinter is ready!` — perfect. If not, reinstall Python and make sure to check the "tcl/tk" option during installation.

### Step 3 — Clone or Download the Project

**If using Git or GitHub Desktop:**
```bash
git clone https://github.com/aliamir26/sudoku-solver.git
cd sudoku-solver
```

**Or download the ZIP** from GitHub and extract it.

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

> This project uses only Python's standard library. No external packages are required. The requirements file is included for completeness.

### Step 5 — Run the Application

```bash
python main.py
```

The Sudoku board window will open, centered on your screen.

### Step 6 — (Optional) Test Algorithms Standalone

```bash
python csp_solver.py
```

This runs both algorithms on a test puzzle and prints the solution and time to the terminal.

---

## 🕹️ How to Use — Step by Step

1. Select a **difficulty** — Easy, Medium, or Hard
2. Select a **puzzle number** — 1 through 4
3. Select an **algorithm** — Backtracking or AC-3
4. Click **LOAD PUZZLE** — the board populates with the given numbers
5. **To auto-solve:** click `⚡ SOLVE` — the board fills and the time appears in the status bar and comparison panel
6. **To play manually:** click any empty cell (it highlights with a blue border), then type a digit 1–9; use arrow keys to move between cells; press Delete or Backspace to clear
7. **Need a nudge:** click `💡 HINT` — one correct cell fills in green and flashes three times
8. **Validate:** click `✓ CHECK` — wrong cells turn red, correct ones are unchanged
9. **Start fresh:** click `↺ RESET` — all your entries are cleared and the original puzzle is restored
10. **Compare both algorithms:** click `⚡ RUN BOTH & COMPARE` in the right panel — both run sequentially, times appear in their respective cards, and the winner is announced


---

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.8+ | Core programming language |
| Tkinter | Built-in | GUI framework |
| `collections.deque` | Built-in | Efficient queue for AC-3 arc processing |
| `copy.deepcopy` | Built-in | Safe immutable puzzle state management |
| `time` module | Built-in | High-precision algorithm runtime measurement |

---

## 📚 References

1. Stuart Russell and Peter Norvig. *Artificial Intelligence: A Modern Approach*, 4th edition. Pearson, 2022.
2. AIMA Python Code Repository: https://github.com/aimacode/aima-python
3. Wei-Meng Lee, *Programming Sudoku*: https://www.apress.com/9781590596623
4. Graphical User Interfaces with Tkinter: http://newcoder.io/gui/
5. Sudoku puzzle dataset sourced from: https://sudokutodo.com

---

## 👤 Author
| | |
|---|---|
| **Name** | *(Ali Amir)* |
| **Contact** | *(maliamir089@gmail.com)* |
| **Institution** | NUCES Faisalabad–Chiniot Campus |


---

*Built with patience, Python, and a healthy respect for constraint propagation.*