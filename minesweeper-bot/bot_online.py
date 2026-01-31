"""
Minesweeper Bot for minesweeperonline.com
Adapted to work with the different DOM structure.
"""
import argparse
import time
import re
from playwright.sync_api import sync_playwright, Page
from solver import MinesweeperSolver, MoveAction


# Game configuration by difficulty
DIFFICULTIES = {
    "beginner": {"rows": 9, "cols": 9, "mines": 10},
    "intermediate": {"rows": 16, "cols": 16, "mines": 40},
    "expert": {"rows": 16, "cols": 30, "mines": 99},
}

DEFAULT_URL = "https://minesweeperonline.com/"


class MinesweeperOnlineBot:
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
        """Start a new game. Difficulty selection via URL parameter."""
        # Just click face to start a new game
        # To change difficulty, use URL: https://minesweeperonline.com/#beginner
        # or #intermediate or #expert
        face = self.page.locator("#face")
        if face.count() > 0:
            face.click()
            time.sleep(0.5)

    def read_game_state(self) -> str:
        """Read the current game state from the face icon."""
        face_class = self.page.locator("#face").get_attribute("class") or ""
        if "facedead" in face_class:
            return "lost"
        elif "facewin" in face_class:
            return "won"
        return "playing"

    def read_board(self, debug: bool = False):
        """Read the board state from DOM using fast batch JavaScript."""
        config = DIFFICULTIES[self.difficulty]
        rows, cols = config["rows"], config["cols"]

        # Read all cells at once using JavaScript (MUCH faster than individual queries)
        board_data = self.page.evaluate("""
            (args) => {
                const rows = args.rows;
                const cols = args.cols;
                const cells = [];
                for (let r = 1; r <= rows; r++) {
                    for (let c = 1; c <= cols; c++) {
                        const cell = document.getElementById(r + '_' + c);
                        if (cell) {
                            cells.push({
                                row: r - 1,
                                col: c - 1,
                                classes: cell.className
                            });
                        }
                    }
                }
                return cells;
            }
        """, {"rows": rows, "cols": cols})

        revealed_count = 0
        unrevealed_count = 0

        for cell_data in board_data:
            classes = cell_data["classes"]
            row = cell_data["row"]
            col = cell_data["col"]

            is_unrevealed = "blank" in classes
            is_flagged = "bombflagged" in classes
            is_mine = "bombrevealed" in classes or "bombdeath" in classes

            adjacent_mines = 0
            match = re.search(r'open(\d)', classes)
            if match:
                adjacent_mines = int(match.group(1))

            is_revealed = not is_unrevealed and not is_flagged

            if is_unrevealed:
                unrevealed_count += 1
            else:
                revealed_count += 1

            self.solver.update_cell(
                row=row,
                col=col,
                is_revealed=is_revealed,
                is_flagged=is_flagged,
                is_mine=is_mine,
                adjacent_mines=adjacent_mines
            )

        if debug:
            print(f"  Board: {revealed_count} revealed, {unrevealed_count} unrevealed")

    def click_cell(self, row: int, col: int, right_click: bool = False):
        """Click a cell on the board."""
        # Convert from 0-based to 1-based index
        cell_id = f"{row + 1}_{col + 1}"
        cell = self.page.locator(f"[id='{cell_id}']")

        if right_click:
            cell.click(button="right")
        else:
            cell.click()

    def make_first_move(self):
        """Make the first move (center of board)."""
        config = DIFFICULTIES[self.difficulty]
        center_row = config["rows"] // 2
        center_col = config["cols"] // 2
        print(f"First move: clicking center ({center_row}, {center_col})")
        self.click_cell(center_row, center_col)
        time.sleep(0.3)

    def play(self) -> bool:
        """Play the game until win or lose. Returns True if won."""
        print(f"\n{'='*50}")
        print(f"Starting Bot on minesweeperonline.com - {self.difficulty.title()}")
        print(f"{'='*50}\n")

        # Select difficulty and start new game
        self.select_difficulty()

        # Make first move
        self.make_first_move()

        move_count = 0
        max_moves = 500

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

        print("Max moves reached!")
        return False


def main():
    parser = argparse.ArgumentParser(description="Minesweeper Bot for minesweeperonline.com")
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

    args = parser.parse_args()

    wins = 0
    losses = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        page = browser.new_page()

        # Add difficulty to URL if specified
        url = args.url
        if not url.endswith(f"#{args.difficulty}"):
            url = f"{args.url}#{args.difficulty}"

        print(f"Opening {url}")
        page.goto(url)

        # Wait for the game to load
        page.wait_for_selector("#game")
        time.sleep(1)

        for game_num in range(args.games):
            if args.games > 1:
                print(f"\n--- Game {game_num + 1}/{args.games} ---")

            bot = MinesweeperOnlineBot(
                page=page,
                difficulty=args.difficulty,
                delay=args.delay
            )

            won = bot.play()

            if won:
                wins += 1
            else:
                losses += 1

            # Click face to restart if playing multiple games
            if game_num < args.games - 1:
                page.locator("#face").click()
                time.sleep(0.5)

        browser.close()

    # Print summary
    if args.games > 1:
        print(f"\n{'='*50}")
        print(f"SUMMARY: {wins} wins, {losses} losses ({wins/args.games*100:.1f}% win rate)")
        print(f"{'='*50}")


if __name__ == "__main__":
    main()
