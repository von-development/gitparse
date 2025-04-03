"""GitParse - A Modern Python Library for Git Repository Analysis."""

from gitparse.core.async_repo_analyzer import AsyncRepositoryAnalyzer

# Re-export core functions
from gitparse.core.functions import (
    async_get_all_contents,
    async_get_dependencies,
    async_get_directory_contents,
    async_get_directory_tree,
    async_get_file_content,
    async_get_file_tree,
    async_get_language_stats,
    async_get_readme_content,
    async_get_repository_info,
    async_get_statistics,
    get_all_contents,
    get_dependencies,
    get_directory_contents,
    get_directory_tree,
    get_file_content,
    get_file_tree,
    get_language_stats,
    get_readme_content,
    get_repository_info,
    get_statistics,
)
from gitparse.core.repository_analyzer import RepositoryAnalyzer
from gitparse.schema.config import ExtractionConfig

__version__ = "0.1.0"

__all__ = [
    "RepositoryAnalyzer",
    "AsyncRepositoryAnalyzer",
    "ExtractionConfig",
    "async_get_all_contents",
    "async_get_dependencies",
    "async_get_directory_contents",
    "async_get_directory_tree",
    "async_get_file_content",
    "async_get_file_tree",
    "async_get_language_stats",
    "async_get_readme_content",
    "async_get_repository_info",
    "async_get_statistics",
    "get_all_contents",
    "get_dependencies",
    "get_directory_contents",
    "get_directory_tree",
    "get_file_content",
    "get_file_tree",
    "get_language_stats",
    "get_readme_content",
    "get_repository_info",
    "get_statistics",
]
