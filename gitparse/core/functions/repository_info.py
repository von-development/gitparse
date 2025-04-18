"""Repository information functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from gitparse.core.async_repo_analyzer import AsyncRepositoryAnalyzer
from gitparse.core.repository_analyzer import RepositoryAnalyzer

if TYPE_CHECKING:
    from pathlib import Path

    from gitparse.schema.config import ExtractionConfig


def get_repository_info(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[Union[str, Path]] = None,
) -> dict[str, str]:
    """Get basic information about a Git repository.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dict with repository information (name, default branch, etc.)
    """
    repo = RepositoryAnalyzer(source, config)
    return repo.get_repository_info(output_file)


async def async_get_repository_info(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[Union[str, Path]] = None,
) -> dict[str, str]:
    """Get basic information about a Git repository asynchronously.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dict with repository information (name, default branch, etc.)
    """
    async with AsyncRepositoryAnalyzer(source, config) as repo:
        return await repo.get_repository_info(output_file)
