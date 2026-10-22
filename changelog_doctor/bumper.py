"""Semantic version bump engine for Keep A Changelog files."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Optional, Tuple, Union

from .models import Changelog, ReleaseVersion
from .parser import ChangelogParser


SEMVER_REGEX = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$")


class SemverBumper:
    """Calculates next semantic versions and transitions Unreleased sections to released versions."""

    @classmethod
    def calculate_next_version(cls, current_version: str, bump_type: str = "patch") -> str:
        bump = bump_type.lower().strip()
        # Direct target version specified
        if SEMVER_REGEX.match(bump):
            return bump.lstrip("v")

        match = SEMVER_REGEX.match(current_version.strip())
        if not match:
            # Default fallback if unparseable
            return "1.0.0"

        major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))

        if bump in ("major", "breaking"):
            return f"{major + 1}.0.0"
        elif bump in ("minor", "feature", "feat"):
            return f"{major}.{minor + 1}.0"
        elif bump in ("patch", "fix", "bugfix"):
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Unknown bump type '{bump_type}'. Choose major, minor, or patch.")

    @classmethod
    def bump_text(
        cls,
        text: str,
        bump_type: str = "patch",
        release_date: Optional[str] = None,
        repo_url: Optional[str] = None,
    ) -> str:
        changelog = ChangelogParser.parse_text(text)
        today_str = release_date or date.today().isoformat()

        # Find latest released version
        prev_version = "0.0.0"
        for r in changelog.releases:
            if not r.is_unreleased:
                prev_version = r.version
                break

        new_version = cls.calculate_next_version(prev_version, bump_type)

        lines = text.splitlines()
        new_lines: List[str] = []

        unreleased_header_idx = -1
        for i, l in enumerate(lines):
            if re.match(r"^##\s+\[?Unreleased\]?", l, re.IGNORECASE):
                unreleased_header_idx = i
                break

        if unreleased_header_idx == -1:
            # If no Unreleased section, find the first ## header
            first_release_idx = -1
            for i, l in enumerate(lines):
                if l.startswith("## "):
                    first_release_idx = i
                    break
            if first_release_idx != -1:
                new_section = [
                    "## [Unreleased]",
                    "",
                    f"## [{new_version}] - {today_str}",
                ]
                new_lines = lines[:first_release_idx] + new_section + lines[first_release_idx:]
            else:
                new_lines = lines + ["", "## [Unreleased]", "", f"## [{new_version}] - {today_str}"]
        else:
            # Insert new release header after Unreleased content or convert Unreleased
            new_lines = []
            for i, line in enumerate(lines):
                if i == unreleased_header_idx:
                    new_lines.append("## [Unreleased]")
                    new_lines.append("")
                    new_lines.append(f"## [{new_version}] - {today_str}")
                else:
                    new_lines.append(line)

        # Update or append comparison links if present or repo_url provided
        clean_repo = repo_url.rstrip("/") if repo_url else None
        if not clean_repo:
            for url in changelog.compare_links.values():
                if "/compare/" in url:
                    clean_repo = url.split("/compare/")[0]
                    break

        result = "\n".join(new_lines)

        if clean_repo:
            link_unreleased = f"[Unreleased]: {clean_repo}/compare/v{new_version}...HEAD"
            link_new = f"[{new_version}]: {clean_repo}/compare/v{prev_version}...v{new_version}"

            # Check if links already exist in text
            if "[Unreleased]:" in result:
                result = re.sub(r"\[Unreleased\]:\s*\S+", link_unreleased, result)
            else:
                result += f"\n\n{link_unreleased}"

            if f"[{new_version}]:" not in result:
                result += f"\n{link_new}"

        if not result.endswith("\n"):
            result += "\n"

        return result


def bump_changelog(
    text_or_path: Union[str, Path],
    bump_type: str = "patch",
    release_date: Optional[str] = None,
    repo_url: Optional[str] = None,
    write: bool = False,
) -> str:
    p = Path(text_or_path) if isinstance(text_or_path, (str, Path)) and "\n" not in str(text_or_path) and Path(text_or_path).exists() else None

    if p is not None:
        raw_text = p.read_text(encoding="utf-8", errors="replace")
    else:
        raw_text = str(text_or_path)

    updated = SemverBumper.bump_text(
        raw_text,
        bump_type=bump_type,
        release_date=release_date,
        repo_url=repo_url,
    )

    if p is not None and write:
        p.write_text(updated, encoding="utf-8")

    return updated
