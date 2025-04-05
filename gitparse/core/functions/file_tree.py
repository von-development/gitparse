"""File tree-related functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Union

from gitparse.core.async_repo_analyzer import AsyncRepositoryAnalyzer
from gitparse.core.repository_analyzer import RepositoryAnalyzer

if TYPE_CHECKING:
    from pathlib import Path

    from gitparse.schema.config import ExtractionConfig


def get_file_tree(
    source: str,
    style: Literal["flattened", "markdown", "structured", "dict"] = "flattened",
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[Union[str, Path]] = None,
) -> Union[list[str], dict]:
    """Get repository file tree in specified format.

    Args:
        source: Local path or GitHub URL to the repository
        style: Output style ("flattened", "markdown", "structured", or "dict")
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        List of files or structured dictionary
    """
    repo = RepositoryAnalyzer(source, config)
    return repo.get_file_tree(style, output_file)


async def async_get_file_tree(
    source: str,
    style: Literal["flattened", "markdown", "structured", "dict"] = "flattened",
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[Union[str, Path]] = None,
) -> Union[list[str], dict]:
    """Get repository file tree asynchronously.

    Args:
        source: Local path or GitHub URL to the repository
        style: Output style ("flattened", "markdown", "structured", or "dict")
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        List of files or structured dictionary
    """
    async with AsyncRepositoryAnalyzer(source, config) as repo:
        return await repo.get_file_tree(style, output_file)
