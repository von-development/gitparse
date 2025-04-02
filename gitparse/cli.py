"""Command line interface for GitParse."""

import argparse
import json
import sys
from typing import Any, Optional

from gitparse import GitRepo
from gitparse.schema.config import ExtractionConfig


def save_output(data: Any, output_file: Optional[str] = None) -> None:
    """Save output to a file or print to console."""
    if output_file:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
    else:
        print(json.dumps(data, indent=2))


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="Extract and analyze Git repository content")

    parser.add_argument("source", help="Local path or GitHub URL to the repository")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get basic repository information")

    # Tree command
    tree_parser = subparsers.add_parser("tree", help="Get repository file tree")
    tree_parser.add_argument(
        "--style",
        choices=["flattened", "markdown", "dict"],
        default="markdown",
        help="Output style format",
    )

    # Dependencies command
    deps_parser = subparsers.add_parser("deps", help="Get repository dependencies")

    # Content command
    content_parser = subparsers.add_parser("content", help="Get file content")
    content_parser.add_argument("path", help="Path to file within repository")

    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Create repository object
    try:
        repo = GitRepo(args.source)
    except Exception as e:
        print(f"Error initializing repository: {e}", file=sys.stderr)
        sys.exit(1)

    # Execute command
    try:
        if args.command == "info":
            result = repo.get_repository_info()
        elif args.command == "tree":
            result = repo.get_file_tree(style=args.style)
        elif args.command == "deps":
            result = repo.get_dependencies()
        elif args.command == "content":
            result = repo.get_file_content(args.path)
        else:
            print("No command specified. Use -h for help.", file=sys.stderr)
            sys.exit(1)

        # Print result
        if isinstance(result, (dict, list)):
            print(json.dumps(result, indent=2))
        else:
            print(result)

    except Exception as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
