# Minesweeper

A cross-platform Minesweeper game with AI solver.

## Projects

- **Minesweeper.Core** - Shared game logic library
- **Minesweeper.Web** - Blazor WebAssembly web version

## Running Locally

### Web Version
```bash
cd Minesweeper.Web
dotnet run
```
Then open http://localhost:5000

## Deploying to GitHub Pages

1. Create a new GitHub repository named `minesweeper-web`
2. Push this code:
   ```bash
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/minesweeper-web.git
   git push -u origin main
   ```
3. Go to repository Settings > Pages
4. Set Source to "GitHub Actions"
5. The workflow will automatically deploy

Your game will be available at: `https://YOUR_USERNAME.github.io/minesweeper-web/`

## Features

- Classic Minesweeper gameplay
- Three difficulty levels (Beginner, Intermediate, Expert)
- AI auto-play solver
- Timer and mine counter
- Flag cells with right-click
- Works on desktop and mobile browsers

## Architecture

The codebase follows clean architecture principles:
- **Models** - Cell, GameState, DifficultySettings
- **Core Logic** - GameBoard with thread-safe operations
- **Solver** - AI using logical deduction and probability analysis
