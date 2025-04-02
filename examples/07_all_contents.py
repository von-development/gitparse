"""
Example showing how to get all file contents from repositories using GitParse.
Demonstrates both synchronous and asynchronous usage with size limits.
"""
import asyncio
from gitparse import GitRepo
from gitparse.core.async_repo import AsyncGitRepo

# Example repository URLs
LOCAL_REPO = "."
REMOTE_REPO = "https://github.com/pallets/flask"

# Size limits for demonstration
SMALL_LIMIT = 100_000  # 100KB
LARGE_LIMIT = 1_000_000  # 1MB

def sync_example():
    """Synchronous example of getting all file contents."""
    print("\n=== Synchronous All Contents Example ===")
    
    repo = GitRepo(LOCAL_REPO)
    
    # Get contents with different size limits
    print("\nGetting files up to 100KB:")
    small_files = repo.get_all_contents(max_file_size=SMALL_LIMIT)
    print(f"Found {len(small_files)} files")
    
    print("\nGetting files up to 1MB:")
    large_files = repo.get_all_contents(max_file_size=LARGE_LIMIT)
    print(f"Found {len(large_files)} files")
    
    # Print first few files
    print("\nSample of files found:")
    for path, content in list(large_files.items())[:3]:
        print(f"\n{path}:")
        print(content[:200] + "..." if content else "Empty file")

async def async_example():
    """Asynchronous example of getting all file contents."""
    print("\n=== Asynchronous All Contents Example ===")
    
    async with AsyncGitRepo(LOCAL_REPO) as repo:
        # Get contents with different size limits concurrently
        small_files, large_files = await asyncio.gather(
            repo.get_all_contents(max_file_size=SMALL_LIMIT),
            repo.get_all_contents(max_file_size=LARGE_LIMIT)
        )
        
        print("\nFiles up to 100KB:", len(small_files))
        print("Files up to 1MB:", len(large_files))
        
        # Print first few files from large files collection
        print("\nSample of files found (from 1MB limit):")
        for path, content in list(large_files.items())[:3]:
            print(f"\n{path}:")
            print(content[:200] + "..." if content else "Empty file")

if __name__ == "__main__":
    # Run synchronous example
    sync_example()
    
    # Run async example
    asyncio.run(async_example()) 