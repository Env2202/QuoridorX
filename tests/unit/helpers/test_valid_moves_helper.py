"""
Tests for valid_moves_helper.py

This module tests the valid move calculation logic for player movement.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from helpers.valid_moves_helper import (
    get_valid_moves_helper,
    where_is_other_player,
    is_there_a_wall
)


class MockPlayer:
    """Mock player for testing."""
    def __init__(self, row, col):
        self.row = row
        self.col = col


class TestWhereIsOtherPlayer:
    """Tests for where_is_other_player function."""

    def test_other_player_above(self):
        """Test detecting player directly above."""
        player = MockPlayer(4, 4)
        other = MockPlayer(3, 4)
        assert where_is_other_player(player, other) == 'up'

    def test_other_player_below(self):
        """Test detecting player directly below."""
        player = MockPlayer(4, 4)
        other = MockPlayer(5, 4)
        assert where_is_other_player(player, other) == 'down'

    def test_other_player_left(self):
        """Test detecting player directly to the left."""
        player = MockPlayer(4, 4)
        other = MockPlayer(4, 3)
        assert where_is_other_player(player, other) == 'left'

    def test_other_player_right(self):
        """Test detecting player directly to the right."""
        player = MockPlayer(4, 4)
        other = MockPlayer(4, 5)
        assert where_is_other_player(player, other) == 'right'

    def test_other_player_not_adjacent(self):
        """Test when other player is not adjacent."""
        player = MockPlayer(4, 4)
        other = MockPlayer(6, 4)  # Two rows away
        assert where_is_other_player(player, other) is None

    def test_other_player_diagonal(self):
        """Test when other player is diagonal (not adjacent in cardinal direction)."""
        player = MockPlayer(4, 4)
        other = MockPlayer(5, 5)
        assert where_is_other_player(player, other) is None

    def test_other_player_same_position(self):
        """Test when other player is at same position."""
        player = MockPlayer(4, 4)
        other = MockPlayer(4, 4)
        assert where_is_other_player(player, other) is None


class TestIsThereAWall:
    """Tests for is_there_a_wall function."""

    def test_no_wall_blocking_jump(self):
        """Test when no wall blocks the jump over another player."""
        player = MockPlayer(4, 4)
        directions = {'up': (0, -2), 'down': (0, 2), 'left': (-2, 0), 'right': (2, 0)}
        blocked_roads = []
        result = is_there_a_wall(player, 'up', directions.copy(), blocked_roads)
        assert 'up' in result

    def test_wall_blocking_jump_up(self):
        """Test when a wall blocks jumping up over another player."""
        player = MockPlayer(4, 4)
        directions = {'up': (0, -2), 'down': (0, 2), 'left': (-2, 0), 'right': (2, 0)}
        # Wall between player and player above
        blocked_roads = [[(4, 4), (3, 4)]]
        result = is_there_a_wall(player, 'up', directions.copy(), blocked_roads)
        assert 'up' not in result

    def test_wall_blocking_jump_down(self):
        """Test when a wall blocks jumping down over another player."""
        player = MockPlayer(4, 4)
        directions = {'up': (0, -2), 'down': (0, 2), 'left': (-2, 0), 'right': (2, 0)}
        blocked_roads = [[(4, 4), (5, 4)]]
        result = is_there_a_wall(player, 'down', directions.copy(), blocked_roads)
        assert 'down' not in result

    def test_wall_blocking_jump_left(self):
        """Test when a wall blocks jumping left over another player."""
        player = MockPlayer(4, 4)
        directions = {'up': (0, -2), 'down': (0, 2), 'left': (-2, 0), 'right': (2, 0)}
        blocked_roads = [[(4, 4), (4, 3)]]
        result = is_there_a_wall(player, 'left', directions.copy(), blocked_roads)
        assert 'left' not in result

    def test_wall_blocking_jump_right(self):
        """Test when a wall blocks jumping right over another player."""
        player = MockPlayer(4, 4)
        directions = {'up': (0, -2), 'down': (0, 2), 'left': (-2, 0), 'right': (2, 0)}
        blocked_roads = [[(4, 4), (4, 5)]]
        result = is_there_a_wall(player, 'right', directions.copy(), blocked_roads)
        assert 'right' not in result


class TestGetValidMovesHelper:
    """Tests for get_valid_moves_helper function."""

    def test_basic_movement_no_walls(self):
        """Test basic movement in all directions with no walls."""
        player = MockPlayer(4, 4)
        other = MockPlayer(0, 0)  # Far away
        grid_size = 9
        blocked_roads = []

        result = get_valid_moves_helper(player, other, grid_size, blocked_roads)

        assert 'up' in result
        assert 'down' in result
        assert 'left' in result
        assert 'right' in result
        assert result['up'] == (3, 4)
        assert result['down'] == (5, 4)
        assert result['left'] == (4, 3)
        assert result['right'] == (4, 5)

    def test_movement_blocked_by_wall(self):
        """Test that movement is blocked by walls."""
        player = MockPlayer(4, 4)
        other = MockPlayer(0, 0)
        grid_size = 9
        blocked_roads = [[(4, 4), (3, 4)]]  # Wall above

        result = get_valid_moves_helper(player, other, grid_size, blocked_roads)

        assert 'up' not in result
        assert 'down' in result
        assert 'left' in result
        assert 'right' in result

    def test_movement_at_edge(self):
        """Test movement at grid edges."""
        player = MockPlayer(0, 0)  # Top-left corner
        other = MockPlayer(4, 4)
        grid_size = 9
        blocked_roads = []

        result = get_valid_moves_helper(player, other, grid_size, blocked_roads)

        assert 'up' not in result  # Would be out of bounds
        assert 'left' not in result  # Would be out of bounds
        assert 'down' in result
        assert 'right' in result

    def test_movement_at_bottom_right_edge(self):
        """Test movement at bottom-right corner."""
        player = MockPlayer(8, 8)  # Bottom-right corner
        other = MockPlayer(4, 4)
        grid_size = 9
        blocked_roads = []

        result = get_valid_moves_helper(player, other, grid_size, blocked_roads)

        assert 'down' not in result  # Would be out of bounds
        assert 'right' not in result  # Would be out of bounds
        assert 'up' in result
        assert 'left' in result

    def test_jump_over_adjacent_player(self):
        """Test jumping over an adjacent player."""
        player = MockPlayer(4, 4)
        other = MockPlayer(3, 4)  # Directly above
        grid_size = 9
        blocked_roads = []

        result = get_valid_moves_helper(player, other, grid_size, blocked_roads)

        # Should be able to jump to (2, 4)
        assert 'up' in result
        assert result['up'] == (2, 4)

    def test_jump_blocked_by_wall(self):
        """Test that jump is blocked when wall is behind opponent."""
        player = MockPlayer(4, 4)
        other = MockPlayer(3, 4)  # Directly above
        grid_size = 9
        # Wall behind the opponent
        blocked_roads = [[(3, 4), (2, 4)]]

        result = get_valid_moves_helper(player, other, grid_size, blocked_roads)

        # Should not be able to jump up
        assert 'up' not in result

    def test_jump_blocked_by_edge(self):
        """Test jump behavior when opponent is at edge."""
        player = MockPlayer(1, 4)
        other = MockPlayer(0, 4)  # At top edge, directly above
        grid_size = 9
        blocked_roads = []

        result = get_valid_moves_helper(player, other, grid_size, blocked_roads)

        # Cannot jump out of bounds
        assert 'up' not in result

    def test_multiple_walls_blocking(self):
        """Test movement with multiple walls blocking different directions."""
        player = MockPlayer(4, 4)
        other = MockPlayer(0, 0)
        grid_size = 9
        blocked_roads = [
            [(4, 4), (3, 4)],  # Block up
            [(4, 4), (5, 4)],  # Block down
        ]

        result = get_valid_moves_helper(player, other, grid_size, blocked_roads)

        assert 'up' not in result
        assert 'down' not in result
        assert 'left' in result
        assert 'right' in result

    def test_blocked_roads_bidirectional(self):
        """Test that blocked roads work in both directions."""
        player = MockPlayer(4, 4)
        other = MockPlayer(0, 0)
        grid_size = 9
        # Wall specified in reverse order
        blocked_roads = [[(3, 4), (4, 4)]]

        result = get_valid_moves_helper(player, other, grid_size, blocked_roads)

        assert 'up' not in result

    def test_no_valid_moves(self):
        """Test when player has no valid moves (surrounded by walls)."""
        player = MockPlayer(4, 4)
        other = MockPlayer(0, 0)
        grid_size = 9
        blocked_roads = [
            [(4, 4), (3, 4)],  # Block up
            [(4, 4), (5, 4)],  # Block down
            [(4, 4), (4, 3)],  # Block left
            [(4, 4), (4, 5)],  # Block right
        ]

        result = get_valid_moves_helper(player, other, grid_size, blocked_roads)

        assert result == {}
