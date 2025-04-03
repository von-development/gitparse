"""Dependency analysis functions."""

from __future__ import annotations

from typing import Optional, Union
from pathlib import Path

from gitparse.core.repo import GitRepo
from gitparse.core.async_repo import AsyncGitRepo
from gitparse.schema.config import ExtractionConfig


def get_dependencies(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
) -> dict[str, Union[list[str], dict[str, str]]]:
    """Get repository dependencies from package files.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dictionary containing dependencies from various package files
    """
    repo = GitRepo(source, config)
    return repo.get_dependencies(output_file)


async def async_get_dependencies(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
) -> dict[str, Union[list[str], dict[str, str]]]:
    """Get repository dependencies from package files asynchronously.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dictionary containing dependencies from various package files
    """
    async with AsyncGitRepo(source, config) as repo:
        return await repo.get_dependencies(output_file) 