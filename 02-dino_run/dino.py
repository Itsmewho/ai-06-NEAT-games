import pygame
import random
import os

# ---- Config
WIN_WIDTH = 800
WIN_HEIGHT = 400
FPS = 30

# ---- Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ---- Paths
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ---- Load assets
BIRD = pygame.image.load(os.path.join(ASSETS_DIR, "bird.png"))
BIRD_TWO = pygame.image.load(os.path.join(ASSETS_DIR, "bird2.png"))
CACTUSBIG = pygame.image.load(os.path.join(ASSETS_DIR, "cactusBig.png"))
CACTUS_SMALL = pygame.image.load(os.path.join(ASSETS_DIR, "cactusSmall.png"))
CACTUS_SMALL_GROUP = pygame.image.load(os.path.join(ASSETS_DIR, "cactusSmallMany.png"))
DINO = pygame.image.load(os.path.join(ASSETS_DIR, "dino.png"))
DINO_DEAD = pygame.image.load(os.path.join(ASSETS_DIR, "dinoDead.png"))
DINO_DUCK = pygame.image.load(os.path.join(ASSETS_DIR, "dinoDuck.png"))
DINO_DUCK_TWO = pygame.image.load(os.path.join(ASSETS_DIR, "dinoDuck1.png"))
DINO_JUMP = pygame.image.load(os.path.join(ASSETS_DIR, "dinoJump.png"))
DINO_RUN = pygame.image.load(os.path.join(ASSETS_DIR, "dinorun.png"))
DINO_RUN_TWO = pygame.image.load(os.path.join(ASSETS_DIR, "dinorun1.png"))

pygame.init()
pygame.font.init()
FONT = pygame.font.SysFont("comicsans", 30)

class Dino:
    
class Obstacle:

def draw_window(win,dino, obstacles, score, game_speed):

def main():
    
    
    
if __name__ == "__main__"
    main()