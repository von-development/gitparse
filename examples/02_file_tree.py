"""
Example showing how to get repository file tree using GitParse.
Demonstrates both synchronous and asynchronous usage with different output styles.
"""
import asyncio

from gitparse import GitRepo
from gitparse.core.async_repo import AsyncGitRepo

# Example repository URLs
LOCAL_REPO = "."
REMOTE_REPO = "https://github.com/pallets/flask"

def sync_example():
    """Synchronous example of getting file tree."""
    print("\n=== Synchronous File Tree Example ===")

    repo = GitRepo(REMOTE_REPO)

    # Get tree in different styles
    flat_tree = repo.get_file_tree(style="flattened")
    print("\nFlattened Tree:")
    print(flat_tree)

    markdown_tree = repo.get_file_tree(style="markdown")
    print("\nMarkdown Tree:")
    print(markdown_tree)

    structured_tree = repo.get_file_tree(style="structured")
    print("\nStructured Tree:")
    print(structured_tree)

async def async_example():
    """Asynchronous example of getting file tree."""
    print("\n=== Asynchronous File Tree Example ===")

    async with AsyncGitRepo(REMOTE_REPO) as repo:
        # Get all tree styles concurrently
        flat_tree, markdown_tree, structured_tree = await asyncio.gather(
            repo.get_file_tree(style="flattened"),
            repo.get_file_tree(style="markdown"),
            repo.get_file_tree(style="structured")
        )

        print("\nFlattened Tree:")
        print(flat_tree)
        print("\nMarkdown Tree:")
        print(markdown_tree)
        print("\nStructured Tree:")
        print(structured_tree)

if __name__ == "__main__":
    # Run synchronous example
    sync_example()

    # Run async example
    asyncio.run(async_example())
