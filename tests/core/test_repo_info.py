"""Tests for repository info functionality."""
import os
from pathlib import Path

import pytest

from gitparse import GitRepo


@pytest.fixture
def local_repo():
    """Create a test repository fixture."""
    # Use the current repository for testing
    current_dir = Path(os.getcwd())
    return GitRepo(current_dir)


def test_get_repo_info(local_repo):
    """Test getting repository information."""
    info = local_repo.get_repo_info()
    
    # Basic assertions
    assert info is not None
    assert isinstance(info, dict)
    assert "name" in info
    assert info["name"] == "git-parser"  # Should match your repository name
    
    # Check for common fields
    assert "is_bare" in info
    assert isinstance(info["is_bare"], bool)
    
    # Check branch info
    assert "default_branch" in info
    assert isinstance(info["default_branch"], str)
    
    # Check commit info
    assert "head_commit" in info
    assert isinstance(info["head_commit"], str)
    
    # Check remotes
    assert "remotes" in info
    assert isinstance(info["remotes"], list) 