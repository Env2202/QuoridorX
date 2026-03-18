"""
Tests for bot_helper.py

This module tests the bot AI helper functions including minimax algorithm,
evaluation function, and move generation.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from bot.bot_helper import (
    minimax,
    game_over,
    evaluate,
    get_intelligent_moves,
    get_by_difficulty
)


class MockGameState:
    """Mock game state for testing."""
    def __init__(self, red_pos=(4, 8), blue_pos=(4, 0), red_walls=10, blue_walls=10):
        self.red_player = MockPlayer(red_pos[0], red_pos[1], 0, 'red', red_walls)
        self.blue_player = MockPlayer(blue_pos[0], blue_pos[1], 8, 'blue', blue_walls)
        self.grid_size = 9
        self.current_blocked_roads = []
        self.valid_walls = []

    def get_player_by_color(self, color):
        if color == 'red':
            return self.red_player
        return self.blue_player

    def get_opponent_color(self, color):
        return 'blue' if color == 'red' else 'red'

    def simulate_move_or_wall(self, action_type, action_value, player):
        # Return a new mock state
        new_state = MockGameState()
        if action_type == 'move':
            if player.color == 'red':
                new_state.red_player.row = action_value[0]
                new_state.red_player.col = action_value[1]
            else:
                new_state.blue_player.row = action_value[0]
                new_state.blue_player.col = action_value[1]
        return new_state


class MockPlayer:
    """Mock player for testing."""
    def __init__(self, row, col, goal_col, color, available_walls=10):
        self.row = row
        self.col = col
        self.goal_col = goal_col
        self.color = color
        self.available_walls = available_walls


class TestGameOver:
    """Tests for game_over function."""

    def test_game_over_red_wins(self):
        """Test game_over when red has reached goal."""
        gs = MockGameState(red_pos=(4, 0), blue_pos=(4, 4))
        assert game_over(gs) is True

    def test_game_over_blue_wins(self):
        """Test game_over when blue has reached goal."""
        gs = MockGameState(red_pos=(4, 4), blue_pos=(4, 8))
        assert game_over(gs) is True

    def test_game_not_over(self):
        """Test game_over when neither player has won."""
        gs = MockGameState(red_pos=(4, 8), blue_pos=(4, 0))
        assert game_over(gs) is False


class TestEvaluate:
    """Tests for evaluate function."""

    def test_evaluate_maximizing_wins(self):
        """Test evaluation when maximizing player has won."""
        gs = MockGameState(red_pos=(4, 0), blue_pos=(4, 4))
        result = evaluate(gs, 'red')
        assert result == float('inf')

    def test_evaluate_minimizing_wins(self):
        """Test evaluation when minimizing player has won."""
        gs = MockGameState(red_pos=(4, 4), blue_pos=(4, 8))
        result = evaluate(gs, 'red')
        # Should return a large negative value
        assert result < -500

    def test_evaluate_neutral_position(self):
        """Test evaluation of a neutral position."""
        gs = MockGameState(red_pos=(4, 8), blue_pos=(4, 0))
        result = evaluate(gs, 'red')
        # Both players equidistant from goal
        assert isinstance(result, (int, float))

    def test_evaluate_wall_advantage(self):
        """Test evaluation with wall advantage."""
        gs1 = MockGameState(red_walls=10, blue_walls=5)
        gs2 = MockGameState(red_walls=5, blue_walls=10)

        eval1 = evaluate(gs1, 'red')
        eval2 = evaluate(gs2, 'red')

        # More walls should be better
        assert eval1 > eval2


class TestGetIntelligentMoves:
    """Tests for get_intelligent_moves function."""

    def test_get_moves_no_walls(self):
        """Test getting intelligent moves with no walls."""
        gs = MockGameState()
        player = gs.red_player
        opponent = gs.blue_player

        intelligent, other = get_intelligent_moves(
            gs, player, gs.grid_size, gs.current_blocked_roads, player.available_walls
        )

        # Should return some moves
        assert len(intelligent) > 0 or len(other) > 0

    def test_get_moves_no_valid_moves_with_no_walls(self):
        """Test when player has no valid moves and no walls."""
        gs = MockGameState()
        player = gs.red_player

        # Block all possible moves (surround player with walls)
        gs.current_blocked_roads = [
            [(player.row, player.col), (player.row - 1, player.col)],
            [(player.row, player.col), (player.row + 1, player.col)],
            [(player.row, player.col), (player.row, player.col - 1)],
            [(player.row, player.col), (player.row, player.col + 1)],
        ]

        intelligent, other = get_intelligent_moves(
            gs, player, gs.grid_size, gs.current_blocked_roads, 0
        )

        # Should indicate skip
        assert intelligent == [('skip', (player.row, player.col))]


class TestGetByDifficulty:
    """Tests for get_by_difficulty function."""

    def test_easy_difficulty(self):
        """Test move generation for easy difficulty."""
        gs = MockGameState()
        player = gs.red_player
        opponent = gs.blue_player

        moves = get_by_difficulty(gs, player, opponent, 5, 'easy')

        # Should return moves
        assert moves is not None
        assert len(moves) > 0

    def test_medium_difficulty(self):
        """Test move generation for medium difficulty."""
        gs = MockGameState()
        player = gs.red_player
        opponent = gs.blue_player

        moves = get_by_difficulty(gs, player, opponent, 5, 'medium')

        assert moves is not None

    def test_hard_difficulty(self):
        """Test move generation for hard difficulty."""
        gs = MockGameState()
        player = gs.red_player
        opponent = gs.blue_player

        moves = get_by_difficulty(gs, player, opponent, 6, 'hard')

        assert moves is not None

    def test_impossible_difficulty(self):
        """Test move generation for impossible difficulty."""
        gs = MockGameState()
        player = gs.red_player
        opponent = gs.blue_player

        moves = get_by_difficulty(gs, player, opponent, 6, 'impossible')

        assert moves is not None
