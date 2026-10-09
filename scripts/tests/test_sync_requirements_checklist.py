"""Tests for scripts/sync_requirements_checklist.py. Run: python -m unittest discover -s scripts/tests"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sync_requirements_checklist as sync  # noqa: E402


class ChecklistAgainstRealSrs(unittest.TestCase):
    def test_every_srs_requirement_appears_once(self) -> None:
        requirements, problems = sync.build()
        self.assertEqual(problems, [])
        ids = [r.id for r in requirements]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sum(r.kind == "FR" for r in requirements), 120)
        self.assertEqual(sum(r.kind == "NFR" for r in requirements), 36)
        text = sync.render(requirements)
        for requirement_id in ids:
            self.assertEqual(text.count(f"**{requirement_id}**"), 1, requirement_id)

    def test_committed_checklist_is_in_sync(self) -> None:
        self.assertEqual(sync.main(["--check"]), 0)


class StatusRules(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.original = sync.CHECKLIST
        sync.CHECKLIST = Path(self.tmp.name) / "checklist.md"

    def tearDown(self) -> None:
        sync.CHECKLIST = self.original
        self.tmp.cleanup()

    def write_status(self, line_suffix: str, requirement_id: str = "FR-001") -> list[str]:
        requirements, _ = sync.build()
        text = sync.render(requirements)
        lines = []
        for line in text.splitlines():
            if line.startswith(f"- [ ] **{requirement_id}**"):
                line = line.replace("— Status: **Not Started**", line_suffix)
            lines.append(line)
        sync.CHECKLIST.write_text("\n".join(lines) + "\n", encoding="utf-8")
        _, problems = sync.build()
        return problems

    def test_implemented_without_evidence_is_rejected(self) -> None:
        problems = self.write_status("— Status: **Implemented**")
        self.assertTrue(any("requires evidence" in p for p in problems), problems)

    def test_verified_without_evidence_is_rejected(self) -> None:
        problems = self.write_status("— Status: **Verified**")
        self.assertTrue(any("requires evidence" in p for p in problems), problems)

    def test_blocked_requires_reason(self) -> None:
        problems = self.write_status("— Status: **Blocked**")
        self.assertTrue(any("requires evidence" in p for p in problems), problems)

    def test_unknown_status_is_rejected(self) -> None:
        problems = self.write_status("— Status: **Done**")
        self.assertTrue(any("unknown status" in p for p in problems), problems)

    def test_status_and_evidence_survive_regeneration(self) -> None:
        self.assertEqual(self.write_status("— Status: **In Progress** — Evidence: draft in branch x"), [])
        requirements, _ = sync.build()
        first = next(r for r in requirements if r.id == "FR-001")
        self.assertEqual((first.status, first.evidence), ("In Progress", "draft in branch x"))

    def test_only_verified_is_ticked(self) -> None:
        requirements, _ = sync.build()
        requirements[0].status, requirements[0].evidence = "Implemented", "tests/x"
        requirements[1].status, requirements[1].evidence = "Verified", "report y"
        text = sync.render(requirements)
        self.assertIn(f"- [ ] **{requirements[0].id}**", text)
        self.assertIn(f"- [x] **{requirements[1].id}**", text)
        self.assertEqual(text.count("- [x]"), 1)

    def test_requirement_removed_from_srs_is_reported(self) -> None:
        sync.CHECKLIST.write_text("- [ ] **FR-999** Gone — Must · MVP · Committed · — — Status: **Not Started**\n", encoding="utf-8")
        _, problems = sync.build()
        self.assertTrue(any("FR-999" in p for p in problems), problems)


if __name__ == "__main__":
    unittest.main()
