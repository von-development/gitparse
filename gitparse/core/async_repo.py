"""Async implementation of GitRepo functionality."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, TypeVar, Union

from gitparse.core.exceptions import GitFileNotFoundError, GitParseError
from gitparse.core.repo import GitRepo

if TYPE_CHECKING:
    import types
    from typing import Self

    from gitparse.schema.config import ExtractionConfig

# Type variable for generic return types
T = TypeVar("T")


class AsyncGitRepo:
    """Async wrapper around GitRepo for non-blocking operations.

    This class provides asynchronous versions of all GitRepo methods,
    allowing for non-blocking I/O operations in async contexts.

    Args:
        source: Local path or GitHub URL to the repository
        config: Configuration for extraction behavior
    """

    def __init__(self, source: str, config: Optional[ExtractionConfig] = None) -> None:
        self._repo = GitRepo(source, config)
        self._executor = ThreadPoolExecutor()

    async def _run_in_executor(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Run a sync function in thread pool executor.

        Args:
            func: The function to run
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the function call
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, partial(func, *args, **kwargs))

    async def get_repository_info(self, output_file: Optional[str] = None) -> dict[str, str]:
        """Async version of get_repository_info."""
        return await self._run_in_executor(self._repo.get_repository_info, output_file)

    async def get_repo_info(self, output_file: Optional[str] = None) -> dict[str, str]:
        """Alias for get_repository_info."""
        return await self.get_repository_info(output_file)

    async def get_file_tree(
        self,
        style: Literal["flattened", "markdown", "structured", "dict"] = "flattened",
        output_file: Optional[str] = None,
    ) -> Union[list[str], dict[str, Any]]:
        """Async version of get_file_tree."""
        return await self._run_in_executor(self._repo.get_file_tree, style, output_file)

    async def get_readme(self) -> Optional[str]:
        """Async version of get_readme."""
        return await self._run_in_executor(self._repo.get_readme)

    async def get_readme_content(self, output_file: Optional[str] = None) -> Optional[str]:
        """Async version of get_readme_content."""
        return await self._run_in_executor(self._repo.get_readme_content, output_file)

    async def get_dependencies(
        self,
        output_file: Optional[str] = None,
    ) -> dict[str, Union[list[str], dict[str, str]]]:
        """Async version of get_dependencies."""
        return await self._run_in_executor(
            self._repo.get_dependencies,
            output_file,
        )

    async def get_language_stats(
        self,
        output_file: Optional[str] = None,
    ) -> dict[str, dict[str, Union[int, float]]]:
        """Async version of get_language_stats."""
        return await self._run_in_executor(
            self._repo.get_language_stats,
            output_file,
        )

    async def get_statistics(
        self,
        output_file: Optional[str] = None,
    ) -> dict[str, Any]:
        """Async version of get_statistics."""
        return await self._run_in_executor(
            self._repo.get_statistics,
            output_file,
        )

    async def get_repo_stats(
        self,
        output_file: Optional[str] = None,
    ) -> dict[str, Any]:
        """Async version of get_repo_stats."""
        return await self._run_in_executor(
            self._repo.get_repo_stats,
            output_file,
        )

    async def get_file_content(
        self,
        file_path: str,
        output_file: Optional[str] = None,
        encoding: str = "utf-8",
    ) -> Optional[str]:
        """Async version of get_file_content."""
        try:
            return await self._run_in_executor(
                self._repo.get_file_content,
                file_path,
                output_file,
                encoding,
            )
        except GitFileNotFoundError:
            return None

    async def get_all_contents(
        self,
        max_file_size: Optional[int] = None,
        exclude_patterns: Optional[list[str]] = None,
        output_file: Optional[str] = None,
    ) -> dict[str, str]:
        """Async version of get_all_contents.

        This implementation is optimized for async by reading files concurrently.
        """
        error_msg = "Failed to get all contents"
        try:
            return await self._run_in_executor(
                self._repo.get_all_contents,
                max_file_size,
                exclude_patterns,
                output_file,
            )
        except GitParseError as e:
            raise GitParseError(error_msg) from e

    async def get_directory_tree(
        self,
        directory: str,
        style: Literal["flattened", "markdown", "structured"] = "flattened",
        output_file: Optional[str] = None,
    ) -> Union[list[str], dict[str, Any]]:
        """Async version of get_directory_tree."""
        return await self._run_in_executor(
            self._repo.get_directory_tree,
            directory,
            style,
            output_file,
        )

    async def get_directory_contents(
        self,
        directory: str,
        output_file: Optional[str] = None,
    ) -> dict[str, str]:
        """Async version of get_directory_contents."""
        return await self._run_in_executor(
            self._repo.get_directory_contents,
            directory,
            output_file,
        )

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[types.TracebackType],
    ) -> None:
        """Async context manager exit."""
        self._executor.shutdown(wait=True)

    def __del__(self) -> None:
        """Cleanup executor on deletion."""
        self._executor.shutdown(wait=False)
