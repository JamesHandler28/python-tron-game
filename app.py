from flask import Flask, render_template, request, jsonify
from game import Game
import random

# --- 1. Import ALL bot modules ---
# We use try/except in case some files are missing
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
    print("--- Make sure all 7 bot files are in the /bots folder ---")


# --- 2. Master Bot Configuration ---
# Map bot names (strings) to their color and the imported module
# This is our central "database" of all bots
BOT_CONFIG = {
    'gemini_bot':   {'color': '#4285F4', 'module': gemini_bot},   # Google Blue
    'chatgpt_bot':  {'color': '#75A593', 'module': chatgpt_bot},  # OpenAI Green
    'claude_bot':   {'color': '#D97A53', 'module': claude_bot},   # Anthropic Orange
    'meta_bot':     {'color': '#0068FA', 'module': meta_bot},     # Meta Blue
    'grok_bot':     {'color': '#8A2BE2', 'module': grok_bot},     # xAI Blue/Purple
    'deepseek_bot': {'color': '#10B981', 'module': deepseek_bot}, # DeepSeek Green
    'qwen_bot':     {'color': '#FF9900', 'module': qwen_bot},     # Alibaba Orange
}

# Get a list of just the bot names (e.g., 'gemini_bot', 'chatgpt_bot', ...)
AVAILABLE_BOT_NAMES = list(BOT_CONFIG.keys())

# --- Flask App ---
app = Flask(__name__)
game_storage = {}

def get_game_instance():
    return game_storage.get('main_game')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-game', methods=['POST'])
def start_game():
    global game_storage
    data = request.get_json()
    player_count = int(data.get('playerCount', 2))
    grid_size = int(data.get('gridSize', 40))
    
    if not 2 <= player_count <= 8:
        return jsonify({'error': 'Player count must be between 2 and 8'}), 400

    # A. Build the player_config list
    player_config = []
    
    # Player 0 is always human
    player_config.append({'name': 'human', 'color': '#FF0000'}) # Red
    
    # B. Randomly select (player_count - 1) bots
    num_bots = player_count - 1
    # Use random.sample to pick unique bot names
    selected_bot_names = random.sample(AVAILABLE_BOT_NAMES, k=min(num_bots, len(AVAILABLE_BOT_NAMES)))
    
    # C. Add selected bots to the config
    bot_modules_for_game = [None] # Player 0 (human) has no bot module
    
    for bot_name in selected_bot_names:
        bot_info = BOT_CONFIG[bot_name]
        player_config.append({
            'name': bot_name,
            'color': bot_info['color']
        })
        bot_modules_for_game.append(bot_info['module'])

    # Create the new game with our specific player config
    game = Game(grid_size, player_config)
    
    # Store the game and the list of bot *modules* for the tick
    game_storage['main_game'] = game
    game_storage['bot_modules_for_game'] = bot_modules_for_game
    
    print(f"Starting new game with: {player_config}")
    
    # The initial state will now contain the bot names
    return jsonify({
        'message': 'Game started',
        'initialState': game.get_state()
    })

@app.route('/submit-move', methods=['POST'])
def submit_move():
    game = get_game_instance()
    if not game or game.game_over:
        return jsonify({'error': 'Game not running'}), 400

    data = request.get_json()
    direction = data.get('direction')

    if direction:
        game.submit_move(0, direction) # Player 0 is human
    return jsonify({'success': True})

@app.route('/game-tick', methods=['GET'])
def game_tick():
    game = get_game_instance()
    if not game:
        return jsonify({'error': 'Game not started'}), 400

    if game.game_over:
        return jsonify(game.get_state())

    # --- 4. Updated Bot-Calling Logic ---
    # Get the list of modules we stored for this game
    bot_modules = game_storage.get('bot_modules_for_game', [])
    current_state = game.get_state() 

    # Loop from 1 up to the number of players
    for i in range(1, len(bot_modules)):
        if current_state['players'][i]['is_alive']:
            try:
                bot_module = bot_modules[i]
                move = bot_module.get_move(current_state, i)
                
                if move:
                    game.submit_move(i, move)
            except Exception as e:
                print(f"Error getting move from bot {i} ({bot_modules[i].__name__}): {e}")

    # Update the game simulation
    game.update()

    # Return the new state
    return jsonify(game.get_state())

if __name__ == '__main__':
    print("Starting Tron server...")
    print("Go to http://127.0.0.1:5000 in your browser.")
    app.run(debug=True, port=5000)