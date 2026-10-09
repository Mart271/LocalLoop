"""Development-only benchmark metadata. Never imported by product code."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata() -> dict:
    def command(args: list[str]) -> str:
        return subprocess.check_output(args, cwd=ROOT, text=True, encoding="utf-8").strip()

    hardware = json.loads(command([
        "powershell", "-NoProfile", "-Command",
        "$c = Get-CimInstance Win32_ComputerSystem; "
        "$p = Get-CimInstance Win32_Processor; "
        "$o = Get-CimInstance Win32_OperatingSystem; "
        "@{manufacturer=$c.Manufacturer;model=$c.Model;cpu=$p.Name;"
        "ram_bytes=$c.TotalPhysicalMemory;os=$o.Caption;build=$o.BuildNumber} | ConvertTo-Json -Compress",
    ]))
    return {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "hardware": hardware,
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "rust": command(["rustc", "-V"]),
        "node": command(["node", "--version"]),
        "packages": {p: importlib.metadata.version(p) for p in ("pillow", "pypdfium2", "reportlab", "openpyxl")},
        "fixture_manifest_sha256": digest(ROOT / "tests/fixtures/manifest.json"),
        "fixture_seed": 20261009,
        "model": "none unless explicitly recorded by the benchmark",
        "reference_machine": False,
        "macos": "deferred by owner on 2026-10-10",
    }


def write_report(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
