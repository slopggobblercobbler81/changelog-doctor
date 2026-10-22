"""Command line interface for changelog-doctor."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .bumper import bump_changelog
from .drafter import extract_release_notes
from .generator import generate_initial_changelog, init_changelog_file
from .linter import ChangelogLinter
from .models import Severity


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="changelog-doctor",
        description="Production Keep-A-Changelog linter, semver bumper, and release notes generator.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: lint
    lint_parser = subparsers.add_parser(
        "lint",
        aliases=["check", "validate"],
        help="Lint CHANGELOG.md against the Keep A Changelog specification.",
    )
    lint_parser.add_argument(
        "file",
        nargs="?",
        default="CHANGELOG.md",
        help="Path to CHANGELOG.md (default: CHANGELOG.md)",
    )
    lint_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat style and formatting recommendations as fatal errors.",
    )
    lint_parser.add_argument(
        "--json",
        action="store_true",
        help="Output diagnostics in JSON format.",
    )

    # Command: bump
    bump_parser = subparsers.add_parser(
        "bump",
        help="Transition [Unreleased] changes into a new SemVer release version.",
    )
    bump_parser.add_argument(
        "bump_type",
        nargs="?",
        default="patch",
        help="Bump increment ('patch', 'minor', 'major', or specific version like '1.2.0').",
    )
    bump_parser.add_argument(
        "--file",
        "-f",
        default="CHANGELOG.md",
        help="Path to CHANGELOG.md (default: CHANGELOG.md)",
    )
    bump_parser.add_argument(
        "--date",
        "-d",
        help="Release date in YYYY-MM-DD format (defaults to today).",
    )
    bump_parser.add_argument(
        "--repo",
        "-r",
        help="GitHub repository URL for updating comparison links.",
    )
    bump_parser.add_argument(
        "-w",
        "--write",
        action="store_true",
        help="Write updated changelog directly to file.",
    )

    # Command: extract
    ext_parser = subparsers.add_parser(
        "extract",
        help="Extract release notes markdown for GitHub Releases or CI/CD pipelines.",
    )
    ext_parser.add_argument(
        "version",
        nargs="?",
        default=None,
        help="Release version to extract (defaults to latest release).",
    )
    ext_parser.add_argument(
        "--file",
        "-f",
        default="CHANGELOG.md",
        help="Path to CHANGELOG.md (default: CHANGELOG.md)",
    )
    ext_parser.add_argument(
        "--include-header",
        action="store_true",
        help="Include the release header line in output.",
    )
    ext_parser.add_argument(
        "-o",
        "--output",
        help="Destination path to write release notes (defaults to stdout).",
    )

    # Command: init
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new, compliant CHANGELOG.md file.",
    )
    init_parser.add_argument(
        "file",
        nargs="?",
        default="CHANGELOG.md",
        help="Destination path (default: CHANGELOG.md)",
    )
    init_parser.add_argument(
        "--repo",
        "-r",
        help="Repository URL (e.g. https://github.com/user/project).",
    )
    init_parser.add_argument(
        "--initial-version",
        default="0.1.0",
        help="Initial version tag (default: 0.1.0)",
    )

    return parser


def handle_lint(args: argparse.Namespace) -> int:
    p = Path(args.file)
    linter = ChangelogLinter(strict=args.strict)
    report = linter.lint_file(p)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
        return 0 if report.is_valid else 1

    print(f"Linting {args.file} against Keep A Changelog standards...")
    if report.is_valid and not report.diagnostics:
        print("  ✓ Perfectly compliant! Zero issues found.")
        return 0

    if report.is_valid:
        print("  ✓ Valid with non-fatal recommendations:")
        for d in report.diagnostics:
            icon = "⚠" if d.severity == Severity.WARNING else "ℹ"
            print(f"    {icon} line {d.line_number}: [{d.code}] {d.message}")
        return 0

    print(f"  ✗ Validation failed with {len(report.errors)} error(s):")
    for d in report.errors:
        print(f"    ✗ line {d.line_number}: [{d.code}] {d.message}")
    for d in report.warnings:
        print(f"    ⚠ line {d.line_number}: [{d.code}] {d.message}")

    return 1


def handle_bump(args: argparse.Namespace) -> int:
    p = Path(args.file)
    if not p.exists():
        print(f"Error: File '{args.file}' does not exist.", file=sys.stderr)
        return 1

    try:
        updated = bump_changelog(
            p,
            bump_type=args.bump_type,
            release_date=args.date,
            repo_url=args.repo,
            write=args.write,
        )
        if args.write:
            print(f"Successfully bumped {args.file} ({args.bump_type}).")
        else:
            sys.stdout.write(updated)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_extract(args: argparse.Namespace) -> int:
    p = Path(args.file)
    if not p.exists():
        print(f"Error: File '{args.file}' does not exist.", file=sys.stderr)
        return 1

    try:
        notes = extract_release_notes(
            p,
            version=args.version,
            include_header=args.include_header,
        )
        if args.output:
            Path(args.output).write_text(notes, encoding="utf-8")
            print(f"Saved release notes to '{args.output}'.")
        else:
            sys.stdout.write(notes)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_init(args: argparse.Namespace) -> int:
    p = Path(args.file)
    if p.exists():
        print(f"Warning: File '{args.file}' already exists. Overwriting.", file=sys.stderr)

    init_changelog_file(p, repo_url=args.repo, initial_version=args.initial_version)
    print(f"Created compliant Keep A Changelog file at '{args.file}'.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    handlers = {
        "lint": handle_lint,
        "check": handle_lint,
        "validate": handle_lint,
        "bump": handle_bump,
        "extract": handle_extract,
        "init": handle_init,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
