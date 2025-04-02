"""File type mappings and common extensions."""

MIME_TO_LANGUAGE = {
    # Programming Languages
    'text/x-python': 'Python',
    'text/x-python3': 'Python',
    'text/javascript': 'JavaScript',
    'application/javascript': 'JavaScript',
    'text/typescript': 'TypeScript',
    'text/x-java': 'Java',
    'text/x-c': 'C',
    'text/x-c++': 'C++',
    'text/x-csharp': 'C#',
    'text/x-go': 'Go',
    'text/x-ruby': 'Ruby',
    'text/x-php': 'PHP',
    'text/x-rust': 'Rust',
    'text/x-swift': 'Swift',
    'text/x-kotlin': 'Kotlin',
    'text/x-scala': 'Scala',

    # Web Technologies
    'text/html': 'HTML',
    'text/css': 'CSS',
    'application/json': 'JSON',
    'application/x-yaml': 'YAML',
    'text/xml': 'XML',
    'application/xml': 'XML',

    # Documentation
    'text/markdown': 'Markdown',
    'text/x-rst': 'reStructuredText',
    'text/asciidoc': 'AsciiDoc',
    'text/plain': 'Plain Text',

    # Configuration
    'text/x-toml': 'TOML',
    'text/x-ini': 'INI',
    'text/x-properties': 'Properties',

    # Shell Scripts
    'text/x-shellscript': 'Shell',
    'text/x-bash': 'Bash',
    'text/x-powershell': 'PowerShell',

    # Other
    'text/x-makefile': 'Makefile',
    'text/x-dockerfile': 'Dockerfile',
    'text/x-cmake': 'CMake',
}

COMMON_EXTENSIONS = {
    # Programming Languages
    '.py': 'Python',
    '.pyi': 'Python',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.java': 'Java',
    '.c': 'C',
    '.h': 'C',
    '.cpp': 'C++',
    '.hpp': 'C++',
    '.cs': 'C#',
    '.go': 'Go',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.rs': 'Rust',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',

    # Web Technologies
    '.html': 'HTML',
    '.htm': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'SASS',
    '.less': 'Less',
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.xml': 'XML',
    '.svg': 'SVG',

    # Documentation
    '.md': 'Markdown',
    '.markdown': 'Markdown',
    '.rst': 'reStructuredText',
    '.adoc': 'AsciiDoc',
    '.txt': 'Plain Text',

    # Configuration
    '.toml': 'TOML',
    '.ini': 'INI',
    '.cfg': 'INI',
    '.conf': 'INI',
    '.properties': 'Properties',

    # Shell Scripts
    '.sh': 'Shell',
    '.bash': 'Bash',
    '.zsh': 'Shell',
    '.fish': 'Shell',
    '.ps1': 'PowerShell',
    '.psm1': 'PowerShell',
    '.psd1': 'PowerShell',

    # Build and Config
    'Makefile': 'Makefile',
    'Dockerfile': 'Dockerfile',
    'CMakeLists.txt': 'CMake',
    '.cmake': 'CMake',
}
