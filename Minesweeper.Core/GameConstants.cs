namespace Minesweeper.Core;

/// <summary>
/// Contains all game constants to avoid magic numbers throughout the codebase.
/// </summary>
public static class GameConstants
{
    // Board size limits
    public const int MinBoardSize = 5;
    public const int MaxBoardSize = 50;
    public const int MinMines = 1;

    // Difficulty presets
    public static readonly DifficultySettings Beginner = new(9, 9, 10);
    public static readonly DifficultySettings Intermediate = new(16, 16, 40);
    public static readonly DifficultySettings Expert = new(16, 30, 99);

    // AI solver thresholds
    public const int MaxCspRegionSize = 20;
    public const double ProbabilityThreshold = 0.35;
    public const double EndgameThreshold = 0.30;
    public const int MovesPerYield = 50;
}

/// <summary>
/// Represents difficulty settings with rows, columns, and mine count.
/// </summary>
public readonly record struct DifficultySettings(int Rows, int Columns, int Mines)
{
    public int TotalCells => Rows * Columns;
    public double MineDensity => (double)Mines / TotalCells;
}
