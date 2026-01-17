import pygame
import random

# ==================== CONFIG ====================
WIN_WIDTH = 700
WIN_HEIGHT = 500
FPS = 120  # Fast training speed

# Define the Curriculum Levels
LEVELS = [
    {"name": "Kindergarten", "hits": 10, "bot": 0.4},  # Slow bot, easy target
    {"name": "Amateur", "hits": 20, "bot": 0.7},  # Decent bot
    {"name": "Pro", "hits": 30, "bot": 1.0},  # Perfect bot
    {"name": "GOD MODE", "hits": 999, "bot": 1.2},  # Survival mode
]

MAX_STEPS = 6000  # Timeout to kill stuck genomes

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
pygame.font.init()
FONT = pygame.font.SysFont("comicsans", 24)


# ==================== GAME OBJECTS ====================
class Paddle:
    VEL = 5
    WIDTH = 20
    HEIGHT = 100

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)

    def move(self, up=True, speed=1.0):
        v = self.VEL * speed
        self.y += -v if up else v
        # Clamp to screen
        self.y = max(0, min(WIN_HEIGHT - self.HEIGHT, self.y))
        self.rect.y = self.y


class Ball:
    BASE_SPEED = 6
    RADIUS = 7

    def __init__(self):
        self.reset(1.0)

    def reset(self, difficulty):
        self.x = WIN_WIDTH // 2
        self.y = WIN_HEIGHT // 2

        # Speed increases slightly with difficulty
        self.speed = 1.0 + (difficulty * 0.1)

        # Ensure it doesn't spawn moving vertically perfectly
        self.x_vel = random.choice([-1, 1]) * self.BASE_SPEED
        self.y_vel = random.uniform(-4, 4)

    def move(self):
        self.x += self.x_vel * self.speed
        self.y += self.y_vel * self.speed


class Game:
    def __init__(self):
        self.left = Paddle(10, WIN_HEIGHT // 2 - 50)
        self.right = Paddle(WIN_WIDTH - 30, WIN_HEIGHT // 2 - 50)
        self.ball = Ball()
        self.hits = 0

    def loop(self, bot_skill):
        self.ball.move()

        # --- BOT LOGIC (Right Paddle) ---
        # Add error based on skill (1.0 = Perfect, 0.0 = Blind)
        error = (1 - bot_skill) * 150
        target = self.ball.y + random.uniform(-error, error)

        if target > self.right.y + Paddle.HEIGHT / 2:
            self.right.move(up=False, speed=bot_skill)
        elif target < self.right.y + Paddle.HEIGHT / 2:
            self.right.move(up=True, speed=bot_skill)

        # --- WALLS ---
        if self.ball.y <= 0:
            self.ball.y_vel = abs(self.ball.y_vel)
        elif self.ball.y >= WIN_HEIGHT:
            self.ball.y_vel = -abs(self.ball.y_vel)

        # --- LEFT PADDLE (AI) ---
        if self.ball.x_vel < 0:
            if (
                self.ball.y >= self.left.y
                and self.ball.y <= self.left.y + Paddle.HEIGHT
                and self.ball.x - Ball.RADIUS <= self.left.x + Paddle.WIDTH
            ):

                self.ball.x_vel *= -1
                self.hits += 1

                # PHYSICS FIX: Change angle based on hit position
                middle_y = self.left.y + Paddle.HEIGHT / 2
                diff_y = middle_y - self.ball.y
                # Map distance from center to angle (Max steepness 5)
                self.ball.y_vel = -1 * (diff_y / (Paddle.HEIGHT / 2) * 5)

                # Add randomness to prevent loops
                self.ball.y_vel += random.uniform(-1, 1)

        # --- RIGHT PADDLE (BOT) ---
        else:
            if (
                self.ball.y >= self.right.y
                and self.ball.y <= self.right.y + Paddle.HEIGHT
                and self.ball.x + Ball.RADIUS >= self.right.x
            ):

                self.ball.x_vel *= -1

                middle_y = self.right.y + Paddle.HEIGHT / 2
                diff_y = middle_y - self.ball.y
                self.ball.y_vel = -1 * (diff_y / (Paddle.HEIGHT / 2) * 5)
                self.ball.y_vel += random.uniform(-1, 1)

        # --- SCORING ---
        if self.ball.x < 0:
            return False  # AI Died
        if self.ball.x > WIN_WIDTH:
            self.ball.reset(bot_skill)  # Bot missed, reset but keep going

        return True

    def draw(self, win, level_name):
        win.fill(BLACK)
        pygame.draw.rect(win, WHITE, self.left.rect)
        pygame.draw.rect(win, WHITE, self.right.rect)
        pygame.draw.circle(
            win, WHITE, (int(self.ball.x), int(self.ball.y)), Ball.RADIUS
        )

        # UI
        text = FONT.render(f"{level_name} | Hits: {self.hits}", True, (255, 255, 0))
        win.blit(text, (10, 10))
