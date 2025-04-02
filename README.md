# GitParse

A typed, modular Python library for structured repository parsing. GitParse allows you to extract metadata and content from Git repositories in a structured way.

## ✅ Features

### 📂 File System Analysis
- Complete file tree traversal with multiple output formats (flattened, markdown, structured)
- Directory-specific operations (tree and contents)
- Pattern-based file filtering (include/exclude patterns)
- File size limits and binary detection
- Configurable output formats

### 📦 Dependency Analysis
- Python requirements.txt parsing
- Poetry (pyproject.toml) dependency extraction
- Node.js package.json parsing
- Support for both main and dev dependencies

### 🔍 Repository Information
- Basic repository metadata
- Git information (when available)
- README content extraction
- Multiple README format support (md, rst)

### 📊 Language Statistics
- File extension analysis
- Content-based language detection
- Size and count statistics
- Binary vs text ratio

## Installation

```bash
pip install gitparse
```

Or with Poetry:

```bash
poetry add gitparse
```

## Usage Examples

### Basic Repository Analysis

```python
from gitparse import GitRepo, ExtractionConfig

# Initialize with configuration
config = ExtractionConfig(
    max_file_size=5_000_000,  # 5MB
    exclude_patterns=["*.pyc", "__pycache__/*"],
    include_patterns=["*.py", "*.md"]
)

# Create repository object
repo = GitRepo("path/to/repo", config=config)

# Get repository information
info = repo.get_repository_info()
print(f"Repository: {info['name']}")

# Get file tree (multiple formats available)
files = repo.get_file_tree(style="markdown")
print("\n".join(files))
```

### Directory-Specific Operations

```python
from gitparse import GitRepo

# Initialize repository
repo = GitRepo("https://github.com/username/repo")

# Get tree for specific directory
tree = repo.get_directory_tree("src/components", style="markdown")
print("\n".join(tree))

# Get contents of specific directory
contents = repo.get_directory_contents("src/components")
for path, content in contents.items():
    print(f"File: {path}, Size: {len(content)} bytes")
```

### Async Support

```python
import asyncio
from gitparse.core.async_repo import AsyncGitRepo

async def analyze_repo():
    async with AsyncGitRepo("https://github.com/username/repo") as repo:
        # Get directory tree and contents concurrently
        tree, contents = await asyncio.gather(
            repo.get_directory_tree("src/components"),
            repo.get_directory_contents("src/components")
        )
        return tree, contents

# Run async code
tree, contents = asyncio.run(analyze_repo())
```

### Command Line Interface

```bash
# Get repository information
gitparse https://github.com/username/repo info

# Get file tree in markdown format
gitparse https://github.com/username/repo tree --style markdown

# Get specific directory tree
gitparse https://github.com/username/repo dir-tree src/components

# Get specific directory contents
gitparse https://github.com/username/repo dir-contents src/components

# Get language statistics
gitparse https://github.com/username/repo langs

# Get file content
gitparse https://github.com/username/repo content README.md
```

## Configuration

The `ExtractionConfig` class supports:

```python
config = ExtractionConfig(
    max_file_size=10_000_000,  # 10MB
    exclude_patterns=["*.pyc", "__pycache__/*", "*.egg-info/*"],
    include_patterns=["*.py", "*.md", "*.txt"],
    output_style="flattened",  # or "markdown" or "structured"
    temp_dir=None  # Optional custom temp directory
)
```

## Development

1. Clone the repository
2. Install dependencies: `poetry install`
3. Run tests: `poetry run pytest`
4. Try examples: `cd examples && python 01_basic_usage.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License 