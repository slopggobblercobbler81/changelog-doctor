"""Data models for changelog-doctor."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class Diagnostic:
    code: str
    line_number: int
    message: str
    severity: Severity = Severity.WARNING
    version: Optional[str] = None
    suggested_fix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "line_number": self.line_number,
            "message": self.message,
            "severity": self.severity.value,
            "version": self.version,
            "suggested_fix": self.suggested_fix,
        }


@dataclass
class ChangelogSection:
    category: str
    line_number: int
    entries: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "line_number": self.line_number,
            "entries_count": len(self.entries),
            "entries": self.entries,
        }


@dataclass
class ReleaseVersion:
    version: str
    line_number: int
    date: Optional[str] = None
    is_unreleased: bool = False
    is_yanked: bool = False
    sections: Dict[str, ChangelogSection] = field(default_factory=dict)
    link_target: Optional[str] = None

    @property
    def total_entries(self) -> int:
        return sum(len(sec.entries) for sec in self.sections.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "line_number": self.line_number,
            "date": self.date,
            "is_unreleased": self.is_unreleased,
            "is_yanked": self.is_yanked,
            "total_entries": self.total_entries,
            "sections": {k: v.to_dict() for k, v in self.sections.items()},
            "link_target": self.link_target,
        }


@dataclass
class Changelog:
    title: Optional[str] = None
    preamble: str = ""
    releases: List[ReleaseVersion] = field(default_factory=list)
    compare_links: Dict[str, str] = field(default_factory=dict)

    def get_release(self, version: str) -> Optional[ReleaseVersion]:
        norm = version.lstrip("v").strip().lower()
        for r in self.releases:
            if r.version.lstrip("v").strip().lower() == norm:
                return r
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "total_releases": len(self.releases),
            "releases": [r.to_dict() for r in self.releases],
            "compare_links": self.compare_links,
        }


@dataclass
class LintReport:
    file_path: str
    is_valid: bool
    diagnostics: List[Diagnostic] = field(default_factory=list)

    @property
    def errors(self) -> List[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == Severity.ERROR]

    @property
    def warnings(self) -> List[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == Severity.WARNING]

    @property
    def info(self) -> List[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == Severity.INFO]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "is_valid": self.is_valid,
            "total_diagnostics": len(self.diagnostics),
            "errors": [d.to_dict() for d in self.errors],
            "warnings": [d.to_dict() for d in self.warnings],
            "info": [d.to_dict() for d in self.info],
        }
