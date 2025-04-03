"""Language statistics functions."""

from __future__ import annotations

from typing import Optional, Union

from gitparse.core.repo import GitRepo
from gitparse.core.async_repo import AsyncGitRepo
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
    repo = GitRepo(source, config)
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
    async with AsyncGitRepo(source, config) as repo:
        return await repo.get_language_stats(output_file) 