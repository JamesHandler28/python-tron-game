import random
import sys
import os
import math

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
        Creates players from the provided player_config, ensuring
        they don't spawn too close to walls or each other.
        """
        start_margin = 5  # Min 5 cells from wall (increased padding)
        min_dist = 10     # Min 10 cells from other players

        # Keep track of spawn points just for this function
        spawn_points = []

        for i, config in enumerate(self.player_config):
            
            # Try 100 times to find a good spot
            for _ in range(100): 
                x = random.randint(start_margin, self.grid_size - 1 - start_margin)
                y = random.randint(start_margin, self.grid_size - 1 - start_margin)
                
                # --- NEW SAFE SPAWN CHECK ---
                # Check distance from other spawn points
                is_safe = True
                for (sx, sy) in spawn_points:
                    dist = math.sqrt((x - sx)**2 + (y - sy)**2)
                    if dist < min_dist:
                        is_safe = False
                        break
                # --- END NEW CHECK ---
                
                # If it's a safe distance, use this spot
                if is_safe:
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
                    spawn_points.append((x, y)) # Add to our local list for checking
                    break # This breaks out of the "for _ in range(100)" loop
            
            # This 'else' belongs to the 'for _ in range(100)' loop
            # It only runs if the loop finishes without 'break'-ing
            else:
                # Fallback: If 100 tries fail, just place the player anywhere
                # to prevent a crash. This should be rare.
                print(f"Warning: Could not find a safe spawn for player {i}. Placing randomly.")
                x = random.randint(start_margin, self.grid_size - 1 - start_margin)
                y = random.randint(start_margin, self.grid_size - 1 - start_margin)
                direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
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
                    'direction': p.direction,
                    'is_alive': p.is_alive,
                    'trail': p.trail,
                    'color': p.color
                } for p in self.players
            ],
            'game_over': self.game_over,
            'winner': self.winner
        }
        
    def _generate_start_positions(self, num_players):
        """
        Generates a list of (x, y, directiton) tuples
        that are not too close to each other or the walls
        """
        padding = 5
        min_dist = 5
        
        positions = []
        
        for _ in range(num_players):
            for _ in range(100):
                x = random.randint(padding, self.grid_size - 1 - padding)
                y = random.randint(padding, self.grid_size - 1 - padding)
                
                is_safe = True
                for (px, py, p_dir) in positions:
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_dist:
                        is_safe = False
                        break
                
                if is_safe:
                    break
            
            direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
            positions.append((x, y, direction))
        
        return positions