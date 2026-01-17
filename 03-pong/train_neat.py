import pygame
import neat
import os
import visualizer

# Import specific items from pong so we can use them
from pong import Game, LEVELS, MAX_STEPS, WIN_WIDTH, WIN_HEIGHT, FPS

# Initialize Font ONCE
pygame.init()
pygame.font.init()


class PongTrainer:
    def __init__(self, genome, config):
        self.genome = genome
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.game = Game()
        self.level = 0
        self.steps = 0
        self.genome.fitness = 0

    def step(self):
        self.steps += 1
        level_cfg = LEVELS[self.level]

        # 1. Inputs
        inputs = (
            self.game.left.y / WIN_HEIGHT,
            self.game.ball.y / WIN_HEIGHT,
            abs(self.game.ball.x - self.game.left.x) / WIN_WIDTH,
            self.game.ball.x_vel / 10,
            self.game.ball.y_vel / 10,
        )

        # 2. Output (Winner Takes All)
        o1, o2 = self.net.activate(inputs)
        move_up = o1 > o2
        self.game.left.move(up=move_up)

        # 3. Game Loop
        alive = self.game.loop(level_cfg["bot"])

        # --- 4. SMART REWARDS ---

        paddle_center_y = self.game.left.y + 50  # +50 is half paddle height

        # Scenario A: Attack Mode (Ball coming at us)
        if self.game.ball.x_vel < 0:
            # Reward: Align paddle with BALL
            diff = abs(paddle_center_y - self.game.ball.y)
            reward = (1.0 - diff / WIN_HEIGHT) ** 2
            self.genome.fitness += reward * 0.1

        # Scenario B: Recovery Mode (Ball moving away)
        else:
            # Reward: Align paddle with SCREEN CENTER
            # This forces it to stop camping at the bottom!
            screen_center = WIN_HEIGHT / 2
            diff = abs(paddle_center_y - screen_center)
            reward = (1.0 - diff / WIN_HEIGHT) ** 2
            # Smaller reward for resetting (we prioritize hitting)
            self.genome.fitness += reward * 0.05

        # 5. Reward: Hits (The main goal)
        if self.game.hits > 0:
            self.genome.fitness += 5
            # We don't reset hits here; we let the level check handle it below

        # 6. Level Up Logic
        if self.game.hits >= level_cfg["hits"]:
            self.genome.fitness += 50
            self.game.hits = 0
            self.level += 1

            # Cap the level so we don't crash
            if self.level >= len(LEVELS):
                self.level = len(LEVELS) - 1

            self.game.ball.reset(LEVELS[self.level]["bot"])

        if self.steps > MAX_STEPS:
            return False

        return alive


# ==================== EVAL ====================
def eval_genomes(genomes, config):
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    trainers = [PongTrainer(g, config) for _, g in genomes]

    # Visualizer Names
    node_names = {
        -1: "PadY",
        -2: "BallY",
        -3: "Dist",
        -4: "VelX",
        -5: "VelY",
        0: "UP",
        1: "DN",
    }

    running = True
    while running and trainers:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Update backwards so we can remove dead ones
        for i in reversed(range(len(trainers))):
            if not trainers[i].step():
                trainers.pop(i)

        if trainers:
            t = trainers[0]
            t.game.draw(win, LEVELS[t.level]["name"])

            try:
                visualizer.draw_net(
                    win, t.genome, config, pos=(400, 350), node_names=node_names
                )
            except:  # noqa: E722
                pass

            pygame.display.update()


# ==================== RUN ====================
def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    pop.add_reporter(neat.StatisticsReporter())

    try:
        # Running for 200 generations to give time for God Mode!
        pop.run(eval_genomes, 200)
    except KeyboardInterrupt:
        print("User Exit")


if __name__ == "__main__":
    run(os.path.join(os.path.dirname(__file__), "config.txt"))
