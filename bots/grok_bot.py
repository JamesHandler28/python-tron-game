import random
from collections import deque

def get_move(game_state, player_id):
    player = game_state['players'][player_id]
    if not player['is_alive']:
        return None

    x = player['x']
    y = player['y']
    grid_size = game_state['grid_size']

    # Build a set of all occupied coordinates
    occupied = set()
    for p in game_state['players']:
        for (tx, ty) in p['trail']:
            occupied.add((tx, ty))

    # Get current direction
    current_direction_str = None
    if len(player['trail']) >= 2:
        prev_pos = player['trail'][-2]
        last_pos = player['trail'][-1]
        dx = last_pos[0] - prev_pos[0]
        dy = last_pos[1] - prev_pos[1]
        if dx == 1:
            current_direction_str = 'RIGHT'
        elif dx == -1:
            current_direction_str = 'LEFT'
        elif dy == 1:
            current_direction_str = 'DOWN'
        elif dy == -1:
            current_direction_str = 'UP'

    # Possible moves, avoiding 180-degree turn if direction exists
    possible_moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    if current_direction_str == 'UP':
        possible_moves.remove('DOWN')
    elif current_direction_str == 'DOWN':
        possible_moves.remove('UP')
    elif current_direction_str == 'LEFT':
        possible_moves.remove('RIGHT')
    elif current_direction_str == 'RIGHT':
        possible_moves.remove('LEFT')

    # Helper to check if a position is safe
    def is_safe(check_x, check_y):
        return 0 <= check_x < grid_size and 0 <= check_y < grid_size and (check_x, check_y) not in occupied

    # Flood fill to compute reachable space
    def flood_fill(start_x, start_y, occupied, grid_size):
        q = deque([(start_x, start_y)])
        visited = set([(start_x, start_y)])
        count = 1
        while q:
            cx, cy = q.popleft()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size and (nx, ny) not in occupied and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny))
                    count += 1
        return count

    # Evaluate each possible move
    move_scores = {}
    for move in possible_moves:
        if move == 'UP':
            new_x, new_y = x, y - 1
        elif move == 'DOWN':
            new_x, new_y = x, y + 1
        elif move == 'LEFT':
            new_x, new_y = x - 1, y
        elif move == 'RIGHT':
            new_x, new_y = x + 1, y
        if is_safe(new_x, new_y):
            score = flood_fill(new_x, new_y, occupied, grid_size)
        else:
            score = 0
        move_scores[move] = score

    # Find the maximum score
    max_score = max(move_scores.values())
    best_moves = [move for move, score in move_scores.items() if score == max_score]

    # Prefer continuing straight if possible
    if current_direction_str in best_moves:
        return current_direction_str

    # Otherwise, choose randomly among best
    return random.choice(best_moves)