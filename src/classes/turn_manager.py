from classes.game_state import GameState

class TurnManager:
    def __init__(self,game,color):
        self.current_turn = color
        self.red_player = None
        self.blue_player = None
        self.game=game
        self.scene=None
        self.move_history = []

    def register_players(self, red_player, blue_player):
        """Register the player objects."""
        self.red_player = red_player
        self.blue_player = blue_player
        self.start_turn()

    def register_scene(self, scene):
        """Register the scene object."""
        print("Registering scene")
        self.scene = scene

    def switch_turn(self,move=None):
        """Switch the turn and perform an action for the new player."""

        self.scene.clear_possible_moves()

        # DRAW CHECK
        self.move_history.append(move)
        if self.draw_check():
            self.draw_game()
            return

        if self.current_turn == 'red':
            self.current_turn = 'blue'
        else:
            self.current_turn = 'red'
        self.start_turn()

    def start_turn(self):
        """Start the turn of the player."""
        #UPDATE GAME STATE
        self.game_state=GameState(self.game)
        if not (hasattr(self.get_current_player(),'bot') and self.get_current_player().bot):
            self.scene.keyPressed=False

        if self.current_turn == 'blue':
            self.red_player.on_end_turn()
            self.blue_player.on_turn()
            self.game.change_turn('blue')
        else:
            self.blue_player.on_end_turn()
            self.red_player.on_turn()
            self.game.change_turn('red')

    def reset_turn(self):
        self.current_turn = 'blue'

    def is_player_turn(self, player):
        return self.current_turn == player.color

    def get_current_player(self):
        return self.red_player if self.current_turn == 'red' else self.blue_player

    def draw_check(self):
        if len(self.move_history) >= 12:
            # Get the last 12 moves (6 moves per player, 3 pairs)
            last_six_moves = self.move_history[-12:]

            # Check if the last three pairs of moves are identical
            first_pair = last_six_moves[0:2]
            second_pair = last_six_moves[2:4]
            third_pair = last_six_moves[4:6]
            fourth_pair = last_six_moves[6:8]
            fifth_pair = last_six_moves[8:10]
            sixth_pair = last_six_moves[10:12]

            # Compare if the last three pairs are identical
            if first_pair == third_pair == fifth_pair and second_pair == fourth_pair == sixth_pair:
                self.game.draw_game()
                return True
        return False

    def draw_game(self):
        self.red_player.set_flags(False)
        self.blue_player.set_flags(False)
        self.scene.disable_mouse_events()
        self.game.draw_game()

    def win_game(self, player):
        self.red_player.set_flags(False)
        self.blue_player.set_flags(False)
        self.scene.disable_mouse_events()
        self.game.win_game(player)

    def __str__(self):
        return f"It is {self.current_turn}'s turn"
