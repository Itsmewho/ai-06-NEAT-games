import pygame
import neat
import os
import pickle
import random
import visualizer

# Import game assets ( the lazy way )
from dino import *  # noqa: F403

best_genome = None
pygame.init()

STAT_FONT = pygame.font.SysFont("comicsans", 30)
RED = (255, 0, 0)
GEN = 0  # Starting point of the genomes.


class DummyInput:
    def __getitem__(self, key):
        return False  # For NEAT to work without keyboard inputs


def eval_genomes(genomes, config):
    global GEN, best_genome
    GEN += 1

    # Update the best genome
    for _, g in genomes:
        if best_genome is None or (
            g.fitness is not None and g.fitness > best_genome.fitness
        ):
            best_genome = g

    dummy_keys = DummyInput()  # Fix for crash keyboard inputs see line 93isch

    # Track Neural Networks, Genomes, and Dinos
    nets = []
    ge = []
    dinos = []

    for _, g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        dinos.append(Dino())  # noqa: F405
        ge.append(g)

    # Game Settings
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  # noqa: F405
    pygame.display.set_caption("Dino Run – NEAT AI")
    clock = pygame.time.Clock()

    obstacles = []
    score = 0

    # Helper to spawn groups (Copied logic to ensure it works in trainer)
    def spawn_obstacle_group(start_x):
        group = []
        patterns = [
            ["L", "L"],
            ["S", "S", "S"],
            ["L", "L", "L"],
            ["S", "L", "S"],
            ["L", "S", "L"],
        ]
        pattern = random.choice(patterns)
        current_x = start_x
        GAP = 10
        for p in pattern:
            if p == "S":
                obs = SmallCactus(SMALL_CACTUS)  # noqa: F405
            else:
                obs = LargeCactus(LARGE_CACTUS)  # noqa: F405
            obs.rect.x = current_x
            current_x += obs.rect.width + GAP
            group.append(obs)
        return group

    run = True
    while run:
        clock.tick(30)  # Increase this to train faster (e.g. 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                return

        # The AI needs to look at the NEXT obstacle, not one it has already passed.
        obstacle_ind = 0
        if len(obstacles) > 0:
            # If the first obstacle is behind, look at the second one
            if (
                len(obstacles) > 1
                and obstacles[0].rect.x + obstacles[0].rect.width < dinos[0].rect.x
            ):
                obstacle_ind = 1

        # --- AI DECISION ---
        speed = get_game_speed(score)  # noqa: F405

        for x, dino in enumerate(dinos):
            # Increase fitness for surviving every frame
            ge[x].fitness += 0.1

            dino.update(dummy_keys)

            if len(obstacles) > 0:
                target = obstacles[obstacle_ind]

                # INPUTS:
                # 1. Speed (Normalized)
                # 2. Distance to Obstacle (Normalized)
                # 3. Obstacle Y Height (Normalized) - Tells it if it's a bird or cactus
                # 4. Obstacle Width (Normalized) - Tells it if it's a group

                inputs = (
                    speed / 100,
                    (target.rect.x - dino.rect.x) / WIN_WIDTH,  # noqa: F405
                    target.rect.y / WIN_HEIGHT,  # noqa: F405
                    target.rect.width / WIN_WIDTH,  # noqa: F405
                )

                output = nets[x].activate(inputs)

                # OUTPUTS:
                # Output 0: Jump
                # Output 1: Duck

                if output[0] > 0.5:
                    dino.want_jump = True
                elif output[1] > 0.5:
                    dino.want_duck = True
                else:
                    # If not jumping or ducking, ensure we are running
                    if not dino.dino_jump:
                        dino.run()

        # --- OBSTACLE LOGIC ---
        if len(obstacles) == 0:
            # Spawn logic (simplified for trainer)
            spawn_x = WIN_WIDTH + random.randint(100, 300)  # noqa: F405
            r = random.random()
            if r < 0.2:
                obstacles.append(Bird(BIRD))  # noqa: F405
                obstacles[-1].rect.x = spawn_x
            elif speed > 18 and r < 0.7:
                obstacles.extend(spawn_obstacle_group(spawn_x))
            else:
                if random.random() < 0.5:
                    obs = SmallCactus(SMALL_CACTUS)  # noqa: F405
                else:
                    obs = LargeCactus(LARGE_CACTUS)  # noqa: F405
                obs.rect.x = spawn_x
                obstacles.append(obs)

        rem = []
        dinos_to_remove = []

        for obstacle in obstacles:
            obstacle.update(speed)

            # Check Collision
            # Note: We use the mask logic from your game file if possible,
            # otherwise fallback to rects for speed if needed.
            # Assuming 'obstacle.collide' isn't a method in your snippet, we do it manually:

            for i, dino in enumerate(dinos):
                if dino.rect.colliderect(
                    obstacle.rect
                ):  # Simple Rect collision for speed
                    # For pixel perfect, copy the mask code from your main() loop
                    # But for training, Rects are often 'good enough' and faster
                    ge[i].fitness -= 1
                    if i not in dinos_to_remove:
                        dinos_to_remove.append(i)

            if obstacle.rect.x < -obstacle.rect.width:
                rem.append(obstacle)

        for r in rem:
            obstacles.remove(r)

        # Remove dead dinos
        for i in sorted(dinos_to_remove, reverse=True):
            dinos.pop(i)
            nets.pop(i)
            ge.pop(i)

        score += speed * 0.015
        if len(dinos) == 0:
            break

        # --- DRAWING ---
        win.fill(WHITE)  # noqa: F405
        pygame.draw.line(
            win, BLACK, (0, GROUND_Y), (WIN_WIDTH, GROUND_Y), 2  # noqa: F405
        )  # noqa: F405

        for dino in dinos:
            dino.draw(win)
        for obs in obstacles:
            obs.draw(win)

        # UI
        text = STAT_FONT.render(f"Score: {int(score)}", 1, BLACK)  # noqa: F405
        win.blit(text, (1000, 10))
        text_gen = STAT_FONT.render(f"Gen: {GEN}", 1, RED)  # noqa: F405
        win.blit(text_gen, (10, 10))
        text_alive = STAT_FONT.render(f"Alive: {len(dinos)}", 1, RED)  # noqa: F405
        win.blit(text_alive, (10, 50))

        # Visualizer
        if len(ge) > 0:
            input_names = ["Speed", "Dist", "Obs Y", "Obs W"]
            try:
                visualizer.draw_net(
                    win, ge[0], config, pos=(950, 100), input_names=input_names
                )
            except Exception as e:
                print(e)

        pygame.display.update()


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    try:
        winner = p.run(eval_genomes, 100)
        save_winner(winner)
    except KeyboardInterrupt:
        print("\nUser interrupted! Saving best bird found so far...")
        save_winner(best_genome)
    except Exception as e:
        print(f"\nCrash! {e}. Saving best bird found so far...")
        if best_genome:
            save_winner(best_genome)


def save_winner(winner):
    if winner:
        print(f"\nSaving champion with fitness: {winner.fitness}")
        with open("winner.pkl", "wb") as f:
            pickle.dump(winner, f)
        print("Done!")
    else:
        print("No valid genome to save.")


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)
