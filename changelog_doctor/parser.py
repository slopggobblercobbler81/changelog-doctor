"""Parser for Keep A Changelog markdown files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from .models import Changelog, ChangelogSection, ReleaseVersion


RELEASE_HEADER_REGEX = re.compile(
    r"^##\s+\[?([A-Za-z0-9._-]+)\]?(?:\s*-\s*([^\[\r\n]+?))?(?:\s*\[(YANKED)\])?\s*$",
    re.IGNORECASE,
)

CATEGORY_HEADER_REGEX = re.compile(r"^###\s+([A-Za-z0-9\s_-]+)$")

LINK_DEF_REGEX = re.compile(r"^\[([A-Za-z0-9._-]+)\]:\s*(\S+)")


class ChangelogParser:
    """Parses standard Keep A Changelog markdown into structured objects."""

    @classmethod
    def parse_text(cls, text: str) -> Changelog:
        lines = text.splitlines()
        changelog = Changelog()

        current_release: Optional[ReleaseVersion] = None
        current_section: Optional[ChangelogSection] = None
        preamble_lines: List[str] = []

        in_preamble = True

        for idx, raw_line in enumerate(lines):
            line_num = idx + 1
            line = raw_line.strip()

            # Check footer links e.g. [1.0.0]: https://...
            link_match = LINK_DEF_REGEX.match(line)
            if link_match:
                tag = link_match.group(1)
                url = link_match.group(2)
                changelog.compare_links[tag] = url
                continue

            # Check top title e.g. # Changelog
            if line.startswith("# ") and in_preamble:
                changelog.title = line[2:].strip()
                continue

            # Check release header e.g. ## [1.0.0] - 2026-10-22
            if line.startswith("## "):
                in_preamble = False
                rel_match = RELEASE_HEADER_REGEX.match(line)
                if rel_match:
                    ver_str = rel_match.group(1).strip()
                    date_str = rel_match.group(2).strip() if rel_match.group(2) else None
                    is_yanked = bool(rel_match.group(3))
                    is_unreleased = ver_str.lower() == "unreleased"

                    current_release = ReleaseVersion(
                        version=ver_str,
                        line_number=line_num,
                        date=date_str,
                        is_unreleased=is_unreleased,
                        is_yanked=is_yanked,
                    )
                    changelog.releases.append(current_release)
                    current_section = None
                else:
                    # Unrecognized release header
                    parts = line[3:].strip().split()
                    ver_str = parts[0].strip("[]") if parts else "unknown"
                    current_release = ReleaseVersion(
                        version=ver_str,
                        line_number=line_num,
                        date=None,
                        is_unreleased=ver_str.lower() == "unreleased",
                    )
                    changelog.releases.append(current_release)
                    current_section = None
                continue

            # Check category header e.g. ### Added
            if line.startswith("### "):
                in_preamble = False
                cat_match = CATEGORY_HEADER_REGEX.match(line)
                cat_name = cat_match.group(1).strip() if cat_match else line[4:].strip()

                if current_release is not None:
                    current_section = ChangelogSection(
                        category=cat_name,
                        line_number=line_num,
                    )
                    current_release.sections[cat_name] = current_section
                continue

            # Bullet points or items
            if line.startswith(("- ", "* ", "+ ")):
                entry_text = line[2:].strip()
                if current_section is not None:
                    current_section.entries.append(entry_text)
                continue

            # Sub-items or continuation lines
            if (raw_line.startswith("  ") or raw_line.startswith("\t")) and current_section and current_section.entries:
                # Append to last entry
                current_section.entries[-1] += " " + line
                continue

            # Preamble text
            if in_preamble and line:
                preamble_lines.append(line)

        changelog.preamble = "\n".join(preamble_lines)
        return changelog

    @classmethod
    def parse_file(cls, path: Union[str, Path]) -> Changelog:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Changelog file not found: {p}")
        text = p.read_text(encoding="utf-8", errors="replace")
        return cls.parse_text(text)


def parse_changelog(text: str) -> Changelog:
    return ChangelogParser.parse_text(text)


def parse_changelog_file(path: Union[str, Path]) -> Changelog:
    return ChangelogParser.parse_file(path)
