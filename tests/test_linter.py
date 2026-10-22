"""Unit tests for ChangelogLinter."""

from changelog_doctor.linter import lint_changelog, lint_changelog_file


CLEAN_CHANGELOG = """# Changelog

All notable changes documented here.

## [Unreleased]

### Added
- Super fast streaming endpoint.

## [1.0.0] - 2026-03-01

### Added
- Initial project release.

[Unreleased]: https://github.com/org/repo/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/org/repo/releases/tag/v1.0.0
"""


def test_lint_clean_changelog():
    report = lint_changelog(CLEAN_CHANGELOG)
    assert report.is_valid
    assert len(report.errors) == 0


def test_missing_title():
    text = "## [Unreleased]\n\n### Added\n- Something\n"
    report = lint_changelog(text)
    assert any(d.code == "KAC100_MISSING_TITLE" for d in report.warnings)


def test_missing_unreleased():
    text = "# Changelog\n\n## [1.0.0] - 2026-01-01\n\n### Added\n- First release\n"
    report = lint_changelog(text)
    assert any(d.code == "KAC103_MISSING_UNRELEASED" for d in report.warnings)


def test_unknown_category_and_alias():
    text = """# Changelog

## [Unreleased]

### Features
- New feature here

### Bug Fixes
- Bug fix here
"""
    report = lint_changelog(text)
    cat_diags = [d for d in report.warnings if d.code == "KAC101_UNKNOWN_CATEGORY"]
    assert len(cat_diags) == 2
    assert any("Added" in d.suggested_fix for d in cat_diags if d.suggested_fix)
    assert any("Fixed" in d.suggested_fix for d in cat_diags if d.suggested_fix)


def test_chronological_date_order():
    bad_dates = """# Changelog

## [Unreleased]

## [1.1.0] - 2026-01-01

### Added
- Older release placed first

## [1.2.0] - 2026-06-01

### Added
- Newer release placed second
"""
    report = lint_changelog(bad_dates)
    assert not report.is_valid
    assert any(d.code == "KAC102_CHRONOLOGICAL_DATE_ORDER" for d in report.errors)


def test_duplicate_version():
    dupe = """# Changelog

## [Unreleased]

## [1.0.0] - 2026-01-01
### Added
- Initial

## [1.0.0] - 2026-01-01
### Fixed
- Duplicate
"""
    report = lint_changelog(dupe)
    assert not report.is_valid
    assert any(d.code == "KAC105_DUPLICATE_VERSION" for d in report.errors)


def test_empty_section():
    empty_sec = """# Changelog

## [Unreleased]

### Added

## [1.0.0] - 2026-01-01
### Added
- Something
"""
    report = lint_changelog(empty_sec)
    assert any(d.code == "KAC104_EMPTY_SECTION" for d in report.warnings)


def test_strict_mode():
    text = "## [Unreleased]\n\n### Added\n- Something\n"
    rep_normal = lint_changelog(text, strict=False)
    assert rep_normal.is_valid  # only warnings

    rep_strict = lint_changelog(text, strict=True)
    assert not rep_strict.is_valid


def test_lint_file_from_disk(tmp_path):
    f = tmp_path / "CHANGELOG.md"
    f.write_text(CLEAN_CHANGELOG, encoding="utf-8")
    report = lint_changelog_file(f)
    assert report.is_valid
    assert report.file_path == str(f)
