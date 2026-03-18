from helpers.path_helper import bfs_pathfinder
from helpers.valid_moves_helper import get_valid_moves_helper
from helpers.wall_helpers import find_forbidden_walls_new, find_valid_walls, get_blocked_roads


class GameState:
    def __init__(self,game):
        """Initialize the game state at each turn."""
        self.grid_size=game.scene.grid_size

        self.turn_manager=game.turn_manager
        self.red_player=game.red_player
        self.blue_player=game.blue_player

        self.current_blocked_roads=game.scene.current_blocked_roads
        self.placed_walls=game.scene.placed_walls

        self.update_wall_states()

        if self.red_player:
            start_position = (self.red_player.row, self.red_player.col)
            self.red_player_shortest_path = bfs_pathfinder(start_position, self.red_player.goal_col,
                                                              self.grid_size, self.current_blocked_roads)

        if self.blue_player:
            start_position = (self.blue_player.row, self.blue_player.col)
            self.blue_player_shortest_path = bfs_pathfinder(start_position, self.blue_player.goal_col,
                                                               self.grid_size, self.current_blocked_roads)
    # === Movement Management ===

    def get_valid_moves(self, player):
        """Return valid moves by calling the helper function."""
        other_player = self.red_player if player == self.blue_player else self.blue_player
        return get_valid_moves_helper(player, other_player, self.grid_size, self.current_blocked_roads)

    # === Wall Management ===

    def update_wall_states(self):
        # Get the red and blue player positions and goals
        red_player_pos = (self.red_player.row, self.red_player.col)
        blue_player_pos = (self.blue_player.row, self.blue_player.col)

        # Update forbidden walls
        self.forbidden_walls = find_forbidden_walls_new(
            self.grid_size, self.placed_walls, self.current_blocked_roads,
            red_player_pos, blue_player_pos, self.red_player.goal_col, self.blue_player.goal_col
        )

        # Update valid walls based on the current state
        self.valid_walls = find_valid_walls(self.grid_size, self.placed_walls, self.forbidden_walls)

    # === Bot Functions ===

    def simulate_move_or_wall(self, action_type, action_value, player):
        """
        Simulate either a move or a wall placement and return a new game state.
        """
        # Create a new GameState instance
        game_state_copy = GameState.__new__(GameState)

        # Copy game state attributes
        game_state_copy.grid_size = self.grid_size
        game_state_copy.current_blocked_roads = self.current_blocked_roads.copy()
        game_state_copy.placed_walls = self.placed_walls.copy()
        game_state_copy.forbidden_walls = self.forbidden_walls.copy()
        game_state_copy.valid_walls = self.valid_walls.copy()

        # Copy player states
        game_state_copy.red_player = self.copy_player(self.red_player)
        game_state_copy.blue_player = self.copy_player(self.blue_player)

        # Simulate move or wall placement based on the action_type
        if action_type == 'wall':
            # Simulate wall placement
            wall = action_value  # The wall coordinates

            # Add the wall to the placed walls
            game_state_copy.placed_walls.append(wall)

            # Get blocked roads due to the wall and update the game state
            blocked_roads = get_blocked_roads(wall)
            game_state_copy.current_blocked_roads += blocked_roads

            # Deduct available walls from the player
            if player == self.red_player:
                game_state_copy.red_player.available_walls -= 1
            else:
                game_state_copy.blue_player.available_walls -= 1

            game_state_copy.update_wall_states()
        elif action_type == 'skip':
            # Skip the player's turn
            pass
        else:
            # Unpack move coordinates
            new_row, new_col = action_value

            # Move the corresponding player
            if player.color == 'red':
                game_state_copy.red_player.row = new_row
                game_state_copy.red_player.col = new_col
            else:
                game_state_copy.blue_player.row = new_row
                game_state_copy.blue_player.col = new_col

        return game_state_copy

    def copy_player(self, player):
        """
        Helper method to copy a player object, preserving its state.
        """
        return SimplePlayer(
            player.row, player.col, player.goal_col, player.available_walls
        )

    def move_player(self, player, new_row, new_col):
        """Move the player to the new row and column."""
        player.row, player.col = new_row, new_col

    def get_player_by_color(self, color):
        if color == 'red':
            return self.red_player
        else:
            return self.blue_player

    def get_opponent_color(self, color):
        return 'blue' if color == 'red' else 'red'

class SimplePlayer:
    def __init__(self, row, col,goal_col,available_walls):
        self.row = row
        self.col = col
        self.goal_col = goal_col
        self.color = 'red' if goal_col == 0 else 'blue'
        self.available_walls = available_walls


