# Flappy AI - High Score System Guide

## Overview
The updated Flappy Bird game now includes a **local, device-only high score system** similar to Bike Race. All scores are saved to `highscores.json` on your device.

## Features

### 1. **Menu Screen**
- Start the game with **[S] Start Game**
- View high scores with **[H] High Scores**
- Change player name with **[C]** (from high scores screen)
- Quit with **[Q]**
- Shows current player name

### 2. **Player Name Management**
- Enter or change your player name before starting
- Name is displayed during gameplay
- Name is saved with your score

### 3. **High Score Saving**
- Scores are automatically saved to `highscores.json`
- Top 10 scores are kept (configurable via `MAX_SCORES`)
- Scores are sorted in descending order
- Format:
  ```json
  [
    {"name": "Hassan", "score": 45},
    {"name": "Brother", "score": 28},
    ...
  ]
  ```

### 4. **Game Over Screen**
- Shows final score
- Displays player name
- Indicates if you made the top 10 (with rank)
- Options:
  - **[M]** - Return to menu
  - **[P]** - Play again with same name

### 5. **High Scores Screen**
- Displays top 10 scores with rank, name, and score
- Shows "No scores yet!" if empty
- Options:
  - **[M]** - Return to menu
  - **[C]** - Change player name

## Game Controls

### During Gameplay
- **SPACE** - Jump (start game)
- **P** - Pause/Unpause
- **R** - Return to menu

### On Game Over
- **SPACE** - Save score and return to menu
- **M** - Return to menu
- **P** - Play again

## Data Persistence
- Scores are saved in `highscores.json` in the game folder
- No internet connection required
- Data persists between game sessions
- Edit `highscores.json` to manually modify scores

## Configuration

In `player_vs_ai.py`, you can modify:
- `MAX_SCORES = 10` - Maximum number of high scores to keep
- `HIGHSCORES_FILE = "highscores.json"` - Location of score file

## Example High Score File

```json
[
  {"name": "Champion", "score": 87},
  {"name": "Player One", "score": 65},
  {"name": "Hassan", "score": 42},
  {"name": "AI Master", "score": 38},
  {"name": "Speedster", "score": 25}
]
```

## Tips

1. **Better Scores**: 
   - Easy mode is easier to score higher
   - Practice the timing of your jumps
   - Watch the AI's strategy

2. **High Score Ranks**:
   - Rank 1-10 = In the high scores!
   - Top 5 is excellent
   - Top score is the champion

3. **Multiple Players**:
   - Change your name before each game
   - All scores are saved locally
   - Share the same device to compete
