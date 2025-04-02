"""Command line interface for GitParse."""

import argparse
import json
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
    parser = argparse.ArgumentParser(
        description="GitParse - A tool for analyzing Git repositories"
    )

    parser.add_argument(
        "repo_path",
        help="Path or URL to the Git repository"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file path (optional)",
        default=None
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Info command
    subparsers.add_parser(
        "info",
        help="Get basic repository information"
    )

    # Tree command
    tree_parser = subparsers.add_parser(
        "tree",
        help="Get repository file tree"
    )
    tree_parser.add_argument(
        "--style",
        choices=["dict", "markdown"],
        default="dict",
        help="Output style for the tree"
    )

    # README command
    subparsers.add_parser(
        "readme",
        help="Get repository README content"
    )

    # Dependencies command
    deps_parser = subparsers.add_parser(
        "deps",
        help="Get repository dependencies"
    )
    deps_parser.add_argument(
        "--package-files",
        nargs="+",
        help="Package files to check (e.g., requirements.txt, package.json)"
    )

    # Languages command
    subparsers.add_parser(
        "langs",
        help="Get repository language statistics"
    )

    # Stats command
    subparsers.add_parser(
        "stats",
        help="Get repository statistics"
    )

    # Content command
    content_parser = subparsers.add_parser(
        "content",
        help="Get content of a specific file"
    )
    content_parser.add_argument(
        "file_path",
        help="Path to the file within the repository"
    )

    # All contents command
    all_contents_parser = subparsers.add_parser(
        "all-contents",
        help="Get all file contents"
    )
    all_contents_parser.add_argument(
        "--max-size",
        type=int,
        help="Maximum file size in bytes"
    )

    return parser

def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    repo = GitRepo(args.repo_path)

    try:
        if args.command == "info":
            result = repo.get_repo_info()

        elif args.command == "tree":
            result = repo.get_file_tree(style=args.style)

        elif args.command == "readme":
            result = repo.get_readme_content()

        elif args.command == "deps":
            config = None
            if args.package_files:
                config = ExtractionConfig(package_files=args.package_files)
            result = repo.get_dependencies(config=config)

        elif args.command == "langs":
            result = repo.get_language_stats()

        elif args.command == "stats":
            result = repo.get_repo_stats()

        elif args.command == "content":
            result = repo.get_file_content(args.file_path)

        elif args.command == "all-contents":
            result = repo.get_all_contents(max_file_size=args.max_size)

        save_output(result, args.output)

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
