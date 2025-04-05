"""Node.js package.json dependency parser."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, ClassVar, Optional

if TYPE_CHECKING:
    from pathlib import Path

from gitparse.parsers.deps.base import DependencyParser

logger = logging.getLogger(__name__)


class NodeJSParser(DependencyParser):
    """Parser for Node.js package.json files.

    This parser handles package.json files and extracts both regular and development
    dependencies. It supports various dependency types including:
    - dependencies
    - devDependencies
    - peerDependencies
    - optionalDependencies
    """

    file_patterns: ClassVar[list[str]] = ["package.json"]
    parser_name: ClassVar[str] = "nodejs"

    def parse(self, file_path: Path) -> Optional[dict[str, list[dict[str, str]]]]:
        """Parse dependencies from a package.json file.

        Args:
            file_path: Path to the package.json file

        Returns:
            Dictionary containing parsed dependencies by type, or None if parsing fails
        """
        if not file_path.exists():
            return None

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, UnicodeError) as e:
            logger.warning("Failed to parse package.json: %s", e)
            return None

        dependencies: dict[str, list[dict[str, str]]] = {
            "dependencies": [],
            "devDependencies": [],
            "peerDependencies": [],
            "optionalDependencies": [],
        }

        # Parse each dependency type
        for dep_type in dependencies:
            if dep_type in data:
                try:
                    deps = data[dep_type]
                    if isinstance(deps, dict):
                        dependencies[dep_type].extend(
                            self._parse_dependency(name, version) for name, version in deps.items()
                        )
                except (KeyError, TypeError, ValueError) as e:
                    logger.warning(
                        "Failed to parse %s in package.json: %s",
                        dep_type,
                        e,
                    )

        return dependencies

    def _parse_dependency(self, name: str, version_spec: Any) -> dict[str, str]:
        """Parse a single dependency entry.

        Args:
            name: Package name
            version_spec: Version specification (can be string or dict)

        Returns:
            Dictionary containing parsed dependency information
        """
        if isinstance(version_spec, dict):
            # Handle git dependencies
            if any(key in version_spec for key in ["git", "github", "gitlab", "bitbucket"]):
                return {
                    "name": name,
                    "type": "vcs",
                    "version": version_spec.get("version", ""),
                    "url": version_spec.get("url", ""),
                }
            # Handle other complex specifications
            return {
                "name": name,
                "version": version_spec.get("version", ""),
            }

        # Handle simple version strings
        version = str(version_spec)
        version = self.normalize_version(version)

        return {
            "name": name,
            "version": version,
        }
