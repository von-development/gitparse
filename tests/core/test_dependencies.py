"""Tests for dependencies functionality."""
import os
from pathlib import Path

import pytest

from gitparse import GitRepo


@pytest.fixture
def local_repo():
    """Create a test repository fixture."""
    current_dir = Path(os.getcwd())
    return GitRepo(current_dir)


def test_get_dependencies(local_repo):
    """Test getting repository dependencies."""
    deps = local_repo.get_dependencies()
    
    # Basic assertions
    assert deps is not None
    assert isinstance(deps, dict)
    
    # Check for package files
    assert "pyproject.toml" in deps
    assert isinstance(deps["pyproject.toml"], dict)
    
    # Check for dependencies sections
    pyproject_deps = deps["pyproject.toml"]
    assert "dependencies" in pyproject_deps
    assert "dev-dependencies" in pyproject_deps
    
    # Check for specific dependencies
    dependencies = pyproject_deps["dependencies"]
    assert isinstance(dependencies, dict)  # Dependencies are now a dict
    
    # Check for specific packages
    assert "gitpython" in dependencies
    assert "pydantic" in dependencies
    
    # Print dependencies for debugging
    print("\nDependencies:", dependencies)
    
    # Check for specific packages
    assert "gitpython" in dependencies or any("gitpython" in name.lower() for name in dependencies)

    # Check for pydantic
    assert any("pydantic" in dep.lower() for dep in dependencies.values()) 