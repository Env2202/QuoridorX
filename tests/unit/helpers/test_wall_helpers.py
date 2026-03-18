"""
Tests for wall_helpers.py

This module tests wall placement logic, validation, and intersection detection.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from helpers.wall_helpers import (
    get_blocked_roads,
    order_walls,
    is_wall_within_bounds,
    walls_intersect,
    is_valid_wall,
    find_valid_walls,
    hashable_walls,
    hashable_blocked_roads,
)


class TestGetBlockedRoads:
    """Tests for get_blocked_roads function."""

    def test_vertical_wall_blocked_roads(self):
        """Test blocked roads for a vertical wall."""
        # Vertical wall at column 4, spanning rows 2-4
        wall = [(2, 4), (4, 4)]
        result = get_blocked_roads(wall)

        # Should block roads to the left of the wall
        expected = [
            [(2, 3), (2, 4)],
            [(3, 3), (3, 4)]
        ]
        assert result == expected

    def test_horizontal_wall_blocked_roads(self):
        """Test blocked roads for a horizontal wall."""
        # Horizontal wall at row 4, spanning columns 2-4
        wall = [(4, 2), (4, 4)]
        result = get_blocked_roads(wall)

        # Should block roads above the wall
        expected = [
            [(3, 2), (4, 2)],
            [(3, 3), (4, 3)]
        ]
        assert result == expected


class TestOrderWalls:
    """Tests for order_walls function."""

    def test_already_ordered_wall(self):
        """Test wall that is already ordered correctly."""
        wall = [(2, 3), (4, 3)]
        result = order_walls(wall)
        assert result == [(2, 3), (4, 3)]

    def test_unordered_wall_vertical(self):
        """Test vertical wall that needs reordering."""
        wall = [(4, 3), (2, 3)]
        result = order_walls(wall)
        assert result == [(2, 3), (4, 3)]

    def test_unordered_wall_horizontal(self):
        """Test horizontal wall that needs reordering."""
        wall = [(3, 5), (3, 3)]
        result = order_walls(wall)
        assert result == [(3, 3), (3, 5)]

    def test_wall_same_row_col(self):
        """Test wall where start > end in both dimensions."""
        wall = [(5, 5), (3, 3)]
        result = order_walls(wall)
        assert result == [(3, 3), (5, 5)]


class TestIsWallWithinBounds:
    """Tests for is_wall_within_bounds function."""

    def test_wall_within_bounds(self):
        """Test wall completely within grid bounds."""
        wall = [(2, 2), (2, 4)]
        assert is_wall_within_bounds(wall, 9) is True

    def test_wall_at_boundary(self):
        """Test wall at grid boundary."""
        wall = [(0, 0), (0, 2)]
        assert is_wall_within_bounds(wall, 9) is True

    def test_wall_at_max_boundary(self):
        """Test wall at maximum grid boundary."""
        wall = [(8, 7), (8, 9)]
        assert is_wall_within_bounds(wall, 9) is True

    def test_wall_out_of_bounds_negative(self):
        """Test wall with negative coordinates."""
        wall = [(-1, 2), (1, 2)]
        assert is_wall_within_bounds(wall, 9) is False

    def test_wall_out_of_bounds_positive(self):
        """Test wall exceeding grid size."""
        wall = [(2, 8), (2, 10)]
        assert is_wall_within_bounds(wall, 9) is False


class TestWallsIntersect:
    """Tests for walls_intersect function."""

    def test_walls_crossing_middle(self):
        """Test walls that cross at their middle points."""
        # Vertical wall
        start1, end1 = (2, 4), (4, 4)
        # Horizontal wall crossing it
        start2, end2 = (3, 3), (3, 5)
        assert walls_intersect(start1, end1, start2, end2) is True

    def test_walls_not_intersecting(self):
        """Test walls that don't intersect."""
        start1, end1 = (2, 2), (4, 2)
        start2, end2 = (2, 5), (4, 5)
        assert walls_intersect(start1, end1, start2, end2) is False

    def test_walls_parallel(self):
        """Test parallel walls."""
        start1, end1 = (2, 2), (4, 2)
        start2, end2 = (2, 4), (4, 4)
        assert walls_intersect(start1, end1, start2, end2) is False

    def test_wall_touches_end(self):
        """Test when one wall touches the end of another."""
        start1, end1 = (2, 4), (4, 4)
        start2, end2 = (4, 4), (4, 6)
        assert walls_intersect(start1, end1, start2, end2) is True


