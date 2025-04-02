"""
Example showing how to get file content from repositories using GitParse.
Demonstrates both synchronous and asynchronous usage.
"""

import asyncio

from gitparse import GitRepo
from gitparse.core.async_repo import AsyncGitRepo

# Example repository URLs and files
LOCAL_REPO = "."
LOCAL_FILE = "README.md"
REMOTE_REPO = "https://github.com/pallets/flask"
REMOTE_FILE = "setup.py"


def sync_example():
    """Synchronous example of getting file content."""
    print("\n=== Synchronous File Content Example ===")

    # Local repository file
    local_repo = GitRepo(LOCAL_REPO)
    local_content = local_repo.get_file_content(LOCAL_FILE)
    print(f"\nLocal Repository File ({LOCAL_FILE}):")
    print(local_content[:500] + "..." if local_content else "File not found")

    # Remote repository file
    remote_repo = GitRepo(REMOTE_REPO)
    remote_content = remote_repo.get_file_content(REMOTE_FILE)
    print(f"\nRemote Repository File ({REMOTE_FILE}):")
    print(remote_content[:500] + "..." if remote_content else "File not found")


async def async_example():
    """Asynchronous example of getting file content."""
    print("\n=== Asynchronous File Content Example ===")

    async with AsyncGitRepo(LOCAL_REPO) as local_repo, AsyncGitRepo(REMOTE_REPO) as remote_repo:

        # Gather results concurrently
        local_content, remote_content = await asyncio.gather(
            local_repo.get_file_content(LOCAL_FILE), remote_repo.get_file_content(REMOTE_FILE)
        )

        print(f"\nLocal Repository File ({LOCAL_FILE}):")
        print(local_content[:500] + "..." if local_content else "File not found")
        print(f"\nRemote Repository File ({REMOTE_FILE}):")
        print(remote_content[:500] + "..." if remote_content else "File not found")


if __name__ == "__main__":
    # Run synchronous example
    sync_example()

    # Run async example
    asyncio.run(async_example())
