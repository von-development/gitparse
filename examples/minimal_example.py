"""Minimal example using only core classes and method chaining."""

import asyncio
from gitparse import GitRepo, AsyncGitRepo, ExtractionConfig


def print_section(title: str) -> None:
    """Print a section title."""
    print(f"\n{'='*20} {title} {'='*20}")


def run_sync_example() -> None:
    """Run synchronous example with method chaining."""
    print_section("Synchronous API")

    # Initialize repo with config
    repo = GitRepo(
        "https://github.com/von-development/gitparse",
        ExtractionConfig(
            max_file_size=1024 * 1024,  # 1MB
            exclude_patterns=["*.pyc"],
            include_patterns=["*.py", "*.md"],
        ),
    )

    # Get repository info
    info = repo.get_repository_info()
    print(f"\nRepository: {info['name']}")
    print(f"Default Branch: {info.get('default_branch')}")
    print(f"Head Commit: {info.get('head_commit')}")

    # Get and print file tree
    print("\nFile Tree:")
    for line in repo.get_file_tree(style="markdown"):
        print(line)

    # Get and print dependencies
    deps = repo.get_dependencies()
    if deps["pyproject.toml"]:
        print("\nPython Dependencies:")
        for name, version in deps["pyproject.toml"]["dependencies"].items():
            print(f"- {name}: {version}")

    # Get and print language stats
    stats = repo.get_language_stats()
    print("\nLanguage Statistics:")
    for lang, data in stats.items():
        print(f"- {lang}: {data['percentage']}% ({data['files']} files)")

    # Get README content
    readme = repo.get_readme_content()
    if readme:
        print("\nREADME Preview (first 3 lines):")
        print("\n".join(readme.splitlines()[:3]))

    # Get gitparse directory contents
    contents = repo.get_directory_contents("gitparse")
    print(f"\nGitparse Directory: {len(contents)} files")


async def run_async_example() -> None:
    """Run asynchronous example with method chaining."""
    print_section("Asynchronous API")

    # Initialize repo with config
    config = ExtractionConfig(
        max_file_size=1024 * 1024,
        exclude_patterns=["*.pyc"],
        include_patterns=["*.py", "*.md"],
    )

    async with AsyncGitRepo("https://github.com/von-development/gitparse", config) as repo:
        # Get repository info and file tree concurrently
        info, tree = await asyncio.gather(
            repo.get_repository_info(),
            repo.get_file_tree(style="markdown"),
        )

        print(f"\nRepository: {info['name']}")
        print(f"Default Branch: {info.get('default_branch')}")
        print(f"Head Commit: {info.get('head_commit')}")

        print("\nFile Tree:")
        for line in tree:
            print(line)

        # Get dependencies and language stats concurrently
        deps, stats = await asyncio.gather(
            repo.get_dependencies(),
            repo.get_language_stats(),
        )

        if deps["pyproject.toml"]:
            print("\nPython Dependencies:")
            for name, version in deps["pyproject.toml"]["dependencies"].items():
                print(f"- {name}: {version}")

        print("\nLanguage Statistics:")
        for lang, data in stats.items():
            print(f"- {lang}: {data['percentage']}% ({data['files']} files)")

        # Get README and directory contents concurrently
        readme, contents = await asyncio.gather(
            repo.get_readme_content(),
            repo.get_directory_contents("gitparse"),
        )

        if readme:
            print("\nREADME Preview (first 3 lines):")
            print("\n".join(readme.splitlines()[:3]))

        print(f"\nGitparse Directory: {len(contents)} files")


async def main() -> None:
    """Run both sync and async examples."""
    # Run sync example
    run_sync_example()

    # Run async example
    await run_async_example()


if __name__ == "__main__":
    asyncio.run(main()) 