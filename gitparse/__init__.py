"""GitParse - A Modern Python Library for Git Repository Analysis."""

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
from gitparse.core.repo import GitRepo
from gitparse.core.async_repo import AsyncGitRepo
from gitparse.schema.config import ExtractionConfig

__version__ = "0.1.0"

__all__ = [
    # Synchronous function-based API
    "get_repository_info",
    "get_file_tree",
    "get_readme_content",
    "get_dependencies",
    "get_language_stats",
    "get_statistics",
    "get_file_content",
    "get_all_contents",
    "get_directory_tree",
    "get_directory_contents",
    # Asynchronous function-based API
    "async_get_repository_info",
    "async_get_file_tree",
    "async_get_readme_content",
    "async_get_dependencies",
    "async_get_language_stats",
    "async_get_statistics",
    "async_get_file_content",
    "async_get_all_contents",
    "async_get_directory_tree",
    "async_get_directory_contents",
    # Class-based APIs (for advanced usage)
    "GitRepo",
    "AsyncGitRepo",
    # Configuration
    "ExtractionConfig",
]
