"""
Example showing how to get repository language statistics using GitParse.
Demonstrates both synchronous and asynchronous usage.
"""
import asyncio

from gitparse import GitRepo
from gitparse.core.async_repo import AsyncGitRepo

# Example repository URLs
LOCAL_REPO = "."
REMOTE_REPO = "https://github.com/pallets/flask"

def sync_example():
    """Synchronous example of getting language statistics."""
    print("\n=== Synchronous Language Statistics Example ===")

    # Local repository
    local_repo = GitRepo(LOCAL_REPO)
    local_stats = local_repo.get_language_stats()
    print("\nLocal Repository Language Stats:")
    print(local_stats)

    # Remote repository
    remote_repo = GitRepo(REMOTE_REPO)
    remote_stats = remote_repo.get_language_stats()
    print("\nRemote Repository Language Stats:")
    print(remote_stats)

async def async_example():
    """Asynchronous example of getting language statistics."""
    print("\n=== Asynchronous Language Statistics Example ===")

    async with AsyncGitRepo(LOCAL_REPO) as local_repo, \
             AsyncGitRepo(REMOTE_REPO) as remote_repo:

        # Gather results concurrently
        local_stats, remote_stats = await asyncio.gather(
            local_repo.get_language_stats(),
            remote_repo.get_language_stats()
        )

        print("\nLocal Repository Language Stats:")
        print(local_stats)
        print("\nRemote Repository Language Stats:")
        print(remote_stats)

if __name__ == "__main__":
    # Run synchronous example
    sync_example()

    # Run async example
    asyncio.run(async_example())
