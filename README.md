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

### Synchronous

```python
from gitparse import RepositoryAnalyzer, ExtractionConfig

# Configure analysis
config = ExtractionConfig(
    max_file_size=1024 * 1024,  # 1MB
    exclude_patterns=["*.pyc"],
    include_patterns=["*.py", "*.md"],
)

# Initialize and analyze repository
repo = RepositoryAnalyzer("https://github.com/username/repo", config)

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


## Command Line Interface

Also, GitParse comes with CLI for quick repository analysis. Use `--help` with any command to see its specific options:

```bash
# Get general help
gitparse --help

# Get help for specific commands
gitparse tree --help
gitparse content --help
gitparse all-contents --help

# Common operations
gitparse <repo_url> info
gitparse <repo_url> tree --style markdown
gitparse <repo_url> deps
gitparse <repo_url> langs
gitparse <repo_url> stats
gitparse <repo_url> readme
gitparse <repo_url> content path/to/file.py
gitparse <repo_url> dir-tree src --style markdown

# Advanced usage with filters
gitparse <repo_url> all-contents --max-size 1048576 --exclude "*.pyc" "*.so"

# Output options
gitparse <repo_url> langs -o language_stats.json  # Save to file
gitparse <repo_url> stats --no-pretty             # Disable pretty printing
```

### Available Commands

Each command supports `--help` for detailed usage information:

- `info`: Get repository information
- `tree`: Get repository file tree
  - See `tree --help` for style options
- `dir-tree`: Get directory file tree
  - See `dir-tree --help` for style options
- `dir-contents`: Get directory contents
- `readme`: Get repository README content
- `content`: Get specific file content
- `all-contents`: Get all file contents
  - See `all-contents --help` for filtering options
- `deps`: Get repository dependencies
- `langs`: Get language statistics
- `stats`: Get repository statistics

### Global Options

Use `gitparse --help` to see all available options:

- `-o, --output`: Save output to file
- `--no-pretty`: Disable pretty printing
- `-h, --help`: Show help message

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
