#!/usr/bin/env python3
"""Record a benchmark command, exit code, timings and machine metadata without hiding failures."""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from common import metadata, write_report

# Cargo can emit Unicode diagnostics even when Windows defaults to a legacy console encoding.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", required=True, type=Path)
parser.add_argument("command", nargs=argparse.REMAINDER)
args = parser.parse_args()
command = args.command[1:] if args.command[:1] == ["--"] else args.command
if not command:
    parser.error("a command is required")
environment = metadata()
started = time.perf_counter()
result = subprocess.run(command, text=True, encoding="utf-8", errors="replace", capture_output=True,
                        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
write_report(args.output, {"environment": environment, "command": command, "exit_code": result.returncode,
                         "elapsed_seconds": round(time.perf_counter() - started, 3),
                         "stdout": result.stdout, "stderr": result.stderr})
print(result.stdout)
print(result.stderr)
raise SystemExit(result.returncode)
