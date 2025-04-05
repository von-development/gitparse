"""Base class for dependency parsers."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Optional

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class DependencyParser(ABC):
    """Base class for all dependency parsers.

    This class defines the interface that all dependency parsers must implement
    and provides common utility methods.
    """

    # Class-level attributes to be defined by subclasses
    file_patterns: ClassVar[list[str]] = []  # File patterns this parser handles
    parser_name: ClassVar[str] = ""  # Name of the parser (e.g., "poetry", "npm")

    def __init__(self, repo_path: Path) -> None:
        """Initialize parser with repository path.

        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = repo_path

    @abstractmethod
    def parse(self, file_path: Path) -> dict[str, Any]:
        """Parse dependency information from a file.

        Args:
            file_path: Path to the dependency file

        Returns:
            Dictionary containing parsed dependency information
        """
        raise NotImplementedError

    def find_dependency_files(self) -> list[Path]:
        """Find all dependency files matching this parser's patterns.

        Returns:
            List of paths to dependency files
        """
        files = []
        try:
            for pattern in self.file_patterns:
                files.extend(self.repo_path.glob(pattern))
        except (OSError, ValueError) as e:
            logger.warning("Failed to find dependency files: %s", e)
        return sorted(files)

    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file.

        Args:
            file_path: Path to check

        Returns:
            True if this parser can handle the file
        """
        return any(file_path.match(pattern) for pattern in self.file_patterns)

    def safe_read(self, file_path: Path, encoding: str = "utf-8") -> Optional[str]:
        """Safely read a file with proper error handling.

        Args:
            file_path: Path to the file
            encoding: File encoding to use

        Returns:
            File contents or None if reading failed
        """
        try:
            return file_path.read_text(encoding=encoding)
        except (OSError, UnicodeError) as e:
            logger.warning("Failed to read %s: %s", file_path, e)
            return None

    def normalize_version(self, version: str) -> str:
        """Normalize version string to a standard format.

        Args:
            version: Version string to normalize

        Returns:
            Normalized version string
        """
        # Remove common prefixes
        version = version.strip().lstrip("^~=<>")

        # Handle common formats
        if version.startswith("v"):
            version = version[1:]

        return version

    def parse_vcs_requirement(self, spec: str) -> dict[str, Any]:
        """Parse a VCS (git/hg/svn) requirement.

        Args:
            spec: VCS requirement specification

        Returns:
            Dictionary with parsed VCS info
        """
        result = {"type": "vcs"}

        # Handle git+http(s) format
        if spec.startswith("git+"):
            result["vcs"] = "git"
            url = spec[4:]
        else:
            result["vcs"] = "unknown"
            url = spec

        # Extract branch/tag/ref if present
        if "@" in url:
            url, ref = url.split("@", 1)
            result["ref"] = ref

        result["url"] = url
        return result

    def get_dependency_type(self, file_path: Path) -> str:
        """Determine if dependencies are dev/main based on file path.

        Args:
            file_path: Path to check

        Returns:
            "dev" or "main" depending on file location/name
        """
        path_str = str(file_path)
        if any(
            indicator in path_str.lower()
            for indicator in ["test", "dev", "development", "requirements-dev"]
        ):
            return "dev"
        return "main"
