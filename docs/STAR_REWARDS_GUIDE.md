# Star Reward System - Feature Guide

## Overview

The game now includes a **Star Reward System** that gives you stars when you defeat the AI! Stars are earned based on your final score and serve as a measure of achievement beyond just the numerical score.

## How Stars Work

### Earning Stars

You earn stars **only when you beat the AI** (i.e., the AI dies but you survive). The number of stars is determined by your final score:

| Score Range | Stars Earned | Emoji |
|-------------|--------------|-------|
| 0-5 points | 1 ⭐ | ⭐ |
| 6-15 points | 2 ⭐⭐ | ⭐⭐ |
| 16-30 points | 3 ⭐⭐⭐ | ⭐⭐⭐ |
| 31-50 points | 4 ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 51+ points | 5 ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### When You Don't Get Stars

- **You Lost** (AI defeats you) → 0 stars
- **Draw** (Both crash) → 0 stars
- **Score = 0** → 0 stars (even if you win)

## Game Over Screen

When the game ends, you'll see:

### Victory Screen (You Win!)
- Title shows **"VICTORY!"** in green
- Large display of your earned stars
- Count: **"REWARD: X STAR(S)"**
- Encouragement message

Example:
```
═══════════════════════════════════
        VICTORY!
─────────────────────────────────
Player: Champion
Score: 45
⭐⭐⭐⭐
REWARD: 4 STARS
───────────────────────────────────
[M] Return to Menu  [P] Play Again
═══════════════════════════════════
```

### Defeat Screen (You Lost)
- Title shows **"GAME OVER"** in red
- No stars displayed
- Encouragement to improve

### Draw Screen (Both Crashed)
- Shows who crashed first
- No stars earned
- Neutral message

## High Scores List

Your earned stars are displayed in the High Scores screen:

| Rank | Player Name | Score | Stars |
|------|-------------|-------|-------|
| 🥇 1 | Champion | 87 | ⭐⭐⭐⭐⭐ |
| 🥈 2 | Expert | 65 | ⭐⭐⭐⭐ |
| 🥉 3 | Player | 52 | ⭐⭐⭐ |
| 4 | Learner | 25 | ⭐⭐ |
| 5 | Newbie | 8 | ⭐ |

Shows:
- Gold stars (⭐) for achieved rewards
- Dash (-) if no stars earned

## Data Storage

Stars are saved automatically in `highscores.json`:

```json
[
  {"name": "Champion", "score": 87, "stars": 5},
  {"name": "Expert", "score": 65, "stars": 4},
  {"name": "Player", "score": 52, "stars": 3},
  {"name": "Learner", "score": 25, "stars": 2},
  {"name": "Newbie", "score": 8, "stars": 1}
]
```

## Star Progression Guide

### Beginner (1 Star ⭐)
- Beat the AI with 1-5 points
- This shows you can defeat the AI at all

### Novice (2 Stars ⭐⭐)
- Beat the AI with 6-15 points
- You're getting consistent at dodging obstacles

### Intermediate (3 Stars ⭐⭐⭐)
- Beat the AI with 16-30 points
- You're mastering the game mechanics

### Advanced (4 Stars ⭐⭐⭐⭐)
- Beat the AI with 31-50 points
- You're playing at an expert level

### Master (5 Stars ⭐⭐⭐⭐⭐)
- Beat the AI with 51+ points
- You've achieved mastery!

## Strategy Tips for More Stars

### To Get 1-2 Stars (Easy)
- Use Easy difficulty
- Focus on surviving
- Play defensively

### To Get 3-4 Stars (Medium)
- Use Normal difficulty
- Balance offense and defense
- Study the AI's patterns
- Predict pipe gaps early

### To Get 5 Stars (Hard!)
- Use Hard difficulty or improve a lot
- Perfect your timing
- Minimize errors
- Practice consistently

## Technical Details

### Star Calculation Function
```python
def calculate_stars(score):
    """Calculate star reward based on score (only if score > 0)."""
    if score == 0:
        return 0
    elif score <= 5:
        return 1
    elif score <= 15:
        return 2
    elif score <= 30:
        return 3
    elif score <= 50:
        return 4
    else:
        return 5
```

### Star Awards Only When
```python
player_won = not game["ai_alive"] and game["player_alive"]
stars_earned = calculate_stars(game['score']) if player_won else 0
```

## Features

✓ Automatic calculation based on score
✓ Displayed on Game Over screen with emojis
✓ Saved in high scores with each entry
✓ Shows in High Scores list
✓ Visible stars for achievements
✓ Color-coded display (gold stars)
✓ Clean, professional presentation

## FAQ

### Q: Can I get stars if I lose?
**A:** No, stars are only earned when you defeat the AI.

### Q: Can I get stars in a draw?
**A:** No, a draw means no victory, so no stars.

### Q: What's the maximum stars I can get?
**A:** 5 stars (when you score 51 or more points while defeating the AI).

### Q: Are stars tied to difficulty?
**A:** No, stars are based on final score only. Getting 5 stars in Easy mode is the same as Hard mode.

### Q: Can I improve my stars?
**A:** Yes! Play again and score higher. Only the top 10 scores are kept, so you can replace old ones.

### Q: Do stars affect ranking?
**A:** No, ranking is based on score only. Stars are just a visual indicator of achievement.

### Q: Can I edit stars manually?
**A:** Yes, you can edit `highscores.json` directly to change any star values.

## Example Progression

### Session 1: Learning
- Game 1: Lost → 0 stars
- Game 2: Score 3, Won → ⭐
- Game 3: Lost → 0 stars
- Game 4: Score 8, Won → ⭐⭐

### Session 2: Improving
- Game 1: Score 12, Won → ⭐⭐
- Game 2: Score 25, Won → ⭐⭐⭐
- Game 3: Score 28, Won → ⭐⭐⭐

### Session 3: Mastering
- Game 1: Score 35, Won → ⭐⭐⭐⭐
- Game 2: Score 45, Won → ⭐⭐⭐⭐
- Game 3: Score 52, Won → ⭐⭐⭐⭐⭐ (Master!)

## Customization

To change star thresholds, edit these lines in `player_vs_ai.py`:

```python
def calculate_stars(score):
    if score == 0:
        return 0
    elif score <= 5:      # Change these numbers
        return 1
    elif score <= 15:     # to adjust star ranges
        return 2
    elif score <= 30:
        return 3
    elif score <= 50:
        return 4
    else:
        return 5
```

## Implementation Summary

- **New Function**: `calculate_stars(score)` - Calculates stars based on score
- **Updated Function**: `add_score()` - Now saves stars with score
- **Enhanced Screen**: Game Over screen shows earned stars
- **Enhanced Screen**: High Scores list displays star rewards
- **Data Format**: JSON includes "stars" field for each entry

## Visual Design

- Gold stars (⭐) for premium visual appearance
- Color-coded victory screens (green for win)
- Prominent star display on game over
- Clear labeling: "REWARD: X STARS"
- Professional spacing and layout
