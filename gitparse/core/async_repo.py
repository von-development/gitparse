"""Async implementation of GitRepo functionality."""

import asyncio
from pathlib import Path
from typing import Optional, Union, Literal, Dict, List
import aiofiles
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from gitparse.core.repo import GitRepo
from gitparse.schema.config import ExtractionConfig


class AsyncGitRepo:
    """Async wrapper around GitRepo for non-blocking operations.
    
    This class provides asynchronous versions of all GitRepo methods,
    allowing for non-blocking I/O operations in async contexts.
    
    Args:
        source (str): Local path or GitHub URL to the repository
        config (Optional[ExtractionConfig]): Configuration for extraction behavior
    """
    
    def __init__(self, source: str, config: Optional[ExtractionConfig] = None):
        self._repo = GitRepo(source, config)
        self._executor = ThreadPoolExecutor()
    
    async def _run_in_executor(self, func, *args, **kwargs):
        """Run a sync function in thread pool executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor, 
            partial(func, *args, **kwargs)
        )
    
    async def get_repository_info(self) -> Dict[str, str]:
        """Async version of get_repository_info."""
        return await self._run_in_executor(self._repo.get_repository_info)
    
    async def get_file_tree(
        self, 
        style: Literal["flattened", "markdown", "structured"] = "flattened"
    ) -> Union[List[str], Dict]:
        """Async version of get_file_tree."""
        return await self._run_in_executor(self._repo.get_file_tree, style)
    
    async def get_readme(self) -> Optional[str]:
        """Async version of get_readme."""
        return await self._run_in_executor(self._repo.get_readme)
    
    async def get_dependencies(self) -> Dict[str, Dict]:
        """Async version of get_dependencies."""
        return await self._run_in_executor(self._repo.get_dependencies)
    
    async def get_language_stats(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """Async version of get_language_stats."""
        return await self._run_in_executor(self._repo.get_language_stats)
    
    async def get_statistics(self) -> Dict[str, Union[int, float, Dict]]:
        """Async version of get_statistics."""
        return await self._run_in_executor(self._repo.get_statistics)
    
    async def get_file_content(self, file_path: Union[str, Path]) -> Optional[str]:
        """Async version of get_file_content."""
        return await self._run_in_executor(self._repo.get_file_content, file_path)
    
    async def get_all_contents(self, max_file_size: int = 1_000_000) -> Dict[str, str]:
        """Async version of get_all_contents.
        
        This implementation is optimized for async by reading files concurrently.
        """
        if not self._repo._repo_path:
            raise RuntimeError("Repository path not initialized")
            
        # Get all files first
        files = await self._run_in_executor(
            self._repo._walk_directory, 
            self._repo._repo_path
        )
        
        # Filter large files and get relative paths
        file_paths = []
        for file_path in files:
            if file_path.stat().st_size <= max_file_size:
                rel_path = str(file_path.relative_to(self._repo._repo_path))
                file_paths.append(rel_path)
        
        # Read all files concurrently
        contents = {}
        async with asyncio.TaskGroup() as tg:
            tasks = {
                file_path: tg.create_task(self.get_file_content(file_path))
                for file_path in file_paths
            }
        
        # Collect results
        for file_path, task in tasks.items():
            content = task.result()
            if content is not None:
                contents[file_path] = content
        
        return contents
    
    async def get_directory_tree(
        self,
        directory: str,
        style: Literal["flattened", "markdown", "structured"] = "flattened"
    ) -> Union[List[str], Dict]:
        """Async version of get_directory_tree."""
        return await self._run_in_executor(
            self._repo.get_directory_tree,
            directory,
            style
        )
    
    async def get_directory_contents(self, directory: str) -> Dict[str, str]:
        """Async version of get_directory_contents."""
        return await self._run_in_executor(
            self._repo.get_directory_contents,
            directory
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self._executor.shutdown(wait=True)
        
    def __del__(self):
        """Cleanup executor on deletion."""
        self._executor.shutdown(wait=False) 