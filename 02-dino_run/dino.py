import pygame
import random
import os

# ---- Config
WIN_WIDTH = 1200
WIN_HEIGHT = 450
GROUND_Y = 430
VELOCITY = 0.6
FPS = 30

# Difficulty settings
BASE_SPEED = 10
MAX_SPEED = 25
POST_500_MAX_SPEED = 40

# Just a list for the 'known obstacles'.
obstacles = []

# ---- Colors
WHITE = (252, 251, 244)  # AWHHHHHH WHITE HURTS MY EYES!!!!!!!! (So this is white)
BLACK = (0, 0, 0)

# ---- Paths
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


# --- Scale
DINO_SCALE = (80, 90)
DUCK_SCALE = (110, 60)
BIRD_SCALE = (90, 70)
CACTUS_SCALE = (50, 90)


# Helper for the scales
def load_scale(name, scale):
    img = pygame.image.load(os.path.join(ASSETS_DIR, name))
    return pygame.transform.scale(img, scale)


# ---- Load assets with scale (alternating images)
RUNNING = [
    load_scale("dinorun.png", DINO_SCALE),
    load_scale("dinorun1.png", DINO_SCALE),
]

JUMPING = load_scale("dinoJump.png", DINO_SCALE)

DUCKING = [
    load_scale("dinoDuck.png", DUCK_SCALE),
    load_scale("dinoDuck1.png", DUCK_SCALE),
]

SMALL_CACTUS = [
    load_scale("cactusSmall.png", CACTUS_SCALE),
    load_scale("cactusSmallMany.png", (100, 90)),
]

LARGE_CACTUS = [load_scale("cactusBig.png", (70, 100))]

BIRD = [load_scale("bird.png", BIRD_SCALE), load_scale("bird2.png", BIRD_SCALE)]

pygame.init()
pygame.font.init()
FONT = pygame.font.SysFont("comicsans", 30)


