"""GitParse - A typed, modular Python library for structured repository parsing."""

from gitparse.core.repo import GitRepo
from gitparse.schema.config import ExtractionConfig

__all__ = ["GitRepo", "ExtractionConfig"]

__version__ = "0.1.0" 