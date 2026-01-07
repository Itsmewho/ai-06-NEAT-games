# Basically the same as flappy_bird but with one small improvement.

import pygame


def get_font():
    return pygame.font.SysFont("comicsans", 20)


def draw_net(win, genome, config=None, pos=(400, 500), input_names=None):
    node_position = {}
    start_x, start_y = pos
    layer_width = 150
    node_spacing = 50

    font = get_font()

    # ---- INPUT LAYER ----
    if input_names is None:
        input_names = [f"In {i}" for i in range(len(config.genome_config.input_keys))]

    for i, input_label in enumerate(input_names):
        x = start_x
        y = start_y + (i * node_spacing)

        # NEAT input node keys are negative
        node_key = config.genome_config.input_keys[i]
        node_position[node_key] = (x, y)

        pygame.draw.circle(win, (200, 200, 200), (x, y), 10)
        label = font.render(input_label, True, (0, 0, 0))
        win.blit(label, (x - 90, y - 10))

    # ---- OUTPUT LAYER (Jump + Duck) ----
    out_x = start_x + layer_width

    output_labels = ["Jump", "Duck"]
    output_keys = config.genome_config.output_keys

    # Center outputs vertically relative to inputs
    total_h = (len(output_labels) - 1) * node_spacing
    base_y = start_y + (len(input_names) * node_spacing) // 2 - total_h // 2

    for i, (label_text, key) in enumerate(zip(output_labels, output_keys)):
        y = base_y + i * node_spacing
        node_position[key] = (out_x, y)

        pygame.draw.circle(win, (200, 200, 200), (out_x, y), 10)
        label = font.render(label_text, True, (0, 0, 0))
        win.blit(label, (out_x + 15, y - 10))

    # ---- CONNECTIONS ----
    for (in_node, out_node), conn in genome.connections.items():
        if not conn.enabled:
            continue

        if in_node in node_position and out_node in node_position:
            start = node_position[in_node]
            end = node_position[out_node]

            color = (0, 200, 0) if conn.weight > 0 else (200, 0, 0)
            width = max(1, min(6, int(abs(conn.weight) * 2)))

            pygame.draw.line(win, color, start, end, width)
