"""
Pytest configuration and shared fixtures for QuoridorX tests.
"""

import pytest
import sys
import os

# Add src directory to Python path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


@pytest.fixture(autouse=True)
def clear_path_cache():
    """Clear the pathfinding cache before each test."""
    from helpers.path_helper import clear_cache
    clear_cache()
    yield
