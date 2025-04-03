"""Repository statistics functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

from gitparse.core.async_repo_analyzer import AsyncRepositoryAnalyzer
from gitparse.core.repository_analyzer import RepositoryAnalyzer

if TYPE_CHECKING:
    from pathlib import Path

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
    repo = RepositoryAnalyzer(source, config)
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
    async with AsyncRepositoryAnalyzer(source, config) as repo:
        return await repo.get_statistics(output_file)
