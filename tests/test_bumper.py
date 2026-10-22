"""Unit tests for SemverBumper."""

import pytest
from changelog_doctor.bumper import SemverBumper, bump_changelog


def test_calculate_next_version():
    assert SemverBumper.calculate_next_version("1.2.3", "patch") == "1.2.4"
    assert SemverBumper.calculate_next_version("1.2.3", "minor") == "1.3.0"
    assert SemverBumper.calculate_next_version("1.2.3", "major") == "2.0.0"
    assert SemverBumper.calculate_next_version("1.2.3", "2.5.0") == "2.5.0"


def test_bump_text():
    sample = """# Changelog

## [Unreleased]

### Added
- Shiny new feature

## [1.0.0] - 2026-01-01

### Added
- First release

[Unreleased]: https://github.com/org/repo/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/org/repo/releases/tag/v1.0.0
"""
    updated = SemverBumper.bump_text(
        sample,
        bump_type="minor",
        release_date="2026-06-15",
        repo_url="https://github.com/org/repo",
    )
    assert "## [Unreleased]" in updated
    assert "## [1.1.0] - 2026-06-15" in updated
    assert "[Unreleased]: https://github.com/org/repo/compare/v1.1.0...HEAD" in updated
    assert "[1.1.0]: https://github.com/org/repo/compare/v1.0.0...v1.1.0" in updated


def test_bump_file_in_place(tmp_path):
    f = tmp_path / "CHANGELOG.md"
    f.write_text(
        """# Changelog

## [Unreleased]
### Added
- Some feature

## [1.0.0] - 2026-01-01
""",
        encoding="utf-8",
    )
    bump_changelog(f, bump_type="patch", release_date="2026-02-01", write=True)
    content = f.read_text(encoding="utf-8")
    assert "## [1.0.1] - 2026-02-01" in content
