"""Core repository handling module."""
from __future__ import annotations

import fnmatch
import json
import mimetypes
import os
import shutil
import stat
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
from urllib.parse import urlparse

import git
from git.exc import GitCommandError
from packaging.requirements import InvalidRequirement, Requirement

try:
    import magic

    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

from datetime import datetime

# Handle TOML parsing for different Python versions
import tomllib as toml_parser

from gitparse.schema.config import ExtractionConfig, DependencyConfig, DependencyGroup
from gitparse.vars.exclude_patterns import DEFAULT_EXCLUDE_PATTERNS
from gitparse.vars.file_types import COMMON_EXTENSIONS, MIME_TO_LANGUAGE


class GitError(Exception):
    """Custom exception class for Git-related errors."""

    pass


def _remove_readonly(func, path, excinfo):
    """Error handler for shutil.rmtree to handle readonly files."""
    # Make the file writable and try again
    os.chmod(path, stat.S_IWRITE)
    func(path)


class GitRepo:
    """Main interface for parsing and extracting data from a Git repository.

    This class provides methods to analyze and extract various types of information
    from either a local Git repository or a remote GitHub repository URL.

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
            self._repo_path = Path(source_str).resolve()
            if not self._repo_path.exists():
                raise ValueError(f"Repository path does not exist: {self._repo_path}")
            if not self._repo_path.is_dir():
                raise ValueError(f"Repository path is not a directory: {self._repo_path}")

            # Try to load as Git repo
            try:
                self._git_repo = git.Repo(self._repo_path)
            except (git.InvalidGitRepositoryError, git.NoSuchPathError):
                # Not a Git repo, but that's okay for local directories
                pass

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

            self._repo_path = self._temp_dir
        except GitCommandError as err:
            raise GitError(f"Failed to clone repository: {err}") from err

    def _save_output(
        self, data: Any, output_file: Optional[Union[str, Path]] = None, prefix: str = ""
    ) -> None:
        """Save data to a file if output_file is specified."""
        if not output_file:
            return

        # Handle auto-generated filenames
        if output_file == "auto":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

    def get_repository_info(self, output_file: Optional[Union[str, Path]] = None) -> Dict[str, str]:
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

            self._save_output(info, output_file, "repo_info")
            return info
        except (git.InvalidGitRepositoryError, git.NoSuchPathError, AttributeError):
            return {"name": self._repo_path.name if self._repo_path else "unknown"}

    def get_repo_info(self, output_file: Optional[Union[str, Path]] = None) -> Dict[str, str]:
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

    def _walk_directory(self, start_path: Path) -> List[Path]:
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

    def _format_tree_flattened(self, files: List[Path]) -> List[str]:
        """Format files as a flat list of relative paths."""
        return [str(f.relative_to(self._repo_path)) for f in files]

    def _format_tree_markdown(self, files: List[Path]) -> List[str]:
        """Format file tree in markdown style."""
        tree = []
        for file in sorted(files):
            rel_path = file.relative_to(self._repo_path)
            indent = "  " * (len(rel_path.parts) - 1)
            tree.append(f"{indent}- {rel_path.name}")
        return tree

    def _format_tree_structured(self, files: List[Path]) -> Dict:
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
    ) -> Union[List[str], Dict]:
        """Get repository file tree in specified format.

        Args:
            style: Output style ("flattened", "markdown", "structured", or "dict")
            output_file: Optional path to save results. Use "auto" for auto-generated filename.

        Returns:
            List of files or structured dictionary
        """
        if not self._repo_path:
            raise RuntimeError("Repository path not initialized")

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
            raise ValueError(f"Unsupported tree style: {style}")

        self._save_output(result, output_file, "file_tree")
        return result

    def get_readme(self) -> Optional[str]:
        """Returns the content of the README file if present.

        Returns:
            Optional[str]: Content of README.md or None if not found
        """
        if not self._repo_path:
            raise RuntimeError("Repository path not initialized")

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

    def _parse_requirements_txt(self, path: Path) -> List[Dict[str, str]]:
        """Parse a requirements.txt file."""
        if not path.exists():
            return []

        requirements = []
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            try:
                req = Requirement(line)
                requirements.append(
                    {
                        "name": req.name,
                        "specifier": str(req.specifier) if req.specifier else "",
                        "extras": sorted(req.extras) if req.extras else [],
                        "url": req.url if hasattr(req, "url") else None,
                    }
                )
            except InvalidRequirement:
                # Skip invalid requirements
                continue

        return requirements

    def _parse_poetry_toml(self, path: Path) -> Dict[str, Dict[str, str]]:
        """Parse a pyproject.toml file with Poetry dependencies."""
        if not path.exists():
            return {}

        try:
            data = toml_parser.loads(path.read_text())
            deps: Dict[str, Dict[str, str]] = {"dependencies": {}, "dev-dependencies": {}}

            # Main dependencies
            if "tool" in data and "poetry" in data["tool"]:
                poetry = data["tool"]["poetry"]
                if "dependencies" in poetry:
                    for name, spec in poetry["dependencies"].items():
                        if name == "python":
                            continue
                        if isinstance(spec, str):
                            deps["dependencies"][name] = spec
                        elif isinstance(spec, dict):
                            deps["dependencies"][name] = spec.get("version", "")

                # Dev dependencies
                if "group" in poetry and "dev" in poetry["group"]:
                    dev = poetry["group"]["dev"]
                    if "dependencies" in dev:
                        for name, spec in dev["dependencies"].items():
                            if isinstance(spec, str):
                                deps["dev-dependencies"][name] = spec
                            elif isinstance(spec, dict):
                                deps["dev-dependencies"][name] = spec.get("version", "")

            return deps
        except Exception:
            return {}

    def _parse_package_json(self, path: Path) -> Dict[str, List[Dict[str, str]]]:
        """Parse a package.json file."""
        if not path.exists():
            return {}

        try:
            data = json.loads(path.read_text())
            deps: Dict[str, List[Dict[str, str]]] = {"dependencies": [], "devDependencies": []}

            # Regular dependencies
            if "dependencies" in data:
                for name, version in data["dependencies"].items():
                    deps["dependencies"].append({"name": name, "version": version})

            # Dev dependencies
            if "devDependencies" in data:
                for name, version in data["devDependencies"].items():
                    deps["devDependencies"].append({"name": name, "version": version})

            return deps
        except Exception:
            return {}

    def get_dependencies(
        self, output_file: Optional[str] = None, config: Optional[ExtractionConfig] = None
    ) -> Dict[str, Union[List[str], Dict[str, str]]]:
        """Get repository dependencies from package files."""
        if not self._repo_path:
            raise GitError("Repository not initialized")

        dependencies = {
            "requirements.txt": [],
            "pyproject.toml": {"dependencies": [], "dev-dependencies": []},
            "package.json": {"dependencies": [], "devDependencies": []},
        }

        # Process each package file if it exists
        req_txt = self._repo_path / "requirements.txt"
        if req_txt.exists():
            dependencies["requirements.txt"] = self._parse_requirements_txt(req_txt)

        pyproject = self._repo_path / "pyproject.toml"
        if pyproject.exists():
            dependencies["pyproject.toml"] = self._parse_poetry_toml(pyproject)

        package_json = self._repo_path / "package.json"
        if package_json.exists():
            dependencies["package.json"] = self._parse_package_json(package_json)

        self._save_output(dependencies, output_file, "dependencies")
        return dependencies

    def _cleanup_temp_dir(self) -> None:
        """Safely cleanup temporary directory."""
        if not self._temp_dir or not self._temp_dir.exists():
            return

        try:
            # On Windows, sometimes Git keeps handles open briefly
            if sys.platform == "win32":
                time.sleep(0.1)  # Small delay to let handles close

            # Close any Git objects that might hold handles
            if self._git_repo:
                self._git_repo.close()

            # Remove the directory with error handler for readonly files
            shutil.rmtree(self._temp_dir, onerror=_remove_readonly)
        except Exception as e:
            # Log error but don't raise - this is cleanup code
            print(f"Warning: Failed to cleanup temporary directory: {e}", file=sys.stderr)

    def __del__(self):
        """Cleanup temporary directory if it exists."""
        self._cleanup_temp_dir()

    def _get_file_type(self, path: Path) -> str:
        """Get MIME type of a file."""
        # First try by extension
        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type:
            return mime_type

        # Then try python-magic if available
        if HAS_MAGIC:
            try:
                return magic.from_file(str(path), mime=True)
            except Exception:
                pass

        # Fallback to basic type mapping
        ext = path.suffix.lower()
        if ext in COMMON_EXTENSIONS:
            return COMMON_EXTENSIONS[ext]
        return "application/octet-stream"

    def _map_mime_to_language(self, mime_type: str) -> str:
        """Map MIME type to programming language name."""
        # First try MIME mapping
        if mime_type in MIME_TO_LANGUAGE:
            return MIME_TO_LANGUAGE[mime_type]

        # Try by extension
        ext = Path(mime_type).suffix.lower()
        if ext in COMMON_EXTENSIONS:
            return COMMON_EXTENSIONS[ext]

        return "Other"

    def get_language_stats(
        self, output_file: Optional[str] = None
    ) -> Dict[str, Dict[str, Union[int, float]]]:
        """Get language statistics for the repository."""
        if not self._repo_path:
            raise GitError("Repository not initialized")

        stats: Dict[str, Dict[str, Union[int, float]]] = {}
        total_bytes = 0
        total_files = 0

        for file_path in self._walk_directory(self._repo_path):
            mime_type, is_binary = self._get_file_type(file_path)
            if is_binary:
                continue

            language = self._map_mime_to_language(mime_type)
            size = file_path.stat().st_size

            if language not in stats:
                stats[language] = {"files": 0, "bytes": 0}

            stats[language]["files"] += 1
            stats[language]["bytes"] += size
            total_bytes += size
            total_files += 1

        # Calculate percentages
        if total_bytes > 0:
            for lang_stats in stats.values():
                bytes_count = lang_stats["bytes"]
                lang_stats["percentage"] = round((bytes_count / total_bytes) * 100, 2)

        self._save_output(stats, output_file, "language_stats")
        return stats

    def get_statistics(self, output_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """Get overall repository statistics.

        Args:
            output_file: Optional path to save results. Use "auto" for auto-generated filename.

        Returns:
            Dict with various repository statistics
        """
        if not self._repo_path:
            raise RuntimeError("Repository path not initialized")

        stats = {
            "total_files": 0,
            "total_size": 0,
            "binary_files": 0,
            "text_files": 0,
            "avg_file_size": 0,
            "binary_ratio": 0.0,
            "language_breakdown": self.get_language_stats(),
        }

        # Process all files
        files = self._walk_directory(self._repo_path)
        for file_path in files:
            # Update counters
            stats["total_files"] += 1
            size = file_path.stat().st_size
            stats["total_size"] += size

            # Check if binary
            _, is_binary = self._get_file_type(file_path)
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

    def get_repo_stats(self, output_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """Get repository statistics including file counts, sizes, and types.

        Args:
            output_file: Optional path to save results. Use "auto" for auto-generated filename.

        Returns:
            Dictionary containing repository statistics
        """
        if not self._repo_path:
            return {}

        files = self._walk_directory(self._repo_path)
        total_size = 0
        binary_count = 0
        file_types: Dict[str, int] = {}
        largest_files = []

        for file in files:
            # Get file size
            size = file.stat().st_size
            total_size += size

            # Track file type
            ext = file.suffix.lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1

            # Check if binary
            if self._is_binary_file(file):
                binary_count += 1

            # Track largest files
            largest_files.append({"path": str(file.relative_to(self._repo_path)), "size": size})

        # Sort and limit largest files
        largest_files.sort(key=lambda x: x["size"], reverse=True)
        largest_files = largest_files[:10]  # Keep top 10

        stats = {
            "total_files": len(files),
            "total_size": total_size,
            "average_file_size": total_size / len(files) if files else 0,
            "binary_ratio": binary_count / len(files) if files else 0,
            "file_types": file_types,
            "largest_files": largest_files,
        }

        self._save_output(stats, output_file, "repo_stats")
        return stats

    def get_file_content(
        self, file_path: str, output_file: Optional[str] = None, encoding: str = "utf-8"
    ) -> Optional[str]:
        """Get content of a specific file from the repository.

        Args:
            file_path: Path to the file relative to repository root
            output_file: Optional file to save the content to
            encoding: File encoding to use

        Returns:
            File content as string or None if file not found/readable
        """
        if not self._repo_path:
            raise RuntimeError("Repository path not initialized")

        full_path = self._repo_path / Path(file_path)
        if not full_path.exists() or not full_path.is_file():
            return None

        # Check if file is text
        content_type, is_binary = self._get_file_type(full_path)
        if is_binary:
            return None

        try:
            content = full_path.read_text(encoding=encoding)
            self._save_output(content, output_file, f"content_{Path(file_path).name}")
            return content
        except UnicodeDecodeError:
            return None

    def get_all_contents(
        self,
        max_file_size: Optional[int] = None,
        exclude_patterns: Optional[List[str]] = None,
        output_file: Optional[str] = None,
    ) -> Dict[str, str]:
        """Get contents of all text files in the repository."""
        if not self._repo_path:
            raise GitError("Repository not initialized")

        contents = {}
        files = self._walk_directory(self._repo_path)

        for file_path in files:
            # Skip if file is too large
            size_limit = max_file_size or self.config.max_file_size
            if file_path.stat().st_size > size_limit:
                continue

            # Skip if file matches any exclude pattern
            rel_path = str(file_path.relative_to(self._repo_path))
            if exclude_patterns and any(
                fnmatch.fnmatch(rel_path, pattern) for pattern in exclude_patterns
            ):
                continue

            # Try to read content
            content = self.get_file_content(rel_path)
            if content is not None:
                contents[rel_path] = content

        self._save_output(contents, output_file, "all_contents")
        return contents

    def get_directory_tree(
        self,
        directory: str,
        style: Literal["flattened", "markdown", "structured"] = "flattened",
        output_file: Optional[str] = None,
    ) -> Union[List[str], Dict]:
        """Get file tree for a specific directory."""
        if not self._repo_path:
            raise GitError("Repository not initialized")

        dir_path = self._repo_path / directory
        if not dir_path.is_dir():
            raise GitError(f"Directory not found: {directory}")

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
        self, directory: str, output_file: Optional[str] = None
    ) -> Dict[str, str]:
        """Get contents of all files in a directory."""
        if not self._repo_path:
            raise GitError("Repository not initialized")

        dir_path = self._repo_path / directory
        if not dir_path.is_dir():
            raise GitError(f"Directory not found: {directory}")

        contents = {}
        for file_path in self._walk_directory(dir_path):
            try:
                content = file_path.read_text(encoding="utf-8")
                rel_path = str(file_path.relative_to(dir_path))
                contents[rel_path] = content
            except UnicodeDecodeError:
                continue

        self._save_output(contents, output_file, "dir_contents")
        return contents

    def _is_binary_file(self, path: Path) -> bool:
        """Check if a file is binary.

        Args:
            path: Path to the file to check

        Returns:
            True if file is binary, False otherwise
        """
        # First check extension
        ext = path.suffix.lower()
        if ext in {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".ico",
            ".pdf",
            ".zip",
            ".gz",
            ".tar",
            ".rar",
            ".exe",
            ".dll",
            ".so",
            ".pyc",
        }:
            return True

        # Use python-magic if available
        if HAS_MAGIC:
            try:
                mime = magic.from_file(str(path), mime=True)
                return not mime.startswith(
                    ("text/", "application/json", "application/xml", "application/x-yaml")
                )
            except Exception:
                pass

        # Fallback: try reading as text
        try:
            with path.open("r", encoding="utf-8") as f:
                f.read(1024)  # Read first 1KB
            return False
        except UnicodeDecodeError:
            return True
        except Exception:
            return False
