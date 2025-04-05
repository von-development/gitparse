"""Python dependency parsers."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import tomli
from packaging.requirements import InvalidRequirement, Requirement


from gitparse.parsers.deps.base import DependencyParser

logger = logging.getLogger(__name__)

# VCS URL patterns
VCS_PATTERNS = {
    "git": r"git\+https?://.*",
    "git+ssh": r"git\+ssh://.*",
    "git+git": r"git\+git://.*",
    "hg": r"hg\+https?://.*",
    "svn": r"svn\+https?://.*",
    "bzr": r"bzr\+https?://.*",
}

# Direct URL patterns
DIRECT_URL_PATTERNS = [
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

    file_patterns = ["requirements*.txt", "requirements/*.txt"]
    parser_name = "requirements.txt"

    def parse(self, file_path: Path) -> Optional[Dict[str, Any]]:
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
        except Exception as e:
            logger.warning("Failed to read requirements file: %s", str(e))
            return None

        dependencies = []
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith("#"):
                continue

            # Try to parse as a regular requirement first
            try:
                req = Requirement(stripped_line)
                dependencies.append({
                    "name": req.name,
                    "specifier": str(req.specifier) if req.specifier else "",
                    "extras": sorted(req.extras) if req.extras else [],
                    "url": req.url if hasattr(req, "url") else None,
                    "markers": str(req.marker) if req.marker else None,
                })
                continue
            except InvalidRequirement:
                # Not a regular requirement, try VCS or direct URL
                pass

            # Check for VCS dependencies
            vcs_match = None
            for vcs_type, pattern in VCS_PATTERNS.items():
                if re.match(pattern, stripped_line):
                    vcs_match = {
                        "type": "vcs",
                        "vcs": vcs_type,
                        "raw": stripped_line,
                        "url": stripped_line,
                    }
                    break

            if vcs_match:
                dependencies.append(vcs_match)
                continue

            # Check for direct URL dependencies
            is_direct_url = any(
                re.match(pattern, stripped_line) for pattern in DIRECT_URL_PATTERNS
            )
            if is_direct_url:
                dependencies.append({
                    "type": "url",
                    "raw": stripped_line,
                    "url": stripped_line,
                })
                continue

            # If we get here, it's an unparseable requirement
            logger.warning("Invalid requirement found: %s", stripped_line)
            dependencies.append({
                "type": "unknown",
                "raw": stripped_line,
                "parsed": False,
            })

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

    file_patterns = ["pyproject.toml"]
    parser_name = "poetry"

    def parse(self, file_path: Path) -> Optional[Dict[str, Dict[str, Any]]]:
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
        except Exception as e:
            logger.warning("Failed to parse pyproject.toml: %s", str(e))
            return None

        deps: Dict[str, Dict[str, Any]] = {
            "dependencies": {},
            "dev-dependencies": {},
            "optional-dependencies": {},
        }

        # Try Poetry format first
        if "tool" in data and "poetry" in data["tool"]:
            poetry = data["tool"]["poetry"]
            
            # Main dependencies
            if "dependencies" in poetry:
                deps["dependencies"] = self._parse_poetry_dependencies(poetry["dependencies"])

            # Dev dependencies (new style)
            if "group" in poetry:
                for group_name, group in poetry["group"].items():
                    if "dependencies" in group:
                        if group_name == "dev":
                            deps["dev-dependencies"] = self._parse_poetry_dependencies(
                                group["dependencies"]
                            )
                        else:
                            deps["optional-dependencies"][group_name] = self._parse_poetry_dependencies(
                                group["dependencies"]
                            )

            # Dev dependencies (old style)
            if "dev-dependencies" in poetry:
                deps["dev-dependencies"].update(
                    self._parse_poetry_dependencies(poetry["dev-dependencies"])
                )

        # Try PEP 621 format
        if "project" in data:
            project = data["project"]
            
            # Main dependencies
            if "dependencies" in project:
                deps["dependencies"].update(
                    self._parse_pep621_dependencies(project["dependencies"])
                )

            # Optional dependencies
            if "optional-dependencies" in project:
                for group_name, group_deps in project["optional-dependencies"].items():
                    deps["optional-dependencies"][group_name] = self._parse_pep621_dependencies(
                        group_deps
                    )

        return deps

    def _parse_poetry_dependencies(
        self,
        deps_dict: Dict[str, Any],
    ) -> Dict[str, Any]:
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
            elif isinstance(spec, dict):
                dep_info = {}
                if "version" in spec:
                    dep_info["version"] = spec["version"]
                if "git" in spec:
                    dep_info["type"] = "vcs"
                    dep_info["vcs"] = "git"
                    dep_info["url"] = spec["git"]
                    if "rev" in spec:
                        dep_info["rev"] = spec["rev"]
                if "path" in spec:
                    dep_info["type"] = "path"
                    dep_info["path"] = spec["path"]
                if "optional" in spec:
                    dep_info["optional"] = spec["optional"]
                if "extras" in spec:
                    dep_info["extras"] = spec["extras"]
                if "markers" in spec:
                    dep_info["markers"] = spec["markers"]
                result[name] = dep_info

        return result

    def _parse_pep621_dependencies(
        self,
        deps_list: List[str],
    ) -> Dict[str, Any]:
        """Parse PEP 621 dependencies section.
        
        Args:
            deps_list: List of dependency strings
            
        Returns:
            Dictionary mapping package names to dependency info
        """
        result = {}
        for dep in deps_list:
            try:
                req = Requirement(dep)
                result[req.name] = {
                    "version": str(req.specifier) if req.specifier else "",
                    "extras": sorted(req.extras) if req.extras else [],
                    "markers": str(req.marker) if req.marker else None,
                }
            except InvalidRequirement:
                logger.warning("Invalid PEP 621 requirement: %s", dep)
                result[dep] = {"version": "", "raw": dep}

        return result 