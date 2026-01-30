namespace Minesweeper.Core.Solver;

/// <summary>
/// Represents a move suggested by the AI solver.
/// </summary>
public record SolverMove(int Row, int Column, MoveAction Action, string Reasoning);

/// <summary>
/// Type of move action.
/// </summary>
public enum MoveAction
{
    Reveal,
    Flag
}
