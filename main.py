import pygame
import random
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# Bird
bird_x = 50
bird_y = 300
bird_vel = 0
gravity = 0.5

# Pipes
pipe_width = 70
gap = 150
pipe_x = 400
pipe_height = random.randint(100, 400)
pipe_speed = 3

score = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_vel = -8

    # Bird physics
    bird_vel += gravity
    bird_y += bird_vel

    # Keep bird inside screen
    if bird_y < 0:
        bird_y = 0
        bird_vel = 0

    if bird_y > HEIGHT - 30:
        bird_y = HEIGHT - 30
        bird_vel = 0

    # Move pipes
    pipe_x -= pipe_speed

    # Reset pipes when going off-screen
    if pipe_x < -pipe_width:
        pipe_x = WIDTH
        pipe_height = random.randint(100, 400)
        score += 1

    # Collision detection
    bird_rect = pygame.Rect(bird_x - 15, bird_y - 15, 30, 30)
    top_pipe = pygame.Rect(pipe_x, 0, pipe_width, pipe_height)
    bottom_pipe = pygame.Rect(pipe_x, pipe_height + gap, pipe_width, HEIGHT)

    if bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe):
        print("GAME OVER")
        pygame.quit()
        sys.exit()

    # Draw everything
    screen.fill((135, 206, 235))

    # Bird
    pygame.draw.circle(screen, (255, 255, 0), (bird_x, int(bird_y)), 15)

    # Pipes
    pygame.draw.rect(screen, (0, 255, 0), top_pipe)
    pygame.draw.rect(screen, (0, 255, 0), bottom_pipe)

    # Score
    text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.update()
    clock.tick(60)
