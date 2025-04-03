# GitParse

A modern Python library for Git repository analysis with async support and type safety.

## Features

- Repository metadata extraction
- File tree analysis with multiple formats
- Dependency parsing (Poetry, requirements.txt, package.json)
- Language statistics and file type detection
- Async support with context managers
- Type-safe API with clear error handling

## Installation

```bash
pip install gitparse
```

## Basic Usage

### Synchronous API

```python
from gitparse import GitRepo, ExtractionConfig

# Configure analysis
config = ExtractionConfig(
    max_file_size=1024 * 1024,  # 1MB
    exclude_patterns=["*.pyc"],
    include_patterns=["*.py", "*.md"],
)

# Initialize and analyze repository
repo = GitRepo("https://github.com/username/repo", config)

# Repository metadata
info = repo.get_repository_info()
# Returns: {"name": "repo", "default_branch": "main", "head_commit": "abc123..."}

# File tree (markdown format)
tree = repo.get_file_tree(style="markdown")
# Returns: ["- README.md", "  - src/", "    - main.py", ...]

# Dependencies
deps = repo.get_dependencies()
# Returns: {
#     "pyproject.toml": {"dependencies": {"requests": "^2.0.0"}},
#     "requirements.txt": [{"name": "flask", "version": "2.0.0"}]
# }

# Language statistics
stats = repo.get_language_stats()
# Returns: {
#     "Python": {"files": 10, "bytes": 1500, "percentage": 75.5},
#     "Markdown": {"files": 2, "bytes": 500, "percentage": 24.5}
# }
```

### Asynchronous API

```python
import asyncio
from gitparse import AsyncGitRepo, ExtractionConfig

async def analyze_repo():
    config = ExtractionConfig(max_file_size=1024 * 1024)
    
    async with AsyncGitRepo("https://github.com/username/repo", config) as repo:
        # Run operations concurrently
        info, tree, deps = await asyncio.gather(
            repo.get_repository_info(),
            repo.get_file_tree(style="markdown"),
            repo.get_dependencies()
        )
        return info, tree, deps

# Returns tuple of (repository_info, file_tree, dependencies)
results = asyncio.run(analyze_repo())
```

## Advanced Features

### File Analysis

```python
# Get specific file content
content = repo.get_file_content("README.md")
# Returns: "# Project Title\n..."

# Get all text files
contents = repo.get_all_contents(
    max_file_size=1024 * 1024,
    exclude_patterns=["*.pyc", "*.so"]
)
# Returns: {"README.md": "# Title...", "src/main.py": "def main():..."}

# Get directory tree
tree = repo.get_directory_tree(
    "src",
    style="structured"  # or "markdown", "flattened"
)
# Returns: {"src": {"main.py": None, "utils": {"helpers.py": None}}}
```

### Statistics

```python
# Repository statistics
stats = repo.get_statistics()
# Returns: {
#     "total_files": 100,
#     "binary_ratio": 0.05,
#     "avg_file_size": 1024,
#     "language_breakdown": {...}
# }

# Language breakdown
langs = repo.get_language_stats()
# Returns: {
#     "Python": {"files": 50, "percentage": 80.5},
#     "JavaScript": {"files": 10, "percentage": 19.5}
# }
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run ruff check .
```

## License

MIT License 