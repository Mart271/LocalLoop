#!/usr/bin/env python3
"""Enforce LocalLoop's crate dependency rules (NFR-030, LL-004).

The rules come from SYSTEM_ARCHITECTURE.md §6.1. A dependency is forbidden whether it is direct
or transitive through other workspace crates, and whatever its kind (normal, build, or dev), so
that, for example, `local-ai` can never name an adapter type even through a helper crate.

Forbidden:
  local-ai          -> policy-engine, execution-engine, adapters/*, storage
  adapters/*        -> local-ai
  observation       -> execution-engine, adapters/*
  workflow-engine   -> any other workspace crate

The script also checks that every crate the architecture requires exists in the workspace.

Usage:
  python scripts/check_crate_deps.py                    # runs `cargo metadata`
  python scripts/check_crate_deps.py --metadata m.json  # uses saved metadata (tests)
Exit status: 0 when no rule is broken, 1 otherwise. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

# Package names of the crates the architecture requires (LL-001).
REQUIRED_CRATES = frozenset(
    {
        "workflow-engine",
        "policy-engine",
        "execution-engine",
        "verification-engine",
        "local-ai",
        "observation",
        "storage",
        "adapter-files",
        "adapter-documents",
        "adapter-spreadsheet",
    }
)


@dataclass(frozen=True)
class Crate:
    name: str
    manifest_dir: PurePath

    @property
    def is_adapter(self) -> bool:
        parts = self.manifest_dir.parts
        return any(a == "crates" and b == "adapters" for a, b in zip(parts, parts[1:]))


Selector = Callable[[Crate], bool]


def named(name: str) -> Selector:
    return lambda crate: crate.name == name


def adapters(crate: Crate) -> bool:
    return crate.is_adapter


def any_crate(_crate: Crate) -> bool:
    return True


@dataclass(frozen=True)
class Rule:
    source: Selector
    targets: tuple[Selector, ...]
    description: str


RULES: tuple[Rule, ...] = (
    Rule(
        named("local-ai"),
        (named("policy-engine"), named("execution-engine"), adapters, named("storage")),
        "local-ai must not depend on policy-engine, execution-engine, adapters, or storage",
    ),
    Rule(adapters, (named("local-ai"),), "adapters must not depend on local-ai"),
    Rule(
        named("observation"),
        (named("execution-engine"), adapters),
        "observation must not depend on execution-engine or adapters",
    ),
    Rule(named("workflow-engine"), (any_crate,), "workflow-engine must not depend on any internal crate"),
)


def _normalize(path: str) -> PurePath:
    return PurePath(Path(path).resolve()) if Path(path).is_absolute() else PurePath(path)


def load_graph(metadata: dict[str, Any]) -> tuple[dict[str, Crate], dict[str, set[str]]]:
    """Return workspace crates by name and internal dependency edges (all dependency kinds)."""
    members = set(metadata["workspace_members"])
    crates: dict[str, Crate] = {}
    by_dir: dict[PurePath, str] = {}
    for package in metadata["packages"]:
        if package["id"] not in members:
            continue
        manifest_dir = _normalize(str(PurePath(package["manifest_path"]).parent))
        crate = Crate(package["name"], manifest_dir)
        crates[crate.name] = crate
        by_dir[manifest_dir] = crate.name

    edges: dict[str, set[str]] = {name: set() for name in crates}
    for package in metadata["packages"]:
        if package["id"] not in members:
            continue
        for dependency in package.get("dependencies", []):
            path = dependency.get("path")
            if path is None:
                continue
            target = by_dir.get(_normalize(path))
            if target is not None and target != package["name"]:
                edges[package["name"]].add(target)
    return crates, edges


def reachable(start: str, edges: dict[str, set[str]]) -> dict[str, list[str]]:
    """Map every crate reachable from `start` to one dependency chain that reaches it."""
    chains: dict[str, list[str]] = {}
    stack: list[list[str]] = [[start]]
    while stack:
        chain = stack.pop()
        for target in sorted(edges.get(chain[-1], ())):
            if target not in chains and target != start:
                chains[target] = [*chain, target]
                stack.append(chains[target])
    return chains


def violations(crates: dict[str, Crate], edges: dict[str, set[str]]) -> list[str]:
    problems: list[str] = []
    for rule in RULES:
        for source in sorted(name for name, crate in crates.items() if rule.source(crate)):
            for target, chain in sorted(reachable(source, edges).items()):
                if any(select(crates[target]) for select in rule.targets):
                    problems.append(f"{' -> '.join(chain)}: {rule.description}")
    return problems


def missing_crates(crates: Iterable[str]) -> list[str]:
    return sorted(REQUIRED_CRATES - set(crates))


def cargo_metadata() -> dict[str, Any]:
    output = subprocess.run(
        ["cargo", "metadata", "--format-version", "1", "--no-deps", "--offline"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return json.loads(output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--metadata", type=Path, help="read `cargo metadata` JSON from this file")
    args = parser.parse_args(argv)

    metadata = json.loads(args.metadata.read_text(encoding="utf-8")) if args.metadata else cargo_metadata()
    crates, edges = load_graph(metadata)
    problems = [f"missing required crate '{name}'" for name in missing_crates(crates)]
    problems += violations(crates, edges)
    if problems:
        print("\n".join(f"FAIL  {problem}" for problem in problems))
        print(f"\n{len(problems)} crate dependency problem(s) found (NFR-030).")
        return 1
    edge_count = sum(len(targets) for targets in edges.values())
    print(f"Crate dependency rules hold: {len(crates)} workspace crates, {edge_count} internal edges.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
