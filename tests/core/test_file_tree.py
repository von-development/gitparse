"""Tests for file tree functionality."""

import os
from pathlib import Path

import pytest

from gitparse import GitRepo


@pytest.fixture
def local_repo():
    """Create a test repository fixture."""
    current_dir = Path(os.getcwd())
    return GitRepo(current_dir)


def test_get_file_tree_dict(local_repo):
    """Test getting file tree in dictionary format."""
    tree = local_repo.get_file_tree(style="dict")

    # Basic assertions
    assert tree is not None
    assert isinstance(tree, dict)
    assert len(tree) > 0

    # Check for common files
    def has_file(tree_dict: dict, filename: str) -> bool:
        """Recursively check if file exists in tree."""
        for key, value in tree_dict.items():
            if key == filename:
                return True
            if isinstance(value, dict):
                if has_file(value, filename):
                    return True
        return False

    # Check for common files
    assert has_file(tree, "pyproject.toml")
    assert has_file(tree, "README.md")


def test_get_file_tree_markdown(local_repo):
    """Test getting file tree in markdown format."""
    tree = local_repo.get_file_tree(style="markdown")

    # Basic assertions
    assert tree is not None
    assert isinstance(tree, list)
    assert len(tree) > 0

    # Check markdown formatting
    for line in tree:
        assert isinstance(line, str)
        # Each line should start with spaces and -
        assert line.lstrip().startswith("-")
