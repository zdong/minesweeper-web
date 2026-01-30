using Minesweeper.Core.Models;

namespace Minesweeper.Core.Solver;

/// <summary>
/// AI solver for Minesweeper using logical deduction and probability analysis.
/// </summary>
public class MinesweeperSolver
{
    private readonly GameBoard _board;
    private readonly HashSet<(int, int)> _knownMines = new();
    private readonly Random _random = new();

    public MinesweeperSolver(GameBoard board)
    {
        _board = board;
    }

    /// <summary>
    /// Gets the next move to make.
    /// </summary>
    public SolverMove? GetNextMove()
    {
        // Strategy 1: Find cells that must be mines
        IdentifyMines();

        // Strategy 2: Find safe cells to reveal
        var safeMove = FindSafeCell();
        if (safeMove != null) return safeMove;

        // Strategy 3: Make educated guess
        return MakeGuess();
    }

    private void IdentifyMines()
    {
        for (int r = 0; r < _board.Rows; r++)
        {
            for (int c = 0; c < _board.Columns; c++)
            {
                var cell = _board.GetCell(r, c);
                if (cell == null || !cell.IsRevealed || cell.AdjacentMines == 0)
                    continue;

                var unrevealed = _board.GetNeighbors(r, c)
                    .Where(n => !n.IsRevealed && !_knownMines.Contains((n.Row, n.Column)))
                    .ToList();

                var knownMineCount = _board.GetNeighbors(r, c)
                    .Count(n => _knownMines.Contains((n.Row, n.Column)));

                int remainingMines = cell.AdjacentMines - knownMineCount;

                if (remainingMines > 0 && unrevealed.Count == remainingMines)
                {
                    foreach (var n in unrevealed)
                        _knownMines.Add((n.Row, n.Column));
                }
            }
        }
    }

    private SolverMove? FindSafeCell()
    {
        for (int r = 0; r < _board.Rows; r++)
        {
            for (int c = 0; c < _board.Columns; c++)
            {
                var cell = _board.GetCell(r, c);
                if (cell == null || !cell.IsRevealed)
                    continue;

                var knownMineCount = _board.GetNeighbors(r, c)
                    .Count(n => _knownMines.Contains((n.Row, n.Column)));

                if (knownMineCount == cell.AdjacentMines)
                {
                    var safeCell = _board.GetNeighbors(r, c)
                        .FirstOrDefault(n => !n.IsRevealed && !_knownMines.Contains((n.Row, n.Column)));

                    if (safeCell != null)
                        return new SolverMove(safeCell.Row, safeCell.Column, MoveAction.Reveal,
                            $"Safe: ({r},{c}) has all mines identified");
                }
            }
        }
        return null;
    }

    private SolverMove? MakeGuess()
    {
        var candidates = new List<(int row, int col, double risk)>();

        for (int r = 0; r < _board.Rows; r++)
        {
            for (int c = 0; c < _board.Columns; c++)
            {
                var cell = _board.GetCell(r, c);
                if (cell != null && !cell.IsRevealed && !_knownMines.Contains((r, c)))
                {
                    double risk = CalculateRisk(r, c);
                    candidates.Add((r, c, risk));
                }
            }
        }

        if (candidates.Count == 0)
            return null;

        // Pick from safest candidates
        var safest = candidates.OrderBy(x => x.risk).Take(5).ToList();
        var chosen = safest[_random.Next(safest.Count)];

        return new SolverMove(chosen.row, chosen.col, MoveAction.Reveal,
            $"Guess: {chosen.risk:P0} risk");
    }

    private double CalculateRisk(int row, int col)
    {
        var neighbors = _board.GetNeighbors(row, col).Where(n => n.IsRevealed).ToList();

        if (neighbors.Count == 0)
            return (double)_board.MineCount / (_board.Rows * _board.Columns);

        double totalRisk = 0;
        int count = 0;

        foreach (var neighbor in neighbors)
        {
            var knownMines = _board.GetNeighbors(neighbor.Row, neighbor.Column)
                .Count(n => _knownMines.Contains((n.Row, n.Column)));
            var unrevealed = _board.GetNeighbors(neighbor.Row, neighbor.Column)
                .Count(n => !n.IsRevealed && !_knownMines.Contains((n.Row, n.Column)));

            if (unrevealed > 0)
            {
                int minesNeeded = neighbor.AdjacentMines - knownMines;
                totalRisk += (double)minesNeeded / unrevealed;
                count++;
            }
        }

        return count > 0 ? totalRisk / count : 0.5;
    }
}
