"""README-related functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from gitparse.core.async_repo_analyzer import AsyncRepositoryAnalyzer
from gitparse.core.repository_analyzer import RepositoryAnalyzer

if TYPE_CHECKING:
    from pathlib import Path

    from gitparse.schema.config import ExtractionConfig


def get_readme_content(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[Union[str, Path]] = None,
) -> Optional[str]:
    """Get the content of a repository's README file.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        README content as string or None if not found
    """
    repo = RepositoryAnalyzer(source, config)
    return repo.get_readme_content(output_file)


async def async_get_readme_content(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[Union[str, Path]] = None,
) -> Optional[str]:
    """Get the content of a repository's README file asynchronously.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        README content as string or None if not found
    """
    async with AsyncRepositoryAnalyzer(source, config) as repo:
        return await repo.get_readme_content(output_file)
