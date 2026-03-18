from bot.bot_worker import BotWorker
from classes.player import Player

class Bot(Player):
    def __init__(self, player_settings,game,difficulty):
        super().__init__(player_settings,game)
        self.bot = True
        self.difficulty = difficulty
        self.grid_size = game.grid_size
        self.scene=game.scene
        self.difficulty_setup()

    def on_turn(self):
        """Bot's turn."""
        self.valid_moves = self.scene_ref.get_valid_moves(self)
        self.scene.disable_mouse_events()
        self.current_game_state = self.turn_manager.game_state
        self.blocked_roads = self.current_game_state.current_blocked_roads
        self.bot_move()

    def bot_move(self):
        # Create the worker and connect the signal to handle the computed move
        self.bot_worker = BotWorker(self.current_game_state, self, self.blocked_roads, self.search_depth,available_walls=self.available_walls,difficulty=self.difficulty)
        self.bot_worker.move_computed.connect(self.handle_computed_move)

        # Start the worker (it will run the bot in a separate thread)
        self.bot_worker.start()

    def handle_computed_move(self, best_type, best_move):
        """Handle the move once it is computed by the worker."""
        if best_type == 'skip':
            self.turn_manager.switch_turn(('skip',))
            return
        if best_move:
            if best_type == 'wall':
                # Handle wall placement (assuming best_move is a tuple with wall coordinates)
                wall_start, wall_end = best_move
                print(f"Bot placing wall from {wall_start} to {wall_end}")
                self.scene_ref.add_wall(custom_start=wall_start, custom_end=wall_end)
            else:
                # Handle player movement
                new_row, new_col = best_move
                print(f"Bot moving to {new_row}, {new_col}")
                self.move_player(new_row, new_col)

    def difficulty_setup(self):
        if self.difficulty == 'easy':
            self.search_depth = 5
        elif self.difficulty == 'medium':
            self.search_depth = 7
        elif self.difficulty == 'hard':
            self.search_depth = 7
        elif self.difficulty == 'impossible':
            self.search_depth = 7