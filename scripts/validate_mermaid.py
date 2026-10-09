#!/usr/bin/env python3
"""Render every Mermaid block in the repository's Markdown files to catch syntax errors.

Each ```mermaid fenced block is written to a temporary .mmd file and rendered with the
Mermaid CLI (mmdc). A block that fails to render is reported with its file and line number.

Usage:
    python3 scripts/validate_mermaid.py --mmdc node_modules/.bin/mmdc \
        [--puppeteer-config scripts/puppeteer-config.json] [paths...]

Exit status: 0 if all blocks render, 1 if any block fails, 2 on usage errors.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIRS = frozenset({".git", "node_modules", "target", "dist", ".venv", ".localloop-dev"})
RENDER_TIMEOUT_SECONDS = 120


@dataclass(frozen=True)
class MermaidBlock:
    """A Mermaid diagram extracted from a Markdown file."""

    source_file: Path
    start_line: int
    text: str


def iter_markdown_files(roots: list[Path]) -> list[Path]:
    """Return Markdown files under the given roots, skipping build and dependency folders."""
    files: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix == ".md":
            files.append(root)
            continue
        for path in sorted(root.rglob("*.md")):
            if not any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
                files.append(path)
    return files


def extract_blocks(path: Path) -> list[MermaidBlock]:
    """Extract fenced ```mermaid blocks; raise ValueError on an unterminated block."""
    blocks: list[MermaidBlock] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    inside = False
    start = 0
    buffer: list[str] = []
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not inside and stripped == "```mermaid":
            inside = True
            start = number
            buffer = []
        elif inside and stripped == "```":
            inside = False
            blocks.append(MermaidBlock(path, start, "\n".join(buffer) + "\n"))
        elif inside:
            buffer.append(line)
    if inside:
        raise ValueError(f"{path}:{start}: unterminated mermaid block")
    return blocks


def render(block: MermaidBlock, mmdc: str, puppeteer_config: Path | None, workdir: Path, index: int) -> str | None:
    """Render one block; return None on success or the error output on failure."""
    source = workdir / f"block_{index}.mmd"
    target = workdir / f"block_{index}.svg"
    source.write_text(block.text, encoding="utf-8")
    command = [mmdc, "--quiet", "-i", str(source), "-o", str(target)]
    if puppeteer_config is not None:
        command += ["-p", str(puppeteer_config)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=RENDER_TIMEOUT_SECONDS, check=False)
    except subprocess.TimeoutExpired:
        return f"render timed out after {RENDER_TIMEOUT_SECONDS}s"
    if result.returncode != 0 or not target.exists():
        return (result.stderr or result.stdout or "unknown error").strip()
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", type=Path, help="Files or folders to scan (default: repository root)")
    parser.add_argument("--mmdc", default=shutil.which("mmdc") or "", help="Path to the Mermaid CLI executable")
    parser.add_argument("--puppeteer-config", type=Path, default=None, help="Puppeteer config JSON passed to mmdc")
    args = parser.parse_args()

    if not args.mmdc:
        print("error: Mermaid CLI not found; pass --mmdc", file=sys.stderr)
        return 2

    roots = [p.resolve() for p in args.paths] if args.paths else [REPO_ROOT]
    try:
        blocks = [block for path in iter_markdown_files(roots) for block in extract_blocks(path)]
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    failures = 0
    with tempfile.TemporaryDirectory(prefix="mermaid-check-") as tmp:
        for index, block in enumerate(blocks):
            location = f"{block.source_file.relative_to(REPO_ROOT)}:{block.start_line}"
            error = render(block, args.mmdc, args.puppeteer_config, Path(tmp), index)
            if error is None:
                print(f"ok    {location}")
            else:
                failures += 1
                print(f"FAIL  {location}\n{error}\n", file=sys.stderr)

    print(f"\n{len(blocks) - failures}/{len(blocks)} Mermaid blocks rendered successfully.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
