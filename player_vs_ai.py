# player_vs_ai_tf.py
import pygame
import random
try:
    import joblib
except Exception:
    joblib = None
    print("Warning: 'joblib' not available. Install it with: venv\\Scripts\\python.exe -m pip install joblib")
import numpy as np
import os
import json
# Try importing `load_model` from TensorFlow first, fall back to standalone Keras.
try:
    from tensorflow.keras.models import load_model
except Exception:
    try:
        from keras.models import load_model
    except Exception:
        load_model = None  # changed: don't raise here, handle later
import time
import argparse
import sys
pygame.init()
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.image.load("bg.jpg").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()



# Load flame (pipe) image ONLY ONCE
flame_img = pygame.image.load("flame.png").convert_alpha()
flame_img = pygame.transform.scale(flame_img, (60, 300))  # adjust size

# use flame as pipe image
pipe_img = flame_img



BIRD_X = 50
GRAVITY = 0.4
JUMP = -7
PIPE_GAP = 150
PIPE_WIDTH = 60
PIPE_SPEED =5
# AI difficulty: 'easy', 'normal', 'hard'
AI_DIFFICULTY = 'easy'

# load model + scaler (graceful fallback if files are missing)
model = None
scaler = None
try:
    model = load_model("tf_model.h5")
except FileNotFoundError:
    print("Warning: model file 'tf_model.h5' not found — falling back to heuristic AI.")
except Exception as e:
    print(f"Warning: failed to load model: {e}\nFalling back to heuristic AI.")

try:
    scaler = joblib.load("scaler.joblib")
except FileNotFoundError:
    print("Warning: scaler file 'scaler.joblib' not found — heuristic AI will be used.")
except Exception as e:
    print(f"Warning: failed to load scaler: {e}\nHeuristic AI will be used.")

def new_game():
    return {
        "p_bird_y": HEIGHT // 2,
        "p_velocity": 0,
        "a_bird_y": HEIGHT // 2,
        "a_velocity": 0,
        "pipe_x": WIDTH,
        "pipe_top": random.randint(60, 350),
        "player_alive": True,
        "ai_alive": True,
        "end_time": None,
        # UI/game state
        "started": False,
        "paused": False,
        "score": 0,
        "pipe_passed": False,
    }

font = pygame.font.SysFont("Arial", 22)
title_font = pygame.font.SysFont("Arial", 36, bold=True)
name_font = pygame.font.SysFont("Arial", 20, bold=True)
button_font = pygame.font.SysFont("Arial", 24, bold=True)

# ============================================================================
# BUTTON CLASS FOR CLICK/TAP CONTROLS
# ============================================================================

