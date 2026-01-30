# Minesweeper Bot

An AI bot that plays Minesweeper using browser automation. It reads the game state from the DOM and makes intelligent moves using logical deduction and probability analysis.

## Setup

```bash
cd minesweeper-bot

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Usage

### Basic Usage
```bash
# Play one game on beginner
python bot.py

# Play on intermediate difficulty
python bot.py -d intermediate

# Play on expert difficulty
python bot.py -d expert
```

### Options
```bash
python bot.py --help

Options:
  -d, --difficulty    beginner|intermediate|expert (default: beginner)
  -u, --url           Game URL (default: https://zdong.github.io/minesweeper-web/)
  -n, --games         Number of games to play (default: 1)
  --delay             Delay between moves in seconds (default: 0.1)
  --headless          Run without visible browser
  --submit-name       Name to submit to leaderboard on win
```

### Examples

```bash
# Play 10 games and see win rate
python bot.py -n 10

# Play fast (0.05s between moves)
python bot.py --delay 0.05

# Play in headless mode (no browser window)
python bot.py --headless -n 100

# Submit score to leaderboard when winning
python bot.py --submit-name "BotPlayer"

# Play against local development server
python bot.py -u http://localhost:5180
```

## How It Works

1. **Browser Automation**: Uses Playwright to control a real Chrome browser
2. **DOM Reading**: Extracts cell states by reading CSS classes and content
3. **AI Solver**: Uses logical deduction to find safe cells and mines
4. **Click Execution**: Clicks cells just like a human would

## Solver Strategy

1. **Identify Mines**: If a revealed cell shows N and has exactly N unrevealed neighbors, all must be mines
2. **Find Safe Cells**: If all mines around a cell are identified, remaining neighbors are safe
3. **Educated Guess**: When stuck, calculate probability for each cell and pick the safest
