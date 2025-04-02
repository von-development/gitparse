from pathlib import Path
from typing import Optional, Union, Literal, Dict, List, Any
import tempfile
import shutil
from urllib.parse import urlparse
import os
import fnmatch
import git
from git.exc import GitCommandError
import json
import re
from packaging.requirements import Requirement, InvalidRequirement
import sys
import stat
import time
import mimetypes
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
from collections import defaultdict
from datetime import datetime

# Handle TOML parsing for different Python versions
import tomllib as toml_parser

from gitparse.schema.config import ExtractionConfig
from gitparse.vars.exclude_patterns import DEFAULT_EXCLUDE_PATTERNS
from gitparse.vars.file_types import MIME_TO_LANGUAGE, COMMON_EXTENSIONS
from gitparse.vars.limits import FILE_SIZE_LIMITS
from gitparse.vars.git_hosts import GIT_HOSTS


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
    
    def __init__(self, source: str, config: Optional[ExtractionConfig] = None):
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
        # Check if source is URL or local path
        parsed = urlparse(self.source)
        self._is_remote = bool(parsed.scheme and parsed.netloc)
        
        if self._is_remote:
            # For remote repos, we'll need to clone later
            if self.config.temp_dir:
                self._temp_dir = Path(self.config.temp_dir)
            else:
                self._temp_dir = Path(tempfile.mkdtemp())
        else:
            # Local path
            self._repo_path = Path(self.source).resolve()
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
            self._git_repo = git.Repo.clone_from(self.source, self._temp_dir)
            self._repo_path = self._temp_dir
        except GitCommandError as e:
            raise RuntimeError(f"Failed to clone repository: {e}")
    
    def _save_output(self, data: Any, output_file: Optional[Union[str, Path]] = None, prefix: str = "") -> None:
        """Save data to a file if output_file is specified.
        
        Args:
            data: Data to save (must be JSON serializable)
            output_file: Path to save file, if None, don't save
            prefix: Prefix for auto-generated filename
        """
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
                "is_bare": self._git_repo.bare
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
        """Format files as a markdown tree."""
        tree = []
        last_parts = []
        
        for file in files:
            rel_path = file.relative_to(self._repo_path)
            parts = rel_path.parts
            
            # Calculate common prefix with last path
            common = 0
            for i, (last, curr) in enumerate(zip(last_parts, parts)):
                if last != curr:
                    break
                common = i + 1
            
            # Add new directory levels
            for level, part in enumerate(parts[common:-1], common):
                tree.append("  " * level + "- " + part + "/")
            
            # Add file
            tree.append("  " * (len(parts) - 1) + "- " + parts[-1])
            last_parts = parts
        
        return tree
    
    def _format_tree_structured(self, files: List[Path]) -> Dict:
        """Format files as a nested dictionary structure."""
        tree: Dict = {}
        
        for file in files:
            rel_path = file.relative_to(self._repo_path)
            parts = rel_path.parts
            
            current = tree
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = None  # Files are leaf nodes
        
        return tree
    
    def get_file_tree(self, style: Literal["flattened", "markdown", "structured"] = "flattened",
                     output_file: Optional[Union[str, Path]] = None) -> Union[List[str], Dict]:
        """Get repository file tree in specified format.
        
        Args:
            style: Output style ("flattened", "markdown", or "structured")
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
        elif style == "structured":
            result = self._format_tree_structured(files)
        else:
            raise ValueError(f"Unsupported tree style: {style}")
        
        self._save_output(result, output_file, f"file_tree_{style}")
        return result
    
    def get_readme(self) -> Optional[str]:
        """Returns the content of the README file if present.
        
        Returns:
            Optional[str]: Content of README.md or None if not found
        """
        if not self._repo_path:
            raise RuntimeError("Repository path not initialized")
        
        # Common README filenames to check
        readme_names = [
            "README.md",
            "Readme.md",
            "readme.md",
            "README",
            "README.rst"
        ]
        
        # Check each possible README file
        for name in readme_names:
            readme_path = self._repo_path / name
            if readme_path.exists() and readme_path.is_file():
                try:
                    return readme_path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    continue  # Try next file if this one isn't text
        
        return None
    
    def _parse_requirements_txt(self, path: Path) -> List[Dict[str, str]]:
        """Parse a requirements.txt file."""
        if not path.exists():
            return []
        
        requirements = []
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                req = Requirement(line)
                requirements.append({
                    "name": req.name,
                    "specifier": str(req.specifier) if req.specifier else "",
                    "extras": sorted(req.extras) if req.extras else [],
                    "url": req.url if hasattr(req, 'url') else None
                })
            except InvalidRequirement:
                # Skip invalid requirements
                continue
        
        return requirements
    
    def _parse_poetry_toml(self, path: Path) -> Dict[str, List[Dict[str, str]]]:
        """Parse a pyproject.toml file with Poetry dependencies."""
        if not path.exists():
            return {}
        
        try:
            data = toml_parser.loads(path.read_text())
            deps: Dict[str, List[Dict[str, str]]] = {
                "dependencies": [],
                "dev-dependencies": []
            }
            
            # Main dependencies
            if "tool" in data and "poetry" in data["tool"]:
                poetry = data["tool"]["poetry"]
                if "dependencies" in poetry:
                    for name, spec in poetry["dependencies"].items():
                        if name == "python":
                            continue
                        if isinstance(spec, str):
                            deps["dependencies"].append({"name": name, "version": spec})
                        elif isinstance(spec, dict):
                            deps["dependencies"].append({
                                "name": name,
                                "version": spec.get("version", ""),
                                "extras": spec.get("extras", [])
                            })
                
                # Dev dependencies
                if "group" in poetry and "dev" in poetry["group"]:
                    dev = poetry["group"]["dev"]
                    if "dependencies" in dev:
                        for name, spec in dev["dependencies"].items():
                            if isinstance(spec, str):
                                deps["dev-dependencies"].append({"name": name, "version": spec})
                            elif isinstance(spec, dict):
                                deps["dev-dependencies"].append({
                                    "name": name,
                                    "version": spec.get("version", ""),
                                    "extras": spec.get("extras", [])
                                })
            
            return deps
        except Exception:
            return {}
    
    def _parse_package_json(self, path: Path) -> Dict[str, List[Dict[str, str]]]:
        """Parse a package.json file."""
        if not path.exists():
            return {}
        
        try:
            data = json.loads(path.read_text())
            deps: Dict[str, List[Dict[str, str]]] = {
                "dependencies": [],
                "devDependencies": []
            }
            
            # Regular dependencies
            if "dependencies" in data:
                for name, version in data["dependencies"].items():
                    deps["dependencies"].append({
                        "name": name,
                        "version": version
                    })
            
            # Dev dependencies
            if "devDependencies" in data:
                for name, version in data["devDependencies"].items():
                    deps["devDependencies"].append({
                        "name": name,
                        "version": version
                    })
            
            return deps
        except Exception:
            return {}
    
    def get_dependencies(self, output_file: Optional[Union[str, Path]] = None) -> Dict[str, Union[List[str], Dict[str, str]]]:
        """Get dependencies from package management files.
        
        Args:
            output_file: Optional path to save results. Use "auto" for auto-generated filename.
        
        Returns:
            Dict mapping file paths to their dependencies
        """
        if not self._repo_path:
            raise RuntimeError("Repository path not initialized")
        
        dependencies = {}
        
        # Python requirements.txt
        req_txt = self._repo_path / "requirements.txt"
        if req_txt.exists():
            dependencies["requirements.txt"] = {
                "dependencies": self._parse_requirements_txt(req_txt)
            }
        
        # Poetry pyproject.toml
        pyproject = self._repo_path / "pyproject.toml"
        if pyproject.exists():
            poetry_deps = self._parse_poetry_toml(pyproject)
            if poetry_deps:
                dependencies["pyproject.toml"] = poetry_deps
        
        # Node.js package.json
        package_json = self._repo_path / "package.json"
        if package_json.exists():
            node_deps = self._parse_package_json(package_json)
            if node_deps:
                dependencies["package.json"] = node_deps
        
        self._save_output(dependencies, output_file, "dependencies")
        return dependencies
    
    def _cleanup_temp_dir(self) -> None:
        """Safely cleanup temporary directory."""
        if not self._temp_dir or not self._temp_dir.exists():
            return
            
        try:
            # On Windows, sometimes Git keeps handles open briefly
            if sys.platform == 'win32':
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
    
    def _get_file_type(self, path: Path) -> tuple[str, bool]:
        """Determine file type and whether it's binary.
        
        Args:
            path: Path to the file
            
        Returns:
            Tuple of (content_type, is_binary)
        """
        # First try by extension
        content_type, _ = mimetypes.guess_type(str(path))
        
        if not content_type:
            if HAS_MAGIC:
                # Try using python-magic for more accurate detection
                try:
                    content_type = magic.from_file(str(path), mime=True)
                except Exception:
                    content_type = None
            
            # Fallback to basic extension mapping
            if not content_type:
                ext = path.suffix.lower()
                content_type = {
                    '.py': 'text/x-python',
                    '.js': 'text/javascript',
                    '.ts': 'text/typescript',
                    '.html': 'text/html',
                    '.css': 'text/css',
                    '.md': 'text/markdown',
                    '.rst': 'text/x-rst',
                    '.json': 'application/json',
                    '.yml': 'application/x-yaml',
                    '.yaml': 'application/x-yaml',
                    '.xml': 'application/xml',
                    '.txt': 'text/plain'
                }.get(ext, 'application/octet-stream')
        
        # Determine if binary
        is_binary = False
        try:
            with open(path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Try reading as text
        except UnicodeDecodeError:
            is_binary = True
        
        return content_type, is_binary
    
    def _map_mime_to_language(self, mime_type: str) -> str:
        """Map MIME type to programming language name."""
        # First try MIME mapping
        if mime_type in MIME_TO_LANGUAGE:
            return MIME_TO_LANGUAGE[mime_type]
            
        # Try by extension
        ext = Path(mime_type).suffix.lower()
        if ext in COMMON_EXTENSIONS:
            return COMMON_EXTENSIONS[ext]
            
        return 'Other'
    
    def get_language_stats(self, output_file: Optional[Union[str, Path]] = None) -> Dict[str, Dict[str, Union[int, float]]]:
        """Get language statistics for the repository.
        
        Args:
            output_file: Optional path to save results. Use "auto" for auto-generated filename.
        
        Returns:
            Dict mapping languages to their statistics
        """
        if not self._repo_path:
            raise RuntimeError("Repository path not initialized")
        
        # Initialize counters
        stats: Dict[str, Dict[str, Union[int, float]]] = defaultdict(
            lambda: {"bytes": 0, "files": 0, "percentage": 0.0}
        )
        total_size = 0
        
        # Process all files
        files = self._walk_directory(self._repo_path)
        for file_path in files:
            # Get file type and size
            content_type, is_binary = self._get_file_type(file_path)
            size = file_path.stat().st_size
            
            # Skip binary files
            if is_binary:
                continue
            
            # Map to language and update stats
            language = self._map_mime_to_language(content_type)
            stats[language]["bytes"] += size
            stats[language]["files"] += 1
            total_size += size
        
        # Calculate percentages
        if total_size > 0:
            for lang_stats in stats.values():
                lang_stats["percentage"] = round(
                    (lang_stats["bytes"] / total_size) * 100, 2
                )
        
        # Convert defaultdict to regular dict and sort by percentage
        sorted_stats = dict(sorted(
            stats.items(),
            key=lambda x: x[1]["bytes"],
            reverse=True
        ))
        
        self._save_output(sorted_stats, output_file, "language_stats")
        return sorted_stats
    
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
            "language_breakdown": self.get_language_stats()
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
            stats["binary_ratio"] = (
                stats["binary_files"] / stats["total_files"]
            ) * 100
        
        self._save_output(stats, output_file, "statistics")
        return stats
    
    def get_file_content(self, file_path: Union[str, Path], output_file: Optional[Union[str, Path]] = None) -> Optional[str]:
        """Get content of a specific file.
        
        Args:
            file_path: Path to the file relative to repository root
            output_file: Optional path to save results. Use "auto" for auto-generated filename.
        
        Returns:
            File content as string or None if file not found/not readable
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
            content = full_path.read_text(encoding='utf-8')
            self._save_output(content, output_file, f"content_{Path(file_path).name}")
            return content
        except UnicodeDecodeError:
            return None

    def get_all_contents(self, output_file: Optional[Union[str, Path]] = None) -> Dict[str, str]:
        """Get contents of all text files in repository.
        
        Args:
            output_file: Optional path to save results. Use "auto" for auto-generated filename.
            
        Returns:
            Dict mapping file paths to their contents
        """
        if not self._repo_path:
            raise RuntimeError("Repository path not initialized")
            
        contents = {}
        files = self._walk_directory(self._repo_path)
        
        for file_path in files:
            # Skip if file is too large
            if file_path.stat().st_size > self.config.max_file_size:
                continue
                
            # Get relative path
            rel_path = str(file_path.relative_to(self._repo_path))
            
            # Try to read content
            content = self.get_file_content(rel_path)
            if content is not None:
                contents[rel_path] = content
                
        self._save_output(contents, output_file, "all_contents")
        return contents

    def get_directory_tree(self, directory: str, style: Literal["flattened", "markdown", "structured"] = "flattened",
                          output_file: Optional[Union[str, Path]] = None) -> Union[List[str], Dict]:
        """Get file tree for a specific directory in the repository.
        
        Args:
            directory: Path to directory relative to repository root
            style: Output style ("flattened", "markdown", or "structured")
            output_file: Optional path to save results. Use "auto" for auto-generated filename.
        
        Returns:
            List of files or structured dictionary for the specified directory
        """
        if not self._repo_path:
            raise RuntimeError("Repository path not initialized")
        
        # Create temporary config for this operation
        temp_config = ExtractionConfig(
            include_patterns=[f"{directory}/*"],
            max_file_size=self.config.max_file_size,
            temp_dir=self.config.temp_dir
        )
        
        # Store original config
        original_config = self.config
        self.config = temp_config
        
        try:
            # Get filtered list of files
            files = self._walk_directory(self._repo_path)
            
            # Format according to requested style
            if style == "flattened":
                result = self._format_tree_flattened(files)
            elif style == "markdown":
                result = self._format_tree_markdown(files)
            elif style == "structured":
                result = self._format_tree_structured(files)
            else:
                raise ValueError(f"Unsupported tree style: {style}")
            
            self._save_output(result, output_file, f"dir_tree_{Path(directory).name}_{style}")
            return result
        finally:
            # Restore original config
            self.config = original_config

    def get_directory_contents(self, directory: str, output_file: Optional[Union[str, Path]] = None) -> Dict[str, str]:
        """Get contents of all text files in a specific directory.
        
        Args:
            directory: Path to directory relative to repository root
            output_file: Optional path to save results. Use "auto" for auto-generated filename.
            
        Returns:
            Dict mapping file paths to their contents
        """
        if not self._repo_path:
            raise RuntimeError("Repository path not initialized")
        
        # Create temporary config for this operation
        temp_config = ExtractionConfig(
            include_patterns=[f"{directory}/*"],
            max_file_size=self.config.max_file_size,
            temp_dir=self.config.temp_dir
        )
        
        # Store original config
        original_config = self.config
        self.config = temp_config
        
        try:
            contents = {}
            files = self._walk_directory(self._repo_path)
            
            for file_path in files:
                # Skip if file is too large
                if file_path.stat().st_size > self.config.max_file_size:
                    continue
                    
                # Get relative path
                rel_path = str(file_path.relative_to(self._repo_path))
                
                # Try to read content
                content = self.get_file_content(rel_path)
                if content is not None:
                    contents[rel_path] = content
                    
            self._save_output(contents, output_file, f"dir_contents_{Path(directory).name}")
            return contents
        finally:
            # Restore original config
            self.config = original_config 