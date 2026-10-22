"""Unit tests for ChangelogParser."""

import pytest
from changelog_doctor.parser import (
    ChangelogParser,
    parse_changelog,
    parse_changelog_file,
)


SAMPLE_CHANGELOG = """# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- New authentication endpoint.

## [1.1.0] - 2026-05-20

### Changed
- Improved database query performance.

### Fixed
- Fixed memory leak in websocket loop.

## [1.0.0] - 2026-01-10 [YANKED]

### Added
- Initial public release.

[Unreleased]: https://github.com/org/repo/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/org/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/org/repo/releases/tag/v1.0.0
"""


def test_parse_structure():
    cl = parse_changelog(SAMPLE_CHANGELOG)
    assert cl.title == "Changelog"
    assert "All notable changes" in cl.preamble
    assert len(cl.releases) == 3

    # Unreleased
    rel_unreleased = cl.releases[0]
    assert rel_unreleased.version == "Unreleased"
    assert rel_unreleased.is_unreleased is True
    assert "Added" in rel_unreleased.sections
    assert len(rel_unreleased.sections["Added"].entries) == 1
    assert "New authentication endpoint." in rel_unreleased.sections["Added"].entries[0]

    # 1.1.0
    rel_110 = cl.releases[1]
    assert rel_110.version == "1.1.0"
    assert rel_110.date == "2026-05-20"
    assert rel_110.is_unreleased is False
    assert rel_110.is_yanked is False
    assert len(rel_110.sections) == 2

    # 1.0.0
    rel_100 = cl.releases[2]
    assert rel_100.version == "1.0.0"
    assert rel_100.date == "2026-01-10"
    assert rel_100.is_yanked is True

    # Links
    assert "Unreleased" in cl.compare_links
    assert "1.1.0" in cl.compare_links
    assert "1.0.0" in cl.compare_links


def test_parse_file_from_disk(tmp_path):
    f = tmp_path / "CHANGELOG.md"
    f.write_text(SAMPLE_CHANGELOG, encoding="utf-8")
    cl = parse_changelog_file(f)
    assert len(cl.releases) == 3


def test_parse_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_changelog_file("nonexistent_changelog_file_9876.md")
