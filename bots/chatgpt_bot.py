import random
from collections import deque

def get_move(game_state, player_id):
    """
    A safer Tron bot that avoids walls, trails, and dead-ends by
    ranking moves by their flood-fill (open space) score.
    """

    player = game_state['players'][player_id]
    if not player['is_alive']:
        return None

    x = player['x']
    y = player['y']
    grid_size = game_state['grid_size']

    # --- Build occupied set ---
    occupied = set()
    for p in game_state['players']:
        for (tx, ty) in p['trail']:
            occupied.add((tx, ty))

    # --- Determine current direction ---
    if len(player['trail']) < 2:
        current_dir = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
    else:
        hx, hy = player['trail'][-1]
        px, py = player['trail'][-2]
        dx, dy = hx - px, hy - py
        if dx == 1: current_dir = 'RIGHT'
        elif dx == -1: current_dir = 'LEFT'
        elif dy == 1: current_dir = 'DOWN'
        else: current_dir = 'UP'

    # --- Move deltas ---
    DIRS = {
        'UP':    (0, -1),
        'DOWN':  (0, 1),
        'LEFT':  (-1, 0),
        'RIGHT': (1, 0)
    }

    # --- Prevent 180-degree turns ---
    opposite = {'UP':'DOWN', 'DOWN':'UP', 'LEFT':'RIGHT', 'RIGHT':'LEFT'}
    possible_moves = [m for m in DIRS if m != opposite[current_dir]]

    # --- Check valid cell ---
    def safe(nx, ny):
        if not (0 <= nx < grid_size and 0 <= ny < grid_size):
            return False
        if (nx, ny) in occupied:
            return False
        return True

    # --- Flood-fill to estimate open space ---
    def flood_score(start):
        if not safe(*start):
            return -1
        seen = {start}
        q = deque([start])
        count = 0
        while q:
            cx, cy = q.popleft()
            count += 1
            for dx, dy in DIRS.values():
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in seen and safe(nx, ny):
                    seen.add((nx, ny))
                    q.append((nx, ny))
            if count > 150:  # Limit for speed
                break
        return count

    # --- Evaluate moves ---
    move_scores = []
    for move in possible_moves:
        dx, dy = DIRS[move]
        nx, ny = x + dx, y + dy
        if safe(nx, ny):
            score = flood_score((nx, ny))
            move_scores.append((score, move))

    if not move_scores:
        return current_dir

    # --- Pick best-scoring moves, then random among them ---
    best_score = max(score for score, _ in move_scores)
    best_moves = [m for s, m in move_scores if s == best_score]

    if current_dir in best_moves and random.random() < 0.6:
        return current_dir

    return random.choice(best_moves)
