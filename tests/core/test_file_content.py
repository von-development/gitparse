"""Tests for file content functionality."""

import os
from pathlib import Path

import pytest

from gitparse import GitRepo


@pytest.fixture
def local_repo():
    """Create a test repository fixture."""
    current_dir = Path(os.getcwd())
    return GitRepo(current_dir)


def test_get_file_content(local_repo):
    """Test getting file content."""
    # Test with README.md
    content = local_repo.get_file_content("README.md")

    # Basic assertions
    assert content is not None
    assert isinstance(content, str)
    assert len(content) > 0
    assert "GitParse" in content

    # Test with pyproject.toml
    content = local_repo.get_file_content("pyproject.toml")
    assert content is not None
    assert isinstance(content, str)
    assert len(content) > 0
    assert "[project]" in content
    assert "gitparse" in content.lower()

    # Test with non-existent file
    content = local_repo.get_file_content("nonexistent.txt")
    assert content is None


def test_get_all_contents(local_repo):
    """Test getting all file contents."""
    contents = local_repo.get_all_contents()

    # Basic assertions
    assert contents is not None
    assert isinstance(contents, dict)
    assert len(contents) > 0

    # Check for common files
    assert any("README.md" in path for path in contents.keys())
    assert any("pyproject.toml" in path for path in contents.keys())

    # Check content types
    for path, content in contents.items():
        assert isinstance(path, str)
        assert isinstance(content, str)
        assert len(content) > 0
