#!/usr/bin/env python3
"""EV-06 / LL-007: offline subprocess comparison on synthetic F1/F2.

Models must already exist locally; this script never downloads them. The score measures
ground-truth field text presence, not extraction correctness or calibrated confidence.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, digest, metadata, write_report

sys.path.insert(0, str(ROOT / "tools/fixtures"))
from fixture_model import VENDORS


def normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.casefold())


def expected(record: dict) -> dict[str, str]:
    result = dict(record)
    vendor = next(v for v in VENDORS if v.name == record["vendor_name"])
    result["invoice_date"] = date.fromisoformat(record["invoice_date"]).strftime(vendor.date_format)
    return result


def score(text: str, record: dict) -> dict[str, bool]:
    haystack = normalized(text)
    return {key: normalized(str(value)) in haystack for key, value in expected(record).items()}


def prepare(source: Path, target: Path) -> None:
    if source.suffix.lower() == ".pdf":
        with pdfium.PdfDocument(source) as document:
            page = document[0]
            bitmap = page.render(scale=200 / 72, grayscale=True)
            bitmap.to_pil().save(target)
            bitmap.close()
            page.close()
    else:
        with Image.open(source) as image:
            image.convert("L").save(target)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ocrs", type=Path, required=True)
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--tesseract", default="tesseract")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    models = {n: args.models.resolve() / n for n in ("text-detection.onnx", "text-recognition.onnx")}
    for path in models.values():
        if not path.is_file():
            parser.error(f"missing local model: {path}")
    report = {"environment": metadata(), "models": {
        n: {"bytes": p.stat().st_size, "sha256": digest(p)} for n, p in models.items()
    }, "tesseract_version": subprocess.check_output([args.tesseract, "--version"], text=True).splitlines()[0],
        "ocrs_version": "0.13.1", "samples": [],
        "method": "7 normalized field-text presence checks/page; case, whitespace and punctuation ignored; no field attribution; fresh process/page; 200 DPI PDF rendering; no deskew or denoise",
    }
    cases: list[tuple[str, Path, dict]] = []
    fixtures = ROOT / "tests/fixtures/generated"
    f1 = json.loads((fixtures / "F1-consistent/truth.json").read_text())["files"]
    for name, entry in sorted(f1.items()):
        # Five invoices for each of the three vendor templates.
        if int(name.rsplit("-", 1)[1].split(".")[0]) <= 5:
            cases.append(("F1-rasterized", fixtures / "F1-consistent" / name, entry))
    f2 = json.loads((fixtures / "F2-scanned/truth.json").read_text())["files"]
    cases.extend((f"F2-{e['quality']}", fixtures / "F2-scanned" / n, e) for n, e in sorted(f2.items()))
    with tempfile.TemporaryDirectory(prefix="localloop-ocr-") as temporary:
        folder = Path(temporary)
        for index, (group, source, entry) in enumerate(cases):
            image = folder / f"{index}.png"
            prepare(source, image)
            commands = {
                "tesseract": [args.tesseract, str(image), "stdout", "-l", "eng", "--psm", "3", "tsv"],
                "ocrs": [str(args.ocrs.resolve()), "--detect-model", str(models["text-detection.onnx"]),
                         "--rec-model", str(models["text-recognition.onnx"]), str(image)],
            }
            for engine, command in commands.items():
                started = time.perf_counter()
                # Fixed parallelism: compare one page at a time, with four CPU threads per engine.
                environment = dict(os.environ, OMP_THREAD_LIMIT="4", RAYON_NUM_THREADS="4", RTEN_NUM_THREADS="4")
                completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                           timeout=120, env=environment)
                elapsed = (time.perf_counter() - started) * 1000
                confidence = None
                text = completed.stdout
                if engine == "tesseract" and completed.returncode == 0:
                    words = [w for w in csv.DictReader(io.StringIO(text), delimiter="\t") if w.get("text", "").strip()]
                    text = " ".join(w["text"] for w in words)
                    values = [float(w["conf"]) for w in words if float(w["conf"]) >= 0]
                    confidence = statistics.mean(values) if values else None
                fields = score(text, entry["record"]) if completed.returncode == 0 else {k: False for k in entry["record"]}
                sample = {"engine": engine, "group": group, "file": source.name, "input_sha256": digest(image),
                          "exit_code": completed.returncode, "elapsed_ms": round(elapsed, 2), "fields": fields,
                          "all_fields_present": all(fields.values()), "mean_word_confidence": confidence}
                if completed.returncode != 0:
                    sample["error"] = completed.stderr[-1000:]
                report["samples"].append(sample)
            print(f"OCR {index + 1}/{len(cases)} {source.name}", flush=True)
    report["summary"] = []
    for engine in ("tesseract", "ocrs"):
        for group in sorted({c[0] for c in cases}):
            samples = [s for s in report["samples"] if s["engine"] == engine and s["group"] == group]
            report["summary"].append({"engine": engine, "group": group, "n": len(samples),
                "fields_present": sum(sum(s["fields"].values()) for s in samples), "fields_total": len(samples) * 7,
                "all_fields_pages": sum(s["all_fields_present"] for s in samples),
                "median_ms": round(statistics.median(s["elapsed_ms"] for s in samples), 2),
                "errors": sum(s["exit_code"] != 0 for s in samples)})
    write_report(args.output, report)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