class Dino:
    X_POS = 80
    Y_POS = GROUND_Y - DINO_SCALE[1]
    Y_POS_DUCK = GROUND_Y - DUCK_SCALE[1]
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.want_jump = False
        self.want_duck = False

        # State flags needed for changing image
        self.dino_duck = False
        self.dino_run = False
        self.dino_jump = False

        self.step_index = 0
        self.vel_y = 0
        self.image = self.run_img[0]  # start with index [0] for alternating

        # Hitting something ( boxes see def draw() for info)
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        # Inputs for animation states:
        if self.want_jump and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
            self.vel_y = -self.JUMP_VEL

        elif self.want_duck and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False

        elif not self.dino_jump:
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

        # reset intents every frame
        self.want_jump = False
        self.want_duck = False

    def duck(self):
        self.image = self.duck_img[
            (self.step_index // 5) % 2
        ]  # update every 5 frames and prevent crashing with %2
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img

        # Physics
        self.vel_y += VELOCITY  # Gravity (Adjust if needed)
        self.rect.y += self.vel_y * 4

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.dino_jump = False
            self.vel_y = 0

    def run(self):
        self.image = self.run_img[(self.step_index // 5) % 2]
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1

    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))
        # Uncomment to see hitboxes:
        # pygame.draw.rect(win, (255, 0, 0), self.rect, 2)


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()  # collision via rect
        self.rect.x = WIN_WIDTH

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, win):
        win.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):  # Inheriting from Obstacle.
    def __init__(self, image):
        self.type = random.randint(0, len(image) - 1)
        super().__init__(image, self.type)
        self.rect.bottom = GROUND_Y


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, len(image) - 1)
        super().__init__(image, self.type)
        self.rect.bottom = GROUND_Y


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0  # Start with first frame
        super().__init__(image, self.type)

        self.index = 0  # required for animations

        # Birds can fly at different heights
        self.rect.y = random.choice(
            [
                GROUND_Y - 400,  # Do nothing
                GROUND_Y - 135,  # Duck
                GROUND_Y - 80,  # Jump
            ]
        )

    def get_current_image(self):
        return self.image[(self.index // 5) % len(self.image)]

    def draw(self, win):
        # Animate Bird Wings
        if self.index >= 9:
            self.index = 0

        img_state = self.image[self.index // 5]
        win.blit(img_state, self.rect)
        self.index += 1

        # Also update Rect for collision (in case shape changes)
        # self.rect = img_state.get_rect() # (Optional, keeps hitbox precise)


def draw_window(win, dino, obstacles, score, speed):
    win.fill(WHITE)

    # Draw Ground Line
    pygame.draw.line(win, BLACK, (0, GROUND_Y), (WIN_WIDTH, GROUND_Y), 2)

    text = FONT.render(f"Points: {int(score)}", True, BLACK)
    win.blit(text, (1000, 20))
    text_speed = FONT.render(f"Speed: {int(speed)}", True, BLACK)
    win.blit(text_speed, (1000, 50))

    dino.draw(win)

    for obstacle in obstacles:
        obstacle.draw(win)

    pygame.display.update()


def spawn_obstacle_group(start_x):
    group = []

    # Patterns of obstacles (L=Large, S=Small)
    patterns = [
        ["L", "L"],
        ["S", "S", "S"],  # Classic triple small cactus
        ["L", "L", "L"],  # Triple large (Very hard)
        ["S", "L", "S"],  # Mixed
        ["L", "S", "L"],  # Mixed
    ]

    pattern = random.choice(patterns)

    # Current X position pointer
    current_x = start_x
    GAP = 5  # Small gap between cacti in a group

    for p in pattern:
        if p == "S":
            obs = SmallCactus(SMALL_CACTUS)
        else:
            obs = LargeCactus(LARGE_CACTUS)

        # Set the position
        obs.rect.x = current_x

        # Advance the pointer for the next cactus
        current_x += obs.rect.width + GAP

        group.append(obs)

    return group


def get_game_speed(score):
    if score < 500:
        return min(MAX_SPEED, BASE_SPEED + score * 0.03)
    return min(POST_500_MAX_SPEED, MAX_SPEED + (score - 500) * 0.04)


def main():
    global obstacles
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Dino Run Human")
    clock = pygame.time.Clock()

    dino = Dino()
    obstacles = []
    score = 0

    run = True
    while run:
        clock.tick(FPS)

        userInput = pygame.key.get_pressed()

        if userInput[pygame.K_SPACE]:
            dino.want_jump = True
        if userInput[pygame.K_DOWN]:
            dino.want_duck = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Remember '===', is with javascript!!!!!
                run = False

        dino.update(userInput)

        # --- Spawn obstacles ---
        if len(obstacles) == 0:
            speed = get_game_speed(score)
            r = random.random()

            # Spawn distance (Start off-screen)
            spawn_x = WIN_WIDTH + random.randint(100, 300)

            # 1. Bird (20% chance)
            if r < 0.2:
                obstacles.append(Bird(BIRD))
                obstacles[-1].rect.x = spawn_x  # Update bird pos

            # 2. Grouped Cacti (Only at high speeds, 50% chance)
            elif speed > 18 and r < 0.7:
                new_group = spawn_obstacle_group(spawn_x)
                obstacles.extend(new_group)

            # 3. Single Cactus (Default)
            else:
                if random.random() < 0.5:
                    obs = SmallCactus(SMALL_CACTUS)
                else:
                    obs = LargeCactus(LARGE_CACTUS)

                obs.rect.x = spawn_x
                obstacles.append(obs)

        # --- Update obstacles
        speed = get_game_speed(score)
        for obstacle in obstacles[:]:
            obstacle.update(speed)

            # Use Masks for Pixel-Perfect Collision
            dino_mask = pygame.mask.from_surface(dino.image)

            # For Animated Bird, we should technically get the current frame mask
            if isinstance(obstacle, Bird):
                obs_mask = pygame.mask.from_surface(obstacle.get_current_image())
            else:
                obs_mask = pygame.mask.from_surface(obstacle.image[obstacle.type])

            offset = (obstacle.rect.x - dino.rect.x, obstacle.rect.y - dino.rect.y)

            if dino_mask.overlap(obs_mask, offset):
                print("GAME OVER")
                run = False  # Or reset

            if obstacle.rect.right < 0:
                obstacles.remove(obstacle)

        score += speed * 0.015
        draw_window(win, dino, obstacles, score, speed)

    pygame.quit()


if __name__ == "__main__":
    main()
