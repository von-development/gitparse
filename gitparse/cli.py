"""Command line interface for GitParse."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

from colorama import Fore, Style, init
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from gitparse import GitRepo

# Initialize colorama for Windows support
init()

# Create rich console for fancy output
console = Console()


def format_error(msg: str) -> str:
    """Format error message with color."""
    return f"{Fore.RED}Error: {msg}{Style.RESET_ALL}"


def format_success(msg: str) -> str:
    """Format success message with color."""
    return f"{Fore.GREEN}{msg}{Style.RESET_ALL}"


def format_info(msg: str) -> str:
    """Format info message with color."""
    return f"{Fore.CYAN}{msg}{Style.RESET_ALL}"


def save_output(data: Any, output_file: Optional[str] = None, pretty: bool = True) -> None:
    """Save output to a file or print to console with proper formatting."""
    if output_file:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2 if pretty else None)
        console.print(f"[green]Output saved to {output_file}[/green]")
    else:
        if isinstance(data, (dict, list)):
            if pretty:
                console.print_json(data=data)
            else:
                print(json.dumps(data))
        elif isinstance(data, str) and data.startswith("```") and data.endswith("```"):
            # Handle markdown code blocks
            lang = data.split("\n")[0][3:].strip()
            code = "\n".join(data.split("\n")[1:-1])
            syntax = Syntax(code, lang, theme="monokai")
            console.print(syntax)
        else:
            print(data)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description=format_info("GitParse - Extract and analyze Git repositories")
    )

    parser.add_argument(
        "repo",
        help="Local path or GitHub URL of the repository",
        type=str,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: print to console)",
        type=str,
        metavar="OUTPUT",
    )

    parser.add_argument(
        "--no-pretty",
        help="Disable pretty printing",
        action="store_true",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Info command
    info_parser = subparsers.add_parser("info", help=format_info("Get repository information"))

    # Tree commands
    tree_parser = subparsers.add_parser("tree", help=format_info("Get repository file tree"))
    tree_parser.add_argument(
        "--style",
        choices=["flattened", "markdown", "dict"],
        default="markdown",
        help="Output style format",
    )

    dir_tree_parser = subparsers.add_parser("dir-tree", help=format_info("Get directory file tree"))
    dir_tree_parser.add_argument(
        "directory",
        help="Directory path within repository",
    )
    dir_tree_parser.add_argument(
        "--style",
        choices=["flattened", "markdown", "dict"],
        default="markdown",
        help="Output style format",
    )

    # Content commands
    dir_contents_parser = subparsers.add_parser(
        "dir-contents", help=format_info("Get directory contents")
    )
    dir_contents_parser.add_argument(
        "directory",
        help="Directory path within repository",
    )

    readme_parser = subparsers.add_parser(
        "readme", help=format_info("Get repository README content")
    )

    content_parser = subparsers.add_parser("content", help=format_info("Get file content"))
    content_parser.add_argument("path", help="Path to file within repository")

    all_contents_parser = subparsers.add_parser(
        "all-contents",
        help=format_info("Get all file contents"),
    )
    all_contents_parser.add_argument(
        "--max-size",
        type=int,
        help="Maximum file size in bytes",
    )
    all_contents_parser.add_argument(
        "--exclude",
        nargs="+",
        help="Glob patterns to exclude",
    )

    # Analysis commands
    deps_parser = subparsers.add_parser("deps", help=format_info("Get repository dependencies"))

    langs_parser = subparsers.add_parser(
        "langs",
        help=format_info("Get language statistics"),
    )

    stats_parser = subparsers.add_parser(
        "stats",
        help=format_info("Get repository statistics"),
    )

    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Create repository object
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]Initializing repository from {args.repo}...[/cyan]")
        try:
            repo = GitRepo(args.repo)
            progress.update(task, completed=True)
        except Exception as e:
            progress.update(task, completed=True)
            console.print(format_error(f"Failed to initialize repository: {e}"))
            sys.exit(1)

    # Execute command
    try:
        result: Union[Dict, str, None] = None

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]Executing {args.command} command...[/cyan]")

            if args.command == "info":
                result = repo.get_repository_info()
            elif args.command == "tree":
                result = repo.get_file_tree(style=args.style)
            elif args.command == "dir-tree":
                result = repo.get_directory_tree(directory=args.directory, style=args.style)
            elif args.command == "dir-contents":
                result = repo.get_directory_contents(directory=args.directory)
            elif args.command == "readme":
                result = repo.get_readme_content()
            elif args.command == "deps":
                result = repo.get_dependencies()
            elif args.command == "content":
                result = repo.get_file_content(args.path)
            elif args.command == "all-contents":
                result = repo.get_all_contents(
                    max_file_size=args.max_size if hasattr(args, "max_size") else None,
                    exclude_patterns=args.exclude if hasattr(args, "exclude") else None,
                )
            elif args.command == "langs":
                result = repo.get_language_stats()
            elif args.command == "stats":
                result = repo.get_repository_stats()

            progress.update(task, completed=True)

        if result is not None:
            save_output(result, args.output, not args.no_pretty)
            if not args.output:
                console.print(format_success("\nCommand completed successfully!"))

    except Exception as e:
        console.print(format_error(f"Error executing command: {e}"))
        sys.exit(1)


if __name__ == "__main__":
    main()
