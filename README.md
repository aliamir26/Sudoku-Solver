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

> **How to take screenshots on Windows:** Press `Win + Shift + S`, draw around the app window, and save the image as PNG into your `/screenshots` folder.

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
sudoku-csp-al2002/
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

| Element | Appearance | What It Means |
|---|---|---|
| `⚡ SOLVE` button | Purple button | Auto-solve the puzzle using the selected algorithm |
| `💡 HINT` button | Green button | Reveal one correct value in one empty cell |
| `✓ CHECK` button | Blue button | Validate all your manually entered numbers |
| `↺ RESET` button | Red button | Clear your entries and restore the original puzzle |
| `LOAD PUZZLE` button | Light purple button | Load the puzzle selected by difficulty and number |
| **Purple highlighted cell** | Solid purple background | Currently selected cell — type your number here |
| **Dark blue cell** | Dark background, white number | Pre-filled cell from the puzzle — cannot be edited |
| **Slightly lighter cell** | Lighter background, blue number | Cell you filled in manually |
| **Green cell** | Green background, green number | Hint cell — correct value revealed by the hint system |
| **Red cell** | Red background, red number | Wrong cell — your entry does not match the solution |
| **Thick purple grid lines** | Bold purple borders | Boundaries of the nine 3×3 boxes |
| **Thin gray grid lines** | Subtle gray dividers | Individual cell borders within each box |
| **`SOLVE TIME: —`** | Dash in the info panel | No solve has been run yet in this session |
| **`SOLVE TIME: 0.000123s`** | Time in green text | Exact time taken by the algorithm in seconds |
| **Status bar** | Text below the time | Real-time feedback — tells you exactly what just happened |
| **Difficulty radio buttons** | Easy / Medium / Hard | Select the challenge level of the puzzle |
| **Puzzle # radio buttons** | Puzzle 1 / 2 / 3 / 4 | Select which of the four puzzles to load |
| **Algorithm radio buttons** | Backtracking / AC-3 | Choose which algorithm will solve the puzzle |

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
git clone https://github.com/YourUsername/sudoku-csp-al2002.git
cd sudoku-csp-al2002
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

1. **Select Difficulty** — Click `Easy`, `Medium`, or `Hard`
2. **Select Puzzle Number** — Click `Puzzle 1`, `Puzzle 2`, `Puzzle 3`, or `Puzzle 4`
3. **Select Algorithm** — Click `Backtracking` or `AC-3`
4. **Click `LOAD PUZZLE`** — The board fills with the puzzle's given numbers
5. **To solve automatically** — Click `⚡ SOLVE`. The board fills instantly and the time appears
6. **To solve manually** — Click any empty cell (turns purple). Type a number 1–9. Press `Delete` or `Backspace` to clear
7. **Need help?** — Click `💡 HINT`. One correct cell fills in green
8. **Check your work** — Click `✓ CHECK`. Wrong cells turn red, correct ones stay as-is
9. **Start over** — Click `↺ RESET` to wipe your entries and get the blank puzzle back

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
|---|---|
| **Name** | *(Ali Amir)* |
| **Contact** | *(maliamir089@gmail.com)* |
| **Institution** | NUCES Faisalabad-Chiniot Campus |


---

*Built with patience, Python, and a healthy respect for constraint propagation.*