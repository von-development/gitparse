"""Directory-related functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Optional, Union

from gitparse.core.async_repo_analyzer import AsyncRepositoryAnalyzer
from gitparse.core.repository_analyzer import RepositoryAnalyzer

if TYPE_CHECKING:
    from gitparse.schema.config import ExtractionConfig


def get_directory_tree(
    source: str,
    directory: str,
    style: Literal["flattened", "markdown", "structured"] = "flattened",
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
) -> Union[list[str], dict]:
    """Get file tree for a specific directory.

    Args:
        source: Local path or GitHub URL to the repository
        directory: Directory path within the repository
        style: Output style ("flattened", "markdown", or "structured")
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        List of files or structured dictionary
    """
    repo = RepositoryAnalyzer(source, config)
    return repo.get_directory_tree(directory, style, output_file)


async def async_get_directory_tree(
    source: str,
    directory: str,
    style: Literal["flattened", "markdown", "structured"] = "flattened",
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
) -> Union[list[str], dict[str, Any]]:
    """Get file tree for a specific directory asynchronously.

    Args:
        source: Local path or GitHub URL to the repository
        directory: Directory path within the repository
        style: Output style ("flattened", "markdown", or "structured")
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        List of files or structured dictionary
    """
    async with AsyncRepositoryAnalyzer(source, config) as repo:
        return await repo.get_directory_tree(directory, style, output_file)


def get_directory_contents(
    source: str,
    directory: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
) -> dict[str, str]:
    """Get contents of all files in a directory.

    Args:
        source: Local path or GitHub URL to the repository
        directory: Directory path within the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dictionary mapping file paths to their contents
    """
    repo = RepositoryAnalyzer(source, config)
    return repo.get_directory_contents(directory, output_file)


async def async_get_directory_contents(
    source: str,
    directory: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
) -> dict[str, str]:
    """Get contents of all files in a directory asynchronously.

    Args:
        source: Local path or GitHub URL to the repository
        directory: Directory path within the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dictionary mapping file paths to their contents
    """
    async with AsyncRepositoryAnalyzer(source, config) as repo:
        return await repo.get_directory_contents(directory, output_file)
