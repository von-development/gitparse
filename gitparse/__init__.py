"""GitParse - A typed, modular Python library for structured repository parsing."""

from gitparse.core import (
    DependencyError,
    DirectoryNotFoundError,
    FileNotFoundError,
    GitParseError,
    GitRepo,
    InvalidRepositoryError,
    ParseError,
    RepositoryNotFoundError,
)

__version__ = "0.1.0"

__all__ = [
    "GitRepo",
    "GitParseError",
    "RepositoryNotFoundError",
    "InvalidRepositoryError",
    "FileNotFoundError",
    "DirectoryNotFoundError",
    "ParseError",
    "DependencyError",
]
