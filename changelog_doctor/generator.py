"""Scaffolds initial Keep A Changelog files."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional, Union


def generate_initial_changelog(
    repo_url: Optional[str] = None,
    initial_version: str = "0.1.0",
) -> str:
    today_str = date.today().isoformat()
    clean_repo = repo_url.rstrip("/") if repo_url else "https://github.com/username/project"

    content = f"""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Work-in-progress features for upcoming release.

## [{initial_version}] - {today_str}

### Added
- Initial public release and project scaffolding.

[Unreleased]: {clean_repo}/compare/v{initial_version}...HEAD
[{initial_version}]: {clean_repo}/releases/tag/v{initial_version}
"""
    return content


def init_changelog_file(
    path: Union[str, Path] = "CHANGELOG.md",
    repo_url: Optional[str] = None,
    initial_version: str = "0.1.0",
) -> str:
    p = Path(path)
    content = generate_initial_changelog(repo_url=repo_url, initial_version=initial_version)
    p.write_text(content, encoding="utf-8")
    return content
