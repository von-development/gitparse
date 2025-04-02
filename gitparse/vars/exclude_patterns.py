"""Default patterns for files and directories to exclude from analysis."""

DEFAULT_EXCLUDE_PATTERNS = {
    # Version Control
    ".git/**",
    ".svn/**",
    ".hg/**",
    ".bzr/**",

    # Python
    "**/__pycache__/**",
    "**/*.pyc",
    "**/*.pyo",
    "**/*.pyd",
    ".Python",
    "**/.pytest_cache/**",
    "**/.coverage",
    "**/.tox/**",
    "**/.env/**",
    "**/.venv/**",
    "**/env/**",
    "**/venv/**",

    # Node.js
    "**/node_modules/**",
    "**/bower_components/**",
    "**/.npm/**",

    # IDEs and Editors
    "**/.idea/**",
    "**/.vscode/**",
    "**/.vs/**",
    "**/*.swp",
    "**/*.swo",
    "**/*~",

    # Build and Distribution
    "**/build/**",
    "**/dist/**",
    "**/*.egg-info/**",

    # Logs and Databases
    "**/*.log",
    "**/*.sqlite",
    "**/*.db",

    # OS Files
    "**/.DS_Store",
    "**/Thumbs.db",

    # Large Media Files
    "**/*.mp4",
    "**/*.mov",
    "**/*.avi",
    "**/*.wmv",
    "**/*.flv",
    "**/*.mp3",
    "**/*.wav",
    "**/*.zip",
    "**/*.tar",
    "**/*.gz",
    "**/*.rar",

    # Documentation Build
    "**/docs/_build/**",
    "**/site/**",

    # Temporary Files
    "**/tmp/**",
    "**/temp/**",
}
