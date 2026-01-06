import pygame


def get_font():
    return pygame.font.SysFont("comicsans", 20)


def draw_net(win, genome, config=None, pos=(400, 500)):
    """Draws the neural net"""
    node_position = {}
    start_x, start_y = pos
    layer_width = 150
    node_spacing = 50

    font = get_font()

    # --- INPUT NODES (Layer 0) ---
    inputs = ["Bird_Y", "Y Diff", "GAP"]

    for i, input_label in enumerate(inputs):
        x = start_x
        y = start_y + (i * node_spacing)

        node_position[-(i + 1)] = (x, y)  # Neat input keys are negative

        # Draw Node
        pygame.draw.circle(win, (200, 200, 200), (x, y), 10)

        # Draw Label (Offset to the left)
        label = font.render(input_label, 1, (0, 0, 0))
        win.blit(label, (x - 90, y - 10))

    # --- OUTPUT NODE (Layer 1) ---
    out_x = start_x + layer_width
    # Center the output node relative to the 3 inputs
    # (Inputs are at 0, 50, 100 -> Middle is 50)
    out_y = start_y + 50
    node_position[0] = (out_x, out_y)

    pygame.draw.circle(win, (200, 200, 200), (out_x, out_y), 10)
    label = font.render("Jump", 1, (0, 0, 0))
    win.blit(label, (out_x + 15, out_y - 10))

    # --- CONNECTIONS ---
    for (in_node, out_node), conn in genome.connections.items():
        if not conn.enabled:
            continue

        if in_node in node_position and out_node in node_position:
            start = node_position[in_node]
            end = node_position[out_node]

            # Green = Excitation (Do it!), Red = Inhibition (Don't do it!)
            color = (0, 255, 0) if conn.weight > 0 else (255, 0, 0)

            # Thickness based on connection strength (clamped between 1 and 6)
            width = max(1, min(6, int(abs(conn.weight) * 2)))

            pygame.draw.line(win, color, start, end, width)