class TestIsValidWall:
    """Tests for is_valid_wall function."""

    def test_valid_wall_placement(self):
        """Test a completely valid wall placement."""
        start, end = (2, 2), (2, 4)
        grid_size = 9
        placed_walls = []
        forbidden_walls = []
        assert is_valid_wall(start, end, grid_size, placed_walls, forbidden_walls) is True

    def test_wall_on_border_top(self):
        """Test wall placed on top border."""
        start, end = (0, 2), (0, 4)
        grid_size = 9
        placed_walls = []
        forbidden_walls = []
        assert is_valid_wall(start, end, grid_size, placed_walls, forbidden_walls) is False

    def test_wall_on_border_bottom(self):
        """Test wall placed on bottom border."""
        start, end = (9, 2), (9, 4)
        grid_size = 9
        placed_walls = []
        forbidden_walls = []
        assert is_valid_wall(start, end, grid_size, placed_walls, forbidden_walls) is False

    def test_wall_on_border_left(self):
        """Test wall placed on left border."""
        start, end = (2, 0), (4, 0)
        grid_size = 9
        placed_walls = []
        forbidden_walls = []
        assert is_valid_wall(start, end, grid_size, placed_walls, forbidden_walls) is False

    def test_wall_on_border_right(self):
        """Test wall placed on right border."""
        start, end = (2, 9), (4, 9)
        grid_size = 9
        placed_walls = []
        forbidden_walls = []
        assert is_valid_wall(start, end, grid_size, placed_walls, forbidden_walls) is False

    def test_wall_already_exists(self):
        """Test placing a wall where one already exists."""
        start, end = (2, 2), (2, 4)
        grid_size = 9
        placed_walls = [[(2, 2), (2, 4)]]
        forbidden_walls = []
        assert is_valid_wall(start, end, grid_size, placed_walls, forbidden_walls) is False

    def test_wall_intersects_existing(self):
        """Test wall that intersects with existing wall."""
        # Existing vertical wall
        placed_walls = [[(2, 4), (4, 4)]]
        # New horizontal wall crossing it
        start, end = (3, 3), (3, 5)
        grid_size = 9
        forbidden_walls = []
        assert is_valid_wall(start, end, grid_size, placed_walls, forbidden_walls) is False

    def test_wall_is_forbidden(self):
        """Test placing a wall that is in the forbidden list."""
        start, end = (2, 2), (2, 4)
        grid_size = 9
        placed_walls = []
        forbidden_walls = [[(2, 2), (2, 4)]]
        assert is_valid_wall(start, end, grid_size, placed_walls, forbidden_walls) is False

    def test_wall_out_of_bounds(self):
        """Test wall placed outside grid bounds."""
        start, end = (10, 2), (10, 4)
        grid_size = 9
        placed_walls = []
        forbidden_walls = []
        assert is_valid_wall(start, end, grid_size, placed_walls, forbidden_walls) is False


class TestFindValidWalls:
    """Tests for find_valid_walls function."""

    def test_no_placed_walls(self):
        """Test finding valid walls with no walls placed."""
        grid_size = 5  # Small grid for testing
        placed_walls = []
        forbidden_walls = []

        result = find_valid_walls(grid_size, placed_walls, forbidden_walls)

        # Should find valid horizontal and vertical walls
        assert len(result) > 0
        # All returned walls should be valid
        for wall in result:
            assert is_valid_wall(wall[0], wall[1], grid_size, placed_walls, forbidden_walls) is True

    def test_with_placed_walls(self):
        """Test finding valid walls with some walls already placed."""
        grid_size = 5
        placed_walls = [[(2, 2), (2, 4)]]  # One horizontal wall
        forbidden_walls = []

        result = find_valid_walls(grid_size, placed_walls, forbidden_walls)

        # Should still find valid walls
        assert len(result) > 0
        # The placed wall should not be in the result
        assert [(2, 2), (2, 4)] not in result

    def test_with_forbidden_walls(self):
        """Test that forbidden walls are excluded."""
        grid_size = 5
        placed_walls = []
        forbidden_walls = [[(3, 3), (3, 5)]]

        result = find_valid_walls(grid_size, placed_walls, forbidden_walls)

        # The forbidden wall should not be in the result
        assert [(3, 3), (3, 5)] not in result


class TestHashableWalls:
    """Tests for hashable_walls function."""

    def test_hashable_walls_conversion(self):
        """Test conversion of walls to hashable format."""
        walls = [[(2, 2), (2, 4)], [(4, 3), (6, 3)]]
        result = hashable_walls(walls)

        # Result should be a tuple
        assert isinstance(result, tuple)
        # Each element should be a frozenset
        for wall in result:
            assert isinstance(wall, frozenset)

    def test_hashable_walls_empty(self):
        """Test conversion of empty walls list."""
        walls = []
        result = hashable_walls(walls)
        assert result == ()


class TestHashableBlockedRoads:
    """Tests for hashable_blocked_roads function."""

    def test_hashable_blocked_roads_conversion(self):
        """Test conversion of blocked roads to hashable format."""
        roads = [[(2, 2), (2, 3)], [(3, 4), (4, 4)]]
        result = hashable_blocked_roads(roads)

        # Result should be a tuple
        assert isinstance(result, tuple)
        # Each element should be a frozenset
        for road in result:
            assert isinstance(road, frozenset)
