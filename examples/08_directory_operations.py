"""
Example showing how to work with specific directories using GitParse.
Demonstrates both synchronous and asynchronous usage of directory operations.
"""
import asyncio

from gitparse import GitRepo
from gitparse.core.async_repo import AsyncGitRepo

# Example repository and directory
REPO_URL = "https://github.com/assafelovic/gpt-researcher"
TARGET_DIR = "multi_agents/agents"

def sync_example():
    """Synchronous example of directory operations."""
    print("\n=== Synchronous Directory Operations Example ===")

    # Initialize repository
    repo = GitRepo(REPO_URL)

    # Get directory tree
    print(f"\nGetting tree for directory: {TARGET_DIR}")
    tree = repo.get_directory_tree(TARGET_DIR, style="markdown")
    print("\n".join(tree))

    # Get directory contents
    print(f"\nGetting contents for directory: {TARGET_DIR}")
    contents = repo.get_directory_contents(TARGET_DIR)
    print(f"\nFound {len(contents)} files:")
    for path in contents:
        print(f"- {path}")

async def async_example():
    """Asynchronous example of directory operations."""
    print("\n=== Asynchronous Directory Operations Example ===")

    async with AsyncGitRepo(REPO_URL) as repo:
        # Get both tree and contents concurrently
        tree, contents = await asyncio.gather(
            repo.get_directory_tree(TARGET_DIR, style="markdown"),
            repo.get_directory_contents(TARGET_DIR)
        )

        print(f"\nDirectory Tree for {TARGET_DIR}:")
        print("\n".join(tree))

        print(f"\nFound {len(contents)} files:")
        for path in contents:
            print(f"- {path}")

def main():
    """Run both sync and async examples."""
    # Run synchronous example
    sync_example()

    # Run async example
    asyncio.run(async_example())

if __name__ == "__main__":
    main()
