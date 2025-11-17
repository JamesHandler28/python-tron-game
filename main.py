import eel
import random
from game import Game

# --- 1. Import ALL bot modules ---
# (Exactly like you had in app.py)
try:
    import bots.gemini_bot as gemini_bot
    import bots.chatgpt_bot as chatgpt_bot
    import bots.claude_bot as claude_bot
    import bots.deepseek_bot as deepseek_bot
    import bots.grok_bot as grok_bot
    import bots.meta_bot as meta_bot
    import bots.qwen_bot as qwen_bot
except ImportError as e:
    print(f"--- WARNING: Could not import all bots: {e} ---")

# --- 2. Master Bot Configuration ---
BOT_CONFIG = {
    'gemini_bot':   {'color': '#4285F4', 'module': gemini_bot},
    'chatgpt_bot':  {'color': '#75A593', 'module': chatgpt_bot},
    'claude_bot':   {'color': '#D97A53', 'module': claude_bot},
    'meta_bot':     {'color': '#0068FA', 'module': meta_bot},
    'grok_bot':     {'color': '#8A2BE2', 'module': grok_bot},
    'deepseek_bot': {'color': '#10B981', 'module': deepseek_bot},
    'qwen_bot':     {'color': '#FF9900', 'module': qwen_bot},
}
AVAILABLE_BOT_NAMES = list(BOT_CONFIG.keys())

# --- 3. Game Storage ---
# We store the game and bots in a simple dictionary
game_storage = {}


# --- 4. Expose Python Functions to JavaScript ---
# Eel uses the @eel.expose decorator
# This is the *magic* that lets JavaScript call Python

@eel.expose  # <-- This function can now be called from JavaScript
def start_game(playerCount):
    """
    Replaces your /start-game route.
    It now returns the initial state directly.
    """
    player_count = int(playerCount)
    
    size_mapping = {
        2: 22,
        3: 25,
        4: 27,
        5: 30,
        6: 33,
        7: 36,
        8: 40,
    }
    grid_size = size_mapping.get(player_count, 50)
    
    player_config = []
    player_config.append({'name': 'human', 'color': '#FF0000'}) # Red
    
    num_bots = player_count - 1
    selected_bot_names = random.sample(AVAILABLE_BOT_NAMES, k=min(num_bots, len(AVAILABLE_BOT_NAMES)))
    
    bot_modules_for_game = [None] # Player 0 (human)
    
    for bot_name in selected_bot_names:
        bot_info = BOT_CONFIG[bot_name]
        player_config.append({
            'name': bot_name,
            'color': bot_info['color']
        })
        bot_modules_for_game.append(bot_info['module'])

    game = Game(grid_size, player_config)
    
    # Store game and bots for the tick
    game_storage['main_game'] = game
    game_storage['bot_modules_for_game'] = bot_modules_for_game
    
    print(f"Starting new game with: {player_config}")
    
    # Just return the state! No more jsonify
    return game.get_state()

@eel.expose  # <-- This function can now be called from JavaScript
def submit_move(direction):
    """
    Replaces your /submit-move route.
    """
    game = game_storage.get('main_game')
    if game and not game.game_over and direction:
        game.submit_move(0, direction) # Player 0 is human
    return {'success': True}

@eel.expose  # <-- This function can now be called from JavaScript
def game_tick():
    """
    Replaces your /game-tick route.
    """
    game = game_storage.get('main_game')
    if not game:
        return {'error': 'Game not started'}

    if game.game_over:
        return game.get_state()

    # Bot-Calling Logic (same as before)
    bot_modules = game_storage.get('bot_modules_for_game', [])
    current_state = game.get_state() 

    for i in range(1, len(bot_modules)):
        if current_state['players'][i]['is_alive']:
            try:
                bot_module = bot_modules[i]
                move = bot_module.get_move(current_state, i)
                if move:
                    game.submit_move(i, move)
            except Exception as e:
                print(f"Error getting move from bot {i}: {e}")

    game.update()
    return game.get_state()


# --- 5. Start the Application ---
if __name__ == '__main__':
    print("Initializing Eel application...")
    # Initialize Eel
    eel.init('web') # 'web' is the folder with your index.html
    
    print("Starting Tron game... Close this window to quit.")
    # Start the app. This opens the window.
    eel.start('index.html', size=(1024, 768))