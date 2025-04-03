"""README content functions."""

from __future__ import annotations

from typing import Optional, Union
from pathlib import Path

from gitparse.core.repo import GitRepo
from gitparse.core.async_repo import AsyncGitRepo
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
    repo = GitRepo(source, config)
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
    async with AsyncGitRepo(source, config) as repo:
        return await repo.get_readme_content(output_file) 