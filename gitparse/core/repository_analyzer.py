"""Repository analysis and parsing module."""

from __future__ import annotations

import contextlib
import fnmatch
import json
import logging
import os
import shutil
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, Union
from urllib.parse import urlparse

if TYPE_CHECKING:
    from collections.abc import Generator

import git
from git.exc import GitCommandError

try:
    import magic

    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

from gitparse.core.exceptions import (
    DependencyError,
    DirectoryNotFoundError,
    GitParseError,
    InvalidRepositoryError,
    ParseError,
    RepositoryNotFoundError,
)
from gitparse.parsers.deps import DependencyParser
from gitparse.schema.config import ExtractionConfig
from gitparse.utils.fs_utils import (
    get_file_type,
    is_binary_file,
    map_mime_to_language,
)
from gitparse.vars.exclude_patterns import DEFAULT_EXCLUDE_PATTERNS

# Set up logging
logger = logging.getLogger(__name__)

# Error messages
ERR_REPO_NOT_INIT = "Repository not initialized"
ERR_CLONE_FAILED = "Failed to clone repository"
ERR_PARSE_REQUIREMENTS = "Failed to parse requirements.txt"
ERR_PARSE_PYPROJECT = "Failed to parse pyproject.toml"
ERR_PARSE_POETRY_DEPS = "Failed to parse Poetry dependencies"
ERR_PARSE_POETRY_DEV = "Failed to parse Poetry dev dependencies"
ERR_PARSE_PACKAGE_JSON = "Failed to parse package.json"
ERR_PARSE_NPM_DEPS = "Failed to parse package.json dependencies"
ERR_PARSE_NPM_DEV = "Failed to parse package.json dev dependencies"


def _handle_readonly(
    func: Callable[[str], None],
    path: str,
    _excinfo: Any,  # Unused but required by rmtree
) -> None:
    """Error handler for shutil.rmtree to handle readonly files.

    Args:
        func: The function that failed
        path: The path that caused the error
        _excinfo: Exception info (unused)
    """
    # Make the file writable and try again
    Path(path).chmod(stat.S_IWRITE)
    func(path)


