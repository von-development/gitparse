"""Tests for repository statistics functionality."""
import os
from pathlib import Path

import pytest

from gitparse import GitRepo


@pytest.fixture
def local_repo():
    """Create a test repository fixture."""
    current_dir = Path(os.getcwd())
    return GitRepo(current_dir)


def test_get_repo_stats(local_repo):
    """Test getting repository statistics."""
    stats = local_repo.get_repo_stats()
    
    # Basic assertions
    assert stats is not None
    assert isinstance(stats, dict)
    
    # Check for required fields
    required_fields = [
        "total_files",
        "total_size",
        "average_file_size",
        "binary_ratio",
        "file_types",
        "largest_files"
    ]
    for field in required_fields:
        assert field in stats
    
    # Check types and values
    assert isinstance(stats["total_files"], int)
    assert stats["total_files"] > 0
    
    assert isinstance(stats["total_size"], int)
    assert stats["total_size"] > 0
    
    assert isinstance(stats["average_file_size"], float)
    assert stats["average_file_size"] > 0
    
    assert isinstance(stats["binary_ratio"], float)
    assert 0 <= stats["binary_ratio"] <= 1
    
    assert isinstance(stats["file_types"], dict)
    assert len(stats["file_types"]) > 0
    
    assert isinstance(stats["largest_files"], list)
    for file_info in stats["largest_files"]:
        assert isinstance(file_info, dict)
        assert "path" in file_info
        assert "size" in file_info 