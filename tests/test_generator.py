"""Unit tests for changelog generator."""

from changelog_doctor.generator import generate_initial_changelog, init_changelog_file
from changelog_doctor.linter import lint_changelog


def test_generate_initial_changelog():
    content = generate_initial_changelog(
        repo_url="https://github.com/org/repo",
        initial_version="1.0.0",
    )
    assert "# Changelog" in content
    assert "## [Unreleased]" in content
    assert "## [1.0.0]" in content
    assert "[Unreleased]: https://github.com/org/repo/compare/v1.0.0...HEAD" in content

    # Verify generated changelog lints 100% cleanly!
    report = lint_changelog(content)
    assert report.is_valid
    assert len(report.errors) == 0


def test_init_file_on_disk(tmp_path):
    f = tmp_path / "CHANGELOG.md"
    init_changelog_file(f, repo_url="https://github.com/org/repo", initial_version="0.5.0")
    assert f.exists()
    content = f.read_text(encoding="utf-8")
    assert "## [0.5.0]" in content
