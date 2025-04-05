"""File system utilities for Git repository analysis."""

import contextlib
import gc
import logging
import mimetypes
import shutil
import stat
from collections.abc import Generator
from pathlib import Path
from typing import Any, Callable

try:
    import magic

    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

from gitparse.vars.file_types import COMMON_EXTENSIONS, MIME_TO_LANGUAGE

logger = logging.getLogger(__name__)


def handle_readonly(
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


def cleanup_directory(directory: Path, is_git: bool = False) -> None:
    """Clean up a directory, handling Git-specific cleanup issues.

    Args:
        directory: Path to the directory to clean up
        is_git: Whether this is a Git repository directory
    """
    if not directory or not directory.exists():
        return

    # Force garbage collection to help release file handles
    gc.collect()

    # Try to remove the directory silently
    try:
        shutil.rmtree(directory)
    except PermissionError:
        # Ignore permission errors on Windows for Git files
        pass
    except OSError as e:
        # Only log if it's not a Git-related file access error
        if not is_git or not (str(e).endswith(".git") or ".git" in str(e)):
            logger.warning("Failed to cleanup directory: %s", directory)


def get_file_type(path: Path) -> tuple[str, bool]:
    """Get MIME type and binary flag for a file.

    Args:
        path: Path to the file

    Returns:
        Tuple of (mime_type, is_binary)
    """
    # First try by extension
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type:
        return mime_type, not mime_type.startswith("text/")

    # Then try python-magic if available
    if HAS_MAGIC:
        try:
            mime_type = magic.from_file(str(path), mime=True)
        except Exception:
            logger.exception("Failed to get file type with magic")
        else:
            return mime_type, not mime_type.startswith(
                ("text/", "application/json", "application/xml", "application/x-yaml"),
            )

    # Fallback to basic binary check
    try:
        with path.open("rb") as f:
            chunk = f.read(1024)  # Read first 1KB
            is_binary = b"\0" in chunk
            return "application/octet-stream" if is_binary else "text/plain", is_binary
    except Exception:
        logger.exception("Failed to check file type")
        return "application/octet-stream", True


def map_mime_to_language(mime_type: str) -> str:
    """Map MIME type to programming language name."""
    # First try MIME mapping
    if mime_type in MIME_TO_LANGUAGE:
        return MIME_TO_LANGUAGE[mime_type]

    # Try by extension
    ext = Path(mime_type).suffix.lower()
    if ext in COMMON_EXTENSIONS:
        return COMMON_EXTENSIONS[ext]

    return "Other"


def is_binary_file(path: Path) -> bool:
    """Check if a file is binary.

    Args:
        path: Path to the file to check

    Returns:
        bool: True if the file is binary, False otherwise
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
                ("text/", "application/json", "application/xml", "application/x-yaml"),
            )
        except Exception:
            logger.exception("Failed to check file type with magic")

    # Fallback: try reading as text
    try:
        with path.open("rb") as f:
            chunk = f.read(1024)  # Read first 1KB
            return b"\0" in chunk
    except Exception:
        logger.exception("Failed to check if file is binary")
        return False


@contextlib.contextmanager
def temp_dir_context() -> Generator[None, None, None]:
    """Context manager for temporary directory cleanup.

    Yields:
        None: This context manager doesn't yield any value
    """
    try:
        yield
    finally:
        cleanup_temp_directories()


def cleanup_temp_directories() -> None:
    """Clean up all temporary directories in the system temp directory."""
    import tempfile

    temp_root = Path(tempfile.gettempdir())
    for item in temp_root.iterdir():
        if item.is_dir() and item.name.startswith("tmp"):
            with contextlib.suppress(Exception):
                shutil.rmtree(item)
