"""Command line interface for GitParse."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

from colorama import Fore, Style, init
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from gitparse.core.exceptions import GitParseError
from gitparse.core.repository_analyzer import RepositoryAnalyzer

# Initialize colorama for Windows support
init()

# Create rich console for fancy output
console = Console()

# Set up logging
logger = logging.getLogger(__name__)


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
    """Save output to a file or print to console with proper formatting.

    Args:
        data: The data to save or print
        output_file: Optional file path to save the output to
        pretty: Whether to use pretty formatting
    """
    if output_file:
        output_path = Path(output_file)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2 if pretty else None)
        console.print(f"[green]Output saved to {output_file}[/green]")
    elif isinstance(data, (dict, list)):
        if pretty:
            console.print_json(data=data)
        else:
            console.print(json.dumps(data))
    elif isinstance(data, str) and data.startswith("```") and data.endswith("```"):
        # Handle markdown code blocks
        lang = data.split("\n")[0][3:].strip()
        code = "\n".join(data.split("\n")[1:-1])
        syntax = Syntax(code, lang, theme="monokai")
        console.print(syntax)
    else:
        console.print(str(data))


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description=format_info("GitParse - Extract and analyze Git repositories"),
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
    subparsers.add_parser("info", help=format_info("Get repository information"))

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
        "dir-contents",
        help=format_info("Get directory contents"),
    )
    dir_contents_parser.add_argument(
        "directory",
        help="Directory path within repository",
    )

    subparsers.add_parser("readme", help=format_info("Get repository README content"))

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
    subparsers.add_parser("deps", help=format_info("Get repository dependencies"))
    subparsers.add_parser("langs", help=format_info("Get language statistics"))
    subparsers.add_parser("stats", help=format_info("Get repository statistics"))

    return parser


def get_command_handler(command: str) -> callable:
    """Get the appropriate command handler function.

    Args:
        command: The command to get a handler for

    Returns:
        A function that handles the specified command
    """
    handlers = {
        "info": lambda repo, _: repo.get_repository_info(),
        "tree": lambda repo, args: repo.get_file_tree(style=args.style),
        "dir-tree": lambda repo, args: repo.get_directory_tree(
            directory=args.directory,
            style=args.style,
        ),
        "dir-contents": lambda repo, args: repo.get_directory_contents(directory=args.directory),
        "readme": lambda repo, _: repo.get_readme_content(),
        "deps": lambda repo, _: repo.get_dependencies(),
        "content": lambda repo, args: repo.get_file_content(args.path),
        "all-contents": lambda repo, args: repo.get_all_contents(
            max_file_size=args.max_size if hasattr(args, "max_size") else None,
            exclude_patterns=args.exclude if hasattr(args, "exclude") else None,
        ),
        "langs": lambda repo, _: repo.get_language_stats(),
        "stats": lambda repo, _: repo.get_repository_stats(),
    }
    return handlers.get(command)


def execute_command(
    repo: RepositoryAnalyzer,
    args: argparse.Namespace,
) -> dict[str, Any] | str | None:
    """Execute the requested command on the repository.

    Args:
        repo: The GitRepo instance to execute commands on
        args: The parsed command line arguments

    Returns:
        The result of the command execution

    Raises:
        GitParseError: If there is an error executing the command
    """
    handler = get_command_handler(args.command)
    if handler:
        return handler(repo, args)
    return None


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
            repo = RepositoryAnalyzer(args.repo)
            progress.update(task, completed=True)
        except GitParseError as e:
            progress.update(task, completed=True)
            logger.exception("Failed to initialize repository")
            console.print(format_error(f"Failed to initialize repository: {e}"))
            sys.exit(1)

    # Execute command
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]Executing {args.command} command...[/cyan]")
            result = execute_command(repo, args)
            progress.update(task, completed=True)

        if result is not None:
            save_output(result, args.output, not args.no_pretty)
            if not args.output:
                console.print(format_success("\nCommand completed successfully!"))

    except GitParseError as e:
        logger.exception("Error executing command")
        console.print(format_error(f"Error executing command: {e}"))
        sys.exit(1)


if __name__ == "__main__":
    main()
