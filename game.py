import random

# -----------------------------------------------
# --- PLAYER CLASS ---
# -----------------------------------------------
class Player:
    """
    Represents a single player.
    NOW stores name and color from a config.
    """
    def __init__(self, id, x, y, direction, name, color):
        self.id = id
        self.x = x
        self.y = y
        self.direction = direction
        self.next_direction = direction
        self.is_alive = True
        self.trail = [(x, y)]
        self.color = color # Assigned color (e.g., '#FF0000')
        self.name = name   # Assigned name (e.g., 'human' or 'gemini_bot')

    def set_direction(self, direction):
        if (self.direction == 'UP' and direction == 'DOWN') or \
           (self.direction == 'DOWN' and direction == 'UP') or \
           (self.direction == 'LEFT' and direction == 'RIGHT') or \
           (self.direction == 'RIGHT' and direction == 'LEFT'):
            return
            
        self.next_direction = direction

    def move(self):
        if not self.is_alive:
            return

        self.direction = self.next_direction

        if self.direction == 'UP':
            self.y -= 1
        elif self.direction == 'DOWN':
            self.y += 1
        elif self.direction == 'LEFT':
            self.x -= 1
        elif self.direction == 'RIGHT':
            self.x += 1
        
        self.trail.append((self.x, self.y))


# -----------------------------------------------
# --- GAME CLASS ---
# -----------------------------------------------
class Game:
    """
    Manages the game state.
    NOW accepts a player_config list to build the players.
    """
    
    # We no longer need PLAYER_COLORS here

    def __init__(self, grid_size, player_config):
        self.grid_size = grid_size
        self.player_config = player_config # e.g., [{'name': 'human', 'color': '#F00'}, ...]
        self.players = []
        self.game_over = False
        self.winner = None
        self.occupied_coords = set()
        self._initialize_players()

    def _initialize_players(self):
        """
        Creates players from the provided player_config.
        """
        start_margin = 3
        
        for i, config in enumerate(self.player_config):
            while True:
                x = random.randint(start_margin, self.grid_size - 1 - start_margin)
                y = random.randint(start_margin, self.grid_size - 1 - start_margin)
                
                if (x, y) not in self.occupied_coords:
                    direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
                    
                    # Create player using the config
                    player = Player(
                        id=i,
                        x=x,
                        y=y,
                        direction=direction,
                        name=config['name'],
                        color=config['color']
                    )
                    
                    self.players.append(player)
                    self.occupied_coords.add((x, y))
                    break
        
    def submit_move(self, player_id, direction):
        if 0 <= player_id < len(self.players):
            self.players[player_id].set_direction(direction)

    def update(self):
        if self.game_over:
            return

        # 1. Move
        for player in self.players:
            if player.is_alive:
                player.move()

        # 2. Collisions
        newly_occupied_by_head = {}
        
        for player in self.players:
            if not player.is_alive:
                continue
            
            x, y = player.x, player.y
            
            # A) Wall
            if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
                player.is_alive = False
                continue

            # B) Trail
            if (x, y) in self.occupied_coords:
                player.is_alive = False
                continue

            # C) Head-on
            if (x, y) in newly_occupied_by_head:
                player.is_alive = False
                other_player_id = newly_occupied_by_head[(x, y)]
                self.players[other_player_id].is_alive = False 
            else:
                newly_occupied_by_head[(x, y)] = player.id

        # 3. Add new positions to occupied set
        for player in self.players:
            if player.is_alive and (player.x, player.y) in newly_occupied_by_head:
                self.occupied_coords.add((player.x, player.y))

        # 4. Check for game over
        alive_players = [p for p in self.players if p.is_alive]
        if len(alive_players) <= 1:
            self.game_over = True
            if len(alive_players) == 1:
                self.winner = alive_players[0].id
            else:
                self.winner = 'DRAW'

    def get_state(self):
        """
        NOW includes the player's name in the state.
        """
        return {
            'grid_size': self.grid_size,
            'players': [
                {
                    'id': p.id,
                    'name': p.name, # <-- NEW
                    'x': p.x,
                    'y': p.y,
                    'is_alive': p.is_alive,
                    'trail': p.trail,
                    'color': p.color
                } for p in self.players
            ],
            'game_over': self.game_over,
            'winner': self.winner
        }