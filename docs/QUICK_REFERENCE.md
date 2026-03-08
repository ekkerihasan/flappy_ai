# Flappy AI High Score System - Quick Reference

## What Changed?

✅ **Added Menu System**
- Main menu with options to start, view scores, or quit
- Change player name anytime
- Current player name displayed

✅ **Added Name Management**
- Enter/change your player name before each game
- Name is saved with your score

✅ **Added Score Saving (JSON)**
- Automatic save after each game
- Local file: `highscores.json`
- Top 10 scores kept (oldest removed if over limit)

✅ **Added High Scores Display**
- View all saved scores ranked by score
- Shows rank, name, and score
- Displays if you made the top 10 when game ends

## File Structure

```
player_vs_ai.py         ← MODIFIED (added menu, score system)
highscores.json         ← NEW (auto-created, stores scores)

Documentation:
├── HIGH_SCORES_GUIDE.md         (Feature overview)
├── IMPLEMENTATION_SUMMARY.md    (Technical details)
└── USAGE_EXAMPLES.md            (How to use)
```

## Menu Navigation Flow

```
┌─────────────┐
│   MENU      │ ◄─┬─ [S] Start Game
│             │   ├─ [H] High Scores ─────────────┐
│ [S] [H] [Q] │   ├─ [C] Change Name   ┌──────────┤
│             │   │                     │          │
└─────────────┘   │              ┌──────▼──────┐  │
      ▲           │              │NAME INPUT   │◄─┘
      │           │              │[ENTER/ESC]  │
      │           │              └──────┬──────┘
      │           │                     │
      │    ┌──────▼─────────┐           │
      │    │  GAMEPLAY      │           │
      │    │ (normal play)  │           │
      │    └──────┬─────────┘           │
      │           │                     │
      │    ┌──────▼──────────────────────┘
      │    │  GAME OVER
      │    │  [M] Save & Menu
      │    │  [P] Save & Play Again
      │    └──────┬──────────┐
      │           │          │
      └───────────┼──────────┘
                  │
        ┌─────────▼──────────┐
        │  HIGH SCORES       │
        │  [M] Menu          │
        │  [C] Change Name   │
        └────────────────────┘
```

## Key Shortcuts

| Location | Shortcut | Effect |
|----------|----------|--------|
| Menu | S | Start Game |
| Menu | H | High Scores |
| Menu | C | Change Name |
| Menu | Q | Quit |
| Name Input | ENTER | Confirm |
| Name Input | ESC | Cancel |
| Game | SPACE | Jump |
| Game | P | Pause |
| Game | R | Back to Menu |
| Game Over | M | Save Score & Menu |
| Game Over | P | Save Score & Play |
| Scores | M | Back to Menu |
| Scores | C | Change Name |

## Score Data Format

```json
[
  {"name": "PlayerName", "score": 45},
  {"name": "PlayerName", "score": 32},
  {"name": "AnotherPlayer", "score": 28}
]
```

## Functions Added

### `load_highscores()`
Loads existing high scores from `highscores.json`

### `save_highscores(scores)`
Saves high scores to `highscores.json`

### `add_score(name, score)`
Adds a new score, sorts descending, keeps top 10

### `get_rank_for_score(score)`
Returns rank if score makes top 10, else None

## Settings (Editable)

In `player_vs_ai.py` around line 120:

```python
HIGHSCORES_FILE = "highscores.json"  # Change filename/path
MAX_SCORES = 10                      # Change to 5, 20, etc.
```

## States (Internal)

The game uses a state machine:
- `"menu"` - Main menu
- `"name_input"` - Entering player name
- `"game"` - Active gameplay
- `"game_over"` - Score display & save prompt
- `"high_scores"` - Viewing high scores

## First Time Setup

1. Run: `python player_vs_ai.py`
2. Press [S] to start
3. Enter your name (or press ENTER for default)
4. Play normally
5. When done, game over screen appears
6. Press [M] or [P] to save and continue
7. Score is now saved in `highscores.json`
8. Press [H] from menu to view scores

## Backwards Compatible

✓ All existing game mechanics unchanged
✓ Command line arguments still work (--difficulty, --no-model)
✓ AI still uses same model/heuristic
✓ Graphics and physics identical
✓ Only addition: Score saving flow

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Scores not saving | Check folder write permissions |
| Name too short/blank | Press [C] to change, enter name, press [ENTER] |
| Scores disappeared | Delete `highscores.json` to reset |
| Want to modify scores | Edit `highscores.json` directly with text editor |
| Only seeing old gameplay | Press [S] then start a new game |

## Testing Checklist

- [ ] Start game and enter player name
- [ ] Play a game to completion
- [ ] See game over screen with score
- [ ] Check `highscores.json` file exists
- [ ] Press [M] to save score
- [ ] View [H] High Scores from menu
- [ ] See your name and score in list
- [ ] Change name with [C] and play again
- [ ] Verify second score is saved separately
- [ ] Play with different difficulty levels
- [ ] Verify command line args still work

## Notes

- 🖥️ **Local Only** - No internet connection needed
- 💾 **Persistent** - Scores saved between sessions
- 🔒 **No Login** - Just enter a name
- 📝 **Editable** - Can manually edit `highscores.json`
- ♾️ **Unlimited Players** - Just change the name!

## Support

For detailed documentation, see:
- `HIGH_SCORES_GUIDE.md` - Feature overview
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `USAGE_EXAMPLES.md` - Complete examples & troubleshooting
