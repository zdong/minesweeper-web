namespace Minesweeper.Core.Models;

/// <summary>
/// Represents the current state of the game.
/// </summary>
public enum GameState
{
    /// <summary>Game has not started yet (no cells revealed).</summary>
    NotStarted,

    /// <summary>Game is in progress.</summary>
    InProgress,

    /// <summary>Player has won (all non-mine cells revealed).</summary>
    Won,

    /// <summary>Player has lost (revealed a mine).</summary>
    Lost
}
