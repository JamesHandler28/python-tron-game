from collections import deque

def get_move(game_state, player_id):
    """
    Advanced Tron bot using flood fill and spatial awareness.
    """
    player = game_state['players'][player_id]
    if not player['is_alive']:
        return None

    x = player['x']
    y = player['y']
    grid_size = game_state['grid_size']

    # Build occupied set
    occupied = set()
    for p in game_state['players']:
        for (tx, ty) in p['trail']:
            occupied.add((tx, ty))

    # Get current direction
    current_direction = 'UP'
    if len(player['trail']) >= 2:
        last_pos = player['trail'][-1]
        prev_pos = player['trail'][-2]
        dx = last_pos[0] - prev_pos[0]
        dy = last_pos[1] - prev_pos[1]
        
        if dx == 1: current_direction = 'RIGHT'
        elif dx == -1: current_direction = 'LEFT'
        elif dy == 1: current_direction = 'DOWN'
        elif dy == -1: current_direction = 'UP'

    # Helper: check if position is valid
    def is_safe(check_x, check_y):
        if not (0 <= check_x < grid_size and 0 <= check_y < grid_size):
            return False
        return (check_x, check_y) not in occupied

    # Flood fill to count reachable spaces
    def flood_fill(start_x, start_y, max_depth=20):
        if not is_safe(start_x, start_y):
            return 0
        
        visited = set()
        queue = deque([(start_x, start_y, 0)])
        visited.add((start_x, start_y))
        count = 0
        
        while queue:
            cx, cy, depth = queue.popleft()
            count += 1
            
            if depth >= max_depth:
                continue
            
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in visited and is_safe(nx, ny):
                    visited.add((nx, ny))
                    queue.append((nx, ny, depth + 1))
        
        return count

    # Get valid moves (no 180-degree turns)
    possible_moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    opposite = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
    if current_direction in opposite:
        possible_moves.remove(opposite[current_direction])

    # Evaluate each move
    move_scores = []
    for move in possible_moves:
        if move == 'UP':
            nx, ny = x, y - 1
        elif move == 'DOWN':
            nx, ny = x, y + 1
        elif move == 'LEFT':
            nx, ny = x - 1, y
        else:  # RIGHT
            nx, ny = x + 1, y
        
        if not is_safe(nx, ny):
            continue
        
        # Score based on available space
        space = flood_fill(nx, ny)
        
        # Bonus for continuing straight
        bonus = 20 if move == current_direction else 0
        
        # Penalty for being near edges
        edge_penalty = 0
        if nx < 3 or nx >= grid_size - 3 or ny < 3 or ny >= grid_size - 3:
            edge_penalty = 10
        
        score = space + bonus - edge_penalty
        move_scores.append((score, move))
    
    # Return best move or fallback
    if not move_scores:
        return current_direction
    
    move_scores.sort(reverse=True)
    return move_scores[0][1]