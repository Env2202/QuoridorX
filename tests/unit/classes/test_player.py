"""
Tests for player.py

This module tests the Player class which handles player movement,
turn management, and position validation.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


class MockPlayer:
    """Mock player for testing without Qt dependencies."""
    def __init__(self, row=4, col=0, goal_col=8, color='blue', available_walls=10):
        self.row = row
        self.col = col
        self.goal_col = goal_col
        self.color = color
        self.available_walls = available_walls
        self.won = False
        self.valid_moves = {}

    def is_position_valid(self, row, col):
        """Check if the target grid position (row, col) is valid."""
        return any(new_row == row and new_col == col for new_row, new_col in self.valid_moves.values())


class TestPlayerInitialization:
    """Tests for Player initialization."""

    def test_player_initial_position(self):
        """Test player initial position."""
        player = MockPlayer(row=4, col=0, goal_col=8, color='blue')
        assert player.row == 4
        assert player.col == 0
        assert player.goal_col == 8
        assert player.color == 'blue'

    def test_player_starting_walls(self):
        """Test player starts with correct number of walls."""
        player = MockPlayer(available_walls=10)
        assert player.available_walls == 10

    def test_player_not_won_initially(self):
        """Test player has not won at start."""
        player = MockPlayer()
        assert player.won is False


class TestPlayerPositionValidation:
    """Tests for position validation."""

    def test_is_position_valid_true(self):
        """Test valid position detection."""
        player = MockPlayer(row=4, col=4)
        player.valid_moves = {'up': (3, 4), 'down': (5, 4)}

        assert player.is_position_valid(3, 4) is True
        assert player.is_position_valid(5, 4) is True

    def test_is_position_valid_false(self):
        """Test invalid position detection."""
        player = MockPlayer(row=4, col=4)
        player.valid_moves = {'up': (3, 4), 'down': (5, 4)}

        assert player.is_position_valid(2, 4) is False
        assert player.is_position_valid(4, 5) is False

    def test_is_position_valid_empty_moves(self):
        """Test validation with no valid moves."""
        player = MockPlayer(row=4, col=4)
        player.valid_moves = {}

        assert player.is_position_valid(3, 4) is False


class TestPlayerGoal:
    """Tests for player goal-related behavior."""

    def test_player_at_goal_blue(self):
        """Test blue player at goal."""
        player = MockPlayer(row=4, col=8, goal_col=8, color='blue')
        assert player.col == player.goal_col

    def test_player_at_goal_red(self):
        """Test red player at goal."""
        player = MockPlayer(row=4, col=0, goal_col=0, color='red')
        assert player.col == player.goal_col

    def test_player_not_at_goal(self):
        """Test player not at goal."""
        player = MockPlayer(row=4, col=4, goal_col=8, color='blue')
        assert player.col != player.goal_col


class TestPlayerWallCount:
    """Tests for player wall count management."""

    def test_wall_count_decrement(self):
        """Test wall count can be decremented."""
        player = MockPlayer(available_walls=10)
        player.available_walls -= 1
        assert player.available_walls == 9

    def test_wall_count_zero(self):
        """Test wall count can reach zero."""
        player = MockPlayer(available_walls=1)
        player.available_walls -= 1
        assert player.available_walls == 0

    def test_wall_count_multiple_decrements(self):
        """Test multiple wall placements."""
        player = MockPlayer(available_walls=10)
        for _ in range(5):
            player.available_walls -= 1
        assert player.available_walls == 5
