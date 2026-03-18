"""
Tests for turn_manager.py

This module tests the TurnManager class which manages turn switching,
win/draw conditions, and game state updates.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from classes.turn_manager import TurnManager


class MockGame:
    """Mock game object for testing."""
    def __init__(self):
        self.scene = MockScene()
        self.win_game_called = False
        self.draw_game_called = False
        self.winner = None

    def win_game(self, player):
        self.win_game_called = True
        self.winner = player

    def draw_game(self):
        self.draw_game_called = True

    def change_turn(self, color):
        pass


class MockScene:
    """Mock scene object for testing."""
    def __init__(self):
        self.mouse_events_enabled = True
        self.grid_size = 9

    def clear_possible_moves(self):
        pass

    def disable_mouse_events(self):
        self.mouse_events_enabled = False


class MockPlayer:
    """Mock player for testing."""
    def __init__(self, color):
        self.color = color
        self.flags_enabled = False
        self.turn_active = False
        self.won = False

    def on_turn(self):
        self.turn_active = True

    def on_end_turn(self):
        self.turn_active = False

    def set_flags(self, flag):
        self.flags_enabled = flag


class TestTurnManagerInitialization:
    """Tests for TurnManager initialization."""

    def test_turn_manager_init(self):
        """Test TurnManager initialization."""
        game = MockGame()
        tm = TurnManager(game, 'blue')

        assert tm.current_turn == 'blue'
        assert tm.red_player is None
        assert tm.blue_player is None
        assert tm.game == game
        assert tm.scene is None
        assert tm.move_history == []

    def test_turn_manager_init_red_start(self):
        """Test TurnManager initialization with red starting."""
        game = MockGame()
        tm = TurnManager(game, 'red')

        assert tm.current_turn == 'red'


class TestTurnManagerPlayerRegistration:
    """Tests for player registration."""

    @pytest.fixture
    def turn_manager(self):
        """Create a TurnManager for testing."""
        game = MockGame()
        return TurnManager(game, 'blue')

    def test_register_players(self, turn_manager):
        """Test registering players."""
        red = MockPlayer('red')
        blue = MockPlayer('blue')

        turn_manager.register_players(red, blue)

        assert turn_manager.red_player == red
        assert turn_manager.blue_player == blue

    def test_register_scene(self, turn_manager):
        """Test registering scene."""
        scene = MockScene()
        turn_manager.register_scene(scene)

        assert turn_manager.scene == scene


class TestTurnManagerTurnSwitching:
    """Tests for turn switching."""

    @pytest.fixture
    def turn_manager_with_players(self):
        """Create a TurnManager with registered players."""
        game = MockGame()
        tm = TurnManager(game, 'blue')
        tm.scene = MockScene()
        tm.red_player = MockPlayer('red')
        tm.blue_player = MockPlayer('blue')
        return tm

    def test_switch_turn_blue_to_red(self, turn_manager_with_players):
        """Test switching turn from blue to red."""
        tm = turn_manager_with_players
        tm.current_turn = 'blue'

        tm.switch_turn(('move', (4, 1)))

        assert tm.current_turn == 'red'

    def test_switch_turn_red_to_blue(self, turn_manager_with_players):
        """Test switching turn from red to blue."""
        tm = turn_manager_with_players
        tm.current_turn = 'red'

        tm.switch_turn(('move', (4, 7)))

        assert tm.current_turn == 'blue'

    def test_switch_turn_records_move(self, turn_manager_with_players):
        """Test that switch_turn records the move."""
        tm = turn_manager_with_players
        move = ('move', (4, 1))

        tm.switch_turn(move)

        assert move in tm.move_history


class TestTurnManagerCurrentPlayer:
    """Tests for getting current player."""

    @pytest.fixture
    def turn_manager_with_players(self):
        """Create a TurnManager with registered players."""
        game = MockGame()
        tm = TurnManager(game, 'blue')
        tm.red_player = MockPlayer('red')
        tm.blue_player = MockPlayer('blue')
        return tm

    def test_get_current_player_blue(self, turn_manager_with_players):
        """Test getting current player when it's blue's turn."""
        tm = turn_manager_with_players
        tm.current_turn = 'blue'

        player = tm.get_current_player()

        assert player.color == 'blue'

    def test_get_current_player_red(self, turn_manager_with_players):
        """Test getting current player when it's red's turn."""
        tm = turn_manager_with_players
        tm.current_turn = 'red'

        player = tm.get_current_player()

        assert player.color == 'red'

    def test_is_player_turn_true(self, turn_manager_with_players):
        """Test is_player_turn when it is the player's turn."""
        tm = turn_manager_with_players
        tm.current_turn = 'blue'

        assert tm.is_player_turn(tm.blue_player) is True

    def test_is_player_turn_false(self, turn_manager_with_players):
        """Test is_player_turn when it is not the player's turn."""
        tm = turn_manager_with_players
        tm.current_turn = 'blue'

        assert tm.is_player_turn(tm.red_player) is False


