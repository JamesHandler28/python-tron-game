import random
from collections import deque

def get_move(game_state, player_id):
    player = game_state['players'][player_id]
    if not player['is_alive']:
        return random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
    
    grid_size = game_state['grid_size']
    x, y = player['x'], player['y']
    
    # Build occupied set and opponent positions
    occupied = set()
    opponents = []
    for p in game_state['players']:
        if p['is_alive']:
            for pos in p['trail']:
                occupied.add(pos)
            if p['id'] != player_id:
                opponents.append((p['x'], p['y']))
    
    # Determine current direction
    current_direction = 'UP'
    if len(player['trail']) >= 2:
        last_x, last_y = player['trail'][-1]
        prev_x, prev_y = player['trail'][-2]
        dx, dy = last_x - prev_x, last_y - prev_y
        if dx == 1: current_direction = 'RIGHT'
        elif dx == -1: current_direction = 'LEFT'
        elif dy == 1: current_direction = 'DOWN'
        elif dy == -1: current_direction = 'UP'
    
    # Check if a move is safe
    def is_safe(nx, ny, depth=1):
        if not (0 <= nx < grid_size and 0 <= ny < grid_size):
            return False
        if (nx, ny) in occupied:
            return False
        
        # Simple flood fill to check future mobility
        if depth > 0:
            visited = set()
            queue = deque([(nx, ny)])
            visited.add((nx, ny))
            count = 0
            while queue and count < 10:
                cx, cy = queue.popleft()
                count += 1
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                    nx2, ny2 = cx + dx, cy + dy
                    if (0 <= nx2 < grid_size and 0 <= ny2 < grid_size and 
                        (nx2, ny2) not in occupied and (nx2, ny2) not in visited):
                        visited.add((nx2, ny2))
                        queue.append((nx2, ny2))
            if count < 5:  # Limited space ahead
                return False
                
        return True
    
    # Get possible moves avoiding 180 turns
    possible_moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    opposite = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
    if current_direction in possible_moves:
        possible_moves.remove(opposite[current_direction])
    
    # Score moves based on safety and strategic value
    move_scores = {}
    for move in possible_moves:
        score = 0
        if move == 'UP': nx, ny = x, y-1
        elif move == 'DOWN': nx, ny = x, y+1
        elif move == 'LEFT': nx, ny = x-1, y
        elif move == 'RIGHT': nx, ny = x+1, y
        
        if is_safe(nx, ny):
            score += 10
            
            # Prefer current direction for consistency
            if move == current_direction:
                score += 2
                
            # Avoid getting too close to walls
            wall_dist = min(nx, grid_size-1-nx, ny, grid_size-1-ny)
            if wall_dist < 3:
                score -= 2
            elif wall_dist > 10:
                score += 1
                
            # Move away from opponents
            for ox, oy in opponents:
                dist = abs(ox - nx) + abs(oy - ny)
                if dist < 5:
                    score -= 1
                elif dist > 15:
                    score += 1
                    
            # Prefer moves that keep options open
            future_moves = 0
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                if is_safe(nx+dx, ny+dy, depth=0):
                    future_moves += 1
            score += future_moves
            
        move_scores[move] = score
    
    # Select best move
    best_score = max(move_scores.values())
    best_moves = [move for move, score in move_scores.items() if score == best_score]
    
    if best_moves:
        return random.choice(best_moves)
    
    # If no safe moves, try any non-180 move
    for move in possible_moves:
        if move == 'UP' and is_safe(x, y-1, depth=0): return 'UP'
        elif move == 'DOWN' and is_safe(x, y+1, depth=0): return 'DOWN'
        elif move == 'LEFT' and is_safe(x-1, y, depth=0): return 'LEFT'
        elif move == 'RIGHT' and is_safe(x+1, y, depth=0): return 'RIGHT'
    
    return current_direction