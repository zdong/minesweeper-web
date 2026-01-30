"""
Minesweeper Bot - Plays the web game using browser automation.
Uses Playwright to control browser and read game state from DOM.
"""
import argparse
import time
import re
from playwright.sync_api import sync_playwright, Page, Locator
from solver import MinesweeperSolver, MoveAction


# Game configuration by difficulty
DIFFICULTIES = {
    "beginner": {"rows": 9, "cols": 9, "mines": 10},
    "intermediate": {"rows": 16, "cols": 16, "mines": 40},
    "expert": {"rows": 16, "cols": 30, "mines": 99},
}

# Default game URL
DEFAULT_URL = "https://zdong.github.io/minesweeper-web/"


class MinesweeperBot:
    def __init__(self, page: Page, difficulty: str = "beginner", delay: float = 0.1):
        self.page = page
        self.difficulty = difficulty
        self.delay = delay
        config = DIFFICULTIES[difficulty]
        self.solver = MinesweeperSolver(
            rows=config["rows"],
            cols=config["cols"],
            mine_count=config["mines"]
        )

    def select_difficulty(self):
        """Click the difficulty button to set up the game."""
        button = self.page.locator(f".difficulty-selector button:has-text('{self.difficulty.title()}')")
        button.click()
        time.sleep(0.5)

    def read_game_state(self) -> str:
        """Read the current game state from the smiley button."""
        smiley = self.page.locator(".smiley-btn").inner_text()
        if smiley == "😎":
            return "won"
        elif smiley == "😵":
            return "lost"
        return "playing"

    def read_board(self, debug: bool = False):
        """Read the board state from DOM and update solver."""
        cells = self.page.locator(".board .cell")
        count = cells.count()

        config = DIFFICULTIES[self.difficulty]
        rows, cols = config["rows"], config["cols"]

        revealed_count = 0
        unrevealed_count = 0

        # Debug: print first cell's classes
        if debug:
            first_cell = cells.nth(0)
            print(f"  Sample cell classes: {first_cell.get_attribute('class')}")

        for i in range(count):
            row = i // cols
            col = i % cols
            cell = cells.nth(i)

            classes = cell.get_attribute("class") or ""
            content = cell.inner_text().strip()

            # Check for unrevealed first (has 'unrevealed' class)
            is_unrevealed = "unrevealed" in classes
            is_revealed = not is_unrevealed and ("revealed" in classes or "mine" in classes)
            is_flagged = "flagged" in classes
            is_mine = "mine" in classes

            if is_unrevealed:
                unrevealed_count += 1
            else:
                revealed_count += 1

            # Parse adjacent mines from class (n1, n2, etc.) or content
            adjacent_mines = 0
            if is_revealed and not is_mine:
                # Try to get from class
                match = re.search(r'\bn(\d)\b', classes)
                if match:
                    adjacent_mines = int(match.group(1))
                elif content.isdigit():
                    adjacent_mines = int(content)

            self.solver.update_cell(
                row=row,
                col=col,
                is_revealed=not is_unrevealed,
                is_flagged=is_flagged,
                is_mine=is_mine,
                adjacent_mines=adjacent_mines
            )

        if debug:
            print(f"  Board: {revealed_count} revealed, {unrevealed_count} unrevealed")

    def click_cell(self, row: int, col: int, right_click: bool = False):
        """Click a cell on the board."""
        config = DIFFICULTIES[self.difficulty]
        cols = config["cols"]
        index = row * cols + col

        cell = self.page.locator(".board .cell").nth(index)

        if right_click:
            cell.click(button="right")
        else:
            cell.click()

    def make_first_move(self):
        """Make the first move (center of board is usually safe)."""
        config = DIFFICULTIES[self.difficulty]
        center_row = config["rows"] // 2
        center_col = config["cols"] // 2
        print(f"First move: clicking center ({center_row}, {center_col})")
        self.click_cell(center_row, center_col)
        time.sleep(0.3)

    def play(self) -> bool:
        """Play the game until win or lose. Returns True if won."""
        print(f"\n{'='*50}")
        print(f"Starting Minesweeper Bot - {self.difficulty.title()}")
        print(f"{'='*50}\n")

        # Select difficulty
        self.select_difficulty()

        # Make first move
        self.make_first_move()

        move_count = 0
        max_moves = 500  # Safety limit
        while move_count < max_moves:
            # Read current state
            self.read_board(debug=(move_count == 0))
            game_state = self.read_game_state()

            if game_state == "won":
                print(f"\n*** WON after {move_count} moves! ***")
                return True
            elif game_state == "lost":
                print(f"\n*** LOST after {move_count} moves! ***")
                return False

            # Get next move from solver
            move = self.solver.get_next_move()

            if move is None:
                # Debug: count unrevealed cells
                unrevealed = sum(1 for c in self.solver.cells.values() if not c.is_revealed)
                known_mines = len(self.solver.known_mines)
                print(f"No moves: {unrevealed} unrevealed, {known_mines} known mines")
                return False

            move_count += 1
            action_str = "FLAG" if move.action == MoveAction.FLAG else "CLICK"
            print(f"Move {move_count}: {action_str} ({move.row}, {move.col}) - {move.reason}")

            # Execute move
            self.click_cell(
                row=move.row,
                col=move.col,
                right_click=(move.action == MoveAction.FLAG)
            )

            time.sleep(self.delay)


def main():
    parser = argparse.ArgumentParser(description="Minesweeper Bot - Automated player")
    parser.add_argument(
        "--difficulty", "-d",
        choices=["beginner", "intermediate", "expert"],
        default="beginner",
        help="Game difficulty (default: beginner)"
    )
    parser.add_argument(
        "--url", "-u",
        default=DEFAULT_URL,
        help=f"Game URL (default: {DEFAULT_URL})"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Delay between moves in seconds (default: 0.1)"
    )
    parser.add_argument(
        "--games", "-n",
        type=int,
        default=1,
        help="Number of games to play (default: 1)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (no visible browser)"
    )
    parser.add_argument(
        "--submit-name",
        help="Name to submit to leaderboard on win (optional)"
    )

    args = parser.parse_args()

    wins = 0
    losses = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        page = browser.new_page()

        print(f"Opening {args.url}")
        page.goto(args.url)
        page.wait_for_selector(".board")

        for game_num in range(args.games):
            if args.games > 1:
                print(f"\n--- Game {game_num + 1}/{args.games} ---")

            bot = MinesweeperBot(
                page=page,
                difficulty=args.difficulty,
                delay=args.delay
            )

            won = bot.play()

            if won:
                wins += 1
                # Submit score if name provided
                if args.submit_name:
                    try:
                        name_input = page.locator(".score-submit input")
                        if name_input.is_visible():
                            name_input.fill(args.submit_name)
                            page.locator(".score-submit button").click()
                            print(f"Score submitted as '{args.submit_name}'")
                            time.sleep(1)
                    except Exception as e:
                        print(f"Could not submit score: {e}")
            else:
                losses += 1

            # Click smiley to restart if playing multiple games
            if game_num < args.games - 1:
                page.locator(".smiley-btn").click()
                time.sleep(0.5)

        browser.close()

    # Print summary
    if args.games > 1:
        print(f"\n{'='*50}")
        print(f"SUMMARY: {wins} wins, {losses} losses ({wins/args.games*100:.1f}% win rate)")
        print(f"{'='*50}")


if __name__ == "__main__":
    main()
