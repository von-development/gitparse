"""Language statistics functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from gitparse.core.async_repo_analyzer import AsyncRepositoryAnalyzer
from gitparse.core.repository_analyzer import RepositoryAnalyzer

if TYPE_CHECKING:
    from gitparse.schema.config import ExtractionConfig


def get_language_stats(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
) -> dict[str, dict[str, Union[int, float]]]:
    """Get language statistics for a repository.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dictionary containing language statistics
    """
    repo = RepositoryAnalyzer(source, config)
    return repo.get_language_stats(output_file)


async def async_get_language_stats(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
) -> dict[str, dict[str, Union[int, float]]]:
    """Get language statistics for a repository asynchronously.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dictionary containing language statistics
    """
    async with AsyncRepositoryAnalyzer(source, config) as repo:
        return await repo.get_language_stats(output_file)