class Button:
    """Reusable button class for mouse click and touch input."""
    def __init__(self, x, y, width, height, text, color=(100, 200, 255), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover = False
    
    def draw(self, surface):
        """Draw the button on the surface."""
        # Draw button rect with border
        pygame.draw.rect(surface, self.color, self.rect, 0)
        pygame.draw.rect(surface, (255, 215, 0) if self.hover else (200, 200, 200), self.rect, 3)
        
        # Draw button text
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def is_clicked(self, pos):
        """Check if button was clicked at position (x, y)."""
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        """Update hover state based on mouse position."""
        self.hover = self.rect.collidepoint(pos)

def draw_outline_text(text, x, y, color):
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        surf = name_font.render(text, True, (0,0,0))
        screen.blit(surf, (x+dx, y+dy))
    surf = name_font.render(text, True, color)
    screen.blit(surf, (x, y))

def draw_text(text, y, color=(255,255,255)):
    surf = font.render(text, True, color)
    screen.blit(surf, (12, y))

def draw_center_text(text, y, color=(255,255,255)):
    surf = title_font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH//2, y))
    screen.blit(surf, rect)

def make_features(bird_y, pipe_top, pipe_bottom, pipe_x):
    distance_to_pipe = pipe_x - BIRD_X
    gap_center = (pipe_top + pipe_bottom) / 2.0
    gap_size = pipe_bottom - pipe_top
    return np.array([bird_y, pipe_top, pipe_bottom, pipe_x, distance_to_pipe, gap_center, gap_size], dtype=float)

THRESHOLD = 0.5  # base threshold (adjusted by difficulty below)

# ============================================================================
# HIGH SCORE MANAGEMENT FUNCTIONS
# ============================================================================

HIGHSCORES_FILE = "highscores.json"
MAX_SCORES = 10

def load_highscores():
    """Load high scores from JSON file."""
    if not os.path.exists(HIGHSCORES_FILE):
        return []
    try:
        with open(HIGHSCORES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load high scores: {e}")
        return []

def save_highscores(scores):
    """Save high scores to JSON file."""
    try:
        with open(HIGHSCORES_FILE, 'w') as f:
            json.dump(scores, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save high scores: {e}")

def add_score(name, score, stars=0):
    """Add a new score to the high scores list with stars, sorted and limited to top 10."""
    scores = load_highscores()
    scores.append({"name": name, "score": score, "stars": stars})
    # Sort descending by score
    scores.sort(key=lambda x: x["score"], reverse=True)
    # Keep only top MAX_SCORES
    scores = scores[:MAX_SCORES]
    save_highscores(scores)
    return scores

def get_rank_for_score(score):
    """Get the rank of a score if it would be in the high scores list."""
    scores = load_highscores()
    if len(scores) < MAX_SCORES:
        return len(scores) + 1
    if score > scores[-1]["score"]:
        return len(scores)
    return None

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

# ============================================================================

# changed: wrap main loop so running the file is safe and controlled via CLI
def safe_load_model_and_scaler(force_no_model=False):
    global model, scaler
    model = None
    scaler = None
    if force_no_model:
        print("Info: --no-model specified; using heuristic AI only.")
        return
    if load_model is None:
        print("Info: Keras/TensorFlow not available; using heuristic AI.")
        return
    try:
        model = load_model("tf_model.h5")
    except FileNotFoundError:
        print("Warning: model file 'tf_model.h5' not found — falling back to heuristic AI.")
        model = None
    except Exception as e:
        print(f"Warning: failed to load model: {e}\nFalling back to heuristic AI.")
        model = None

    if joblib is None:
        print("Warning: joblib not installed; scaler cannot be loaded — heuristic AI will be used.")
        scaler = None
    else:
        try:
            scaler = joblib.load("scaler.joblib")
        except FileNotFoundError:
            print("Warning: scaler file 'scaler.joblib' not found — heuristic AI will be used.")
            scaler = None
        except Exception as e:
            print(f"Warning: failed to load scaler: {e}\nHeuristic AI will be used.")
            scaler = None

def main(argv=None):
    global PIPE_SPEED, AI_DIFFICULTY
    parser = argparse.ArgumentParser(description="Player vs AI Flappy demo (safe mode).")
    parser.add_argument("--difficulty", choices=["easy","normal","hard"], default="easy", help="AI difficulty")
    parser.add_argument("--no-model", action="store_true", help="Force heuristic AI (ignore tf_model.h5/scaler.joblib)")
    parser.add_argument("--auto-reset", action="store_true", help="Automatically restart after a crash (unsafe for manual testing)")
    args = parser.parse_args(argv)
    AI_DIFFICULTY = args.difficulty
    safe_load_model_and_scaler(force_no_model=args.no_model)

    current_player_name = "Player"
    app_state = "menu"  # States: menu, name_input, game, game_over, high_scores
    game = new_game()
    PIPE_SPEED = 5
    running = True
    
    # Text input for player name
    input_text = ""
    input_active = False
    
    # Create menu buttons
    btn_start = Button(WIDTH//2 - 100, 200, 200, 50, "START GAME")
    btn_high_scores = Button(WIDTH//2 - 100, 280, 200, 50, "HIGH SCORES")
    btn_change_name = Button(WIDTH//2 - 100, 360, 200, 50, "CHANGE NAME", (150, 150, 200))
    btn_quit = Button(WIDTH//2 - 100, 440, 200, 50, "QUIT", (200, 100, 100))
    
    # High scores buttons
    btn_menu_from_scores = Button(WIDTH//2 - 95, HEIGHT - 80, 75, 40, "MENU", (100, 200, 100))
    btn_change_from_scores = Button(WIDTH//2 + 20, HEIGHT - 80, 75, 40, "CHANGE", (150, 150, 200))
    
    # Game over buttons
    btn_menu_from_over = Button(WIDTH//2 - 100, 510, 180, 40, "RETURN TO MENU", (100, 200, 100))
    btn_play_again = Button(WIDTH//2 - 100, 560, 180, 40, "PLAY AGAIN", (100, 200, 255))
    
    try:
        while running:
            clock.tick(45)
            screen.blit(background, (0, 0))

            # ================================================================
            # MENU SCREEN
            # ================================================================
            if app_state == "menu":
                # Title with larger font
                title_surf = pygame.font.SysFont("Arial", 56, bold=True).render("Flappy AI", True, (255, 215, 0))
                title_rect = title_surf.get_rect(center=(WIDTH//2, 80))
                screen.blit(title_surf, title_rect)
                
                # Separator line
                pygame.draw.line(screen, (255, 215, 0), (40, 130), (WIDTH-40, 130), 2)
                
                # Get mouse position for hover effect
                mouse_pos = pygame.mouse.get_pos()
                btn_start.update_hover(mouse_pos)
                btn_high_scores.update_hover(mouse_pos)
                btn_change_name.update_hover(mouse_pos)
                btn_quit.update_hover(mouse_pos)
                
                # Draw buttons
                btn_start.draw(screen)
                btn_high_scores.draw(screen)
                btn_change_name.draw(screen)
                btn_quit.draw(screen)
                
                # Bottom separator and player info
                pygame.draw.line(screen, (255, 215, 0), (40, HEIGHT-70), (WIDTH-40, HEIGHT-70), 2)
                
                player_label = pygame.font.SysFont("Arial", 16).render("CURRENT PLAYER:", True, (200, 200, 200))
                label_rect = player_label.get_rect(center=(WIDTH//2, HEIGHT-50))
                screen.blit(player_label, label_rect)
                
                player_name_surf = pygame.font.SysFont("Arial", 28, bold=True).render(current_player_name, True, (100, 255, 100))
                name_rect = player_name_surf.get_rect(center=(WIDTH//2, HEIGHT-20))
                screen.blit(player_name_surf, name_rect)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    # Handle mouse click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if btn_start.is_clicked(event.pos):
                            app_state = "game"
                            game = new_game()
                            PIPE_SPEED = 5
                        elif btn_high_scores.is_clicked(event.pos):
                            app_state = "high_scores"
                        elif btn_change_name.is_clicked(event.pos):
                            app_state = "name_input"
                            input_text = current_player_name
                            input_active = True
                        elif btn_quit.is_clicked(event.pos):
                            running = False
                    # Handle touch input (mobile)
                    if event.type == pygame.FINGERDOWN:
                        touch_pos = (int(event.x * WIDTH), int(event.y * HEIGHT))
                        if btn_start.is_clicked(touch_pos):
                            app_state = "game"
                            game = new_game()
                            PIPE_SPEED = 5
                        elif btn_high_scores.is_clicked(touch_pos):
                            app_state = "high_scores"
                        elif btn_change_name.is_clicked(touch_pos):
                            app_state = "name_input"
                            input_text = current_player_name
                            input_active = True
                        elif btn_quit.is_clicked(touch_pos):
                            running = False
                    # Keep keyboard as fallback
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_s:
                            app_state = "game"
                            game = new_game()
                            PIPE_SPEED = 5
                        elif event.key == pygame.K_h:
                            app_state = "high_scores"
                        elif event.key == pygame.K_q:
                            running = False
                        elif event.key == pygame.K_c:
                            app_state = "name_input"
                            input_text = current_player_name
                            input_active = True

            # ================================================================
            # NAME INPUT SCREEN
            # ================================================================
            elif app_state == "name_input":
                # Title
                title_surf = pygame.font.SysFont("Arial", 48, bold=True).render("Enter Player Name", True, (255, 215, 0))
                title_rect = title_surf.get_rect(center=(WIDTH//2, 80))
                screen.blit(title_surf, title_rect)
                
                # Separator line
                pygame.draw.line(screen, (255, 215, 0), (40, 140), (WIDTH-40, 140), 2)
                
                # Input box with better styling
                input_rect = pygame.Rect(WIDTH//2 - 130, 220, 260, 50)
                pygame.draw.rect(screen, (50, 50, 50), input_rect)
                pygame.draw.rect(screen, (255, 215, 0), input_rect, 3)
                
                # Render input text centered with smaller font to fit
                input_surf = pygame.font.SysFont("Arial", 26).render(input_text[:20], True, (255, 255, 255))
                input_text_rect = input_surf.get_rect(center=(input_rect.centerx, input_rect.centery))
                screen.blit(input_surf, input_text_rect)
                
                # Cursor
                cursor_x = input_text_rect.right + 5
                pygame.draw.line(screen, (255, 255, 255), (cursor_x, input_rect.top + 10), (cursor_x, input_rect.bottom - 10), 2)
                
                # Instructions
                instr1 = pygame.font.SysFont("Arial", 18).render("Type your name (max 20 characters)", True, (200, 200, 200))
                instr1_rect = instr1.get_rect(center=(WIDTH//2, 330))
                screen.blit(instr1, instr1_rect)
                
                # Confirm/Cancel instructions
                confirm_surf = pygame.font.SysFont("Arial", 16, bold=True).render("[ENTER] Confirm  |  [ESC] Cancel", True, (100, 200, 100))
                confirm_rect = confirm_surf.get_rect(center=(WIDTH//2, HEIGHT - 60))
                screen.blit(confirm_surf, confirm_rect)
                
                # Character count
                char_count = pygame.font.SysFont("Arial", 14).render(f"Characters: {len(input_text)}/20", True, (150, 150, 150))
                char_rect = char_count.get_rect(center=(WIDTH//2, HEIGHT - 30))
                screen.blit(char_count, char_rect)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if input_text.strip():
                                current_player_name = input_text.strip()
                            app_state = "menu"
                            input_text = ""
                        elif event.key == pygame.K_ESCAPE:
                            app_state = "menu"
                            input_text = ""
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            # Add character to input
                            if len(input_text) < 20:
                                if event.unicode.isprintable():
                                    input_text += event.unicode

            # ================================================================
            # HIGH SCORES SCREEN
            # ================================================================
            elif app_state == "high_scores":
                # Title
                title_surf = pygame.font.SysFont("Arial", 52, bold=True).render("HIGH SCORES", True, (255, 215, 0))
                title_rect = title_surf.get_rect(center=(WIDTH//2, 50))
                screen.blit(title_surf, title_rect)
                
                # Separator line
                pygame.draw.line(screen, (255, 215, 0), (40, 100), (WIDTH-40, 100), 2)
                
                scores = load_highscores()
                
                if not scores:
                    no_scores = pygame.font.SysFont("Arial", 32).render("No scores yet!", True, (150, 150, 150))
                    no_rect = no_scores.get_rect(center=(WIDTH//2, HEIGHT//2))
                    screen.blit(no_scores, no_rect)
                    
                    hint = pygame.font.SysFont("Arial", 20).render("Start a game to see scores appear here", True, (100, 100, 100))
                    hint_rect = hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
                    screen.blit(hint, hint_rect)
                else:
                    # Header
                    header_y = 130
                    header_font = pygame.font.SysFont("Arial", 18, bold=True)
                    
                    # Column headers with better spacing
                    rank_header = header_font.render("Rank", True, (255, 215, 0))
                    rank_rect = rank_header.get_rect(topleft=(20, header_y))
                    screen.blit(rank_header, rank_rect)
                    
                    name_header = header_font.render("Player Name", True, (255, 215, 0))
                    name_rect = name_header.get_rect(topleft=(70, header_y))
                    screen.blit(name_header, name_rect)
                    
                    score_header = header_font.render("Score", True, (255, 215, 0))
                    score_rect = score_header.get_rect(topleft=(240, header_y))
                    screen.blit(score_header, score_rect)
                    
                    stars_header = header_font.render("Stars", True, (255, 215, 0))
                    stars_rect = stars_header.get_rect(topleft=(310, header_y))
                    screen.blit(stars_header, stars_rect)
                    
                    # Separator line below header
                    pygame.draw.line(screen, (100, 100, 100), (40, 160), (WIDTH-40, 160), 1)
                    
                    # Draw scores
                    entry_font = pygame.font.SysFont("Arial", 18)
                    y_pos = 180
                    
                    # Column widths for fixed layout
                    rank_col_width = 40
                    name_col_width = 150
                    score_col_width = 60
                    stars_col_width = 100
                    
                    for idx, entry in enumerate(scores, 1):
                        # Draw background row boxes
                        if idx % 2 == 0:
                            pygame.draw.rect(screen, (30, 30, 40), (20, y_pos - 5, WIDTH - 40, 35))
                        
                        # Rank box with medal
                        rank_box = pygame.Rect(20, y_pos - 5, rank_col_width, 35)
                        if idx == 1:
                            color = (255, 215, 0)
                        elif idx == 2:
                            color = (192, 192, 192)
                        elif idx == 3:
                            color = (205, 127, 50)
                        else:
                            color = (200, 200, 200)
                        
                        rank_text = entry_font.render(f"{idx}.", True, color)
                        rank_rect = rank_text.get_rect(center=(rank_box.centerx, rank_box.centery))
                        screen.blit(rank_text, rank_rect)
                        
                        # Name box - max 10 characters with smaller font
                        name_box = pygame.Rect(rank_col_width + 20, y_pos - 5, name_col_width, 35)
                        display_name = entry["name"][:10]
                        name_text = entry_font.render(display_name, True, (100, 200, 255))
                        name_rect = name_text.get_rect(topleft=(name_box.left + 5, name_box.centery - name_text.get_height()//2))
                        screen.blit(name_text, name_rect)
                        
                        # Score box
                        score_box = pygame.Rect(rank_col_width + name_col_width + 20, y_pos - 5, score_col_width, 35)
                        score_text = entry_font.render(str(entry["score"]), True, (150, 255, 150))
                        score_rect = score_text.get_rect(center=(score_box.centerx, score_box.centery))
                        screen.blit(score_text, score_rect)
                        
                        # Stars box
                        stars_box = pygame.Rect(rank_col_width + name_col_width + score_col_width + 20, y_pos - 5, stars_col_width, 35)
                        stars = entry.get("stars", 0)
                        stars_display = "⭐ " * stars if stars > 0 else "-"
                        stars_text = entry_font.render(stars_display[:15], True, (255, 215, 0))
                        stars_rect = stars_text.get_rect(center=(stars_box.centerx, stars_box.centery))
                        screen.blit(stars_text, stars_rect)
                        
                        y_pos += 35
                        
                        if y_pos > HEIGHT - 100:
                            break
                
                # Bottom separator
                pygame.draw.line(screen, (255, 215, 0), (40, HEIGHT-70), (WIDTH-40, HEIGHT-70), 2)
                
                # Get mouse position for button hover
                mouse_pos = pygame.mouse.get_pos()
                btn_menu_from_scores.update_hover(mouse_pos)
                btn_change_from_scores.update_hover(mouse_pos)
                
                # Draw buttons
                btn_menu_from_scores.draw(screen)
                btn_change_from_scores.draw(screen)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    # Handle mouse click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if btn_menu_from_scores.is_clicked(event.pos):
                            app_state = "menu"
                        elif btn_change_from_scores.is_clicked(event.pos):
                            app_state = "name_input"
                            input_text = current_player_name
                            input_active = True
                    # Handle touch input
                    if event.type == pygame.FINGERDOWN:
                        touch_pos = (int(event.x * WIDTH), int(event.y * HEIGHT))
                        if btn_menu_from_scores.is_clicked(touch_pos):
                            app_state = "menu"
                        elif btn_change_from_scores.is_clicked(touch_pos):
                            app_state = "name_input"
                            input_text = current_player_name
                            input_active = True
                    # Keep keyboard as fallback
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m:
                            app_state = "menu"
                        elif event.key == pygame.K_c:
                            app_state = "name_input"
                            input_text = current_player_name
                            input_active = True

            # ================================================================
            # GAMEPLAY
            # ================================================================
            elif app_state == "game":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    # Handle mouse click for jump/start
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if not game["started"]:
                            game["started"] = True
                            game["end_time"] = None
                        else:
                            if game["player_alive"] and game["end_time"] is None and not game.get("paused", False):
                                game["p_velocity"] = JUMP
                        if game["end_time"] is not None:
                            app_state = "game_over"
                    # Handle touch input for jump/start
                    if event.type == pygame.FINGERDOWN:
                        if not game["started"]:
                            game["started"] = True
                            game["end_time"] = None
                        else:
                            if game["player_alive"] and game["end_time"] is None and not game.get("paused", False):
                                game["p_velocity"] = JUMP
                        if game["end_time"] is not None:
                            app_state = "game_over"
                    # Keep keyboard as fallback
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            # If game not started, start on SPACE
                            if not game["started"]:
                                game["started"] = True
                                game["end_time"] = None
                            else:
                                # normal player jump when playing
                                if game["player_alive"] and game["end_time"] is None and not game.get("paused", False):
                                    game["p_velocity"] = JUMP
                            # if game over, go to game over screen on SPACE
                            if game["end_time"] is not None:
                                app_state = "game_over"
                                continue
                        if event.key == pygame.K_p:
                            # toggle pause when game started and not ended
                            if game["started"] and game["end_time"] is None:
                                game["paused"] = not game.get("paused", False)
                        if event.key == pygame.K_r:
                            # manual restart to menu
                            app_state = "menu"
                            continue

                # only update game physics when started, not paused, and not finished
                if game["started"] and not game.get("paused", False) and game["end_time"] is None:
                    # player physics
                    if game["player_alive"]:
                        game["p_velocity"] += GRAVITY
                        game["p_bird_y"] += game["p_velocity"]

                    # ai decision + physics
                    if game["ai_alive"]:
                        pipe_bottom = game["pipe_top"] + PIPE_GAP

                        # difficulty parameters
                        diff_threshold = {'easy': 0.8, 'normal': 0.5, 'hard': 0.35}.get(AI_DIFFICULTY, 0.5)
                        heuristic_margin = {'easy': 20.0, 'normal': 0.0, 'hard': -10.0}.get(AI_DIFFICULTY, 0.0)

                        # If model or scaler missing, use a simple heuristic: jump when bird is below gap center plus a margin.
                        if model is None or scaler is None:
                            gap_center = (game["pipe_top"] + pipe_bottom) / 2.0
                            if game["a_bird_y"] > gap_center + heuristic_margin:
                                game["a_velocity"] = JUMP
                        else:
                            feats = make_features(game["a_bird_y"], game["pipe_top"], pipe_bottom, game["pipe_x"])
                            try:
                                feats_scaled = scaler.transform(feats.reshape(1, -1))
                                prob = float(model.predict(feats_scaled, verbose=0)[0][0])
                                if prob > diff_threshold:
                                    game["a_velocity"] = JUMP
                            except Exception as e:
                                # On any runtime error with model/scaler, fallback to heuristic
                                print(f"Model runtime error: {e} — using heuristic AI this frame")
                                gap_center = (game["pipe_top"] + pipe_bottom) / 2.0
                                if game["a_bird_y"] > gap_center + heuristic_margin:
                                    game["a_velocity"] = JUMP

                        game["a_velocity"] += GRAVITY
                        game["a_bird_y"] += game["a_velocity"]

                    # pipe movement
                    game["pipe_x"] -= PIPE_SPEED
                    # scoring: when bird passes pipe
                    if (game["pipe_x"] + PIPE_WIDTH) < BIRD_X and not game.get("pipe_passed", False):
                        game["score"] += 1
                        game["pipe_passed"] = True

                    if game["pipe_x"] < -PIPE_WIDTH:
                        game["pipe_x"] = WIDTH
                        game["pipe_top"] = random.randint(60, 350)
                        game["pipe_passed"] = False
                        # gradually increase difficulty
                        PIPE_SPEED += 0.15

                pipe_bottom = game["pipe_top"] + PIPE_GAP

                # draw birds
                if game["player_alive"]:
                    pygame.draw.circle(screen, (255, 255, 0), (BIRD_X, int(game["p_bird_y"])), 15)

                # draw player name
                draw_outline_text("YOU", BIRD_X - 18, int(game["p_bird_y"]) - 35, (255,255,255))

                if game["ai_alive"]:
                    pygame.draw.circle(screen, (255,0,0), (BIRD_X+40, int(game["a_bird_y"])), 15)
                # draw AI name
                draw_outline_text("AI", BIRD_X + 40 - 10, int(game["a_bird_y"]) - 35, (255,255,0))

                # draw pipes (top and bottom). bottom height = remaining screen height
                if pipe_img is None:
                    pygame.draw.rect(screen, (0,200,0), (game["pipe_x"], 0, PIPE_WIDTH, game["pipe_top"]))
                    pygame.draw.rect(screen, (0,200,0), (game["pipe_x"], pipe_bottom, PIPE_WIDTH, HEIGHT - pipe_bottom))
                else:
                    top_h = max(1, int(game["pipe_top"]))
                    bottom_h = max(1, int(HEIGHT - pipe_bottom))
                    try:
                        top_surf = pygame.transform.scale(pipe_img, (PIPE_WIDTH, top_h))
                        top_surf = pygame.transform.flip(top_surf, False, True)
                        screen.blit(top_surf, (game["pipe_x"], 0))
                    except Exception:
                        pygame.draw.rect(screen, (0,200,0), (game["pipe_x"], 0, PIPE_WIDTH, game["pipe_top"]))
                    try:
                        bottom_surf = pygame.transform.scale(pipe_img, (PIPE_WIDTH, bottom_h))
                        screen.blit(bottom_surf, (game["pipe_x"], pipe_bottom))
                    except Exception:
                        pygame.draw.rect(screen, (0,200,0), (game["pipe_x"], pipe_bottom, PIPE_WIDTH, HEIGHT - pipe_bottom))

                # collision check
                def check_collision(bird_x, bird_y):
                    # bird represented as a circle with radius 15
                    r = 15
                    bird_top = bird_y - r
                    bird_bottom = bird_y + r
                    bird_left = bird_x - r
                    bird_right = bird_x + r

                    pipe_left = game["pipe_x"]
                    pipe_right = game["pipe_x"] + PIPE_WIDTH

                    # horizontal overlap between bird and pipe
                    hit_pipe_x = (bird_right > pipe_left) and (bird_left < pipe_right)

                    # vertical overlap with pipes (true if bird is above bottom of top pipe OR below top of bottom pipe)
                    hit_pipe_y = (bird_top < game["pipe_top"]) or (bird_bottom > pipe_bottom)

                    # out of bounds if bird touches floor or ceiling
                    out = (bird_bottom >= HEIGHT) or (bird_top <= 0)

                    return (hit_pipe_x and hit_pipe_y) or out

                if game["player_alive"] and check_collision(BIRD_X, game["p_bird_y"]):
                    game["player_alive"] = False
                    game["end_time"] = time.time()
                if game["ai_alive"] and check_collision(BIRD_X+40, game["a_bird_y"]):
                    game["ai_alive"] = False
                    game["end_time"] = time.time()

                # draw UI
                # Score and stats
                draw_center_text(f"Score: {game['score']}", 26, (255,255,255))
                draw_center_text(f"Player: {current_player_name}", HEIGHT - 30, (200,255,200))

                if game["end_time"]:
                    if not game["player_alive"] and game["ai_alive"]:
                        draw_text("AI Wins! You Lost 💀", HEIGHT//2 - 10, (255, 0, 0))
                    elif not game["ai_alive"] and game["player_alive"]:
                        draw_text("You Win! AI Lost 🏆", HEIGHT//2 - 10, (0, 200, 0))
                    else:
                        draw_text("Draw! Both crashed.", HEIGHT//2 - 10, (200,200,200))
                    draw_center_text("Press SPACE to save score", HEIGHT//2 + 30, (255,255,255))

                # start screen
                if not game["started"]:
                    draw_center_text("Flappy AI", HEIGHT//2 - 40, (255,255,255))
                    draw_center_text("Press SPACE to start", HEIGHT//2 + 10, (255,255,255))
                    draw_center_text("P to pause — R to menu", HEIGHT//2 + 50, (240,240,240))

            # ================================================================
            # GAME OVER SCREEN
            # ================================================================
            elif app_state == "game_over":
                # Determine if player won
                player_won = not game["ai_alive"] and game["player_alive"]
                stars_earned = calculate_stars(game['score']) if player_won else 0
                
                # Title
                title_color = (100, 255, 100) if player_won else (255, 100, 100)
                title_text = "VICTORY!" if player_won else "GAME OVER"
                title_surf = pygame.font.SysFont("Arial", 56, bold=True).render(title_text, True, title_color)
                title_rect = title_surf.get_rect(center=(WIDTH//2, 50))
                screen.blit(title_surf, title_rect)
                
                # Separator line
                pygame.draw.line(screen, title_color, (40, 110), (WIDTH-40, 110), 2)
                
                # Result box
                result_y = 160
                box_color = (30, 40, 30) if player_won else (40, 30, 30)
                border_color = (100, 255, 100) if player_won else (255, 100, 100)
                pygame.draw.rect(screen, box_color, (30, result_y, WIDTH - 60, 240))
                pygame.draw.rect(screen, border_color, (30, result_y, WIDTH - 60, 240), 2)
                
                # Player name
                player_name_surf = pygame.font.SysFont("Arial", 26).render(f"Player: {current_player_name}", True, (100, 200, 255))
                player_rect = player_name_surf.get_rect(center=(WIDTH//2, result_y + 30))
                screen.blit(player_name_surf, player_rect)
                
                # Final score - large and prominent
                score_surf = pygame.font.SysFont("Arial", 48, bold=True).render(f"{game['score']}", True, (255, 255, 100))
                score_rect = score_surf.get_rect(center=(WIDTH//2, result_y + 95))
                screen.blit(score_surf, score_rect)
                
                score_label = pygame.font.SysFont("Arial", 20).render("FINAL SCORE", True, (200, 200, 200))
                label_rect = score_label.get_rect(center=(WIDTH//2, result_y + 140))
                screen.blit(score_label, label_rect)
                
                # Star reward display (only if player won)
                if player_won:
                    # Draw stars
                    stars_text = " ".join(["⭐"] * stars_earned)
                    stars_surf = pygame.font.SysFont("Arial", 36).render(stars_text, True, (255, 215, 0))
                    stars_rect = stars_surf.get_rect(center=(WIDTH//2, result_y + 185))
                    screen.blit(stars_surf, stars_rect)
                    
                    star_label = pygame.font.SysFont("Arial", 16).render(f"REWARD: {stars_earned} STAR{'S' if stars_earned != 1 else ''}", True, (255, 215, 0))
                    star_label_rect = star_label.get_rect(center=(WIDTH//2, result_y + 220))
                    screen.blit(star_label, star_label_rect)
                else:
                    defeat_msg = pygame.font.SysFont("Arial", 18).render("You were defeated by the AI", True, (255, 150, 150))
                    defeat_rect = defeat_msg.get_rect(center=(WIDTH//2, result_y + 195))
                    screen.blit(defeat_msg, defeat_rect)
                
                # Check if this is a high score
                rank = get_rank_for_score(game['score'])
                if rank and game['score'] > 0:
                    rank_text = pygame.font.SysFont("Arial", 22, bold=True).render(f"🎉 Rank #{rank} - NEW HIGH SCORE! 🎉", True, (255, 215, 0))
                    rank_rect = rank_text.get_rect(center=(WIDTH//2, 420))
                    screen.blit(rank_text, rank_rect)
                else:
                    if player_won:
                        no_rank = pygame.font.SysFont("Arial", 18).render("Keep playing to make the high scores!", True, (150, 150, 150))
                    else:
                        no_rank = pygame.font.SysFont("Arial", 18).render("Keep practicing to defeat the AI!", True, (150, 150, 150))
                    no_rank_rect = no_rank.get_rect(center=(WIDTH//2, 420))
                    screen.blit(no_rank, no_rank_rect)
                
                # Separator line
                pygame.draw.line(screen, border_color, (40, 460), (WIDTH-40, 460), 2)
                
                # Get mouse position for button hover
                mouse_pos = pygame.mouse.get_pos()
                btn_menu_from_over.update_hover(mouse_pos)
                btn_play_again.update_hover(mouse_pos)
                
                # Draw buttons
                btn_menu_from_over.draw(screen)
                btn_play_again.draw(screen)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    # Handle mouse click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if btn_menu_from_over.is_clicked(event.pos):
                            add_score(current_player_name, game['score'], stars_earned)
                            app_state = "menu"
                        elif btn_play_again.is_clicked(event.pos):
                            add_score(current_player_name, game['score'], stars_earned)
                            app_state = "game"
                            game = new_game()
                            PIPE_SPEED = 5
                    # Handle touch input
                    if event.type == pygame.FINGERDOWN:
                        touch_pos = (int(event.x * WIDTH), int(event.y * HEIGHT))
                        if btn_menu_from_over.is_clicked(touch_pos):
                            add_score(current_player_name, game['score'], stars_earned)
                            app_state = "menu"
                        elif btn_play_again.is_clicked(touch_pos):
                            add_score(current_player_name, game['score'], stars_earned)
                            app_state = "game"
                            game = new_game()
                            PIPE_SPEED = 5
                    # Keep keyboard as fallback
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m:
                            # Save score before returning to menu
                            add_score(current_player_name, game['score'], stars_earned)
                            app_state = "menu"
                        elif event.key == pygame.K_p:
                            # Save score and start new game
                            add_score(current_player_name, game['score'], stars_earned)
                            app_state = "game"
                            game = new_game()
                            PIPE_SPEED = 5

            pygame.display.update()

    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()
