"""Unit tests for ReleaseDrafter."""

import pytest
from changelog_doctor.drafter import extract_release_notes


SAMPLE = """# Changelog

## [Unreleased]
### Added
- WIP item

## [1.2.0] - 2026-06-01
### Added
- Feature A
- Feature B

### Fixed
- Bug C

## [1.1.0] - 2026-01-01
### Added
- Initial stuff
"""


def test_extract_latest_release():
    notes = extract_release_notes(SAMPLE)
    assert "### Added" in notes
    assert "- Feature A" in notes
    assert "- Feature B" in notes
    assert "### Fixed" in notes
    assert "- Bug C" in notes
    assert "Initial stuff" not in notes


def test_extract_specific_version():
    notes = extract_release_notes(SAMPLE, version="1.1.0")
    assert "### Added" in notes
    assert "- Initial stuff" in notes
    assert "Feature A" not in notes


def test_extract_with_header():
    notes = extract_release_notes(SAMPLE, version="1.2.0", include_header=True)
    assert "## [1.2.0] - 2026-06-01" in notes


def test_extract_unknown_version_raises():
    with pytest.raises(ValueError):
        extract_release_notes(SAMPLE, version="9.9.9")
