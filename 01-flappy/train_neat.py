import pygame
import neat
import os
import pickle
import visualizer

from flappy_bird import Bird, Pipe, BG_IMG, WIN_WIDTH, WIN_HEIGHT, GROUND_Y


# ---- Config
GEN = 0
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 40)
best_genome = None


def eval_genomes(genomes, config):
    global GEN, best_genome
    GEN += 1

    # Update the best genome
    for _, g in genomes:
        if best_genome is None or (
            g.fitness is not None and g.fitness > best_genome.fitness
        ):
            best_genome = g

    Pipe.VEL = 5
    Pipe.GAP = 200
    Pipe.MOVING_Y = False
    Pipe.PULSING_GAP = False

    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(g)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    pipes = [Pipe(600)]
    score = 0

    run = True
    while run:
        clock.tick(100)  # Fast Training Speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].top_rect.width:
                pipe_ind = 1
        else:
            run = False
            break

        # --- DIFFICULTY RAMP ---
        if score > 0 and score % 15 == 0:
            Pipe.VEL = min(10, 5 + (score // 15))
        if score > 50:
            Pipe.MOVING_Y = True
        if score > 200:
            Pipe.PULSING_GAP = True

        # --- AI LOGIC ---
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            # Use instance GAP if available (for pulsing), otherwise use Class GAP
            current_gap = pipes[pipe_ind].GAP
            gap_center = pipes[pipe_ind].height + (current_gap / 2)
            diff_y = bird.y - gap_center

            output = nets[x].activate(
                (
                    bird.y / WIN_HEIGHT,
                    diff_y / WIN_HEIGHT,
                    bird.vel / 10,
                )
            )

            if output[0] > 0.5:
                bird.jump()

        # --- PHYSICS ---
        add_pipe = False
        rem = []
        birds_to_remove = []

        for pipe in pipes:
            pipe.move()
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    if x not in birds_to_remove:
                        birds_to_remove.append(x)

            if pipe.x + pipe.top_rect.width < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= GROUND_Y or bird.y < 0:
                if x not in birds_to_remove:
                    birds_to_remove.append(x)

        for x in sorted(birds_to_remove, reverse=True):
            birds.pop(x)
            nets.pop(x)
            ge.pop(x)

        if len(birds) == 0:
            run = False
            break

        # --- DRAWING ---
        win.blit(BG_IMG, (0, 0))
        for pipe in pipes:
            pipe.draw(win)
        for bird in birds:
            bird.draw(win)
        pygame.draw.rect(win, (200, 200, 200), (0, GROUND_Y, WIN_WIDTH, 70))

        text = STAT_FONT.render(f"Score: {score}", 1, (255, 255, 255))
        win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

        level_text = "Lvl 1"
        if score > 200:
            level_text = "Lvl 4 (GOD)"
        elif score > 50:
            level_text = "Lvl 3 (Move)"
        elif score > 15:
            level_text = "Lvl 2 (Speed)"

        lvl_lbl = STAT_FONT.render(level_text, 1, (255, 255, 255))
        win.blit(lvl_lbl, (10, 10))

        if len(ge) > 0:
            try:
                visualizer.draw_net(win, ge[0], config, pos=(WIN_WIDTH - 250, 500))
            except:  # noqa: E722
                pass

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