class RepositoryAnalyzer:
    """Main interface for analyzing and extracting data from Git repositories.

    This class provides comprehensive analysis and data extraction capabilities
    for both local and remote Git repositories. It handles repository metadata,
    file analysis, dependency parsing, and statistical analysis.

    Args:
        source (str): Local path or GitHub URL to the repository
        config (Optional[ExtractionConfig]): Configuration for extraction behavior

    Attributes:
        source (str): Original source path/URL
        config (ExtractionConfig): Extraction configuration
        _repo_path (Optional[Path]): Path to the repository on disk
        _is_remote (bool): Whether source is remote or local
        _temp_dir (Optional[Path]): Temporary directory if repo was cloned
        _git_repo (Optional[git.Repo]): Git repository object if local
    """

    def __init__(self, source: str, config: Optional[ExtractionConfig] = None) -> None:
        self.source = source
        self.config = config or ExtractionConfig()
        self._repo_path: Optional[Path] = None
        self._is_remote = False
        self._temp_dir: Optional[Path] = None
        self._git_repo: Optional[git.Repo] = None

        # Parse source and set up repo path
        self._setup_repo_path()

        # Clone if remote
        if self._is_remote:
            self._clone_repository()

    def _validate_path(self, path: Path, is_dir: bool = True) -> None:
        """Validate that a path exists and is of the correct type.

        Args:
            path: Path to validate
            is_dir: Whether the path should be a directory

        Raises:
            RepositoryNotFoundError: If path does not exist
            InvalidRepositoryError: If path is not of the correct type
        """
        if not path.exists():
            msg = f"Path does not exist: {path}"
            raise RepositoryNotFoundError(msg)
        if is_dir and not path.is_dir():
            msg = f"Path is not a directory: {path}"
            raise InvalidRepositoryError(msg)

    def _setup_repo_path(self) -> None:
        """Initialize repository path from source."""
        # Convert source to string if it's a Path object
        source_str = str(self.source) if isinstance(self.source, Path) else self.source

        # Check if source is URL or local path
        parsed = urlparse(source_str)
        self._is_remote = bool(parsed.scheme and parsed.netloc)

        if self._is_remote:
            # For remote repos, we'll need to clone later
            if self.config.temp_dir:
                self._temp_dir = Path(self.config.temp_dir)
            else:
                self._temp_dir = Path(tempfile.mkdtemp())
        else:
            # Local path
            try:
                repo_path = Path(source_str).resolve()
                self._validate_path(repo_path)
            except (RepositoryNotFoundError, InvalidRepositoryError):
                logger.exception("Failed to resolve repository path")
                raise
            else:
                self._repo_path = repo_path
                # Try to load as Git repo
                with contextlib.suppress(git.InvalidGitRepositoryError, git.NoSuchPathError):
                    self._git_repo = git.Repo(self._repo_path)

    def _clone_repository(self) -> None:
        """Clone remote repository to temporary directory."""
        if not self._is_remote or not self._temp_dir:
            return

        try:
            # Check if repo already exists
            if (self._temp_dir / ".git").exists():
                self._git_repo = git.Repo(self._temp_dir)
                # Pull latest changes
                origin = self._git_repo.remotes.origin
                origin.fetch()
                origin.pull()
            else:
                self._git_repo = git.Repo.clone_from(self.source, self._temp_dir)
        except GitCommandError as err:
            msg = f"Failed to clone repository: {err}"
            raise GitParseError(msg) from err
        else:
            self._repo_path = self._temp_dir

    def _save_output(
        self,
        data: Any,
        output_file: Optional[Union[str, Path]] = None,
        prefix: str = "",
    ) -> None:
        """Save data to a file if output_file is specified."""
        if not output_file:
            return

        # Handle auto-generated filenames
        if output_file == "auto":
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            repo_name = self._repo_path.name if self._repo_path else "unknown"
            output_file = f"{prefix}_{repo_name}_{timestamp}.json"

        # Ensure parent directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save data
        with output_path.open("w", encoding="utf-8") as f:
            if isinstance(data, str):
                f.write(data)
            else:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def get_repository_info(self, output_file: Optional[Union[str, Path]] = None) -> dict[str, str]:
        """Get basic information about the Git repository.

        Args:
            output_file: Optional path to save results. Use "auto" for auto-generated filename.

        Returns:
            Dict with repository information (name, default branch, etc.)
        """
        if not self._git_repo:
            return {"name": self._repo_path.name if self._repo_path else "unknown"}

        try:
            info = {
                "name": self._git_repo.working_dir.split(os.path.sep)[-1],
                "is_bare": self._git_repo.bare,
            }

            # Try to get branch and commit info
            try:
                info["default_branch"] = self._git_repo.active_branch.name
            except (TypeError, ValueError):
                info["default_branch"] = "unknown"

            try:
                info["head_commit"] = str(self._git_repo.head.commit)
            except (ValueError, TypeError):
                info["head_commit"] = "no commits yet"

            # Get remotes if any
            try:
                info["remotes"] = [r.name for r in self._git_repo.remotes]
            except (AttributeError, TypeError):
                info["remotes"] = []
        except (git.InvalidGitRepositoryError, git.NoSuchPathError, AttributeError):
            return {"name": self._repo_path.name if self._repo_path else "unknown"}
        else:
            self._save_output(info, output_file, "repo_info")
            return info

    def get_repo_info(self, output_file: Optional[Union[str, Path]] = None) -> dict[str, str]:
        """Alias for get_repository_info."""
        return self.get_repository_info(output_file)

    def _should_include_file(self, path: Path) -> bool:
        """Check if a file should be included based on config patterns."""
        rel_path = str(path.relative_to(self._repo_path))

        # Check exclude patterns first
        for pattern in self.config.exclude_patterns or DEFAULT_EXCLUDE_PATTERNS:
            if fnmatch.fnmatch(rel_path, pattern):
                return False

        # If include patterns exist, file must match at least one
        if self.config.include_patterns:
            return any(fnmatch.fnmatch(rel_path, p) for p in self.config.include_patterns)

        return True

    def _walk_directory(self, start_path: Path) -> list[Path]:
        """Walk directory and return filtered list of files."""
        files = []

        for root, _, filenames in os.walk(start_path):
            root_path = Path(root)
            for filename in filenames:
                file_path = root_path / filename

                # Skip files larger than max_file_size
                if file_path.stat().st_size > self.config.max_file_size:
                    continue

                # Apply include/exclude patterns
                if self._should_include_file(file_path):
                    files.append(file_path)

        return sorted(files)

    def _format_tree_flattened(self, files: list[Path]) -> list[str]:
        """Format files as a flat list of relative paths."""
        return [str(f.relative_to(self._repo_path)) for f in files]

    def _format_tree_markdown(self, files: list[Path]) -> list[str]:
        """Format file tree in markdown style."""
        tree = []
        for file in sorted(files):
            rel_path = file.relative_to(self._repo_path)
            indent = "  " * (len(rel_path.parts) - 1)
            tree.append(f"{indent}- {rel_path.name}")
        return tree

    def _format_tree_structured(self, files: list[Path]) -> dict:
        """Format file tree as nested dictionary."""
        tree = {}
        for file in sorted(files):
            current = tree
            rel_path = file.relative_to(self._repo_path)
            for part in rel_path.parts[:-1]:
                current = current.setdefault(part, {})
            current[rel_path.name] = None
        return tree

    def get_file_tree(
        self,
        style: Literal["flattened", "markdown", "structured", "dict"] = "flattened",
        output_file: Optional[Union[str, Path]] = None,
    ) -> Union[list[str], dict]:
        """Get repository file tree in specified format.

        Args:
            style: Output style ("flattened", "markdown", "structured", or "dict")
            output_file: Optional path to save results. Use "auto" for auto-generated filename.

        Returns:
            List of files or structured dictionary
        """
        if not self._repo_path:
            msg = "Repository path not initialized"
            raise RuntimeError(msg)

        # Get filtered list of files
        files = self._walk_directory(self._repo_path)

        # Format according to requested style
        if style == "flattened":
            result = self._format_tree_flattened(files)
        elif style == "markdown":
            result = self._format_tree_markdown(files)
        elif style in ("structured", "dict"):  # Handle dict as alias for structured
            result = self._format_tree_structured(files)
        else:
            msg = f"Unsupported tree style: {style}"
            raise ValueError(msg)

        self._save_output(result, output_file, "file_tree")
        return result

    def get_readme(self) -> Optional[str]:
        """Returns the content of the README file if present.

        Returns:
            Optional[str]: Content of README.md or None if not found
        """
        if not self._repo_path:
            msg = "Repository path not initialized"
            raise RuntimeError(msg)

        # Common README filenames to check
        readme_names = ["README.md", "Readme.md", "readme.md", "README", "README.rst"]

        # Check each possible README file
        for name in readme_names:
            readme_path = self._repo_path / name
            if readme_path.exists() and readme_path.is_file():
                try:
                    return readme_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue  # Try next file if this one isn't text

        return None

    def get_readme_content(self, output_file: Optional[Union[str, Path]] = None) -> Optional[str]:
        """Get the content of the repository's README file.

        Args:
            output_file: Optional path to save results. Use "auto" for auto-generated filename.

        Returns:
            README content as string or None if not found
        """
        if not self._repo_path:
            return None

        # Look for README files with common extensions
        readme_patterns = ["README.md", "README.rst", "README.txt", "README"]
        for pattern in readme_patterns:
            for file in self._repo_path.glob(pattern):
                if file.is_file():
                    content = self.get_file_content(str(file.relative_to(self._repo_path)))
                    if content:
                        self._save_output(content, output_file, "readme")
                        return content
        return None

    @contextlib.contextmanager
    def _temp_dir_context(self) -> Generator[None, None, None]:
        """Create and manage a temporary directory context.

        Yields:
            None
        """
        try:
            temp_dir = Path(tempfile.mkdtemp())
            yield
        finally:
            if temp_dir.exists():
                shutil.rmtree(str(temp_dir), onerror=_handle_readonly)

    @staticmethod
    def cleanup_temp_directories() -> None:
        """Clean up all temporary directories in the system temp directory."""
        temp_root = Path(tempfile.gettempdir())
        for path in temp_root.iterdir():
            if path.is_dir():
                with contextlib.suppress(Exception):
                    logger.debug("Cleaning up temporary directory: %s", path)
                    shutil.rmtree(str(path), onerror=_handle_readonly)

    def _cleanup_temp_dir(self) -> None:
        """Clean up temporary directory if it exists."""
        if self._temp_dir and self._temp_dir.exists():
            with contextlib.suppress(Exception):
                logger.debug("Cleaning up temporary directory: %s", self._temp_dir)
                shutil.rmtree(str(self._temp_dir), onerror=_handle_readonly)
            self._temp_dir = None

    def __del__(self) -> None:
        """Clean up resources when object is deleted."""
        with contextlib.suppress(Exception):
            self._cleanup_temp_dir()

    def _get_file_type(self, path: Path) -> tuple[str, bool]:
        """Get MIME type and binary status for a file using python-magic."""
        if not HAS_MAGIC or not magic:
            return get_file_type(path)

        try:
            mime_type = magic.from_file(str(path), mime=True)
            is_binary = not mime_type.startswith(("text/", "application/json"))
        except (OSError, PermissionError):
            logger.warning("Failed to get MIME type for %s", path)
            return get_file_type(path)
        else:
            return mime_type, is_binary

    def _map_mime_to_language(self, mime_type: str) -> str:
        """Map MIME type to programming language name."""
        return map_mime_to_language(mime_type)

    def _is_binary_file(self, path: Path) -> bool:
        """Check if a file is binary."""
        return is_binary_file(path)

    def get_language_stats(
        self,
        output_file: Optional[str] = None,
    ) -> dict[str, dict[str, Union[int, float]]]:
        """Get language statistics for the repository."""
        if not self._repo_path:
            msg = "Repository not initialized"
            raise GitParseError(msg)

        stats: dict[str, dict[str, Union[int, float]]] = {}
        total_bytes = 0
        total_files = 0

        # Pre-process files to minimize try-except overhead
        valid_files = []
        for path in self._walk_directory(self._repo_path):
            mime_type, is_binary = self._get_file_type(path)
            if not is_binary:
                valid_files.append((path, mime_type))

        # Process valid files in a single try-except block
        try:
            for path, mime_type in valid_files:
                language = self._map_mime_to_language(mime_type)
                size = path.stat().st_size

                if language not in stats:
                    stats[language] = {"files": 0, "bytes": 0}

                stats[language]["files"] += 1
                stats[language]["bytes"] += size
                total_bytes += size
                total_files += 1
        except OSError:
            logger.exception("Failed to process files for language statistics")
            return stats
        else:
            # Calculate percentages
            if total_bytes > 0:
                for lang_stats in stats.values():
                    bytes_count = lang_stats["bytes"]
                    lang_stats["percentage"] = round((bytes_count / total_bytes) * 100, 2)

            self._save_output(stats, output_file, "language_stats")
            return stats

        return stats

    def get_statistics(
        self,
        output_file: Optional[Union[str, Path]] = None,
    ) -> dict[str, Any]:
        """Get overall repository statistics."""
        if not self._repo_path:
            msg = "Repository path not initialized"
            raise RuntimeError(msg)

        stats = {
            "total_files": 0,
            "total_size": 0,
            "binary_files": 0,
            "text_files": 0,
            "avg_file_size": 0,
            "binary_ratio": 0.0,
            "language_breakdown": self.get_language_stats(),
        }

        # Pre-process files to minimize try-except overhead
        files = self._walk_directory(self._repo_path)
        file_info = []

        # Collect all file info in a single try block
        try:
            for file_path in files:
                size = file_path.stat().st_size
                is_binary = self._is_binary_file(file_path)
                file_info.append((file_path, size, is_binary))
        except (OSError, PermissionError):
            logger.exception("Failed to process files")
            return stats

        # Process collected stats without try-except
        for _, size, is_binary in file_info:
            stats["total_files"] += 1
            stats["total_size"] += size
            if is_binary:
                stats["binary_files"] += 1
            else:
                stats["text_files"] += 1

        # Calculate averages and ratios
        if stats["total_files"] > 0:
            stats["avg_file_size"] = stats["total_size"] / stats["total_files"]
            stats["binary_ratio"] = (stats["binary_files"] / stats["total_files"]) * 100

        self._save_output(stats, output_file, "statistics")
        return stats

    def get_repo_stats(
        self,
        output_file: Optional[Union[str, Path]] = None,
    ) -> dict[str, Any]:
        """Get repository statistics including file counts, sizes, and types."""
        if not self._repo_path:
            return {}

        # Initialize stats
        stats = {
            "total_files": 0,
            "total_size": 0,
            "binary_count": 0,
            "file_types": {},
            "largest_files": [],
        }

        # Pre-process files to minimize try-except overhead
        files = self._walk_directory(self._repo_path)
        file_info = []

        # Collect all file info in a single try block
        try:
            for file_path in files:
                size = file_path.stat().st_size
                ext = file_path.suffix.lower()
                is_binary = self._is_binary_file(file_path)
                rel_path = str(file_path.relative_to(self._repo_path))
                file_info.append((size, ext, is_binary, rel_path))
        except Exception:
            logger.exception("Failed to process files")
            return stats
        else:
            # Process collected info
            for size, ext, is_binary, rel_path in file_info:
                stats["total_size"] += size
                stats["total_files"] += 1

                if ext:
                    stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                if is_binary:
                    stats["binary_count"] += 1

                stats["largest_files"].append({"path": rel_path, "size": size})

            # Post-process stats
            if stats["total_files"] > 0:
                stats["average_file_size"] = stats["total_size"] / stats["total_files"]
                stats["binary_ratio"] = stats["binary_count"] / stats["total_files"]
            else:
                stats["average_file_size"] = 0
                stats["binary_ratio"] = 0

            # Sort and limit largest files
            stats["largest_files"].sort(key=lambda x: x["size"], reverse=True)
            stats["largest_files"] = stats["largest_files"][:10]  # Keep top 10

            self._save_output(stats, output_file, "repo_stats")
            return stats

    def get_file_content(
        self,
        file_path: str,
        output_file: Optional[str] = None,
        encoding: str = "utf-8",
    ) -> Optional[str]:
        """Get the content of a specific file.

        Args:
            file_path: Path to the file relative to repository root
            output_file: Optional path to save output to
            encoding: File encoding to use

        Returns:
            File content as string or None if file cannot be read
        """
        if not self._repo_path:
            raise GitParseError(ERR_REPO_NOT_INIT)

        target = self._repo_path / file_path
        if not target.exists():
            logger.warning("File does not exist: %s", target)
            return None

        if target.is_dir():
            logger.warning("Path is a directory: %s", target)
            return None

        try:
            content = target.read_text(encoding=encoding)
            if output_file:
                Path(output_file).write_text(content, encoding=encoding)
        except (OSError, UnicodeError):
            logger.warning("Failed to read file %s", target)
            return None
        else:
            return content

    def get_all_contents(
        self,
        max_file_size: Optional[int] = None,
        exclude_patterns: Optional[list[str]] = None,
        output_file: Optional[str] = None,
    ) -> dict[str, str]:
        """Get contents of all text files in the repository.

        Args:
            max_file_size: Maximum file size in bytes to read
            exclude_patterns: List of glob patterns to exclude
            output_file: Optional path to save output to

        Returns:
            Dictionary mapping file paths to their contents
        """
        if not self._repo_path:
            raise GitParseError(ERR_REPO_NOT_INIT)

        exclude_patterns = exclude_patterns or []
        contents: dict[str, str] = {}

        for path in self._walk_directory(self._repo_path):
            try:
                # Skip excluded files
                if any(fnmatch.fnmatch(str(path), pattern) for pattern in exclude_patterns):
                    continue

                # Skip large files
                if max_file_size and path.stat().st_size > max_file_size:
                    logger.warning("Skipping large file: %s", path)
                    continue

                # Skip binary files
                if self._is_binary_file(path):
                    continue

                # Read file content
                rel_path = str(path.relative_to(self._repo_path))
                contents[rel_path] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as e:
                logger.warning("Failed to read file %s: %s", path, e)
                continue

        if output_file:
            Path(output_file).write_text(json.dumps(contents, indent=2), encoding="utf-8")

        return contents

    def get_directory_tree(
        self,
        directory: str,
        style: Literal["flattened", "markdown", "structured"] = "flattened",
        output_file: Optional[str] = None,
    ) -> Union[list[str], dict]:
        """Get file tree for a specific directory."""
        if not self._repo_path:
            msg = "Repository not initialized"
            raise GitParseError(msg)

        dir_path = self._repo_path / directory
        if not dir_path.is_dir():
            msg = f"Directory not found: {directory}"
            raise DirectoryNotFoundError(msg)

        files = self._walk_directory(dir_path)

        if style == "flattened":
            result = self._format_tree_flattened(files)
        elif style == "markdown":
            result = self._format_tree_markdown(files)
        else:
            result = self._format_tree_structured(files)

        self._save_output(result, output_file, f"dir_tree_{style}")
        return result

    def get_directory_contents(
        self,
        directory: str,
        output_file: Optional[str] = None,
    ) -> dict[str, str]:
        """Get contents of all files in a directory."""
        if not self._repo_path:
            msg = "Repository not initialized"
            raise GitParseError(msg)

        dir_path = self._repo_path / directory
        if not dir_path.is_dir():
            msg = f"Directory not found: {directory}"
            raise DirectoryNotFoundError(msg)

        contents = {}
        files = list(self._walk_directory(dir_path))  # Convert to list to avoid multiple iterations

        # Process all files in a single try block
        try:
            for file_path in files:
                content = file_path.read_text(encoding="utf-8")
                rel_path = str(file_path.relative_to(dir_path))
                contents[rel_path] = content
        except UnicodeDecodeError as e:
            logger.warning("Failed to decode file: %s", e)
        except OSError:
            logger.exception("Failed to process files")

        self._save_output(contents, output_file, "dir_contents")
        return contents

    def get_dependencies(
        self,
        output_file: Optional[Union[str, Path]] = None,
    ) -> dict[str, Any]:
        """Get all dependencies from the repository."""
        if not self._repo_path:
            msg = "Repository not initialized"
            raise GitParseError(msg)

        with self._temp_dir_context():
            dependencies = {}

            # Find all dependency files
            for path in self._walk_directory(self._repo_path):
                # Skip if file doesn't match any parser patterns
                if not any(
                    fnmatch.fnmatch(path.name, pattern)
                    for parser in DependencyParser.__subclasses__()
                    for pattern in parser.file_patterns
                ):
                    continue

                # Try each parser
                for parser_cls in DependencyParser.__subclasses__():
                    parser = parser_cls(self._repo_path)
                    if parser.can_parse(path):
                        try:
                            deps = parser.parse(path)
                            if deps:
                                dependencies[str(path.relative_to(self._repo_path))] = deps
                        except (ParseError, DependencyError, OSError) as e:
                            logger.warning("Failed to parse dependencies: %s", e)

            self._save_output(dependencies, output_file, "dependencies")
            return dependencies
