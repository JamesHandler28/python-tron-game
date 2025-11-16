import random

def get_move(game_state, player_id):
    player = game_state['players'][player_id]
    if not player['is_alive']:
        return None 

    x = player['x']
    y = player['y']
    grid_size = game_state['grid_size']

    occupied = set()
    for p in game_state['players']:
        for (tx, ty) in p['trail']:
            occupied.add((tx, ty))

    current_direction_str = 'UP' 
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

    def is_safe(check_x, check_y):
        if not (0 <= check_x < grid_size and 0 <= check_y < grid_size):
            return False
        if (check_x, check_y) in occupied:
            return False
        return True

    possible_moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    if current_direction_str == 'UP':
        possible_moves.remove('DOWN')
    elif current_direction_str == 'DOWN':
        possible_moves.remove('UP')
    elif current_direction_str == 'LEFT':
        possible_moves.remove('RIGHT')
    elif current_direction_str == 'RIGHT':
        possible_moves.remove('LEFT')

    safe_moves = []
    for move in possible_moves:
        if move == 'UP' and is_safe(x, y - 1):
            safe_moves.append('UP')
        elif move == 'DOWN' and is_safe(x, y + 1):
            safe_moves.append('DOWN')
        elif move == 'LEFT' and is_safe(x - 1, y):
            safe_moves.append('LEFT')
        elif move == 'RIGHT' and is_safe(x + 1, y):
            safe_moves.append('RIGHT')
            
    if not safe_moves:
        return current_direction_str 

    # Prioritize moves that lead to open spaces
    preferred_moves = []
    for move in safe_moves:
        if move == 'UP' and is_safe(x, y - 2) and is_safe(x-1, y-1) and is_safe(x+1, y-1):
            preferred_moves.append('UP')
        elif move == 'DOWN' and is_safe(x, y + 2) and is_safe(x-1, y+1) and is_safe(x+1, y+1):
            preferred_moves.append('DOWN')
        elif move == 'LEFT' and is_safe(x - 2, y) and is_safe(x-1, y-1) and is_safe(x-1, y+1):
            preferred_moves.append('LEFT')
        elif move == 'RIGHT' and is_safe(x + 2, y) and is_safe(x+1, y-1) and is_safe(x+1, y+1):
            preferred_moves.append('RIGHT')

    if preferred_moves:
        return random.choice(preferred_moves)
    return random.choice(safe_moves)