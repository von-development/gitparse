"""Function-based API for GitParse."""

from gitparse.core.functions.dependencies import async_get_dependencies, get_dependencies
from gitparse.core.functions.directory import (
    async_get_directory_contents,
    async_get_directory_tree,
    get_directory_contents,
    get_directory_tree,
)
from gitparse.core.functions.file_content import (
    async_get_all_contents,
    async_get_file_content,
    get_all_contents,
    get_file_content,
)
from gitparse.core.functions.file_tree import async_get_file_tree, get_file_tree
from gitparse.core.functions.language_stats import (
    async_get_language_stats,
    get_language_stats,
)
from gitparse.core.functions.readme import async_get_readme_content, get_readme_content
from gitparse.core.functions.repository_info import (
    async_get_repository_info,
    get_repository_info,
)
from gitparse.core.functions.statistics import async_get_statistics, get_statistics

__all__ = [
    # Sync functions
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
    # Async functions
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
]
