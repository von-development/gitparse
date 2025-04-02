"""Command Line Interface for GitParse."""

import argparse
import json
from pathlib import Path
from typing import Optional, Union, Dict, Any
import sys
from colorama import init, Fore, Back, Style

from gitparse import GitRepo, ExtractionConfig

# Initialize colorama
init(autoreset=True)

def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} {text} {Style.RESET_ALL}\n")

def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Fore.CYAN}ℹ {text}{Style.RESET_ALL}")

def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def format_json(data: Dict[str, Any], indent: int = 2) -> str:
    """Format JSON with colors."""
    if isinstance(data, (dict, list)):
        formatted = json.dumps(data, indent=indent, ensure_ascii=False)
        # Add colors to keys
        formatted = formatted.replace('"', f'{Fore.YELLOW}"')
        return formatted
    return str(data)

def save_output(data: Any, output_file: Optional[str] = None, pretty: bool = True) -> None:
    """Save or print data in a readable format."""
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open('w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f)
        print_success(f"Results saved to {output_file}")
    else:
        if pretty:
            print(format_json(data) if isinstance(data, (dict, list)) else f"{Fore.WHITE}{data}")
        else:
            print(data)

def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="GitParse - Extract and analyze Git repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global arguments
    parser.add_argument(
        "repo",
        help=f"{Fore.GREEN}Local path or GitHub URL of the repository{Style.RESET_ALL}"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: print to console)",
        default=None
    )
    parser.add_argument(
        "--no-pretty",
        help="Disable pretty printing",
        action="store_true"
    )
    
    # Create subparsers for each command
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # info command
    info_parser = subparsers.add_parser("info", help=f"{Fore.YELLOW}Get repository information{Style.RESET_ALL}")
    
    # tree command
    tree_parser = subparsers.add_parser("tree", help=f"{Fore.YELLOW}Get repository file tree{Style.RESET_ALL}")
    tree_parser.add_argument(
        "--style",
        choices=["flattened", "markdown", "structured"],
        default="flattened",
        help="Output style (default: flattened)"
    )
    
    # Directory tree command
    dir_tree_parser = subparsers.add_parser("dir-tree", help="Get directory file tree")
    dir_tree_parser.add_argument("directory", help="Directory path relative to repository root")
    dir_tree_parser.add_argument(
        "--style",
        choices=["flattened", "markdown", "structured"],
        default="flattened",
        help="Output style"
    )
    
    # Directory contents command
    dir_contents_parser = subparsers.add_parser("dir-contents", help="Get directory contents")
    dir_contents_parser.add_argument("directory", help="Directory path relative to repository root")
    
    # readme command
    subparsers.add_parser("readme", help=f"{Fore.YELLOW}Get repository README content{Style.RESET_ALL}")
    
    # deps command
    subparsers.add_parser("deps", help=f"{Fore.YELLOW}Get repository dependencies{Style.RESET_ALL}")
    
    # langs command
    subparsers.add_parser("langs", help=f"{Fore.YELLOW}Get language statistics{Style.RESET_ALL}")
    
    # stats command
    subparsers.add_parser("stats", help=f"{Fore.YELLOW}Get repository statistics{Style.RESET_ALL}")
    
    # content command
    content_parser = subparsers.add_parser("content", help=f"{Fore.YELLOW}Get file content{Style.RESET_ALL}")
    content_parser.add_argument(
        "file_path",
        help="Path to file relative to repository root"
    )
    
    # all-contents command
    all_contents_parser = subparsers.add_parser("all-contents", help=f"{Fore.YELLOW}Get all file contents{Style.RESET_ALL}")
    all_contents_parser.add_argument(
        "--max-size",
        type=int,
        default=1_000_000,
        help="Maximum file size in bytes (default: 1MB)"
    )
    
    return parser

def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Initialize repository
        print_header(f"Analyzing repository: {args.repo}")
        repo = GitRepo(args.repo)
        
        # Execute requested command
        print_info(f"Executing command: {args.command}")
        
        if args.command == "info":
            result = repo.get_repository_info()
        
        elif args.command == "tree":
            result = repo.get_file_tree(style=args.style)
        
        elif args.command == "dir-tree":
            result = repo.get_directory_tree(args.directory, style=args.style)
        
        elif args.command == "dir-contents":
            result = repo.get_directory_contents(args.directory)
        
        elif args.command == "readme":
            result = repo.get_readme()
            if result is None:
                print_error("No README found")
                sys.exit(0)
        
        elif args.command == "deps":
            result = repo.get_dependencies()
        
        elif args.command == "langs":
            result = repo.get_language_stats()
        
        elif args.command == "stats":
            result = repo.get_statistics()
        
        elif args.command == "content":
            result = repo.get_file_content(args.file_path)
            if result is None:
                print_error(f"Could not read file: {args.file_path}")
                sys.exit(1)
        
        elif args.command == "all-contents":
            result = repo.get_all_contents()
        
        # Save or print results
        save_output(result, args.output, not args.no_pretty)
        print_success("Analysis completed successfully!")
        
    except Exception as e:
        print_error(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main() 