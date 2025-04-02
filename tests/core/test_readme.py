"""Tests for README functionality."""

import os
from pathlib import Path

import pytest

from gitparse import GitRepo


@pytest.fixture
def local_repo():
    """Create a test repository fixture."""
    current_dir = Path(os.getcwd())
    return GitRepo(current_dir)


def test_get_readme_content(local_repo):
    """Test getting README content."""
    content = local_repo.get_readme_content()

    # Basic assertions
    assert content is not None
    assert isinstance(content, str)
    assert len(content) > 0

    # Check for common README sections
    assert "# GitParse" in content
    assert "## Installation" in content
    assert "## Usage" in content

    # Check content type
    assert content.startswith("#") or content.startswith("GitParse")
