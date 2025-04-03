"""Full example demonstrating all GitParse functionality."""

import asyncio
from pathlib import Path

from gitparse import (
    # Core classes
    RepositoryAnalyzer,
    AsyncRepositoryAnalyzer,
    ExtractionConfig,
    # Sync functions
    get_repository_info,
    get_file_tree,
    get_readme_content,
    get_dependencies,
    get_language_stats,
    get_statistics,
    get_file_content,
    get_all_contents,
    get_directory_tree,
    get_directory_contents,
    # Async functions
    async_get_repository_info,
    async_get_file_tree,
    async_get_readme_content,
    async_get_dependencies,
    async_get_language_stats,
    async_get_statistics,
    async_get_file_content,
    async_get_all_contents,
    async_get_directory_tree,
    async_get_directory_contents,
)

# Use a small GitHub repository for testing
REPO_URL = "https://github.com/von-development/gitparse"


def test_sync_class_api():
    """Test synchronous class-based API."""
    print("\n=== Testing Synchronous Class API ===")
    
    # Initialize with config
    config = ExtractionConfig(
        max_file_size=1024 * 1024,  # 1MB
        exclude_patterns=["*.pyc", "__pycache__/*"],
        include_patterns=["*.py", "*.md"],
    )
    
    repo = RepositoryAnalyzer(REPO_URL, config)
    
    # Test all methods
    print("\nRepository Info:", repo.get_repository_info())
    print("\nFile Tree:", repo.get_file_tree(style="markdown"))
    print("\nREADME:", repo.get_readme_content())
    print("\nDependencies:", repo.get_dependencies())
    print("\nLanguage Stats:", repo.get_language_stats())
    print("\nStatistics:", repo.get_statistics())
    print("\nFile Content:", repo.get_file_content("README.md"))
    print("\nAll Contents:", len(repo.get_all_contents()), "files")
    print("\nDirectory Tree:", repo.get_directory_tree("gitparse"))
    print("\nDirectory Contents:", len(repo.get_directory_contents("gitparse")), "files")


async def test_async_class_api():
    """Test asynchronous class-based API."""
    print("\n=== Testing Asynchronous Class API ===")
    
    config = ExtractionConfig(
        max_file_size=1024 * 1024,
        exclude_patterns=["*.pyc", "__pycache__/*"],
        include_patterns=["*.py", "*.md"],
    )
    
    async with AsyncRepositoryAnalyzer(REPO_URL, config) as repo:
        # Test all methods
        print("\nRepository Info:", await repo.get_repository_info())
        print("\nFile Tree:", await repo.get_file_tree(style="markdown"))
        print("\nREADME:", await repo.get_readme_content())
        print("\nDependencies:", await repo.get_dependencies())
        print("\nLanguage Stats:", await repo.get_language_stats())
        print("\nStatistics:", await repo.get_statistics())
        print("\nFile Content:", await repo.get_file_content("README.md"))
        print("\nAll Contents:", len(await repo.get_all_contents()), "files")
        print("\nDirectory Tree:", await repo.get_directory_tree("gitparse"))
        print("\nDirectory Contents:", len(await repo.get_directory_contents("gitparse")), "files")


def test_sync_functional_api():
    """Test synchronous functional API."""
    print("\n=== Testing Synchronous Functional API ===")
    
    config = ExtractionConfig(
        max_file_size=1024 * 1024,
        exclude_patterns=["*.pyc", "__pycache__/*"],
        include_patterns=["*.py", "*.md"],
    )
    
    # Test all functions
    print("\nRepository Info:", get_repository_info(REPO_URL, config))
    print("\nFile Tree:", get_file_tree(REPO_URL, style="markdown", config=config))
    print("\nREADME:", get_readme_content(REPO_URL, config))
    print("\nDependencies:", get_dependencies(REPO_URL, config))
    print("\nLanguage Stats:", get_language_stats(REPO_URL, config))
    print("\nStatistics:", get_statistics(REPO_URL, config))
    print("\nFile Content:", get_file_content(REPO_URL, "README.md", config))
    print("\nAll Contents:", len(get_all_contents(REPO_URL, config)), "files")
    print("\nDirectory Tree:", get_directory_tree(REPO_URL, "gitparse", config=config))
    print("\nDirectory Contents:", len(get_directory_contents(REPO_URL, "gitparse", config)), "files")


async def test_async_functional_api():
    """Test asynchronous functional API."""
    print("\n=== Testing Asynchronous Functional API ===")
    
    config = ExtractionConfig(
        max_file_size=1024 * 1024,
        exclude_patterns=["*.pyc", "__pycache__/*"],
        include_patterns=["*.py", "*.md"],
    )
    
    # Test all functions
    print("\nRepository Info:", await async_get_repository_info(REPO_URL, config))
    print("\nFile Tree:", await async_get_file_tree(REPO_URL, style="markdown", config=config))
    print("\nREADME:", await async_get_readme_content(REPO_URL, config))
    print("\nDependencies:", await async_get_dependencies(REPO_URL, config))
    print("\nLanguage Stats:", await async_get_language_stats(REPO_URL, config))
    print("\nStatistics:", await async_get_statistics(REPO_URL, config))
    print("\nFile Content:", await async_get_file_content(REPO_URL, "README.md", config))
    print("\nAll Contents:", len(await async_get_all_contents(REPO_URL, config)), "files")
    print("\nDirectory Tree:", await async_get_directory_tree(REPO_URL, "gitparse", config=config))
    print("\nDirectory Contents:", len(await async_get_directory_contents(REPO_URL, "gitparse", config)), "files")


async def main():
    """Run all tests."""
    # Test class-based APIs
    test_sync_class_api()
    await test_async_class_api()
    
    # Test functional APIs
    test_sync_functional_api()
    await test_async_functional_api()


if __name__ == "__main__":
    asyncio.run(main()) 