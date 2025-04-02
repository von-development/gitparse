"""Test configuration for pytest."""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir) 