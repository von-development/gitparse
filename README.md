# GitParse

A Python library for extracting and analyzing Git repository content with type safety.

## Installation

```bash
pip install gitparse
```

## Quick Start

```python
from gitparse import GitRepo

# Local repository
repo = GitRepo("path/to/repo")

# Remote repository
repo = GitRepo("https://github.com/username/repo")
```

## Features & Examples

### Repository Info

```python
repo = GitRepo("path/to/repo")
info = repo.get_repository_info()

print(f"Name: {info['name']}")
print(f"Default Branch: {info.get('default_branch')}")
print(f"Head Commit: {info.get('head_commit')}")
```

### File Tree

```python
# Get file tree in different formats
markdown_tree = repo.get_file_tree(style="markdown")
dict_tree = repo.get_file_tree(style="dict")
flat_tree = repo.get_file_tree(style="flattened")

# Print markdown tree
print("\n".join(markdown_tree))
```

### Dependencies

```python
deps = repo.get_dependencies()

# Python dependencies from pyproject.toml
if "pyproject.toml" in deps:
    python_deps = deps["pyproject.toml"]
    print("\nPython Dependencies:")
    for name, version in python_deps["dependencies"].items():
        print(f"- {name}: {version}")

# Node.js dependencies from package.json
if "package.json" in deps:
    node_deps = deps["package.json"]
    print("\nNode.js Dependencies:")
    for name, version in node_deps["dependencies"].items():
        print(f"- {name}: {version}")
```

### Async Support

```python
import asyncio
from gitparse import AsyncGitRepo

async def main():
    async with AsyncGitRepo("path/to/repo") as repo:
        # Get multiple pieces of info concurrently
        info, tree = await asyncio.gather(
            repo.get_repository_info(),
            repo.get_file_tree(style="markdown")
        )
        return info, tree

# Run async code
info, tree = asyncio.run(main())
```

### CLI Usage

```bash
# Get basic info
gitparse path/to/repo info

# Get file tree
gitparse path/to/repo tree --style markdown

# Get dependencies
gitparse path/to/repo deps

# Get specific file content
gitparse path/to/repo content README.md
```

### Configuration

```python
from gitparse import GitRepo, ExtractionConfig

config = ExtractionConfig(
    max_file_size=5_000_000,  # 5MB limit
    exclude_patterns=["*.pyc", "__pycache__/*"],
    include_patterns=["*.py", "*.md"]
)

repo = GitRepo("path/to/repo", config=config)
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