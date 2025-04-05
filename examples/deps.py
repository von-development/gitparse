"""Examples demonstrating GitParse dependency parsing functionality."""

import asyncio
from pprint import pprint

from gitparse import (
    AsyncRepositoryAnalyzer,
    ExtractionConfig,
    RepositoryAnalyzer,
    async_get_dependencies,
    get_dependencies,
)

# Test repositories with different dependency files
REPOS = {
    "Flask": "https://github.com/pallets/flask",  # requirements.txt
    "Poetry": "https://github.com/python-poetry/poetry",  # pyproject.toml
    "Express": "https://github.com/expressjs/express",  # package.json
}


def test_sync_dependencies():
    """Test synchronous dependency parsing."""
    print("\n=== Testing Synchronous Dependency Parsing ===")
    
    config = ExtractionConfig(
        max_file_size=1024 * 1024,  # 1MB
        include_patterns=[
            "requirements*.txt",
            "pyproject.toml",
            "package.json",
        ],
    )
    
    # Test class-based API
    print("\nUsing Class-based API:")
    for name, url in REPOS.items():
        print(f"\n{name} Dependencies:")
        repo = RepositoryAnalyzer(url, config)
        deps = repo.get_dependencies()
        pprint(deps)
    
    # Test functional API
    print("\nUsing Functional API:")
    for name, url in REPOS.items():
        print(f"\n{name} Dependencies:")
        deps = get_dependencies(url, config)
        pprint(deps)


async def test_async_dependencies():
    """Test asynchronous dependency parsing."""
    print("\n=== Testing Asynchronous Dependency Parsing ===")
    
    config = ExtractionConfig(
        max_file_size=1024 * 1024,
        include_patterns=[
            "requirements*.txt",
            "pyproject.toml",
            "package.json",
        ],
    )
    
    # Test class-based API
    print("\nUsing Async Class-based API:")
    for name, url in REPOS.items():
        print(f"\n{name} Dependencies:")
        async with AsyncRepositoryAnalyzer(url, config) as repo:
            deps = await repo.get_dependencies()
            pprint(deps)
    
    # Test functional API
    print("\nUsing Async Functional API:")
    for name, url in REPOS.items():
        print(f"\n{name} Dependencies:")
        deps = await async_get_dependencies(url, config)
        pprint(deps)


async def main():
    """Run all dependency parsing examples."""
    # Test synchronous APIs
    test_sync_dependencies()
    
    # Test asynchronous APIs
    await test_async_dependencies()


if __name__ == "__main__":
    asyncio.run(main()) 