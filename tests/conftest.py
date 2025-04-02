"""Test configuration for pytest."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture()
def temp_repo():
    """Create a temporary repository for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)
