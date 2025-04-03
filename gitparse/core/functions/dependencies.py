"""Dependency-related functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from gitparse.core.async_repo_analyzer import AsyncRepositoryAnalyzer
from gitparse.core.repository_analyzer import RepositoryAnalyzer

if TYPE_CHECKING:
    from gitparse.schema.config import ExtractionConfig


async def async_get_dependencies(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
) -> dict[str, Union[list[str], dict[str, str]]]:
    """Get repository dependencies asynchronously."""
    async with AsyncRepositoryAnalyzer(source, config) as repo:
        return await repo.get_dependencies(output_file)


def get_dependencies(
    source: str,
    config: Optional[ExtractionConfig] = None,
    output_file: Optional[str] = None,
) -> dict[str, Union[list[str], dict[str, str]]]:
    """Get repository dependencies."""
    repo = RepositoryAnalyzer(source, config)
    return repo.get_dependencies(output_file)
