# changelog-doctor 📝🩺

[![CI](https://github.com/slopggobblercobbler81/changelog-doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/slopggobblercobbler81/changelog-doctor/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](https://github.com/slopggobblercobbler81/changelog-doctor)

**changelog-doctor** is a production-grade, zero-dependency developer CLI utility and Python library to lint, validate, bump, and extract release notes from [Keep a Changelog](https://keepachangelog.com/) files.

Enforce clean release documentation, eliminate formatting drift, automate SemVer version transitions, and generate formatted GitHub Release notes seamlessly.

---

## 🚀 Key Capabilities

- 🔍 **Strict Keep-A-Changelog Linter (`lint`)**:
  - Enforces standard change categories (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`).
  - Detects common category misspellings or non-standard synonyms (`Features` -> `Added`, `Bugs` -> `Fixed`, `Breaking Changes` -> `Changed`).
  - Enforces strict reverse-chronological release date ordering (`YYYY-MM-DD`).
  - Verifies presence of the `[Unreleased]` work-in-progress section.
  - Flags duplicate versions and empty sections.
  - Verifies footer comparison link consistency (`[1.0.0]: https://...`).
- 🏷️ **SemVer Release Bumper (`bump`)**:
  - Automatically transitions entries from `[Unreleased]` into a new version release header (`## [1.2.0] - 2026-10-22`).
  - Supports `patch`, `minor`, `major`, or explicit version string targets.
  - Updates GitHub commit comparison links at the document footer (`compare/v1.1.0...v1.2.0`).
- 📤 **GitHub Release Notes Extractor (`extract`)**:
  - Extracts clean, isolated Markdown release notes for a specified version tag (or the latest release).
  - Perfect for CI/CD integration with `gh release create v1.0.0 --notes-file notes.md`.
- ⚡ **Compliant Changelog Scaffolder (`init`)**:
  - Generates standard `CHANGELOG.md` adhering to Keep A Changelog 1.0.0 and Semantic Versioning 2.0.0.
- 📦 **Zero External Dependencies**: Standard library only, ultra-fast startup for pre-commit hooks and GitHub Actions.

---

## 📦 Installation

```bash
pip install changelog-doctor
```

Or install from source:
```bash
git clone https://github.com/slopggobblercobbler81/changelog-doctor.git
cd changelog-doctor
pip install -e .
```

---

## 🛠️ Usage Guide

### 1. Lint `CHANGELOG.md`
Validate compliance against Keep A Changelog standards:
```bash
changelog-doctor lint CHANGELOG.md
```

Strict mode (fail on any warnings):
```bash
changelog-doctor lint --strict CHANGELOG.md
```

Machine-readable JSON output:
```bash
changelog-doctor lint --json CHANGELOG.md
```

### 2. Bump Version & Cut Release
Bump current version (`patch`, `minor`, or `major`) and transition `[Unreleased]` items:
```bash
# Preview bump
changelog-doctor bump minor

# Write bump in-place with GitHub comparison links updated
changelog-doctor bump minor -w --repo https://github.com/username/project
```

### 3. Extract Release Notes for GitHub Releases
Extract Markdown notes for the latest release:
```bash
changelog-doctor extract -o release_notes.md
```

Extract specific version notes:
```bash
changelog-doctor extract 1.2.0
```

### 4. Initialize New Changelog
Scaffold a new, compliant `CHANGELOG.md`:
```bash
changelog-doctor init CHANGELOG.md --repo https://github.com/username/project
```

---

## 🤖 Pre-commit Integration

Add **changelog-doctor** to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/slopggobblercobbler81/changelog-doctor
    rev: v1.0.0
    hooks:
      - id: changelog-doctor
        name: Validate CHANGELOG.md
        entry: changelog-doctor lint --strict
        language: python
        files: ^CHANGELOG\.md$
```

---

## 🧪 Running Tests

```bash
pytest -v
```

100% test coverage across parser, linter, bumper, release drafter, generator, and CLI workflows.

---

## 📄 License

MIT © [slopggobblercobbler81](https://github.com/slopggobblercobbler81)
