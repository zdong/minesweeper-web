namespace Minesweeper.Core.Models;

/// <summary>
/// Represents a single cell on the Minesweeper game board.
/// </summary>
public class Cell
{
    public int Row { get; }
    public int Column { get; }
    public bool IsMine { get; set; }
    public bool IsRevealed { get; set; }
    public bool IsFlagged { get; set; }
    public int AdjacentMines { get; set; }
    public bool IsTriggered { get; set; }

    public Cell(int row, int column)
    {
        Row = row;
        Column = column;
    }

    /// <summary>
    /// Returns true if this cell should display a number (revealed, not a mine, has adjacent mines).
    /// </summary>
    public bool ShouldShowNumber => IsRevealed && !IsMine && AdjacentMines > 0;

    /// <summary>
    /// Returns true if this cell is empty (revealed, not a mine, no adjacent mines).
    /// </summary>
    public bool IsEmpty => IsRevealed && !IsMine && AdjacentMines == 0;
}
