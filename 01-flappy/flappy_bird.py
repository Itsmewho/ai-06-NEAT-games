import pygame
import random
import os


# ---- Config
WIN_WIDTH = 600
WIN_HEIGHT = 630
GROUND_Y = 630
PIPE_VEL = 5
GRAVITY = 0.15
LIFT = -7.2

pygame.init()
pygame.font.init()
FONT = pygame.font.SysFont("comicsans", 50)

# ---- Paths
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ---- Load assets
BIRD_IMG = pygame.image.load(os.path.join(ASSETS_DIR, "fatBird.png"))
PIPE_TOP_IMG = pygame.image.load(os.path.join(ASSETS_DIR, "full pipe top.png"))
PIPE_BOTTOM_IMG = pygame.image.load(os.path.join(ASSETS_DIR, "full pipe bottom.png"))

# Load bg
bg_raw = pygame.image.load(os.path.join(ASSETS_DIR, "background.png"))
# Scale it to fit the window exactly
BG_IMG = pygame.transform.scale(bg_raw, (WIN_WIDTH, WIN_HEIGHT))


class Bird:
    MAX_ROTATION = 25
    ROT_VEL = 15

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0
        self.tilt = 0
        self.tick_count = 0
        self.height = self.y
        self.img = BIRD_IMG
        self.rect = self.img.get_rect(center=(self.x, self.y))

    def jump(self):
        self.vel = LIFT
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel * self.tick_count + 1.5 * self.tick_count**2

        if d >= 16:
            d = 16
        if d < 0:
            d -= 2

        self.y += d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -35:
                self.tilt -= self.ROT_VEL

        self.rect.center = (self.x, int(self.y))

    def draw(self, win):
        rotated = pygame.transform.rotate(self.img, self.tilt)
        rect = rotated.get_rect(center=self.rect.center)
        win.blit(rotated, rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5
    MOVING_Y = False
    PULSING_GAP = False

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.GAP = Pipe.GAP
        self.VEL = Pipe.VEL

        self.y_dir = 1
        self.gap_dir = 1
        self.top_img = PIPE_TOP_IMG
        self.bottom_img = PIPE_BOTTOM_IMG
        self.top_rect = self.top_img.get_rect()
        self.bottom_rect = self.bottom_img.get_rect()
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 400)
        self.update_rects()

    def update_rects(self):
        top_y = self.height - self.top_img.get_height()
        bottom_y = self.height + self.GAP  # Uses instance GAP
        self.top_rect.topleft = (self.x, top_y)
        self.bottom_rect.topleft = (self.x, bottom_y)

    def move(self):
        self.x -= self.VEL

        if Pipe.MOVING_Y:
            self.height += self.y_dir * 4

            if self.height > 400:
                self.y_dir = -1
            if self.height < 50:
                self.y_dir = 1

        if Pipe.PULSING_GAP:
            self.GAP += self.gap_dir * 2
            if self.GAP > 220:
                self.gap_dir = -1
            if self.GAP < 150:
                self.gap_dir = 1

        self.update_rects()

    def draw(self, win):
        win.blit(self.top_img, self.top_rect)
        win.blit(self.bottom_img, self.bottom_rect)

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.top_img)
        bottom_mask = pygame.mask.from_surface(self.bottom_img)

        top_offset = (self.top_rect.x - bird.rect.x, self.top_rect.y - bird.rect.y)
        bottom_offset = (
            self.bottom_rect.x - bird.rect.x,
            self.bottom_rect.y - bird.rect.y,
        )

        return bird_mask.overlap(top_mask, top_offset) or bird_mask.overlap(
            bottom_mask, bottom_offset
        )


def draw_window(win, bird, pipes, score):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    bird.draw(win)
    pygame.draw.rect(win, (200, 200, 200), (0, GROUND_Y, WIN_WIDTH, 70))
    text = FONT.render(f"Score: {score}", True, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    pygame.display.update()


# --- HUMAN GAME LOOP  ---
def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Flappy Bird (Pro Mode)")
    clock = pygame.time.Clock()

    # Reset Difficulty
    Pipe.VEL = 5
    Pipe.MOVING_Y = False
    Pipe.PULSING_GAP = False

    bird = Bird(230, 350)
    pipes = [Pipe(600)]
    score = 0

    run = True
    while run:
        clock.tick(30)

        # --- DIFFICULTY CONTROLLER ---
        if score > 0 and score % 15 == 0:
            Pipe.VEL = min(10, 5 + (score // 15))
        if score > 50:
            Pipe.MOVING_Y = True
        if score > 200:
            Pipe.PULSING_GAP = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        bird.move()

        add_pipe = False
        rem = []
        for pipe in pipes:
            pipe.move()
            if pipe.collide(bird):
                run = False

            if pipe.x + pipe.top_rect.width < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        if bird.rect.bottom >= GROUND_Y or bird.rect.top <= 0:
            run = False

        draw_window(win, bird, pipes, score)

    pygame.quit()


if __name__ == "__main__":
    main()
