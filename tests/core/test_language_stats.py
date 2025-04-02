"""Tests for language statistics functionality."""

import os
from pathlib import Path

import pytest

from gitparse import GitRepo


@pytest.fixture
def local_repo():
    """Create a test repository fixture."""
    current_dir = Path(os.getcwd())
    return GitRepo(current_dir)


def test_get_language_stats(local_repo):
    """Test getting language statistics."""
    stats = local_repo.get_language_stats()

    # Basic assertions
    assert stats is not None
    assert isinstance(stats, dict)
    assert len(stats) > 0

    # Check for Python stats (since this is a Python project)
    assert "Python" in stats
    python_stats = stats["Python"]

    # Check stats structure
    assert isinstance(python_stats, dict)
    assert "files" in python_stats
    assert "bytes" in python_stats
    assert "percentage" in python_stats

    # Check stats types
    assert isinstance(python_stats["files"], int)
    assert isinstance(python_stats["bytes"], int)
    assert isinstance(python_stats["percentage"], float)

    # Check reasonable values
    assert python_stats["files"] > 0
    assert python_stats["bytes"] > 0
    assert 0 <= python_stats["percentage"] <= 100
