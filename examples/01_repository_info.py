"""
Example showing how to get repository information using GitParse.
Demonstrates both synchronous and asynchronous usage.
"""
import asyncio
from gitparse import GitRepo
from gitparse.core.async_repo import AsyncGitRepo

# Example repository URLs
LOCAL_REPO = "."
REMOTE_REPO = "https://github.com/pallets/flask"

def sync_example():
    """Synchronous example of getting repository info."""
    print("\n=== Synchronous Repository Info Example ===")
    
    # Local repository
    local_repo = GitRepo(LOCAL_REPO)
    local_info = local_repo.get_repository_info()
    print("\nLocal Repository Info:")
    print(local_info)
    
    # Remote repository
    remote_repo = GitRepo(REMOTE_REPO)
    remote_info = remote_repo.get_repository_info()
    print("\nRemote Repository Info:")
    print(remote_info)

async def async_example():
    """Asynchronous example of getting repository info."""
    print("\n=== Asynchronous Repository Info Example ===")
    
    # Create async repositories
    async with AsyncGitRepo(LOCAL_REPO) as local_repo, \
             AsyncGitRepo(REMOTE_REPO) as remote_repo:
        
        # Gather results concurrently
        local_info, remote_info = await asyncio.gather(
            local_repo.get_repository_info(),
            remote_repo.get_repository_info()
        )
        
        print("\nLocal Repository Info:")
        print(local_info)
        print("\nRemote Repository Info:")
        print(remote_info)

if __name__ == "__main__":
    # Run synchronous example
    sync_example()
    
    # Run async example
    asyncio.run(async_example()) 