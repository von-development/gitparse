"""Dependency parser implementations."""

from __future__ import annotations

from gitparse.parsers.deps.base import DependencyParser
from gitparse.parsers.deps.nodejs import NodeJSParser
from gitparse.parsers.deps.python import PoetryParser, RequirementsTxtParser

__all__ = [
    "DependencyParser",
    "NodeJSParser",
    "PoetryParser",
    "RequirementsTxtParser",
]
