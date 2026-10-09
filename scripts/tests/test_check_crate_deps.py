"""Tests for scripts/check_crate_deps.py (LL-004, TC-120). Run: python -m unittest discover scripts/tests"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import check_crate_deps as checker  # noqa: E402

CRATE_DIRS = {
    "workflow-engine": "crates/workflow-engine",
    "policy-engine": "crates/policy-engine",
    "execution-engine": "crates/execution-engine",
    "verification-engine": "crates/verification-engine",
    "local-ai": "crates/local-ai",
    "observation": "crates/observation",
    "storage": "crates/storage",
    "adapter-files": "crates/adapters/files",
    "adapter-documents": "crates/adapters/documents",
    "adapter-spreadsheet": "crates/adapters/spreadsheet",
    "desktop": "apps/desktop/src-tauri",
    "helper": "crates/helper",
}

# The allowed graph from SYSTEM_ARCHITECTURE.md §6.1.
ALLOWED = {
    "policy-engine": ["workflow-engine"],
    "verification-engine": ["workflow-engine"],
    "execution-engine": ["workflow-engine", "policy-engine", "verification-engine"],
    "local-ai": ["workflow-engine"],
    "observation": ["workflow-engine"],
    "storage": ["workflow-engine", "policy-engine"],
    "adapter-files": ["workflow-engine", "policy-engine", "execution-engine", "verification-engine"],
    "adapter-documents": ["workflow-engine", "policy-engine", "execution-engine", "verification-engine"],
    "adapter-spreadsheet": ["workflow-engine", "policy-engine", "execution-engine", "verification-engine"],
    "desktop": ["execution-engine", "local-ai", "observation", "storage", "adapter-files"],
}


def metadata(edges: dict[str, list[str]], kinds: dict[tuple[str, str], str] | None = None) -> dict[str, Any]:
    kinds = kinds or {}
    packages = []
    for name, directory in CRATE_DIRS.items():
        packages.append(
            {
                "id": f"path+file:///ws/{directory}#{name}@0.1.0",
                "name": name,
                "manifest_path": f"ws/{directory}/Cargo.toml",
                "dependencies": [
                    {"name": target, "path": f"ws/{CRATE_DIRS[target]}", "kind": kinds.get((name, target))}
                    for target in edges.get(name, [])
                ]
                + [{"name": "serde", "kind": None}],  # external crates are ignored
            }
        )
    return {"packages": packages, "workspace_members": [p["id"] for p in packages]}


def problems(edges: dict[str, list[str]], **kwargs: Any) -> list[str]:
    crates, graph = checker.load_graph(metadata(edges, **kwargs))
    return checker.violations(crates, graph)


class CrateDependencyRules(unittest.TestCase):
    def test_architecture_graph_is_allowed(self) -> None:
        self.assertEqual(problems(ALLOWED), [])

    def test_local_ai_to_adapter_is_forbidden(self) -> None:
        # The "Done when" case of LL-004: adding local-ai -> adapters fails.
        found = problems({**ALLOWED, "local-ai": ["workflow-engine", "adapter-files"]})
        # The direct edge, plus what it makes reachable (adapters depend on policy and execution).
        self.assertIn("local-ai -> adapter-files: local-ai must not depend on", found[0])
        self.assertEqual(len(found), 3)

    def test_local_ai_forbidden_targets(self) -> None:
        for target in ["policy-engine", "execution-engine", "storage", "adapter-spreadsheet"]:
            with self.subTest(target=target):
                found = problems({**ALLOWED, "local-ai": ["workflow-engine", target]})
                self.assertTrue(any(f.startswith(f"local-ai -> {target}") for f in found), found)

    def test_transitive_dependency_is_forbidden(self) -> None:
        found = problems({**ALLOWED, "local-ai": ["helper"], "helper": ["execution-engine"]})
        self.assertTrue(any("local-ai -> helper -> execution-engine" in f for f in found), found)

    def test_dev_dependency_is_forbidden(self) -> None:
        edges = {**ALLOWED, "adapter-files": [*ALLOWED["adapter-files"], "local-ai"]}
        found = problems(edges, kinds={("adapter-files", "local-ai"): "dev"})
        self.assertTrue(any("adapter-files -> local-ai" in f for f in found), found)

    def test_observation_rules(self) -> None:
        for target in ["execution-engine", "adapter-documents"]:
            with self.subTest(target=target):
                found = problems({**ALLOWED, "observation": ["workflow-engine", target]})
                self.assertTrue(any(f.startswith(f"observation -> {target}") for f in found), found)

    def test_workflow_engine_depends_on_nothing_internal(self) -> None:
        found = problems({**ALLOWED, "workflow-engine": ["storage"]})
        self.assertTrue(any(f.startswith("workflow-engine -> storage") for f in found), found)

    def test_adapter_detected_by_location(self) -> None:
        crates, _ = checker.load_graph(metadata({}))
        self.assertTrue(crates["adapter-files"].is_adapter)
        self.assertFalse(crates["storage"].is_adapter)

    def test_missing_required_crate_reported(self) -> None:
        self.assertEqual(checker.missing_crates(set(checker.REQUIRED_CRATES) - {"storage"}), ["storage"])
        self.assertEqual(checker.missing_crates(CRATE_DIRS), [])

    def test_main_fails_on_violation(self) -> None:
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.json"
            path.write_text(json.dumps(metadata({**ALLOWED, "local-ai": ["adapter-files"]})), encoding="utf-8")
            self.assertEqual(checker.main(["--metadata", str(path)]), 1)
            path.write_text(json.dumps(metadata(ALLOWED)), encoding="utf-8")
            self.assertEqual(checker.main(["--metadata", str(path)]), 0)


if __name__ == "__main__":
    unittest.main()
