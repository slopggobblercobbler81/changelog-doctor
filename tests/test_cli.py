"""Integration tests for changelog-doctor CLI."""

import json
from pathlib import Path
import pytest
from changelog_doctor.cli import main


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "changelog-doctor 1.0.0" in captured.out


def test_cli_help(capsys):
    ret = main([])
    assert ret == 0
    captured = capsys.readouterr()
    assert "usage: changelog-doctor" in captured.out


def test_cli_lint_clean(tmp_path, capsys):
    f = tmp_path / "CHANGELOG.md"
    f.write_text(
        """# Changelog

## [Unreleased]

### Added
- Working item

## [1.0.0] - 2026-01-01

### Added
- First release
""",
        encoding="utf-8",
    )
    ret = main(["lint", str(f)])
    assert ret == 0
    out = capsys.readouterr().out
    assert "Valid" in out or "compliant" in out


def test_cli_lint_error_and_json(tmp_path, capsys):
    f = tmp_path / "CHANGELOG.md"
    f.write_text("## [1.0.0] - invalid-date\n", encoding="utf-8")
    ret = main(["lint", "--json", str(f)])
    assert ret == 1
    data = json.loads(capsys.readouterr().out)
    assert data["is_valid"] is False


def test_cli_bump(tmp_path, capsys):
    f = tmp_path / "CHANGELOG.md"
    f.write_text(
        """# Changelog

## [Unreleased]
### Added
- New cool feature

## [1.0.0] - 2026-01-01
""",
        encoding="utf-8",
    )
    # Write bump
    ret = main(["bump", "minor", "-f", str(f), "-w", "--date", "2026-05-01"])
    assert ret == 0
    content = f.read_text(encoding="utf-8")
    assert "## [1.1.0] - 2026-05-01" in content


def test_cli_extract(tmp_path, capsys):
    f = tmp_path / "CHANGELOG.md"
    f.write_text(
        """# Changelog

## [1.0.0] - 2026-01-01
### Added
- Awesome feature
""",
        encoding="utf-8",
    )
    # Output to stdout
    ret = main(["extract", "--file", str(f)])
    assert ret == 0
    out = capsys.readouterr().out
    assert "Awesome feature" in out

    # Output to file
    out_file = tmp_path / "notes.md"
    ret_f = main(["extract", "--file", str(f), "-o", str(out_file)])
    assert ret_f == 0
    assert out_file.exists()
    assert "Awesome feature" in out_file.read_text(encoding="utf-8")


def test_cli_init(tmp_path, capsys):
    f = tmp_path / "CHANGELOG.md"
    ret = main(["init", str(f), "--repo", "https://github.com/org/repo"])
    assert ret == 0
    assert f.exists()
    assert "# Changelog" in f.read_text(encoding="utf-8")


def test_cli_lint_non_json_errors_and_warnings(tmp_path, capsys):
    f = tmp_path / "CHANGELOG.md"
    f.write_text("# Changelog\n\n## [1.0.0] - invalid-date\n### Bugz\n- Broken\n", encoding="utf-8")
    ret = main(["lint", str(f)])
    assert ret == 1
    out = capsys.readouterr().out
    assert "Validation failed" in out


def test_cli_lint_warnings_only(tmp_path, capsys):
    f = tmp_path / "CHANGELOG.md"
    f.write_text("# Changelog\n\n## [1.0.0] - 2026-01-01\n### Bugz\n- Broken\n", encoding="utf-8")
    ret = main(["lint", str(f)])
    assert ret == 0
    out = capsys.readouterr().out
    assert "Valid with non-fatal recommendations" in out


def test_cli_bump_stdout(tmp_path, capsys):
    f = tmp_path / "CHANGELOG.md"
    f.write_text("# Changelog\n\n## [Unreleased]\n### Added\n- Item\n\n## [1.0.0] - 2026-01-01\n", encoding="utf-8")
    ret = main(["bump", "patch", "-f", str(f), "--repo", "https://github.com/owner/repo"])
    assert ret == 0
    out = capsys.readouterr().out
    assert "## [1.0.1]" in out


def test_cli_missing_files(tmp_path, capsys):
    missing = str(tmp_path / "nonexistent.md")
    assert main(["bump", "patch", "-f", missing]) == 1
    assert main(["extract", "-f", missing]) == 1


def test_cli_no_command(capsys):
    assert main([]) == 0

