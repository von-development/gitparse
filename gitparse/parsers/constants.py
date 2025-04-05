"""Constants for dependency parsing."""

from __future__ import annotations

# File patterns for different package managers
DEPENDENCY_PATTERNS = {
    "python": {
        "requirements": ["requirements.txt", "requirements/*.txt", "requirements/**/*.txt"],
        "poetry": ["pyproject.toml"],
        "pipenv": ["Pipfile", "Pipfile.lock"],
        "setup": ["setup.py", "setup.cfg"],
    },
    "javascript": {
        "npm": ["package.json", "package-lock.json"],
        "yarn": ["yarn.lock"],
        "pnpm": ["pnpm-lock.yaml"],
    },
    "ruby": {
        "bundler": ["Gemfile", "Gemfile.lock"],
    },
    "rust": {
        "cargo": ["Cargo.toml", "Cargo.lock"],
    },
    "java": {
        "maven": ["pom.xml"],
        "gradle": ["build.gradle", "build.gradle.kts"],
    },
    "php": {
        "composer": ["composer.json", "composer.lock"],
    },
    "go": {
        "modules": ["go.mod", "go.sum"],
    },
}

# Common version prefixes to normalize
VERSION_PREFIXES = ["^", "~", ">=", "<=", ">", "<", "==", "!=", "~=", "==="]

# Common dependency types
DEPENDENCY_TYPES = {
    "main": ["dependencies", "requires", "install_requires"],
    "dev": [
        "dev-dependencies",
        "devDependencies",
        "development",
        "test",
        "tests",
        "testing",
    ],
    "optional": ["extras_require", "optional-dependencies"],
    "peer": ["peerDependencies"],
}

# Lock file mappings
LOCK_FILE_MAPPING = {
    "pyproject.toml": "poetry.lock",
    "Pipfile": "Pipfile.lock",
    "package.json": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
    "Cargo.toml": "Cargo.lock",
    "Gemfile": "Gemfile.lock",
    "composer.json": "composer.lock",
}

# Common environment markers
ENV_MARKERS = [
    "os_name",
    "sys_platform",
    "platform_machine",
    "platform_python_implementation",
    "platform_release",
    "platform_system",
    "platform_version",
    "python_version",
    "python_full_version",
    "implementation_name",
    "implementation_version",
]

# VCS prefixes
VCS_PREFIXES = {
    "git": ["git+https://", "git+ssh://", "git://"],
    "hg": ["hg+https://", "hg+ssh://", "hg://"],
    "svn": ["svn+https://", "svn+ssh://", "svn://"],
    "bzr": ["bzr+https://", "bzr+ssh://", "bzr://"],
}

# Common file locations
COMMON_LOCATIONS = {
    "requirements": ["requirements", "requirements.d", "pip", "dependencies"],
    "python": ["python", "py", "python3"],
    "node": ["node", "nodejs", "js"],
    "ruby": ["ruby", "rb"],
    "java": ["java", "jvm"],
} 