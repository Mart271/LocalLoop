#!/usr/bin/env python3
"""Consistency checks for LocalLoop's documentation.

Checks:
  1. Identifier definitions are unique (FR, NFR, EXC, UC, TC, OBJ, LL, EV, A, C, D, …).
  2. Every identifier referenced in Markdown is defined somewhere.
  3. Every SRS requirement has an attribute line (priority/category · release · validation · source)
     and acceptance criteria (FR) or a measure (NFR).
  4. The traceability matrix lists every FR and NFR exactly once, references only defined
     objectives and test cases, uses every catalogued test case, gives every MVP requirement at
     least one test case, and agrees with the SRS on whether a requirement is in the MVP.
  5. Relative Markdown links point to existing files, and #anchors match a heading
     (GitHub-style slugs, ignoring headings inside fenced code blocks).
  6. Fenced code blocks are balanced.

Usage: python3 scripts/check_docs.py
Exit status: 0 when all checks pass, 1 otherwise. Standard library only.
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIRS = frozenset({".git", "node_modules", "target", "dist", ".venv"})
PROPOSAL = REPO_ROOT / "docs" / "proposal" / "LocalLoop-Proposal.md"
SRS = REPO_ROOT / "docs" / "requirements" / "SRS.md"
USE_CASES = REPO_ROOT / "docs" / "requirements" / "use-cases.md"
TRACE = REPO_ROOT / "docs" / "requirements" / "requirements-traceability.md"
BACKLOG = REPO_ROOT / "docs" / "development" / "BACKLOG.md"
ARCH = REPO_ROOT / "docs" / "architecture" / "SYSTEM_ARCHITECTURE.md"
SECURITY_ARCH = REPO_ROOT / "docs" / "architecture" / "security-architecture.md"
ADR_DIR = REPO_ROOT / "docs" / "adr"

ID_PATTERN = (
    r"FR-\d{3}|NFR-\d{3}|EXC-\d{2}|UC-\d{2}|TC-\d{3}|OBJ-\d{2}|LL-\d{3}|EV-\d{2}|AIC-\d{2}|AI-\d{2}"
    r"|MVP-AC-\d{2}|USR-\d|ADR-\d{4}|AR-\d{2}|T-\d{2}|A-\d{2}|C-\d{2}|D-\d{2}"
)
REFERENCE_RE = re.compile(rf"(?<![\w-])({ID_PATTERN})(?![\w])")
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def markdown_files() -> list[Path]:
    return [
        path
        for path in sorted(REPO_ROOT.rglob("*.md"))
        if not any(part in EXCLUDED_DIRS for part in path.relative_to(REPO_ROOT).parts)
    ]


def strip_code_blocks(text: str) -> list[tuple[int, str]]:
    """Return (line number, line) pairs outside fenced code blocks."""
    lines: list[tuple[int, str]] = []
    inside = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            inside = not inside
            continue
        if not inside:
            lines.append((number, line))
    return lines


def table_first_cells(text: str, pattern: str) -> list[str]:
    return re.findall(rf"^\|\s*({pattern})\s*\|", text, flags=re.MULTILINE)


def section(text: str, start_heading: str, end_prefix: str) -> str:
    start = text.index(start_heading)
    end = text.find(end_prefix, start + len(start_heading))
    return text[start:] if end == -1 else text[start:end]


def collect_definitions(report: Report) -> dict[str, list[str]]:
    """Map each defined identifier to the places that define it."""
    srs = SRS.read_text(encoding="utf-8")
    trace = TRACE.read_text(encoding="utf-8")
    definitions: dict[str, list[str]] = defaultdict(list)

    def add(ids: Iterable[str], where: str) -> None:
        for identifier in ids:
            definitions[identifier].append(where)

    add(re.findall(r"^#### ((?:N?FR)-\d{3}) — ", srs, flags=re.MULTILINE), "SRS heading")
    add(table_first_cells(srs, r"EXC-\d{2}|A-\d{2}|C-\d{2}|D-\d{2}|EV-\d{2}|AI-\d{2}|MVP-AC-\d{2}|USR-\d"), "SRS table")
    add(re.findall(r"\*\*(AIC-\d{2}) — ", srs), "SRS AI constraint")
    add(re.findall(r"^## (UC-\d{2}) — ", USE_CASES.read_text(encoding="utf-8"), flags=re.MULTILINE), "use-cases heading")
    add(table_first_cells(section(trace, "## 1. Product Objectives", "\n## "), r"OBJ-\d{2}"), "traceability objectives")
    add(table_first_cells(section(trace, "## 5. Test Case Catalogue", "\n## "), r"TC-\d{3}"), "traceability catalogue")
    add(table_first_cells(BACKLOG.read_text(encoding="utf-8"), r"LL-\d{3}"), "backlog")
    add(table_first_cells(ARCH.read_text(encoding="utf-8"), r"AR-\d{2}"), "architecture risks")
    add(table_first_cells(SECURITY_ARCH.read_text(encoding="utf-8"), r"T-\d{2}"), "threat model")
    for adr in sorted(ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md")):
        add([f"ADR-{adr.name[:4]}"], rel(adr))

    for identifier, places in sorted(definitions.items()):
        if len(places) > 1:
            report.error(f"duplicate definition of {identifier}: {', '.join(places)}")
    return definitions


def check_references(definitions: dict[str, list[str]], report: Report) -> None:
    for path in markdown_files():
        if path == PROPOSAL:
            continue
        for number, line in strip_code_blocks(path.read_text(encoding="utf-8")):
            for identifier in REFERENCE_RE.findall(line):
                if identifier not in definitions:
                    report.error(f"{rel(path)}:{number}: undefined identifier {identifier}")


def check_srs_structure(report: Report) -> dict[str, str]:
    """Validate requirement blocks; return requirement id -> release field."""
    srs = SRS.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^#### (?:N?FR)-\d{3} — )", srs, flags=re.MULTILINE)
    releases: dict[str, str] = {}
    for block in blocks[1:]:
        block = re.split(r"^#{2,3} ", block, flags=re.MULTILINE)[0]
        identifier = block[5:12].rstrip(" —") if block.startswith("#### NFR") else block[5:11]
        lines = block.splitlines()
        attributes = lines[1] if len(lines) > 1 else ""
        match = re.fullmatch(r"\*\*(.+)\*\*", attributes.strip())
        if not match or len(match.group(1).split(" · ")) < 4:
            report.error(f"SRS {identifier}: missing or malformed attribute line")
            continue
        releases[identifier] = match.group(1).split(" · ")[1]
        if identifier.startswith("FR") and "- AC1:" not in block:
            report.error(f"SRS {identifier}: no acceptance criteria (expected '- AC1:')")
        if identifier.startswith("NFR") and "*Measure" not in block:
            report.error(f"SRS {identifier}: no measure")
    return releases


def check_traceability(definitions: dict[str, list[str]], releases: dict[str, str], report: Report) -> None:
    trace = TRACE.read_text(encoding="utf-8")
    matrix_text = section(trace, "## 3. Traceability Matrix", "\n## 5.")
    catalogue = set(table_first_cells(section(trace, "## 5. Test Case Catalogue", "\n## "), r"TC-\d{3}"))
    seen: Counter[str] = Counter()
    used_tests: set[str] = set()

    for line in matrix_text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8 or not re.fullmatch(r"N?FR-\d{3}", cells[1]):
            continue
        objective, requirement, _title, release, _validation, _components, tests, _phase = cells
        seen[requirement] += 1
        if objective not in definitions:
            report.error(f"traceability {requirement}: undefined objective {objective}")
        test_ids = [t.strip() for t in tests.split(",") if t.strip()]
        for test in test_ids:
            if test not in catalogue:
                report.error(f"traceability {requirement}: test case {test} not in catalogue")
            used_tests.add(test)
        if "MVP" in release and not test_ids:
            report.error(f"traceability {requirement}: MVP requirement without a test case")
        srs_release = releases.get(requirement)
        if srs_release is not None and ("MVP" in srs_release) != ("MVP" in release):
            report.error(f"traceability {requirement}: release '{release}' disagrees with SRS '{srs_release}'")

    for requirement in sorted(releases):
        if seen[requirement] == 0:
            report.error(f"traceability: {requirement} missing from matrix")
        elif seen[requirement] > 1:
            report.error(f"traceability: {requirement} listed {seen[requirement]} times")
    for test in sorted(catalogue - used_tests):
        report.error(f"traceability: test case {test} is not linked to any requirement")


def github_slug(heading: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # keep link text only
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def heading_slugs(path: Path) -> set[str]:
    slugs: set[str] = set()
    counts: Counter[str] = Counter()
    for _, line in strip_code_blocks(path.read_text(encoding="utf-8")):
        match = HEADING_RE.match(line)
        if not match:
            continue
        base = github_slug(match.group(2))
        slug = base if counts[base] == 0 else f"{base}-{counts[base]}"
        counts[base] += 1
        slugs.add(slug)
    return slugs


def check_links(report: Report) -> None:
    slug_cache: dict[Path, set[str]] = {}
    for path in markdown_files():
        for number, line in strip_code_blocks(path.read_text(encoding="utf-8")):
            for target in LINK_RE.findall(line):
                if re.match(r"^[a-z][a-z0-9+.-]*:", target):  # http:, https:, mailto:, …
                    continue
                file_part, _, anchor = target.partition("#")
                destination = (path.parent / file_part).resolve() if file_part else path
                if not destination.exists():
                    report.error(f"{rel(path)}:{number}: broken link {target}")
                    continue
                if anchor and destination.suffix == ".md":
                    slugs = slug_cache.setdefault(destination, heading_slugs(destination))
                    if anchor not in slugs:
                        report.error(f"{rel(path)}:{number}: missing anchor #{anchor} in {rel(destination)}")


def check_fences(report: Report) -> None:
    for path in markdown_files():
        fences = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.lstrip().startswith("```"))
        if fences % 2:
            report.error(f"{rel(path)}: unbalanced code fences")


def main() -> int:
    report = Report()
    for required in (PROPOSAL, SRS, USE_CASES, TRACE, BACKLOG, ARCH, SECURITY_ARCH):
        if not required.exists():
            report.error(f"missing required document {rel(required)}")
    if report.errors:
        print("\n".join(report.errors))
        return 1

    definitions = collect_definitions(report)
    releases = check_srs_structure(report)
    check_references(definitions, report)
    check_traceability(definitions, releases, report)
    check_links(report)
    check_fences(report)

    counts = Counter(re.sub(r"-\d+$", "", identifier) for identifier in definitions)
    summary = ", ".join(f"{prefix}: {count}" for prefix, count in sorted(counts.items()))
    if report.errors:
        print("\n".join(report.errors))
        print(f"\n{len(report.errors)} documentation problem(s) found.")
        return 1
    print(f"Documentation checks passed. Identifiers defined — {summary}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
