from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

DocStatus = Literal["documented", "stub_only", "missing"]
SUBSTANTIVE_MIN_BYTES = 80


@dataclass(frozen=True)
class ModuleSpec:
    """Configured module entry from configs/module_inventory.json."""

    module_id: str
    name: str
    category: Literal["subteam", "agentic_package"]
    lead_or_owner: str
    priority_phase: str
    expected_docs: tuple[str, ...]

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> ModuleSpec:
        return cls(
            module_id=str(raw["module_id"]),
            name=str(raw["name"]),
            category=raw["category"],
            lead_or_owner=str(raw["lead_or_owner"]),
            priority_phase=str(raw["priority_phase"]),
            expected_docs=tuple(raw.get("expected_docs", ())),
        )


@dataclass(frozen=True)
class ModuleDocCheck:
    """Status of a single expected documentation path."""

    path: str
    status: DocStatus
    byte_size: int


@dataclass(frozen=True)
class ModuleGapEntry:
    """Aggregated documentation status for one module."""

    spec: ModuleSpec
    checks: tuple[ModuleDocCheck, ...]
    overall_status: DocStatus


@dataclass
class GapReport:
    """Full T23 module and documentation inventory report."""

    entries: list[ModuleGapEntry] = field(default_factory=list)

    @property
    def total_modules(self) -> int:
        return len(self.entries)

    @property
    def documented_count(self) -> int:
        return sum(1 for e in self.entries if e.overall_status == "documented")

    @property
    def stub_count(self) -> int:
        return sum(1 for e in self.entries if e.overall_status == "stub_only")

    @property
    def missing_count(self) -> int:
        return sum(1 for e in self.entries if e.overall_status == "missing")


def classify_doc_file(path: Path) -> ModuleDocCheck:
    """Classify a doc path as documented (>=80 B), stub_only (<80 B), or missing."""
    if not path.exists() or not path.is_file():
        return ModuleDocCheck(path=path.as_posix(), status="missing", byte_size=0)

    content = path.read_text(encoding="utf-8").strip()
    byte_size = len(content.encode("utf-8"))
    status: DocStatus = "documented" if byte_size >= SUBSTANTIVE_MIN_BYTES else "stub_only"
    return ModuleDocCheck(path=path.as_posix(), status=status, byte_size=byte_size)


def load_inventory_config(config_path: Path) -> list[ModuleSpec]:
    """Load module inventory specifications from JSON."""
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    return [ModuleSpec.from_dict(item) for item in raw.get("modules", [])]


def evaluate_inventory(config_path: Path, base_dir: Path = Path(".")) -> GapReport:
    """Evaluate all configured modules against documentation files on disk."""
    report = GapReport()
    for spec in load_inventory_config(config_path):
        checks: list[ModuleDocCheck] = []
        for rel_path in spec.expected_docs:
            check = classify_doc_file(base_dir / rel_path)
            checks.append(
                ModuleDocCheck(path=rel_path, status=check.status, byte_size=check.byte_size)
            )

        statuses = {c.status for c in checks}
        if "documented" in statuses:
            overall: DocStatus = "documented"
        elif "stub_only" in statuses:
            overall = "stub_only"
        else:
            overall = "missing"

        report.entries.append(
            ModuleGapEntry(spec=spec, checks=tuple(checks), overall_status=overall)
        )
    return report


def modules_without_documents(report: GapReport) -> list[ModuleGapEntry]:
    """Return modules whose documentation is missing or only a stub (<80 bytes)."""
    return [e for e in report.entries if e.overall_status != "documented"]


def render_gap_report_markdown(report: GapReport) -> str:
    """Render the T23 module inventory and documentation gap report as Markdown."""
    gaps = modules_without_documents(report)
    lines = [
        "# T23 Module & Documentation Inventory — Gap Report v1",
        "",
        "Generated from `configs/module_inventory.json` by `scripts/generate_gap_report.py`.",
        "",
        "## Summary",
        "",
        f"- **Total modules tracked:** {report.total_modules}",
        f"- **Documented (>= {SUBSTANTIVE_MIN_BYTES} bytes):** {report.documented_count}",
        f"- **Stub only (< {SUBSTANTIVE_MIN_BYTES} bytes):** {report.stub_count}",
        f"- **Missing:** {report.missing_count}",
        "",
        "## Modules With No Substantive Documentation",
        "",
        "| Module | Category | Owner / Lead | Phase | Status | Expected Doc(s) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for entry in gaps:
        docs_col = ", ".join(f"`{c.path}` ({c.status})" for c in entry.checks)
        lines.append(
            f"| {entry.spec.name} | {entry.spec.category} | {entry.spec.lead_or_owner} | "
            f"{entry.spec.priority_phase} | `{entry.overall_status}` | {docs_col} |"
        )

    lines.extend(
        [
            "",
            "## Full Inventory",
            "",
            "| Module ID | Name | Category | Status | Expected Doc(s) |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
    )
    for entry in report.entries:
        docs_col = ", ".join(f"`{c.path}` ({c.byte_size} B)" for c in entry.checks)
        lines.append(
            f"| `{entry.spec.module_id}` | {entry.spec.name} | {entry.spec.category} | "
            f"`{entry.overall_status}` | {docs_col} |"
        )

    lines.append("")
    return "\n".join(lines)
