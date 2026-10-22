"""Extracts clean release notes for GitHub Releases and release announcements."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from .models import Changelog, ReleaseVersion
from .parser import ChangelogParser


class ReleaseDrafter:
    """Extracts Markdown release notes for a specific release version."""

    @classmethod
    def extract_notes(
        cls,
        changelog: Changelog,
        version: Optional[str] = None,
        include_header: bool = False,
    ) -> str:
        target_release: Optional[ReleaseVersion] = None

        if version:
            target_release = changelog.get_release(version)
            if not target_release:
                available = ", ".join(r.version for r in changelog.releases)
                raise ValueError(f"Version '{version}' not found in changelog. Available: {available}")
        else:
            # Default to latest non-unreleased release, or unreleased if none
            for r in changelog.releases:
                if not r.is_unreleased:
                    target_release = r
                    break
            if not target_release and changelog.releases:
                target_release = changelog.releases[0]

        if not target_release:
            return ""

        lines = []
        if include_header:
            date_part = f" - {target_release.date}" if target_release.date else ""
            lines.append(f"## [{target_release.version}]{date_part}\n")

        for cat_name, sec in target_release.sections.items():
            if sec.entries:
                lines.append(f"### {cat_name}")
                for entry in sec.entries:
                    lines.append(f"- {entry}")
                lines.append("")

        return "\n".join(lines).strip() + "\n"


def extract_release_notes(
    text_or_path: Union[str, Path],
    version: Optional[str] = None,
    include_header: bool = False,
) -> str:
    p = Path(text_or_path) if isinstance(text_or_path, (str, Path)) and "\n" not in str(text_or_path) and Path(text_or_path).exists() else None

    if p is not None:
        raw_text = p.read_text(encoding="utf-8", errors="replace")
    else:
        raw_text = str(text_or_path)

    changelog = ChangelogParser.parse_text(raw_text)
    return ReleaseDrafter.extract_notes(changelog, version=version, include_header=include_header)
