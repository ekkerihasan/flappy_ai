# Flappy AI - Usage Examples

## Quick Start

### 1. **First Time Playing**
```
1. Run: python player_vs_ai.py
2. Menu appears - Press [S] to start
3. You're prompted to enter a name (or use default "Player")
4. Play the game normally
5. When you die, press [M] to save and go to menu
6. Your score is saved to highscores.json
```

### 2. **View Your Scores**
```
1. From the menu, press [H]
2. See top 10 scores with rank, name, and score
3. Your recent scores appear in the list
4. Press [M] to return to menu
```

### 3. **Play with Different Names**
```
Menu → [C] Change Name → Enter new name → [ENTER]
Now when you play, your new name will be saved with the score
```

### 4. **Play Again**
```
From main menu:
- Press [S] to start a new game with current player name
- Or change name first with [C] then start
```

## Example Workflow

### Scenario 1: Single Player, Multiple Games
```
Player: "Hassan"

Game 1: Score 42
Game 2: Score 55  ← Now rank 1!
Game 3: Score 28

highscores.json contains:
[
  {"name": "Hassan", "score": 55},
  {"name": "Hassan", "score": 42},
  {"name": "Hassan", "score": 28}
]
```

### Scenario 2: Multiple Players (Same Device)
```
Player "Hassan" plays:
  Game 1: Score 45
  
Player "Brother" plays:
  Game 1: Score 38
  Game 2: Score 52

Player "Hassan" plays again:
  Game 2: Score 51

highscores.json contains (sorted by score):
[
  {"name": "Hassan", "score": 51},
  {"name": "Brother", "score": 52},
  {"name": "Hassan", "score": 45},
  {"name": "Brother", "score": 38}
]
```

### Scenario 3: Competing with Friends
```
Everyone can change their name and play:

1. Me: Press [C] → Enter "Me" → [ENTER] → Play → Save
2. Friend1: Press [C] → Enter "Friend1" → [ENTER] → Play → Save
3. Friend2: Press [C] → Enter "Friend2" → [ENTER] → Play → Save

Everyone checks scores: Press [H]
See final rankings!
```

## Keyboard Controls Reference

| Screen | Key | Action |
|--------|-----|--------|
| **Menu** | S | Start Game |
| | H | View High Scores |
| | C | Change Player Name |
| | Q | Quit |
| **Name Input** | ENTER | Confirm Name |
| | ESC | Cancel |
| | BACKSPACE | Delete Character |
| **Playing** | SPACE | Jump |
| | P | Pause/Resume |
| | R | Return to Menu |
| **Game Over** | M | Save & Go to Menu |
| | P | Save & Play Again |
| **High Scores** | M | Return to Menu |
| | C | Change Player Name |

## Command Line Options

```bash
# Normal mode
python player_vs_ai.py

# Set difficulty
python player_vs_ai.py --difficulty easy
python player_vs_ai.py --difficulty normal
python player_vs_ai.py --difficulty hard

# Use heuristic AI only (no model)
python player_vs_ai.py --no-model

# Auto-reset after crash (not recommended for manual play)
python player_vs_ai.py --auto-reset

# Combine options
python player_vs_ai.py --difficulty hard --no-model
```

## Tips for Better Scores

### Gameplay Tips
1. **Timing is Key** - Jump at the right moment to pass through gaps
2. **Watch the AI** - It often makes good decisions, learn from it
3. **Easy Mode** - Use easy difficulty to practice and get higher scores
4. **Consistency** - Play regularly to improve your technique

### Score Rankings
| Rank | Difficulty | Avg Score |
|------|------------|-----------|
| #1 (Champion) | Hard | 50+ |
| #2-3 | Hard | 35-50 |
| #4-5 | Normal | 30-40 |
| #6-10 | Easy | 20-35 |

## Troubleshooting

### "ModuleNotFoundError: No module named 'pygame'"
```bash
pip install pygame
# or
venv\Scripts\python.exe -m pip install pygame
```

### "FileNotFoundError: bg.jpg not found"
Ensure you have `bg.jpg` and `flame.png` in the same directory as the script

### Scores Not Saving
- Check permissions on the folder (read/write access)
- `highscores.json` should be created automatically
- If deleted, it will be recreated next game

### Resetting Scores
Simply delete `highscores.json` - it will be recreated empty on next game

## Data File Details

### highscores.json
- **Location**: Same folder as `player_vs_ai.py`
- **Format**: JSON array of objects
- **Max Entries**: 10 (by default)
- **Auto-created**: Yes, on first save
- **Editable**: Yes, you can edit manually

Example of manually editing for testing:
```json
[
  {"name": "Test1", "score": 100},
  {"name": "Test2", "score": 99},
  {"name": "Test3", "score": 98},
  {"name": "Test4", "score": 97},
  {"name": "Test5", "score": 96}
]
```

## Advanced Usage

### Modify Score Limits
Edit `player_vs_ai.py` line ~121:
```python
MAX_SCORES = 10  # Change to 5 for top 5, 20 for top 20, etc.
```

### Modify Score File Location
Edit `player_vs_ai.py` line ~120:
```python
HIGHSCORES_FILE = "my_custom_path/scores.json"  # Different location
```

### Access Scores Programmatically
```python
from player_vs_ai import load_highscores, add_score

# Get all scores
scores = load_highscores()
for rank, entry in enumerate(scores, 1):
    print(f"{rank}. {entry['name']}: {entry['score']}")

# Add a score manually
add_score("NewPlayer", 75)
```
