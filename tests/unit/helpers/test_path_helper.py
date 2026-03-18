"""
Tests for path_helper.py

This module tests pathfinding algorithms (BFS and DFS) used for player movement
and wall placement validation.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from helpers.path_helper import (
    bfs_pathfinder,
    dfs_path_exists,
    bfs_pathfinder_cell_to_cell,
    is_path_blocked,
    clear_cache,
    cache
)


class TestBFSPathfinder:
    """Tests for bfs_pathfinder function."""

    def test_simple_path_no_walls(self):
        """Test finding path with no walls."""
        start = (4, 0)  # Starting position
        goal_col = 8    # Goal column
        grid_size = 9
        blocked_roads = []

        result = bfs_pathfinder(start, goal_col, grid_size, blocked_roads)

        assert result is not None
        assert len(result) > 0
        assert result[-1][1] == goal_col  # Last position should be in goal column

    def test_path_blocked_no_solution(self):
        """Test when path is completely blocked."""
        start = (4, 0)
        goal_col = 8
        grid_size = 9
        # Create a vertical wall blocking all paths
        blocked_roads = [
            [(i, 4), (i, 5)] for i in range(grid_size)
        ]

        result = bfs_pathfinder(start, goal_col, grid_size, blocked_roads)

        assert result is None

    def test_start_already_at_goal(self):
        """Test when start position is already at goal column."""
        start = (4, 8)
        goal_col = 8
        grid_size = 9
        blocked_roads = []

        result = bfs_pathfinder(start, goal_col, grid_size, blocked_roads)

        assert result is not None
        assert result[-1] == start

    def test_path_with_single_wall(self):
        """Test path with a single wall blocking direct route."""
        start = (4, 0)
        goal_col = 8
        grid_size = 9
        # Wall blocking direct horizontal path
        blocked_roads = [[(4, 3), (4, 4)]]

        result = bfs_pathfinder(start, goal_col, grid_size, blocked_roads)

        assert result is not None
        assert result[-1][1] == goal_col

    def test_shortest_path_length(self):
        """Test that BFS returns the shortest path."""
        start = (4, 0)
        goal_col = 4
        grid_size = 9
        blocked_roads = []

        result = bfs_pathfinder(start, goal_col, grid_size, blocked_roads)

        # Shortest path should be 5 positions (including start)
        assert len(result) == 5
        assert result == [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]

    def test_bfs_cache_usage(self):
        """Test that BFS results are cached."""
        # Clear cache first
        clear_cache()

        start = (4, 0)
        goal_col = 4
        grid_size = 9
        blocked_roads = []

        # First call should populate cache
        result1 = bfs_pathfinder(start, goal_col, grid_size, blocked_roads)

        # Second call should use cache
        result2 = bfs_pathfinder(start, goal_col, grid_size, blocked_roads)

        assert result1 == result2


class TestDFSPathExists:
    """Tests for dfs_path_exists function."""

    def test_path_exists_no_walls(self):
        """Test that path exists with no walls."""
        start = (4, 0)
        goal_col = 8
        grid_size = 9
        blocked_roads = []

        result = dfs_path_exists(start, goal_col, grid_size, blocked_roads)

        assert result is True

    def test_path_blocked(self):
        """Test when path is completely blocked."""
        start = (4, 0)
        goal_col = 8
        grid_size = 9
        # Create a vertical wall blocking all paths
        blocked_roads = [
            [(i, 4), (i, 5)] for i in range(grid_size)
        ]

        result = dfs_path_exists(start, goal_col, grid_size, blocked_roads)

        assert result is False

    def test_start_at_goal(self):
        """Test when start is already at goal."""
        start = (4, 8)
        goal_col = 8
        grid_size = 9
        blocked_roads = []

        result = dfs_path_exists(start, goal_col, grid_size, blocked_roads)

        assert result is True

    def test_dfs_cache_usage(self):
        """Test that DFS results are cached."""
        clear_cache()

        start = (4, 0)
        goal_col = 4
        grid_size = 9
        blocked_roads = []

        # First call
        result1 = dfs_path_exists(start, goal_col, grid_size, blocked_roads)

        # Second call should use cache
        result2 = dfs_path_exists(start, goal_col, grid_size, blocked_roads)

        assert result1 == result2


class TestBFSPathfinderCellToCell:
    """Tests for bfs_pathfinder_cell_to_cell function."""

    def test_path_exists_cell_to_cell(self):
        """Test finding path between two cells."""
        start = (0, 0)
        goal = (4, 4)
        grid_size = 9
        blocked_roads = []

        result = bfs_pathfinder_cell_to_cell(start, goal, grid_size, blocked_roads)

        assert result is True

    def test_path_blocked_cell_to_cell(self):
        """Test when path between cells is blocked."""
        start = (0, 0)
        goal = (0, 4)
        grid_size = 9
        # Wall completely blocking rightward movement
        blocked_roads = [
            [(i, 2), (i, 3)] for i in range(grid_size)
        ]

        result = bfs_pathfinder_cell_to_cell(start, goal, grid_size, blocked_roads)

        assert result is False

    def test_same_start_and_goal(self):
        """Test when start and goal are the same cell."""
        start = (4, 4)
        goal = (4, 4)
        grid_size = 9
        blocked_roads = []

        result = bfs_pathfinder_cell_to_cell(start, goal, grid_size, blocked_roads)

        assert result is True

    def test_shortest_path_cell_to_cell(self):
        """Test getting shortest path between cells."""
        start = (0, 0)
        goal = (0, 4)
        grid_size = 9
        blocked_roads = []

        result = bfs_pathfinder_cell_to_cell(
            start, goal, grid_size, blocked_roads, find_shortest_path=True
        )

        assert isinstance(result, list)
        assert result[0] == start
        assert result[-1] == goal
        assert len(result) == 5  # Direct path: 4 steps + start

    def test_no_path_returns_empty_list(self):
        """Test that empty list is returned when no path exists."""
        start = (0, 0)
        goal = (0, 4)
        grid_size = 9
        # Wall completely blocking
        blocked_roads = [
            [(i, 2), (i, 3)] for i in range(grid_size)
        ]

        result = bfs_pathfinder_cell_to_cell(
            start, goal, grid_size, blocked_roads, find_shortest_path=True
        )

        assert result == []


class TestIsPathBlocked:
    """Tests for is_path_blocked function."""

    def test_path_is_blocked(self):
        """Test detecting blocked path."""
        pos1 = (2, 2)
        pos2 = (2, 3)
        blocked_roads = [[(2, 2), (2, 3)]]

        assert is_path_blocked(pos1, pos2, blocked_roads) is True

    def test_path_not_blocked(self):
        """Test when path is not blocked."""
        pos1 = (2, 2)
        pos2 = (2, 3)
        blocked_roads = [[(3, 2), (3, 3)]]

        assert is_path_blocked(pos1, pos2, blocked_roads) is False

    def test_path_blocked_reverse_order(self):
        """Test that blocked path detection works in reverse order."""
        pos1 = (2, 2)
        pos2 = (2, 3)
        blocked_roads = [[(2, 3), (2, 2)]]

        assert is_path_blocked(pos1, pos2, blocked_roads) is True


class TestClearCache:
    """Tests for clear_cache function."""

    def test_clear_cache_reduces_size(self):
        """Test that clear_cache reduces cache size when over limit."""
        global cache
        # Fully clear the cache first
        cache.clear()

        # Populate cache with many entries
        for i in range(1100):
            cache[f'key_{i}'] = f'value_{i}'

        assert len(cache) == 1100

        clear_cache()

        # Cache should be reduced to 1000 entries
        assert len(cache) == 1000

    def test_clear_cache_preserves_small_cache(self):
        """Test that clear_cache doesn't affect small caches."""
        global cache
        # Fully clear the cache first
        cache.clear()
        cache['test_key'] = 'test_value'

        clear_cache()

        assert 'test_key' in cache
