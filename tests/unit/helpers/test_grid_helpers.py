"""
Tests for grid_helpers.py

This module tests coordinate conversion functions between grid and scene coordinates.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from helpers.grid_helpers import grid_to_scene, scene_to_grid


class TestGridToScene:
    """Tests for grid_to_scene function."""

    def test_grid_to_scene_origin(self):
        """Test conversion of (0, 0) grid position."""
        result = grid_to_scene(0, 0, 50)
        assert result.x() == 0
        assert result.y() == 0

    def test_grid_to_scene_simple_position(self):
        """Test conversion of a simple grid position."""
        result = grid_to_scene(1, 2, 50)
        assert result.x() == 100  # col * cell_size = 2 * 50
        assert result.y() == 50   # row * cell_size = 1 * 50

    def test_grid_to_scene_larger_grid(self):
        """Test conversion with larger grid coordinates."""
        result = grid_to_scene(4, 8, 60)
        assert result.x() == 480  # 8 * 60
        assert result.y() == 240  # 4 * 60

    def test_grid_to_scene_different_cell_sizes(self):
        """Test conversion with different cell sizes."""
        # Small cell size
        result = grid_to_scene(2, 3, 10)
        assert result.x() == 30
        assert result.y() == 20

        # Large cell size
        result = grid_to_scene(2, 3, 100)
        assert result.x() == 300
        assert result.y() == 200


class TestSceneToGrid:
    """Tests for scene_to_grid function."""

    def test_scene_to_grid_origin(self):
        """Test conversion of (0, 0) scene position."""
        from PyQt6.QtCore import QPointF
        result = scene_to_grid(QPointF(0, 0), 50)
        assert result == (0, 0)

    def test_scene_to_grid_simple_position(self):
        """Test conversion of a simple scene position."""
        from PyQt6.QtCore import QPointF
        result = scene_to_grid(QPointF(100, 50), 50)
        assert result == (1, 2)  # (y/cell_size, x/cell_size)

    def test_scene_to_grid_rounding(self):
        """Test that scene_to_grid properly rounds values."""
        from PyQt6.QtCore import QPointF
        # Position slightly off exact grid point
        result = scene_to_grid(QPointF(105, 55), 50)
        assert result == (1, 2)  # Should round to same position

    def test_scene_to_grid_different_cell_sizes(self):
        """Test conversion with different cell sizes."""
        from PyQt6.QtCore import QPointF
        result = scene_to_grid(QPointF(300, 200), 100)
        assert result == (2, 3)


class TestGridSceneRoundTrip:
    """Tests for round-trip conversions between grid and scene."""

    def test_round_trip_conversion(self):
        """Test that grid->scene->grid returns original coordinates."""
        original_row, original_col = 3, 5
        cell_size = 50

        scene_pos = grid_to_scene(original_row, original_col, cell_size)
        result_row, result_col = scene_to_grid(scene_pos, cell_size)

        assert (result_row, result_col) == (original_row, original_col)

    def test_round_trip_multiple_positions(self):
        """Test round-trip for multiple positions."""
        cell_size = 60
        test_positions = [
            (0, 0),
            (4, 4),
            (8, 8),
            (0, 8),
            (8, 0),
        ]

        for row, col in test_positions:
            scene_pos = grid_to_scene(row, col, cell_size)
            result_row, result_col = scene_to_grid(scene_pos, cell_size)
            assert (result_row, result_col) == (row, col)
