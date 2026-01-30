using Minesweeper.Core.Models;

namespace Minesweeper.Core;

/// <summary>
/// Manages the Minesweeper game board state and logic.
/// Thread-safe for use with AI solver.
/// </summary>
public class GameBoard
{
    private readonly Cell[,] _cells;
    private readonly object _lock = new();
    private bool _minesPlaced;

    public int Rows { get; }
    public int Columns { get; }
    public int MineCount { get; }
    public GameState State { get; private set; } = GameState.NotStarted;

    public GameBoard(int rows, int columns, int mineCount)
    {
        if (rows < GameConstants.MinBoardSize || rows > GameConstants.MaxBoardSize)
            throw new ArgumentOutOfRangeException(nameof(rows));
        if (columns < GameConstants.MinBoardSize || columns > GameConstants.MaxBoardSize)
            throw new ArgumentOutOfRangeException(nameof(columns));
        if (mineCount < GameConstants.MinMines || mineCount >= rows * columns)
            throw new ArgumentOutOfRangeException(nameof(mineCount));

        Rows = rows;
        Columns = columns;
        MineCount = mineCount;
        _cells = new Cell[rows, columns];

        InitializeBoard();
    }

    public GameBoard(DifficultySettings difficulty)
        : this(difficulty.Rows, difficulty.Columns, difficulty.Mines) { }

    private void InitializeBoard()
    {
        for (int r = 0; r < Rows; r++)
            for (int c = 0; c < Columns; c++)
                _cells[r, c] = new Cell(r, c);
    }

    /// <summary>
    /// Gets the cell at the specified position, or null if out of bounds.
    /// </summary>
    public Cell? GetCell(int row, int col)
    {
        if (row < 0 || row >= Rows || col < 0 || col >= Columns)
            return null;
        return _cells[row, col];
    }

    /// <summary>
    /// Reveals a cell. On first click, places mines avoiding the clicked area.
    /// </summary>
    public GameState RevealCell(int row, int col)
    {
        lock (_lock)
        {
            if (!IsValidCell(row, col) || State == GameState.Won || State == GameState.Lost)
                return State;

            var cell = _cells[row, col];
            if (cell.IsRevealed || cell.IsFlagged)
                return State;

            // Place mines on first click
            if (!_minesPlaced)
            {
                PlaceMines(row, col);
                _minesPlaced = true;
                State = GameState.InProgress;
            }

            cell.IsRevealed = true;

            if (cell.IsMine)
            {
                cell.IsTriggered = true;
                State = GameState.Lost;
                RevealAllMines();
                return State;
            }

            if (cell.AdjacentMines == 0)
                FloodReveal(row, col);

            if (CheckWinCondition())
                State = GameState.Won;

            return State;
        }
    }

    /// <summary>
    /// Toggles flag on an unrevealed cell.
    /// </summary>
    public void ToggleFlag(int row, int col)
    {
        lock (_lock)
        {
            if (!IsValidCell(row, col) || State == GameState.Won || State == GameState.Lost)
                return;

            var cell = _cells[row, col];
            if (!cell.IsRevealed)
                cell.IsFlagged = !cell.IsFlagged;
        }
    }

    /// <summary>
    /// Gets the number of flagged cells.
    /// </summary>
    public int GetFlagCount()
    {
        lock (_lock)
        {
            int count = 0;
            foreach (var cell in _cells)
                if (cell.IsFlagged) count++;
            return count;
        }
    }

    /// <summary>
    /// Gets all neighbors of a cell.
    /// </summary>
    public IEnumerable<Cell> GetNeighbors(int row, int col)
    {
        for (int dr = -1; dr <= 1; dr++)
        {
            for (int dc = -1; dc <= 1; dc++)
            {
                if (dr == 0 && dc == 0) continue;
                var cell = GetCell(row + dr, col + dc);
                if (cell != null) yield return cell;
            }
        }
    }

    private bool IsValidCell(int row, int col) =>
        row >= 0 && row < Rows && col >= 0 && col < Columns;

    private void PlaceMines(int excludeRow, int excludeCol)
    {
        var random = new Random();
        var exclusionZone = new HashSet<(int, int)>();

        // Create safe zone around first click
        for (int dr = -1; dr <= 1; dr++)
            for (int dc = -1; dc <= 1; dc++)
                if (IsValidCell(excludeRow + dr, excludeCol + dc))
                    exclusionZone.Add((excludeRow + dr, excludeCol + dc));

        int placed = 0;
        while (placed < MineCount)
        {
            int r = random.Next(Rows);
            int c = random.Next(Columns);

            if (!_cells[r, c].IsMine && !exclusionZone.Contains((r, c)))
            {
                _cells[r, c].IsMine = true;
                placed++;
            }
        }

        CalculateAdjacentMines();
    }

    private void CalculateAdjacentMines()
    {
        for (int r = 0; r < Rows; r++)
        {
            for (int c = 0; c < Columns; c++)
            {
                if (!_cells[r, c].IsMine)
                    _cells[r, c].AdjacentMines = GetNeighbors(r, c).Count(n => n.IsMine);
            }
        }
    }

    private void FloodReveal(int startRow, int startCol)
    {
        var queue = new Queue<(int, int)>();
        var visited = new HashSet<(int, int)> { (startRow, startCol) };
        queue.Enqueue((startRow, startCol));

        while (queue.Count > 0)
        {
            var (r, c) = queue.Dequeue();

            foreach (var neighbor in GetNeighbors(r, c))
            {
                if (visited.Contains((neighbor.Row, neighbor.Column))) continue;
                if (neighbor.IsFlagged || neighbor.IsMine) continue;

                visited.Add((neighbor.Row, neighbor.Column));
                neighbor.IsRevealed = true;

                if (neighbor.AdjacentMines == 0)
                    queue.Enqueue((neighbor.Row, neighbor.Column));
            }
        }
    }

    private bool CheckWinCondition()
    {
        foreach (var cell in _cells)
            if (!cell.IsRevealed && !cell.IsMine)
                return false;
        return true;
    }

    private void RevealAllMines()
    {
        foreach (var cell in _cells)
            if (cell.IsMine)
                cell.IsRevealed = true;
    }
}
