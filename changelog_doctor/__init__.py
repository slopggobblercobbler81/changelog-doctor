"""changelog-doctor: Production Keep-A-Changelog linter, semver bumper, and release notes generator."""

__version__ = "1.0.0"

from .bumper import SemverBumper, bump_changelog
from .drafter import ReleaseDrafter, extract_release_notes
from .generator import generate_initial_changelog
from .linter import ChangelogLinter, lint_changelog, lint_changelog_file
from .models import (
    Changelog,
    ChangelogSection,
    Diagnostic,
    LintReport,
    ReleaseVersion,
    Severity,
)
from .parser import ChangelogParser, parse_changelog, parse_changelog_file

__all__ = [
    "__version__",
    "Severity",
    "Diagnostic",
    "ChangelogSection",
    "ReleaseVersion",
    "Changelog",
    "LintReport",
    "ChangelogParser",
    "parse_changelog",
    "parse_changelog_file",
    "ChangelogLinter",
    "lint_changelog",
    "lint_changelog_file",
    "SemverBumper",
    "bump_changelog",
    "ReleaseDrafter",
    "extract_release_notes",
    "generate_initial_changelog",
]
