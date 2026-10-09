#!/usr/bin/env python3
"""Validate the draft workflow schema, the example workflows, and the negative fixtures.

Checks:
  1. The schema itself is a valid JSON Schema (draft 2020-12).
  2. Every examples/workflows/*.workflow.json validates against the schema and passes
     lightweight consistency checks that a compiler would also apply:
       - step ids are unique;
       - every referenced location is declared, with the access the operation needs;
       - the declared operation list equals the operations the steps use (FR-102);
       - decision options have unique ids and a fallback option refers to one of them.
  3. Every tests/fixtures/schema/invalid/*.json is REJECTED by the schema.

This is a documentation check for the draft format, not the LocalLoop compiler.

Usage: python3 scripts/validate_schemas.py
Exit status: 0 on success, 1 on any failure.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "workflow" / "0.1" / "workflow.schema.json"
EXAMPLES_DIR = REPO_ROOT / "examples" / "workflows"
INVALID_DIR = REPO_ROOT / "tests" / "fixtures" / "schema" / "invalid"

CONTROL_OPS = frozenset({"control.for_each", "control.if", "control.decide", "control.stop_item", "human.approve"})
READ_OPS = frozenset({"files.list"})
WRITE_OPS = frozenset({"files.copy", "files.move", "files.rename", "report.write", "review.enqueue"})

JsonObject = dict[str, Any]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def iter_steps(steps: list[JsonObject]) -> Iterator[JsonObject]:
    """Yield every step, including steps nested in control constructs."""
    for step in steps:
        yield step
        for key in ("steps", "then", "else"):
            nested = step.get(key)
            if isinstance(nested, list):
                yield from iter_steps(nested)
        if step.get("op") == "control.decide":
            for option in step["params"]["options"]:
                yield from iter_steps(option["steps"])


def location_uses(step: JsonObject) -> Iterator[tuple[str, str]]:
    """Yield (location name, needed access) pairs referenced by a step."""
    op = step.get("op", "")
    params = step.get("params", {})
    if op in READ_OPS:
        yield params["location"], "read"
    if op in {"files.copy", "files.move", "files.rename"}:
        yield params["destination"]["location"], "write"
    if op == "report.write":
        yield params["location"], "write"
    if op == "review.enqueue" and "moveTo" in params:
        yield params["moveTo"]["location"], "write"
    if op == "sheet.upsert_rows":
        yield params["target"]["location"], "read_write"
    if op == "validate.record":
        for rule in params.get("rules", []):
            if rule.get("kind") == "notInSheet":
                yield rule["target"]["location"], "read"
    for post in step.get("postconditions", []):
        if post.get("kind") == "sheet.row_present":
            yield post["target"]["location"], "read"


def access_satisfies(granted: str, needed: str) -> bool:
    if granted == "read_write":
        return True
    if needed == "read_write":
        return False
    return granted == needed


def consistency_errors(workflow: JsonObject) -> list[str]:
    errors: list[str] = []
    steps = list(iter_steps(workflow["steps"]))

    seen: set[str] = set()
    for step in steps:
        if step["id"] in seen:
            errors.append(f"duplicate step id '{step['id']}'")
        seen.add(step["id"])

    locations: JsonObject = workflow["locations"]
    for step in steps:
        for name, needed in location_uses(step):
            if name not in locations:
                errors.append(f"step '{step['id']}' uses undeclared location '{name}'")
            elif not access_satisfies(locations[name]["access"], needed):
                errors.append(
                    f"step '{step['id']}' needs '{needed}' on location '{name}' "
                    f"but it is declared '{locations[name]['access']}'"
                )

    used_ops = {step["op"] for step in steps if step["op"] not in CONTROL_OPS}
    declared_ops = set(workflow["permissions"]["operations"])
    for op in sorted(used_ops - declared_ops):
        errors.append(f"operation '{op}' is used but not declared in permissions.operations")
    for op in sorted(declared_ops - used_ops):
        errors.append(f"operation '{op}' is declared but no step uses it (FR-102)")

    for step in steps:
        if step["op"] != "control.decide":
            continue
        option_ids = [option["id"] for option in step["params"]["options"]]
        if len(option_ids) != len(set(option_ids)):
            errors.append(f"decision '{step['id']}' has duplicate option ids")
        fallback = step["params"]["fallback"]
        if fallback["kind"] == "option" and fallback["optionId"] not in option_ids:
            errors.append(f"decision '{step['id']}' fallback refers to unknown option '{fallback['optionId']}'")

    if workflow["executionMode"] == "exact_replay" and any(s["op"] == "control.decide" for s in steps):
        errors.append("exact_replay workflow contains a decision point (SRS §13.4)")
    return errors


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    failures = 0

    examples = sorted(EXAMPLES_DIR.glob("*.workflow.json"))
    if not examples:
        print(f"FAIL  no example workflows found in {EXAMPLES_DIR.relative_to(REPO_ROOT)}")
        return 1
    for path in examples:
        rel = path.relative_to(REPO_ROOT)
        workflow = load_json(path)
        schema_errors = sorted(validator.iter_errors(workflow), key=lambda e: list(e.absolute_path))
        if schema_errors:
            failures += 1
            print(f"FAIL  {rel}")
            for error in schema_errors[:10]:
                pointer = "/" + "/".join(str(p) for p in error.absolute_path)
                print(f"      {pointer}: {error.message[:300]}")
            continue
        problems = consistency_errors(workflow)
        if problems:
            failures += 1
            print(f"FAIL  {rel}")
            for problem in problems:
                print(f"      {problem}")
        else:
            print(f"ok    {rel} (valid)")

    for path in sorted(INVALID_DIR.glob("*.json")):
        rel = path.relative_to(REPO_ROOT)
        if validator.is_valid(load_json(path)):
            failures += 1
            print(f"FAIL  {rel} was accepted but must be rejected")
        else:
            print(f"ok    {rel} (rejected as expected)")

    print("\nAll schema checks passed." if failures == 0 else f"\n{failures} schema check(s) failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