class TestTurnManagerDrawCheck:
    """Tests for draw detection."""

    @pytest.fixture
    def turn_manager(self):
        """Create a TurnManager for testing."""
        game = MockGame()
        return TurnManager(game, 'blue')

    def test_draw_check_not_enough_moves(self, turn_manager):
        """Test draw check with fewer than 12 moves."""
        tm = turn_manager
        tm.move_history = [('move', (4, 1))] * 10

        result = tm.draw_check()

        assert result is False

    def test_draw_check_no_repetition(self, turn_manager):
        """Test draw check with no threefold repetition."""
        tm = turn_manager
        # 12 different moves
        tm.move_history = [
            ('move', (4, 1)), ('move', (4, 7)),
            ('move', (4, 2)), ('move', (4, 6)),
            ('move', (4, 3)), ('move', (4, 5)),
            ('move', (3, 3)), ('move', (3, 5)),
            ('move', (5, 3)), ('move', (5, 5)),
            ('move', (4, 3)), ('move', (4, 5)),
        ]

        result = tm.draw_check()

        assert result is False

    def test_draw_check_with_repetition(self, turn_manager):
        """Test draw check with threefold repetition.

        The draw check looks for ABABAB pattern where:
        - first_pair (0-1) == third_pair (4-5) == fifth_pair (8-9)
        - second_pair (2-3) == fourth_pair (6-7) == sixth_pair (10-11)
        """
        tm = turn_manager
        # Create pairs of moves that repeat
        pair_a = ('move', (4, 1))
        pair_b = ('move', (4, 7))
        pair_c = ('move', (4, 2))
        pair_d = ('move', (4, 6))

        # Pattern: A, B, A, B, A, B (where each is a pair)
        # Positions: 0-1, 2-3, 4-5, 6-7, 8-9, 10-11
        tm.move_history = [
            pair_a, pair_b,  # first_pair (0-1)
            pair_c, pair_d,  # second_pair (2-3)
            pair_a, pair_b,  # third_pair (4-5) - same as first
            pair_c, pair_d,  # fourth_pair (6-7) - same as second
            pair_a, pair_b,  # fifth_pair (8-9) - same as first
            pair_c, pair_d,  # sixth_pair (10-11) - same as second
        ]

        result = tm.draw_check()

        assert result is True

    def test_reset_turn(self, turn_manager):
        """Test reset_turn method."""
        tm = turn_manager
        tm.current_turn = 'red'

        tm.reset_turn()

        assert tm.current_turn == 'blue'


class TestTurnManagerString:
    """Tests for string representation."""

    def test_str_representation_blue(self):
        """Test string representation when it's blue's turn."""
        game = MockGame()
        tm = TurnManager(game, 'blue')

        assert str(tm) == "It is blue's turn"

    def test_str_representation_red(self):
        """Test string representation when it's red's turn."""
        game = MockGame()
        tm = TurnManager(game, 'red')

        assert str(tm) == "It is red's turn"
