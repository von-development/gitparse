"""File tree functions."""

from __future__ import annotations

from typing import Any, Literal, Optional, Union
from pathlib import Path

from gitparse.core.repo import GitRepo
from gitparse.core.async_repo import AsyncGitRepo
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
    repo = GitRepo(source, config)
    return repo.get_file_tree(style, output_file)


async def async_get_file_tree(
    source: str,
    style: Literal["flattened", "markdown", "structured", "dict"] = "flattened",
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[Union[str, Path]] = None,
) -> Union[list[str], dict[str, Any]]:
    """Get repository file tree asynchronously.

    Args:
        source: Local path or GitHub URL to the repository
        style: Output style ("flattened", "markdown", "structured", or "dict")
        config: Configuration for extraction behavior
        output_file: Optional path to save results. Use "auto" for auto-generated filename.

    Returns:
        List of files or structured dictionary
    """
    async with AsyncGitRepo(source, config) as repo:
        return await repo.get_file_tree(style, output_file) 