import random
from collections import deque

def get_move(game_state, player_id):
    """
    An advanced bot that uses BFS to find the safest move by evaluating space availability.
    """
    
    player = game_state['players'][player_id]
    if not player['is_alive']:
        return None 

    x = player['x']
    y = player['y']
    grid_size = game_state['grid_size']

    # --- Build a set of all occupied coordinates for quick lookup ---
    occupied = set()
    for p in game_state['players']:
        for (tx, ty) in p['trail']:
            occupied.add((tx, ty))

    # --- Get current direction from trail ---
    current_direction_str = 'UP' # Default
    if len(player['trail']) < 2:
        current_direction_str = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
    else:
        last_pos = player['trail'][-1]
        prev_pos = player['trail'][-2]
        dx = last_pos[0] - prev_pos[0]
        dy = last_pos[1] - prev_pos[1]

        if dx == 1: current_direction_str = 'RIGHT'
        elif dx == -1: current_direction_str = 'LEFT'
        elif dy == 1: current_direction_str = 'DOWN'
        elif dy == -1: current_direction_str = 'UP'

    # --- Helper to check if a future coordinate is safe ---
    def is_safe(check_x, check_y):
        if not (0 <= check_x < grid_size and 0 <= check_y < grid_size):
            return False
        if (check_x, check_y) in occupied:
            return False
        return True

    # --- BFS to find reachable space from a given position ---
    def get_reachable_space(start_x, start_y):
        if not is_safe(start_x, start_y):
            return 0
        
        visited = set()
        queue = deque([(start_x, start_y)])
        visited.add((start_x, start_y))
        count = 0
        
        while queue:
            curr_x, curr_y = queue.popleft()
            count += 1
            
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x, new_y = curr_x + dx, curr_y + dy
                if (new_x, new_y) not in visited and is_safe(new_x, new_y):
                    visited.add((new_x, new_y))
                    queue.append((new_x, new_y))
                    
                    # Limit search to avoid taking too long
                    if count > grid_size * grid_size * 0.5:
                        break
        
        return count

    # --- Check potential moves (avoid 180 turns) ---
    possible_moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    if current_direction_str == 'UP':
        possible_moves.remove('DOWN')
    elif current_direction_str == 'DOWN':
        possible_moves.remove('UP')
    elif current_direction_str == 'LEFT':
        possible_moves.remove('RIGHT')
    elif current_direction_str == 'RIGHT':
        possible_moves.remove('LEFT')

    # Evaluate each safe move based on reachable space
    move_scores = {}
    safe_moves = []
    
    for move in possible_moves:
        new_x, new_y = x, y
        if move == 'UP':
            new_x, new_y = x, y - 1
        elif move == 'DOWN':
            new_x, new_y = x, y + 1
        elif move == 'LEFT':
            new_x, new_y = x - 1, y
        elif move == 'RIGHT':
            new_x, new_y = x + 1, y
        
        if is_safe(new_x, new_y):
            safe_moves.append(move)
            space_count = get_reachable_space(new_x, new_y)
            move_scores[move] = space_count

    # --- Make a decision ---
    if not safe_moves:
        # If no safe moves, just continue in current direction (will die)
        return current_direction_str

    # If current direction is safe and has good space, prefer it
    if current_direction_str in safe_moves:
        current_space = move_scores[current_direction_str]
        # If current direction has significantly less space than others, reconsider
        max_space = max(move_scores.values())
        if current_space >= max_space * 0.8 or random.random() < 0.6:
            return current_direction_str

    # Choose the move with the most reachable space
    best_move = safe_moves[0]
    best_space = move_scores[best_move]
    for move in safe_moves:
        if move_scores[move] > best_space:
            best_move = move
            best_space = move_scores[move]
    
    return best_move