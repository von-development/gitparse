"""Custom exceptions for the GitParse library."""

from __future__ import annotations


class GitParseError(Exception):
    """Base exception class for GitParse errors.

    This exception is raised when there is an error during repository parsing
    or analysis operations.

    Args:
        message: The error message
        original_error: The original exception that caused this error
    """

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        super().__init__(message)
        self.original_error = original_error
        self.message = message

    def __str__(self) -> str:
        """Return a string representation of the error.

        Returns:
            A formatted error message including the original error if present.
        """
        if self.original_error:
            return f"{self.message} (Caused by: {type(self.original_error).__name__}: {self.original_error!s})"
        return self.message


class RepositoryNotFoundError(GitParseError):
    """Raised when a repository cannot be found at the specified path or URL."""


class InvalidRepositoryError(GitParseError):
    """Raised when a repository is invalid or corrupted."""


class GitFileNotFoundError(GitParseError):
    """Raised when a file cannot be found in the repository."""


class DirectoryNotFoundError(GitParseError):
    """Raised when a directory cannot be found in the repository."""


class ParseError(GitParseError):
    """Raised when there is an error parsing repository content."""


class DependencyError(GitParseError):
    """Raised when there is an error analyzing repository dependencies."""
