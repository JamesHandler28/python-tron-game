import random
from collections import deque # We need a deque for an efficient Flood Fill

def get_reachable_space(start_x, start_y, occupied_coords, grid_size):
    """
    Uses a Flood Fill (Breadth-First Search) to count all reachable
    empty squares from a given starting point.
    """
    queue = deque([(start_x, start_y)])
    visited = set([(start_x, start_y)])
    count = 0

    while queue:
        # Limit search depth to avoid slow turns in large open fields.
        # A 200-step search is more than enough to know if it's a good path.
        if count > 200: 
            return count

        cx, cy = queue.popleft()
        count += 1

        # Check all four neighbors (UP, DOWN, LEFT, RIGHT)
        for (dx, dy) in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = cx + dx, cy + dy

            # Check if the neighbor is valid
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                if (nx, ny) not in occupied_coords and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    
    return count

def get_move(game_state, player_id):
    """
    Gemini Bot: Chooses the move that leads to the largest open space.
    """
    player = game_state['players'][player_id]
    if not player['is_alive']:
        return None

    x, y = player['x'], player['y']
    grid_size = game_state['grid_size']

    # --- 1. Build a set of all occupied coordinates for fast lookup ---
    occupied = set()
    for p in game_state['players']:
        for (tx, ty) in p['trail']:
            occupied.add((tx, ty))

    # --- 2. Figure out the bot's current direction (from trail) ---
    trail = player['trail']
    current_direction_str = 'UP' # Default
    if len(trail) < 2:
        # Just spawned, pick a random safe direction
        current_direction_str = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
    else:
        last_pos = trail[-1]
        prev_pos = trail[-2]
        
        dx = last_pos[0] - prev_pos[0]
        dy = last_pos[1] - prev_pos[1]

        if dx == 1: current_direction_str = 'RIGHT'
        elif dx == -1: current_direction_str = 'LEFT'
        elif dy == 1: current_direction_str = 'DOWN'
        elif dy == -1: current_direction_str = 'UP'

    # --- 3. Define the 3 possible moves (Forward, Left, Right) ---
    # (We can't turn 180 degrees)
    possible_moves = {}
    if current_direction_str == 'UP':
        possible_moves = {'UP': (0, -1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}
    elif current_direction_str == 'DOWN':
        possible_moves = {'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}
    elif current_direction_str == 'LEFT':
        possible_moves = {'LEFT': (-1, 0), 'UP': (0, -1), 'DOWN': (0, 1)}
    elif current_direction_str == 'RIGHT':
        possible_moves = {'RIGHT': (1, 0), 'UP': (0, -1), 'DOWN': (0, 1)}

    # --- 4. Score each possible move ---
    scored_moves = []
    for move_name, (dx, dy) in possible_moves.items():
        next_x, next_y = x + dx, y + dy
        next_coord = (next_x, next_y)

        # Check if the *immediate* next square is safe
        is_in_bounds = (0 <= next_x < grid_size and 0 <= next_y < grid_size)
        is_unoccupied = (next_coord not in occupied)

        if is_in_bounds and is_unoccupied:
            # If it's safe, run the Flood Fill to see how much space is beyond it
            score = get_reachable_space(next_x, next_y, occupied, grid_size)
            scored_moves.append((score, move_name))
        else:
            # This move is a wall or trail, give it a score of -1
            scored_moves.append((-1, move_name))
    
    # --- 5. Make the decision ---
    if not scored_moves:
        # This should never happen, but as a fallback, go straight
        return current_direction_str

    # Sort moves by score, highest score first
    scored_moves.sort(key=lambda item: item[0], reverse=True)
    
    # Choose the move with the highest score
    best_move = scored_moves[0][1]
    
    return best_move