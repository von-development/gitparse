"""Python dependency parsers."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, ClassVar, Optional

if TYPE_CHECKING:
    from pathlib import Path

import tomli
from packaging.requirements import InvalidRequirement, Requirement

from gitparse.parsers.deps.base import DependencyParser

logger = logging.getLogger(__name__)

# VCS URL patterns
VCS_PATTERNS: dict[str, str] = {
    "git": r"git\+https?://.*",
    "git+ssh": r"git\+ssh://.*",
    "git+git": r"git\+git://.*",
    "hg": r"hg\+https?://.*",
    "svn": r"svn\+https?://.*",
    "bzr": r"bzr\+https?://.*",
}

# Direct URL patterns
DIRECT_URL_PATTERNS: list[str] = [
    r"https?://.*\.(tar\.gz|zip|whl|tgz|tar\.bz2)$",
    r"https?://github\.com/.*/archive/.*\.(tar\.gz|zip)$",
    r"https?://github\.com/.*/releases/download/.*\.(tar\.gz|zip|whl)$",
]


class RequirementsTxtParser(DependencyParser):
    """Parser for requirements.txt files.

    This parser handles requirements.txt files and extracts dependencies including:
    - Package names with version specifiers
    - VCS dependencies (git, hg, svn, bzr)
    - Direct URL dependencies
    - Environment markers
    - Extras
    """

    file_patterns: ClassVar[list[str]] = ["requirements*.txt", "requirements/*.txt"]
    parser_name: ClassVar[str] = "requirements.txt"

    def _parse_requirement_line(self, line: str) -> Optional[dict[str, Any]]:
        """Parse a single requirement line.

        Args:
            line: Line from requirements.txt

        Returns:
            Parsed requirement or None if invalid
        """
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            return None

        # Try to parse as a regular requirement
        try:
            req = Requirement(stripped_line)
            return {
                "name": req.name,
                "specifier": str(req.specifier) if req.specifier else "",
                "extras": sorted(req.extras) if req.extras else [],
                "url": req.url if hasattr(req, "url") else None,
                "markers": str(req.marker) if req.marker else None,
            }
        except InvalidRequirement:
            pass

        # Check for VCS dependencies
        for vcs_type, pattern in VCS_PATTERNS.items():
            if re.match(pattern, stripped_line):
                return {
                    "type": "vcs",
                    "vcs": vcs_type,
                    "raw": stripped_line,
                    "url": stripped_line,
                }

        # Check for direct URL dependencies
        if any(re.match(pattern, stripped_line) for pattern in DIRECT_URL_PATTERNS):
            return {
                "type": "url",
                "raw": stripped_line,
                "url": stripped_line,
            }

        logger.warning("Invalid requirement found: %s", stripped_line)
        return {
            "type": "unknown",
            "raw": stripped_line,
            "parsed": False,
        }

    def parse(self, file_path: Path) -> Optional[dict[str, Any]]:
        """Parse dependencies from a requirements.txt file.

        Args:
            file_path: Path to the requirements.txt file

        Returns:
            Dictionary containing parsed dependencies, or None if parsing fails
        """
        if not file_path.exists():
            return None

        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as e:
            logger.warning("Failed to read requirements file: %s", e)
            return None

        dependencies = []
        parsed_deps = [self._parse_requirement_line(line) for line in lines]
        dependencies.extend(dep for dep in parsed_deps if dep is not None)

        # Determine dependency type from file path
        dep_type = "main"
        path_str = str(file_path).lower()
        if any(x in path_str for x in ["dev", "test", "doc"]):
            dep_type = "dev"

        return {
            "type": dep_type,
            "dependencies": dependencies,
        }


class PoetryParser(DependencyParser):
    """Parser for Poetry dependencies in pyproject.toml files.

    This parser handles both Poetry and PEP 621 dependencies including:
    - Main dependencies
    - Development dependencies
    - Optional dependencies
    - Python version constraints
    - VCS dependencies
    - Path dependencies
    """

    file_patterns: ClassVar[list[str]] = ["pyproject.toml"]
    parser_name: ClassVar[str] = "poetry"

    def _parse_poetry_section(self, poetry: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Parse the Poetry section of pyproject.toml.

        Args:
            poetry: Poetry section data

        Returns:
            Parsed dependencies
        """
        deps: dict[str, dict[str, Any]] = {
            "dependencies": {},
            "dev-dependencies": {},
            "optional-dependencies": {},
        }

        # Main dependencies
        if "dependencies" in poetry:
            deps["dependencies"] = self._parse_poetry_dependencies(poetry["dependencies"])

        # Dev dependencies (new style)
        if "group" in poetry:
            for group_name, group in poetry["group"].items():
                if "dependencies" in group:
                    if group_name == "dev":
                        deps["dev-dependencies"] = self._parse_poetry_dependencies(
                            group["dependencies"],
                        )
                    else:
                        deps["optional-dependencies"][group_name] = self._parse_poetry_dependencies(
                            group["dependencies"],
                        )

        # Dev dependencies (old style)
        if "dev-dependencies" in poetry:
            deps["dev-dependencies"].update(
                self._parse_poetry_dependencies(poetry["dev-dependencies"]),
            )

        return deps

    def _parse_pep621_section(self, project: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Parse the PEP 621 section of pyproject.toml.

        Args:
            project: Project section data

        Returns:
            Parsed dependencies
        """
        deps: dict[str, dict[str, Any]] = {
            "dependencies": {},
            "dev-dependencies": {},
            "optional-dependencies": {},
        }

        # Main dependencies
        if "dependencies" in project:
            deps["dependencies"] = self._parse_pep621_dependencies(project["dependencies"])

        # Optional dependencies
        if "optional-dependencies" in project:
            for group_name, group_deps in project["optional-dependencies"].items():
                deps["optional-dependencies"][group_name] = self._parse_pep621_dependencies(
                    group_deps,
                )

        return deps

    def parse(self, file_path: Path) -> Optional[dict[str, dict[str, Any]]]:
        """Parse dependencies from a pyproject.toml file.

        Args:
            file_path: Path to the pyproject.toml file

        Returns:
            Dictionary containing parsed dependencies, or None if parsing fails
        """
        if not file_path.exists():
            return None

        try:
            data = tomli.loads(file_path.read_text(encoding="utf-8"))
        except (tomli.TOMLDecodeError, OSError, UnicodeError) as e:
            logger.warning("Failed to parse pyproject.toml: %s", e)
            return None

        deps: dict[str, dict[str, Any]] = {
            "dependencies": {},
            "dev-dependencies": {},
            "optional-dependencies": {},
        }

        # Try Poetry format
        if "tool" in data and "poetry" in data["tool"]:
            poetry_deps = self._parse_poetry_section(data["tool"]["poetry"])
            deps.update(poetry_deps)

        # Try PEP 621 format
        if "project" in data:
            pep621_deps = self._parse_pep621_section(data["project"])
            deps.update(pep621_deps)

        return deps

    def _parse_vcs_dependency(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Parse VCS (git) dependency specification.

        Args:
            spec: Dictionary containing VCS dependency info

        Returns:
            Parsed VCS dependency info
        """
        dep_info = {"type": "vcs", "vcs": "git", "url": spec["git"]}
        if "rev" in spec:
            dep_info["rev"] = spec["rev"]
        return dep_info

    def _parse_path_dependency(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Parse local path dependency specification.

        Args:
            spec: Dictionary containing path dependency info

        Returns:
            Parsed path dependency info
        """
        return {"type": "path", "path": spec["path"]}

    def _parse_standard_fields(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Parse standard dependency fields.

        Args:
            spec: Dictionary containing dependency info

        Returns:
            Parsed standard fields
        """
        dep_info = {}
        if "version" in spec:
            dep_info["version"] = spec["version"]
        if "optional" in spec:
            dep_info["optional"] = spec["optional"]
        if "extras" in spec:
            dep_info["extras"] = spec["extras"]
        if "markers" in spec:
            dep_info["markers"] = spec["markers"]
        return dep_info

    def _parse_poetry_dependencies(
        self,
        deps_dict: dict[str, Any],
    ) -> dict[str, Any]:
        """Parse Poetry dependencies section.

        Args:
            deps_dict: Dictionary containing dependencies

        Returns:
            Dictionary mapping package names to dependency info
        """
        result = {}
        for name, spec in deps_dict.items():
            if name == "python":
                continue

            if isinstance(spec, str):
                result[name] = {"version": spec}
                continue

            if not isinstance(spec, dict):
                continue

            dep_info = self._parse_standard_fields(spec)

            if "git" in spec:
                dep_info.update(self._parse_vcs_dependency(spec))
            elif "path" in spec:
                dep_info.update(self._parse_path_dependency(spec))

            result[name] = dep_info

        return result

    def _parse_pep621_dependencies(
        self,
        deps_list: list[str],
    ) -> dict[str, Any]:
        """Parse PEP 621 dependencies section.

        Args:
            deps_list: List of dependency strings

        Returns:
            Dictionary mapping package names to dependency info
        """
        result = {}
        # Process all dependencies at once to avoid try-except in loop
        try:
            for dep in deps_list:
                req = Requirement(dep)
                result[req.name] = {
                    "version": str(req.specifier) if req.specifier else "",
                    "extras": sorted(req.extras) if req.extras else [],
                    "markers": str(req.marker) if req.marker else None,
                }
        except InvalidRequirement as e:
            logger.warning("Invalid PEP 621 requirement: %s", e)

        return result
