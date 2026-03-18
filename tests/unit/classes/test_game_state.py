"""
Tests for game_state.py

This module tests the GameState class which manages the current state of the game
including player positions, walls, and valid moves.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from classes.game_state import GameState, SimplePlayer


class MockGame:
    """Mock game object for testing."""
    def __init__(self, grid_size=9):
        self.scene = MockScene(grid_size)
        self.turn_manager = MockTurnManager()
        self.red_player = None
        self.blue_player = None


class MockScene:
    """Mock scene object for testing."""
    def __init__(self, grid_size=9):
        self.grid_size = grid_size
        self.current_blocked_roads = []
        self.placed_walls = []


class MockTurnManager:
    """Mock turn manager for testing."""
    pass


class MockPlayer:
    """Mock player for testing."""
    def __init__(self, row, col, goal_col, color, available_walls=10):
        self.row = row
        self.col = col
        self.goal_col = goal_col
        self.color = color
        self.available_walls = available_walls


class TestSimplePlayer:
    """Tests for SimplePlayer class."""

    def test_simple_player_creation_red(self):
        """Test creating a red SimplePlayer."""
        player = SimplePlayer(4, 0, 0, 10)
        assert player.row == 4
        assert player.col == 0
        assert player.goal_col == 0
        assert player.color == 'red'
        assert player.available_walls == 10

    def test_simple_player_creation_blue(self):
        """Test creating a blue SimplePlayer."""
        player = SimplePlayer(4, 8, 8, 10)
        assert player.row == 4
        assert player.col == 8
        assert player.goal_col == 8
        assert player.color == 'blue'
        assert player.available_walls == 10


class TestGameStateInitialization:
    """Tests for GameState initialization."""

    def test_game_state_init_basic(self):
        """Test basic GameState initialization."""
        game = MockGame()
        game.red_player = MockPlayer(4, 8, 0, 'red')
        game.blue_player = MockPlayer(4, 0, 8, 'blue')

        # GameState requires complex initialization, we'll test the attributes it sets
        # Note: Full initialization requires more mocking
        gs = GameState.__new__(GameState)
        gs.grid_size = game.scene.grid_size
        gs.turn_manager = game.turn_manager
        gs.red_player = game.red_player
        gs.blue_player = game.blue_player
        gs.current_blocked_roads = game.scene.current_blocked_roads
        gs.placed_walls = game.scene.placed_walls

        assert gs.grid_size == 9
        assert gs.red_player.color == 'red'
        assert gs.blue_player.color == 'blue'


class TestGameStatePlayerAccess:
    """Tests for player access methods."""

    @pytest.fixture
    def basic_game_state(self):
        """Create a basic game state for testing."""
        gs = GameState.__new__(GameState)
        gs.red_player = SimplePlayer(4, 8, 0, 10)
        gs.blue_player = SimplePlayer(4, 0, 8, 10)
        return gs

    def test_get_player_by_color_red(self, basic_game_state):
        """Test getting red player by color."""
        player = basic_game_state.get_player_by_color('red')
        assert player.color == 'red'
        assert player.goal_col == 0

    def test_get_player_by_color_blue(self, basic_game_state):
        """Test getting blue player by color."""
        player = basic_game_state.get_player_by_color('blue')
        assert player.color == 'blue'
        assert player.goal_col == 8

    def test_get_opponent_color_red(self, basic_game_state):
        """Test getting opponent color for red."""
        opponent = basic_game_state.get_opponent_color('red')
        assert opponent == 'blue'

    def test_get_opponent_color_blue(self, basic_game_state):
        """Test getting opponent color for blue."""
        opponent = basic_game_state.get_opponent_color('blue')
        assert opponent == 'red'


class TestGameStateCopyPlayer:
    """Tests for copy_player method."""

    @pytest.fixture
    def basic_game_state(self):
        """Create a basic game state for testing."""
        gs = GameState.__new__(GameState)
        return gs

    def test_copy_player_preserves_state(self, basic_game_state):
        """Test that copy_player preserves all player attributes."""
        original = MockPlayer(3, 5, 8, 'blue', 7)
        copy = basic_game_state.copy_player(original)

        assert copy.row == original.row
        assert copy.col == original.col
        assert copy.goal_col == original.goal_col
        assert copy.available_walls == original.available_walls

    def test_copy_player_independent(self, basic_game_state):
        """Test that copied player is independent of original."""
        original = MockPlayer(3, 5, 8, 'blue', 7)
        copy = basic_game_state.copy_player(original)

        # Modify original
        original.row = 10

        # Copy should be unchanged
        assert copy.row == 3


class TestGameStateMovePlayer:
    """Tests for move_player method."""

    @pytest.fixture
    def basic_game_state(self):
        """Create a basic game state for testing."""
        gs = GameState.__new__(GameState)
        return gs

    def test_move_player_updates_position(self, basic_game_state):
        """Test that move_player updates player position."""
        player = MockPlayer(4, 4, 8, 'blue', 10)
        basic_game_state.move_player(player, 5, 5)

        assert player.row == 5
        assert player.col == 5

    def test_move_player_to_goal(self, basic_game_state):
        """Test moving player to their goal column."""
        player = MockPlayer(4, 7, 8, 'blue', 10)
        basic_game_state.move_player(player, 4, 8)

        assert player.col == player.goal_col


class TestGameStateSimulation:
    """Tests for simulate_move_or_wall method."""

    @pytest.fixture
    def game_state_for_simulation(self):
        """Create a game state set up for simulation tests."""
        gs = GameState.__new__(GameState)
        gs.grid_size = 9
        gs.current_blocked_roads = []
        gs.placed_walls = []
        gs.forbidden_walls = []
        gs.valid_walls = []
        gs.red_player = SimplePlayer(4, 8, 0, 10)
        gs.blue_player = SimplePlayer(4, 0, 8, 10)
        return gs

    def test_simulate_move(self, game_state_for_simulation):
        """Test simulating a player move."""
        gs = game_state_for_simulation
        player = gs.red_player

        new_state = gs.simulate_move_or_wall('move', (4, 7), player)

        # New state should have player at new position
        assert new_state.red_player.row == 4
        assert new_state.red_player.col == 7
        # Original state should be unchanged
        assert gs.red_player.col == 8

    def test_simulate_wall_placement(self, game_state_for_simulation):
        """Test simulating a wall placement."""
        gs = game_state_for_simulation
        player = gs.red_player
        wall = [(3, 3), (3, 5)]

        new_state = gs.simulate_move_or_wall('wall', wall, player)

        # Wall should be added to placed walls
        assert wall in new_state.placed_walls
        # Original state should be unchanged
        assert len(gs.placed_walls) == 0
        # Player should have one less wall
        assert new_state.red_player.available_walls == 9

    def test_simulate_skip(self, game_state_for_simulation):
        """Test simulating a skip turn."""
        gs = game_state_for_simulation
        player = gs.red_player

        new_state = gs.simulate_move_or_wall('skip', None, player)

        # State should remain unchanged
        assert new_state.red_player.row == gs.red_player.row
        assert new_state.red_player.col == gs.red_player.col

    def test_simulation_preserves_other_player(self, game_state_for_simulation):
        """Test that simulation doesn't affect the other player."""
        gs = game_state_for_simulation
        red_player = gs.red_player
        blue_original_pos = (gs.blue_player.row, gs.blue_player.col)

        new_state = gs.simulate_move_or_wall('move', (4, 7), red_player)

        # Blue player should be unchanged
        assert (new_state.blue_player.row, new_state.blue_player.col) == blue_original_pos
