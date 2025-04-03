"""Repository statistics functions."""

from __future__ import annotations

from typing import Any, Optional, Union
from pathlib import Path

from gitparse.core.repo import GitRepo
from gitparse.core.async_repo import AsyncGitRepo
from gitparse.schema.config import ExtractionConfig


def get_statistics(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[Union[str, Path]] = None,
) -> dict[str, Any]:
    """Get overall repository statistics.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dictionary containing repository statistics
    """
    repo = GitRepo(source, config)
    return repo.get_statistics(output_file)


async def async_get_statistics(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[Union[str, Path]] = None,
) -> dict[str, Any]:
    """Get overall repository statistics asynchronously.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dictionary containing repository statistics
    """
    async with AsyncGitRepo(source, config) as repo:
        return await repo.get_statistics(output_file) 