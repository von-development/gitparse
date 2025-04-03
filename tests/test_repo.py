"""Tests for the GitRepo class."""

import tempfile
from pathlib import Path

import pytest

from gitparse.core.repository_analyzer import RepositoryAnalyzer


@pytest.fixture()
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


def test_init_with_local_path(temp_dir):
    """Test initializing GitRepo with a local path."""
    # Create a test directory
    test_dir = Path(temp_dir) / "test_repo"
    test_dir.mkdir()

    # Create a test file
    test_file = test_dir / "test.txt"
    test_file.write_text("test content")

    # Initialize repo with the test directory
    repo = RepositoryAnalyzer(str(test_dir))

    # Test public interface instead of private members
    repo_info = repo.get_repository_info()
    assert repo_info["name"] == "test_repo"

    # Test file content
    content = repo.get_file_content("test.txt")
    assert content == "test content"
