# record_game_improved.py
import pygame
import csv
import random
import os

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BIRD_X = 50
GRAVITY = 0.4
JUMP = -7
PIPE_GAP = 150
PIPE_WIDTH = 60
PIPE_SPEED = 5   # a bit faster for more challenging data

OUT_FILE = "training_data_improved.csv"

# remove old file if you want fresh dataset
if os.path.exists(OUT_FILE):
    print(f"Appending to existing {OUT_FILE}. Delete it to start fresh.")

gameplay_data = []

def new_game():
    return {
        "bird_y": HEIGHT // 2,
        "velocity": 0,
        "pipe_x": WIDTH,
        "pipe_top": random.randint(60, 350),
    }

game = new_game()
running = True

while running:
    clock.tick(40)  # higher FPS -> smoother data
    screen.fill((135, 206, 235))

    action = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game["velocity"] = JUMP
            action = 1

    # bird physics
    game["velocity"] += GRAVITY
    game["bird_y"] += game["velocity"]

    # pipe movement
    game["pipe_x"] -= PIPE_SPEED
    if game["pipe_x"] < -PIPE_WIDTH:
        game["pipe_x"] = WIDTH
        game["pipe_top"] = random.randint(60, 350)

    pipe_bottom = game["pipe_top"] + PIPE_GAP

    # compute improved features
    distance_to_pipe = game["pipe_x"] - BIRD_X
    gap_center = (game["pipe_top"] + pipe_bottom) / 2.0
    gap_size = PIPE_GAP

    # draw
    pygame.draw.circle(screen, (255, 255, 0), (BIRD_X, int(game["bird_y"])), 15)
    pygame.draw.rect(screen, (0, 200, 0), (game["pipe_x"], 0, PIPE_WIDTH, game["pipe_top"]))
    pygame.draw.rect(screen, (0, 200, 0), (game["pipe_x"], pipe_bottom, PIPE_WIDTH, HEIGHT))

    # record frame (use floats)
    gameplay_data.append([
        float(game["bird_y"]),
        float(game["pipe_top"]),
        float(pipe_bottom),
        float(game["pipe_x"]),
        float(distance_to_pipe),
        float(gap_center),
        float(gap_size),
        int(action)
    ])

    pygame.display.update()

pygame.quit()

# save CSV (append if file exists)
header = ["bird_y", "top_pipe_y", "bottom_pipe_y", "pipe_x", "distance_to_pipe", "gap_center", "gap_size", "action"]
write_mode = "a" if os.path.exists(OUT_FILE) else "w"
with open(OUT_FILE, write_mode, newline="") as f:
    import csv
    writer = csv.writer(f)
    if write_mode == "w":
        writer.writerow(header)
    writer.writerows(gameplay_data)

print(f"Saved {len(gameplay_data)} rows to {OUT_FILE}")
