"""
Minesweeper AI Solver - Ported from C# implementation.
Uses logical deduction and probability analysis.
"""
import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MoveAction(Enum):
    REVEAL = "reveal"
    FLAG = "flag"


@dataclass
class Cell:
    row: int
    col: int
    is_revealed: bool
    is_flagged: bool
    is_mine: bool
    adjacent_mines: int


@dataclass
class SolverMove:
    row: int
    col: int
    action: MoveAction
    reason: str


class MinesweeperSolver:
    def __init__(self, rows: int, cols: int, mine_count: int):
        self.rows = rows
        self.cols = cols
        self.mine_count = mine_count
        self.cells: dict[tuple[int, int], Cell] = {}
        self.known_mines: set[tuple[int, int]] = set()

    def update_cell(self, row: int, col: int, is_revealed: bool, is_flagged: bool,
                    is_mine: bool = False, adjacent_mines: int = 0):
        """Update cell state from game DOM."""
        self.cells[(row, col)] = Cell(
            row=row,
            col=col,
            is_revealed=is_revealed,
            is_flagged=is_flagged,
            is_mine=is_mine,
            adjacent_mines=adjacent_mines
        )

    def get_cell(self, row: int, col: int) -> Optional[Cell]:
        return self.cells.get((row, col))

    def get_neighbors(self, row: int, col: int) -> list[Cell]:
        """Get all valid neighboring cells."""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    cell = self.get_cell(nr, nc)
                    if cell:
                        neighbors.append(cell)
        return neighbors

    def get_next_move(self) -> Optional[SolverMove]:
        """Get the next move to make."""
        # Strategy 1: Find cells that must be mines
        self._identify_mines()

        # Strategy 2: Find safe cells to reveal
        safe_move = self._find_safe_cell()
        if safe_move:
            return safe_move

        # Strategy 3: Make educated guess
        return self._make_guess()

    def _identify_mines(self):
        """Identify cells that must be mines based on number constraints."""
        for (r, c), cell in self.cells.items():
            if not cell.is_revealed or cell.adjacent_mines == 0:
                continue

            neighbors = self.get_neighbors(r, c)
            unrevealed = [
                n for n in neighbors
                if not n.is_revealed and (n.row, n.col) not in self.known_mines
            ]

            known_mine_count = sum(
                1 for n in neighbors
                if (n.row, n.col) in self.known_mines
            )

            remaining_mines = cell.adjacent_mines - known_mine_count

            # If unrevealed count equals remaining mines, all must be mines
            if remaining_mines > 0 and len(unrevealed) == remaining_mines:
                for n in unrevealed:
                    self.known_mines.add((n.row, n.col))

    def _find_safe_cell(self) -> Optional[SolverMove]:
        """Find a cell that is guaranteed safe to reveal."""
        for (r, c), cell in self.cells.items():
            if not cell.is_revealed:
                continue

            neighbors = self.get_neighbors(r, c)
            known_mine_count = sum(
                1 for n in neighbors
                if (n.row, n.col) in self.known_mines
            )

            # If all mines around this cell are identified, remaining cells are safe
            if known_mine_count == cell.adjacent_mines:
                for n in neighbors:
                    if not n.is_revealed and (n.row, n.col) not in self.known_mines:
                        return SolverMove(
                            row=n.row,
                            col=n.col,
                            action=MoveAction.REVEAL,
                            reason=f"Safe: ({r},{c}) has all mines identified"
                        )
        return None

    def _make_guess(self) -> Optional[SolverMove]:
        """Make an educated guess when no safe move exists."""
        candidates = []

        for (r, c), cell in self.cells.items():
            if not cell.is_revealed and (r, c) not in self.known_mines:
                risk = self._calculate_risk(r, c)
                candidates.append((r, c, risk))

        if not candidates:
            return None

        # Sort by risk and pick from safest candidates
        candidates.sort(key=lambda x: x[2])
        safest = candidates[:5]
        chosen = random.choice(safest)

        return SolverMove(
            row=chosen[0],
            col=chosen[1],
            action=MoveAction.REVEAL,
            reason=f"Guess: {chosen[2]:.0%} risk"
        )

    def _calculate_risk(self, row: int, col: int) -> float:
        """Calculate the probability that a cell contains a mine."""
        neighbors = [n for n in self.get_neighbors(row, col) if n.is_revealed]

        if not neighbors:
            # No info - use global probability
            return self.mine_count / (self.rows * self.cols)

        total_risk = 0.0
        count = 0

        for neighbor in neighbors:
            n_neighbors = self.get_neighbors(neighbor.row, neighbor.col)
            known_mines = sum(
                1 for n in n_neighbors
                if (n.row, n.col) in self.known_mines
            )
            unrevealed = sum(
                1 for n in n_neighbors
                if not n.is_revealed and (n.row, n.col) not in self.known_mines
            )

            if unrevealed > 0:
                mines_needed = neighbor.adjacent_mines - known_mines
                total_risk += mines_needed / unrevealed
                count += 1

        return total_risk / count if count > 0 else 0.5
