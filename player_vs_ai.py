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

    game = new_game()
    PIPE_SPEED = 5
    running = True
    try:
        while running:
            clock.tick(45)
            screen.blit(background, (0, 0))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
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
                        # if game over, restart on SPACE (manual)
                        if game["end_time"] is not None:
                            game = new_game()
                            PIPE_SPEED = 5
                            continue
                    if event.key == pygame.K_p:
                        # toggle pause when game started and not ended
                        if game["started"] and game["end_time"] is None:
                            game["paused"] = not game.get("paused", False)
                    if event.key == pygame.K_r:
                        # manual restart
                        game = new_game()
                        PIPE_SPEED = 5

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
            

            if game["end_time"]:
                if not game["player_alive"] and game["ai_alive"]:
                    draw_text("AI Wins! You Lost 💀", HEIGHT//2 - 10, (255, 0, 0))
                elif not game["ai_alive"] and game["player_alive"]:
                    draw_text("You Win! AI Lost 🏆", HEIGHT//2 - 10, (0, 200, 0))
                else:
                    draw_text("Draw! Both crashed.", HEIGHT//2 - 10, (200,200,200))
                # changed: don't auto-reset unless user asked
                if args.auto_reset:
                    # auto reset after 2 seconds
                    if time.time() - game["end_time"] > 2:
                        game = new_game()
                        PIPE_SPEED = 5
                else:
                    draw_center_text("Press R or SPACE to restart", HEIGHT//2 + 30, (255,255,255))

            # start screen
            if not game["started"]:
                draw_center_text("Flappy AI", HEIGHT//2 - 40, (255,255,255))
                draw_center_text("Press SPACE to start", HEIGHT//2 + 10, (255,255,255))
                draw_center_text("P to pause during play — R to restart", HEIGHT//2 + 50, (240,240,240))

            pygame.display.update()

            # allow manual restart with R (instant)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                game = new_game()
                PIPE_SPEED = 5
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()
