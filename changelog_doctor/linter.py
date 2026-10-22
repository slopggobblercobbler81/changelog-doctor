"""Linter for Keep A Changelog specification compliance."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from .models import Changelog, Diagnostic, LintReport, Severity
from .parser import ChangelogParser


STANDARD_CATEGORIES = {
    "Added",
    "Changed",
    "Deprecated",
    "Removed",
    "Fixed",
    "Security",
}

COMMON_ALIASES: Dict[str, str] = {
    "features": "Added",
    "feature": "Added",
    "new": "Added",
    "bug fixes": "Fixed",
    "bugs": "Fixed",
    "bugfixes": "Fixed",
    "fixes": "Fixed",
    "breaking changes": "Changed",
    "enhancements": "Changed",
    "improvements": "Changed",
    "docs": "Changed",
    "documentation": "Changed",
    "dependencies": "Security",
}

DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ChangelogLinter:
    """Lints Keep A Changelog markdown files."""

    def __init__(self, strict: bool = False):
        self.strict = strict

    def lint_text(self, text: str, file_path: str = "CHANGELOG.md") -> LintReport:
        diagnostics: List[Diagnostic] = []

        try:
            changelog = ChangelogParser.parse_text(text)
        except Exception as e:
            diagnostics.append(
                Diagnostic(
                    code="KAC001_PARSER_ERROR",
                    line_number=1,
                    message=f"Failed to parse changelog: {e}",
                    severity=Severity.ERROR,
                )
            )
            return LintReport(file_path=file_path, is_valid=False, diagnostics=diagnostics)

        # 1. Check title
        if not changelog.title:
            diagnostics.append(
                Diagnostic(
                    code="KAC100_MISSING_TITLE",
                    line_number=1,
                    message="Missing '# Changelog' top-level header.",
                    severity=Severity.WARNING,
                    suggested_fix="# Changelog",
                )
            )

        # 2. Check Unreleased section
        if not changelog.releases or not changelog.releases[0].is_unreleased:
            diagnostics.append(
                Diagnostic(
                    code="KAC103_MISSING_UNRELEASED",
                    line_number=changelog.releases[0].line_number if changelog.releases else 1,
                    message="Changelog should start with an '## [Unreleased]' section at the top of releases.",
                    severity=Severity.WARNING,
                    suggested_fix="Add '## [Unreleased]' heading",
                )
            )

        seen_versions: Set[str] = set()
        prev_date: Optional[datetime] = None
        has_compare_links = len(changelog.compare_links) > 0

        # 3. Check releases
        for rel in changelog.releases:
            norm_ver = rel.version.lstrip("v").lower()

            # Duplicate version
            if norm_ver in seen_versions:
                diagnostics.append(
                    Diagnostic(
                        code="KAC105_DUPLICATE_VERSION",
                        line_number=rel.line_number,
                        message=f"Duplicate release version '{rel.version}' found.",
                        severity=Severity.ERROR,
                        version=rel.version,
                    )
                )
            seen_versions.add(norm_ver)

            # Date format and chronological order
            if not rel.is_unreleased:
                if not rel.date:
                    diagnostics.append(
                        Diagnostic(
                            code="KAC107_MISSING_RELEASE_DATE",
                            line_number=rel.line_number,
                            message=f"Release '{rel.version}' is missing an ISO-8601 release date (YYYY-MM-DD).",
                            severity=Severity.WARNING,
                            version=rel.version,
                            suggested_fix=f"## [{rel.version}] - YYYY-MM-DD",
                        )
                    )
                elif not DATE_REGEX.match(rel.date):
                    diagnostics.append(
                        Diagnostic(
                            code="KAC107_INVALID_DATE_FORMAT",
                            line_number=rel.line_number,
                            message=f"Date '{rel.date}' in release '{rel.version}' is not in ISO-8601 YYYY-MM-DD format.",
                            severity=Severity.ERROR,
                            version=rel.version,
                        )
                    )
                else:
                    try:
                        cur_date = datetime.strptime(rel.date, "%Y-%m-%d")
                        if prev_date is not None and cur_date > prev_date:
                            diagnostics.append(
                                Diagnostic(
                                    code="KAC102_CHRONOLOGICAL_DATE_ORDER",
                                    line_number=rel.line_number,
                                    message=f"Release '{rel.version}' ({rel.date}) is newer than the preceding release date ({prev_date.strftime('%Y-%m-%d')}). Releases must be in reverse-chronological order.",
                                    severity=Severity.ERROR,
                                    version=rel.version,
                                )
                            )
                        prev_date = cur_date
                    except ValueError:
                        pass

            # 4. Check categories within release
            for cat_name, sec in rel.sections.items():
                if cat_name not in STANDARD_CATEGORIES:
                    suggested = COMMON_ALIASES.get(cat_name.lower())
                    msg = f"Unknown category '### {cat_name}' in release '{rel.version}'. Standard categories are: {', '.join(sorted(STANDARD_CATEGORIES))}."
                    if suggested:
                        msg += f" Did you mean '### {suggested}'?"
                    diagnostics.append(
                        Diagnostic(
                            code="KAC101_UNKNOWN_CATEGORY",
                            line_number=sec.line_number,
                            message=msg,
                            severity=Severity.WARNING,
                            version=rel.version,
                            suggested_fix=f"### {suggested}" if suggested else None,
                        )
                    )

                if len(sec.entries) == 0:
                    diagnostics.append(
                        Diagnostic(
                            code="KAC104_EMPTY_SECTION",
                            line_number=sec.line_number,
                            message=f"Category '### {cat_name}' in release '{rel.version}' is empty (no list items).",
                            severity=Severity.WARNING,
                            version=rel.version,
                        )
                    )

            # 5. Check footer link reference
            if has_compare_links:
                tag_candidates = [rel.version, f"[{rel.version}]", rel.version.lstrip("v"), f"v{rel.version.lstrip('v')}"]
                if not any(c in changelog.compare_links for c in tag_candidates):
                    diagnostics.append(
                        Diagnostic(
                            code="KAC106_UNLINKED_VERSION",
                            line_number=rel.line_number,
                            message=f"Release '{rel.version}' does not have a corresponding comparison link definition at the bottom of the changelog.",
                            severity=Severity.INFO if not self.strict else Severity.WARNING,
                            version=rel.version,
                        )
                    )

        is_valid = not any(d.severity == Severity.ERROR for d in diagnostics)
        if self.strict and any(d.severity == Severity.WARNING for d in diagnostics):
            is_valid = False

        diagnostics.sort(key=lambda d: d.line_number)

        return LintReport(
            file_path=file_path,
            is_valid=is_valid,
            diagnostics=diagnostics,
        )

    def lint_file(self, path: Union[str, Path]) -> LintReport:
        p = Path(path)
        if not p.exists():
            return LintReport(
                file_path=str(p),
                is_valid=False,
                diagnostics=[
                    Diagnostic(
                        code="FILE_NOT_FOUND",
                        line_number=1,
                        message=f"Changelog file '{p}' does not exist.",
                        severity=Severity.ERROR,
                    )
                ],
            )
        text = p.read_text(encoding="utf-8", errors="replace")
        return self.lint_text(text, file_path=str(p))


def lint_changelog(text: str, strict: bool = False) -> LintReport:
    return ChangelogLinter(strict=strict).lint_text(text)


def lint_changelog_file(path: Union[str, Path], strict: bool = False) -> LintReport:
    return ChangelogLinter(strict=strict).lint_file(path)
