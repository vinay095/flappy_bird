import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Game window
WIDTH, HEIGHT = 360, 640
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

import sys

def resource_path(relative_path):
    """ Get absolute path to resource """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Load images
BIRD_IMG = pygame.image.load(resource_path("flappybird.png"))
BG_IMG = pygame.image.load(resource_path("flappybirdbg.png"))
TOP_PIPE_IMG = pygame.image.load(resource_path("toppipe.png"))
BOTTOM_PIPE_IMG = pygame.image.load(resource_path("bottompipe.png"))

# Resize assets
BIRD_IMG = pygame.transform.scale(BIRD_IMG, (34, 24))
TOP_PIPE_IMG = pygame.transform.scale(TOP_PIPE_IMG, (64, 512))
BOTTOM_PIPE_IMG = pygame.transform.scale(BOTTOM_PIPE_IMG, (64, 512))
BG_IMG = pygame.transform.scale(BG_IMG, (WIDTH, HEIGHT))

# Game variables
FPS = 60
GRAVITY = 0.6
JUMP_VELOCITY = -9
PIPE_GAP = random.randint(130, 180)
PIPE_FREQUENCY_RANGE = (1200, 1700)  # a tuple
next_pipe_interval = random.randint(*PIPE_FREQUENCY_RANGE)  # ms
HIGH_SCORE_FILE = "highscore.txt"

# Bird class
class Bird:
    def __init__(self):
        self.x = WIDTH // 8
        self.y = HEIGHT // 2
        self.width = 34
        self.height = 24
        self.velocity_y = 0

    def move(self):
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        if self.y < 0:
            self.y = 0

    def jump(self):
        self.velocity_y = JUMP_VELOCITY

    def get_rect(self):
        return pygame.Rect(self.x, int(self.y), self.width, self.height)

# Pipe class
class Pipe:
    def __init__(self, x, y, is_top):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 512
        self.is_top = is_top
        self.passed = False
        self.image = TOP_PIPE_IMG if is_top else BOTTOM_PIPE_IMG

    def move(self, velocity):
        self.x += velocity

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Load high score
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

# Save high score
def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

# Place a new pair of pipes
def place_pipes(pipes):
    top_y = random.randint(-400, -100)
    bottom_y = top_y + 512 + PIPE_GAP
    pipes.append(Pipe(WIDTH, top_y, True))
    pipes.append(Pipe(WIDTH, bottom_y, False))

# Game loop
def main():
    clock = pygame.time.Clock()
    run = True
    game_state = "START"

    bird = Bird()
    pipes = []
    score = 0
    high_score = load_high_score()
    last_pipe_time = pygame.time.get_ticks()
    next_pipe_interval = random.randint(*PIPE_FREQUENCY_RANGE)  # Initialize here!

    font = pygame.font.SysFont("Consolas", 24)
    big_font = pygame.font.SysFont("Consolas", 24)

    while run:
        clock.tick(FPS)
        WIN.blit(BG_IMG, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if game_state == "START":
                    game_state = "PLAYING"
                    pipes.clear()
                    score = 0
                    bird = Bird()
                    last_pipe_time = pygame.time.get_ticks()
                    next_pipe_interval = random.randint(*PIPE_FREQUENCY_RANGE)  # Reset interval on start
                elif game_state == "PLAYING":
                    bird.jump()
                elif game_state == "GAME_OVER":
                    game_state = "START"
                    bird = Bird()
                    pipes.clear()
                    score = 0

        if game_state == "START":
            text = big_font.render("Press SPACE to Start", True, (255, 255, 255))
            WIN.blit(text, (50, HEIGHT // 2 - 50))
            WIN.blit(font.render(f"High Score: {high_score}", True, (255, 255, 255)), (10, 30))

        elif game_state == "PLAYING":
            current_time = pygame.time.get_ticks()
            if current_time - last_pipe_time > next_pipe_interval:
                global PIPE_GAP  # If you want to change it globally (optional)
                PIPE_GAP = random.randint(130, 180)
                place_pipes(pipes)
                last_pipe_time = current_time
                next_pipe_interval = random.randint(*PIPE_FREQUENCY_RANGE)

            for pipe in pipes:
                pipe.move(-4)
                WIN.blit(pipe.image, (pipe.x, pipe.y))

            pipes = [pipe for pipe in pipes if pipe.x + pipe.width > 0]

            bird_rect = bird.get_rect()
            for pipe in pipes:
                if bird_rect.colliderect(pipe.get_rect()):
                    game_state = "GAME_OVER"
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                    break

            if bird.y > HEIGHT:
                game_state = "GAME_OVER"
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)

            for pipe in pipes:
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    if not pipe.is_top:
                        score += 1

            bird.move()
            WIN.blit(BIRD_IMG, (bird.x, int(bird.y)))

            WIN.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 50))
            WIN.blit(font.render(f"High Score: {high_score}", True, (255, 255, 255)), (10, 25))

        elif game_state == "GAME_OVER":
            WIN.blit(BIRD_IMG, (bird.x, int(bird.y)))
            for pipe in pipes:
                WIN.blit(pipe.image, (pipe.x, pipe.y))
            WIN.blit(big_font.render("Game Over", True, (255, 0, 0)), (WIDTH // 2 - 50, HEIGHT // 2 - 20))
            WIN.blit(font.render("Press SPACE to Restart", True, (255, 255, 255)), (40, HEIGHT // 2 + 20))
            WIN.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 50))
            WIN.blit(font.render(f"High Score: {high_score}", True, (255, 255, 255)), (10, 25))

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
