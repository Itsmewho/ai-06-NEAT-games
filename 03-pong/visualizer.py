import pygame


def draw_net(win, genome, config, pos, node_names=None):
    """
    Draws a visual representation of a NEAT neural network.
    """
    node_radius = 10
    layer_spacing = 100
    node_spacing = 40

    # Dictionary: layer_index -> list[node_ids]
    layer_nodes = {}

    # --- Input Layer (Negative IDs) ---
    inputs = config.genome_config.num_inputs
    layer_nodes[0] = []
    for i in range(1, inputs + 1):
        layer_nodes[0].append(-i)

    # --- Output Layer (Positive IDs starting at 0) ---
    outputs = config.genome_config.num_outputs
    layer_nodes[2] = []
    for i in range(outputs):
        layer_nodes[2].append(i)

    # --- Hidden Layer ---
    # Nodes that are not inputs or outputs
    layer_nodes[1] = [
        n
        for n in genome.nodes.keys()
        if n not in layer_nodes[0] and n not in layer_nodes[2]
    ]

    # --- Calculate Positions ---
    node_positions = {}
    start_x, start_y = pos

    for layer_idx, nodes in layer_nodes.items():
        x = start_x + layer_idx * layer_spacing
        y_offset = (len(nodes) * node_spacing) / 2

        for i, node_key in enumerate(nodes):
            y = start_y + (i * node_spacing) - y_offset
            node_positions[node_key] = (x, y)

    # --- Draw Connections ---
    for cg in genome.connections.values():
        if not cg.enabled:
            continue

        input_node, output_node = cg.key
        if input_node not in node_positions or output_node not in node_positions:
            continue

        start = node_positions[input_node]
        end = node_positions[output_node]

        # Green = Positive Weight, Red = Negative Weight
        color = (0, 255, 0) if cg.weight > 0 else (255, 0, 0)
        width = max(1, int(abs(cg.weight)))

        pygame.draw.line(win, color, start, end, width)

    # --- Draw Nodes & Labels ---
    font = pygame.font.SysFont("comicsans", 15)
    for node_key, (x, y) in node_positions.items():
        pygame.draw.circle(win, (255, 255, 255), (int(x), int(y)), node_radius)

        if node_names and node_key in node_names:
            label = font.render(node_names[node_key], True, (255, 255, 255))
            # Inputs on Left, Outputs on Right
            if node_key < 0:
                win.blit(label, (x - label.get_width() - 15, y - 10))
            else:
                win.blit(label, (x + 15, y - 10))
