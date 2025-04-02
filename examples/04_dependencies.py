"""
Example showing how to get repository dependencies using GitParse.
Demonstrates both synchronous and asynchronous usage.
"""

import asyncio

from gitparse import GitRepo
from gitparse.core.async_repo import AsyncGitRepo

# Example repository URLs
LOCAL_REPO = "."
REMOTE_REPO = "https://github.com/pallets/flask"


def sync_example():
    """Synchronous example of getting dependencies."""
    print("\n=== Synchronous Dependencies Example ===")

    # Local repository
    local_repo = GitRepo(LOCAL_REPO)
    local_deps = local_repo.get_dependencies()
    print("\nLocal Repository Dependencies:")
    print(local_deps)

    # Remote repository
    remote_repo = GitRepo(REMOTE_REPO)
    remote_deps = remote_repo.get_dependencies()
    print("\nRemote Repository Dependencies:")
    print(remote_deps)


async def async_example():
    """Asynchronous example of getting dependencies."""
    print("\n=== Asynchronous Dependencies Example ===")

    async with AsyncGitRepo(LOCAL_REPO) as local_repo, AsyncGitRepo(REMOTE_REPO) as remote_repo:

        # Gather results concurrently
        local_deps, remote_deps = await asyncio.gather(
            local_repo.get_dependencies(), remote_repo.get_dependencies()
        )

        print("\nLocal Repository Dependencies:")
        print(local_deps)
        print("\nRemote Repository Dependencies:")
        print(remote_deps)


if __name__ == "__main__":
    # Run synchronous example
    sync_example()

    # Run async example
    asyncio.run(async_example())
