"""
Integration tests for complete game flow scenarios.

These tests verify that multiple components work together correctly
to handle complete game scenarios.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from helpers.path_helper import bfs_pathfinder, dfs_path_exists
from helpers.wall_helpers import get_blocked_roads, is_valid_wall
from helpers.valid_moves_helper import get_valid_moves_helper


class MockPlayer:
    """Mock player for integration testing."""
    def __init__(self, row, col, goal_col, color='blue', available_walls=10):
        self.row = row
        self.col = col
        self.goal_col = goal_col
        self.color = color
        self.available_walls = available_walls


class TestCompleteGameScenarios:
    """Tests for complete game scenarios."""

    def test_simple_game_no_walls(self):
        """Test a simple game where blue moves directly to goal."""
        grid_size = 9
        blocked_roads = []

        # Blue starts at (4, 0), goal is col 8
        start = (4, 0)
        goal_col = 8

        path = bfs_pathfinder(start, goal_col, grid_size, blocked_roads)

        assert path is not None
        assert path[-1][1] == goal_col
        assert len(path) == 9  # Direct path: 8 moves + start

    def test_game_with_blocking_wall(self):
        """Test game where a wall blocks the direct path."""
        grid_size = 9

        # Place a vertical wall that blocks the direct horizontal path at row 4
        # A vertical wall at column 4 between rows 3-5 blocks horizontal movement
        # at positions (4, 3)-(4, 4) and (4, 4)-(4, 5)
        wall = [(3, 4), (5, 4)]
        blocked_roads = get_blocked_roads(wall)

        start = (4, 0)
        goal_col = 8

        path = bfs_pathfinder(start, goal_col, grid_size, blocked_roads)

        assert path is not None
        assert path[-1][1] == goal_col
        # Path should be longer due to wall blocking direct route
        assert len(path) >= 9

    def test_complete_path_blocking_invalid(self):
        """Test that completely blocking a player is detected as invalid."""
        grid_size = 9

        # Create a vertical wall that would completely block blue
        wall1 = [(3, 4), (5, 4)]
        blocked_roads = get_blocked_roads(wall1)

        start = (4, 0)
        goal_col = 8

        # Path should still exist around the wall
        path = bfs_pathfinder(start, goal_col, grid_size, blocked_roads)
        assert path is not None

    def test_valid_moves_with_opponent(self):
        """Test valid moves when opponent is adjacent."""
        blue = MockPlayer(4, 4, 8, 'blue')
        red = MockPlayer(4, 5, 0, 'red')  # Adjacent to blue
        grid_size = 9
        blocked_roads = []

        valid_moves = get_valid_moves_helper(blue, red, grid_size, blocked_roads)

        # Should be able to jump over opponent
        assert 'right' in valid_moves
        assert valid_moves['right'] == (4, 6)


class TestWallPlacementScenarios:
    """Tests for wall placement scenarios."""

    def test_wall_placement_valid(self):
        """Test valid wall placement."""
        start, end = (3, 3), (3, 5)
        grid_size = 9
        placed_walls = []
        forbidden_walls = []

        assert is_valid_wall(start, end, grid_size, placed_walls, forbidden_walls) is True

    def test_wall_placement_on_border_invalid(self):
        """Test that walls on border are invalid."""
        start, end = (0, 3), (0, 5)
        grid_size = 9
        placed_walls = []
        forbidden_walls = []

        assert is_valid_wall(start, end, grid_size, placed_walls, forbidden_walls) is False

    def test_overlapping_walls_invalid(self):
        """Test that overlapping walls are invalid."""
        grid_size = 9
        placed_walls = [[(3, 3), (3, 5)]]
        forbidden_walls = []

        # Try to place the same wall again
        assert is_valid_wall((3, 3), (3, 5), grid_size, placed_walls, forbidden_walls) is False


class TestPathExistence:
    """Tests for path existence verification."""

    def test_path_exists_no_obstacles(self):
        """Test path exists with no obstacles."""
        start = (4, 0)
        goal_col = 8
        grid_size = 9
        blocked_roads = []

        assert dfs_path_exists(start, goal_col, grid_size, blocked_roads) is True

    def test_path_exists_with_walls(self):
        """Test path exists with some walls."""
        start = (4, 0)
        goal_col = 8
        grid_size = 9
        wall = [(4, 3), (4, 5)]
        blocked_roads = get_blocked_roads(wall)

        assert dfs_path_exists(start, goal_col, grid_size, blocked_roads) is True


class TestPlayerMovementIntegration:
    """Integration tests for player movement."""

    def test_blue_reaches_goal(self):
        """Test scenario where blue reaches goal."""
        blue = MockPlayer(4, 7, 8, 'blue')
        red = MockPlayer(4, 1, 0, 'red')
        grid_size = 9
        blocked_roads = []

        # Blue moves to goal
        valid_moves = get_valid_moves_helper(blue, red, grid_size, blocked_roads)
        assert 'right' in valid_moves
        assert valid_moves['right'] == (4, 8)

        # After moving, blue is at goal
        blue.col = 8
        assert blue.col == blue.goal_col

    def test_red_reaches_goal(self):
        """Test scenario where red reaches goal."""
        red = MockPlayer(4, 1, 0, 'red')
        blue = MockPlayer(4, 7, 8, 'blue')
        grid_size = 9
        blocked_roads = []

        # Red moves to goal
        valid_moves = get_valid_moves_helper(red, blue, grid_size, blocked_roads)
        assert 'left' in valid_moves
        assert valid_moves['left'] == (4, 0)

        # After moving, red is at goal
        red.col = 0
        assert red.col == red.goal_col
