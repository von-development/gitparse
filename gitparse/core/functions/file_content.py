"""File content-related functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from gitparse.core.async_repo_analyzer import AsyncRepositoryAnalyzer
from gitparse.core.repository_analyzer import RepositoryAnalyzer

if TYPE_CHECKING:
    from gitparse.schema.config import ExtractionConfig


def get_file_content(
    source: str,
    file_path: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
    encoding: str = "utf-8",
) -> Optional[str]:
    """Get content of a specific file from the repository.

    Args:
        source: Local path or GitHub URL to the repository
        file_path: Path to the file within the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.
        encoding: File encoding to use when reading

    Returns:
        File content as string or None if file is binary/unreadable
    """
    repo = RepositoryAnalyzer(source, config)
    return repo.get_file_content(file_path, output_file, encoding)


async def async_get_file_content(
    source: str,
    file_path: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
    encoding: str = "utf-8",
) -> Optional[str]:
    """Get content of a specific file from the repository asynchronously.

    Args:
        source: Local path or GitHub URL to the repository
        file_path: Path to the file within the repository
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.
        encoding: File encoding to use when reading

    Returns:
        File content as string or None if file is binary/unreadable
    """
    async with AsyncRepositoryAnalyzer(source, config) as repo:
        return await repo.get_file_content(file_path, output_file, encoding)


def get_all_contents(
    source: str,
    config: Optional[ExtractionConfig] = None,
    max_file_size: Optional[int] = None,
    exclude_patterns: Optional[list[str]] = None,
    output_file: Optional[str] = None,
) -> dict[str, str]:
    """Get contents of all text files in the repository.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        max_file_size: Maximum file size to read
        exclude_patterns: List of glob patterns to exclude
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dictionary mapping file paths to their contents
    """
    repo = RepositoryAnalyzer(source, config)
    return repo.get_all_contents(max_file_size, exclude_patterns, output_file)


async def async_get_all_contents(
    source: str,
    config: Optional[ExtractionConfig] = None,
    max_file_size: Optional[int] = None,
    exclude_patterns: Optional[list[str]] = None,
    output_file: Optional[str] = None,
) -> dict[str, str]:
    """Get contents of all text files in the repository asynchronously.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
        max_file_size: Maximum file size to read
        exclude_patterns: List of glob patterns to exclude
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        Dictionary mapping file paths to their contents
    """
    async with AsyncRepositoryAnalyzer(source, config) as repo:
        return await repo.get_all_contents(max_file_size, exclude_patterns, output_file)
