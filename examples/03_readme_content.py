"""
Example showing how to get repository README content using GitParse.
Demonstrates both synchronous and asynchronous usage.
"""
import asyncio

from gitparse import GitRepo
from gitparse.core.async_repo import AsyncGitRepo

# Example repository URLs
LOCAL_REPO = "."
REMOTE_REPO = "https://github.com/pallets/flask"

def sync_example():
    """Synchronous example of getting README content."""
    print("\n=== Synchronous README Example ===")

    # Local repository
    local_repo = GitRepo(LOCAL_REPO)
    local_readme = local_repo.get_readme()
    print("\nLocal Repository README:")
    print(local_readme[:500] + "..." if local_readme else "No README found")

    # Remote repository
    remote_repo = GitRepo(REMOTE_REPO)
    remote_readme = remote_repo.get_readme()
    print("\nRemote Repository README:")
    print(remote_readme[:500] + "..." if remote_readme else "No README found")

async def async_example():
    """Asynchronous example of getting README content."""
    print("\n=== Asynchronous README Example ===")

    async with AsyncGitRepo(LOCAL_REPO) as local_repo, \
             AsyncGitRepo(REMOTE_REPO) as remote_repo:

        # Gather results concurrently
        local_readme, remote_readme = await asyncio.gather(
            local_repo.get_readme(),
            remote_repo.get_readme()
        )

        print("\nLocal Repository README:")
        print(local_readme[:500] + "..." if local_readme else "No README found")
        print("\nRemote Repository README:")
        print(remote_readme[:500] + "..." if remote_readme else "No README found")

if __name__ == "__main__":
    # Run synchronous example
    sync_example()

    # Run async example
    asyncio.run(async_example())
