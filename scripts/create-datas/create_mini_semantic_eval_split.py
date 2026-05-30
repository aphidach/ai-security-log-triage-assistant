#!/usr/bin/env python3
"""Create the Phase 5 mini semantic eval split.

The split is intentionally validation-derived and label-balanced so Phase 5 can
inspect semantic behavior before touching the fixed test split.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "data" / "splits" / "validation.jsonl"
DEFAULT_OUT = ROOT / "data" / "splits" / "mini-semantic-eval.jsonl"
DEFAULT_EXCLUDES = (
    ROOT / "data" / "splits" / "test.jsonl",
    ROOT / "data" / "splits" / "smoke-output-contract.jsonl",
)
LABELS = (
    "normal",
    "failed_login_bruteforce",
    "sql_injection_attempt",
    "directory_traversal_attempt",
    "port_scan_or_recon",
)


JsonObject = dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a balanced mini semantic eval JSONL split.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Source JSONL split.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output JSONL split.")
    parser.add_argument("--per-label", type=int, default=5, help="Number of examples per label.")
    parser.add_argument(
        "--exclude",
        type=Path,
        action="append",
        default=list(DEFAULT_EXCLUDES),
        help="JSONL split whose ids must not appear in the output. Can be passed more than once.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite --out if it already exists.")
    return parser.parse_args()


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def load_jsonl(path: Path, *, strict: bool) -> tuple[list[JsonObject], list[str]]:
    records: list[JsonObject] = []
    warnings: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            message = f"{path}:{line_number}: invalid JSONL record: {exc}"
            if strict:
                raise ValueError(message) from exc
            warnings.append(message)
            continue
        if not isinstance(item, dict):
            message = f"{path}:{line_number}: JSONL record must be an object"
            if strict:
                raise ValueError(message)
            warnings.append(message)
            continue
        records.append(item)
    return records, warnings


def load_excluded_ids(paths: list[Path]) -> set[str]:
    excluded_ids: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        records, _ = load_jsonl(path, strict=True)
        for record in records:
            record_id = record.get("id")
            if isinstance(record_id, str):
                excluded_ids.add(record_id)
    return excluded_ids


def select_records(records: list[JsonObject], *, per_label: int, excluded_ids: set[str]) -> list[JsonObject]:
    selected: list[JsonObject] = []
    counts: Counter[str] = Counter()
    for record in records:
        record_id = record.get("id")
        if isinstance(record_id, str) and record_id in excluded_ids:
            continue
        output = record.get("output")
        label = output.get("label") if isinstance(output, dict) else None
        if label not in LABELS or counts[str(label)] >= per_label:
            continue
        validate_record(record)
        selected.append(record)
        counts[str(label)] += 1

    missing = {label: per_label - counts[label] for label in LABELS if counts[label] < per_label}
    if missing:
        detail = ", ".join(f"{label} needs {needed}" for label, needed in missing.items())
        raise ValueError(f"Not enough source records for balanced split: {detail}")
    return selected


def validate_record(record: JsonObject) -> None:
    record_id = record.get("id", "<missing>")
    log_line = record.get("input")
    output = record.get("output")
    if not isinstance(record_id, str) or not record_id:
        raise ValueError("selected record has missing id")
    if not isinstance(log_line, str) or not log_line:
        raise ValueError(f"{record_id}: selected record has missing input")
    if not isinstance(output, dict):
        raise ValueError(f"{record_id}: selected record has missing output object")
    evidence = output.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError(f"{record_id}: selected record has missing evidence")
    for item in evidence:
        if not isinstance(item, str) or not item:
            raise ValueError(f"{record_id}: evidence values must be non-empty strings")
        if item not in log_line:
            raise ValueError(f"{record_id}: evidence is not a substring of input: {item!r}")


def write_jsonl(records: list[JsonObject], path: Path, *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; pass --force to overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    if args.per_label < 1:
        raise SystemExit("--per-label must be at least 1")

    source = repo_path(args.source)
    out = repo_path(args.out)
    excludes = [repo_path(path) for path in args.exclude]

    try:
        source_records, warnings = load_jsonl(source, strict=False)
        excluded_ids = load_excluded_ids(excludes)
        selected = select_records(source_records, per_label=args.per_label, excluded_ids=excluded_ids)
        write_jsonl(selected, out, force=args.force)
    except Exception as exc:
        raise SystemExit(f"error: {exc}") from exc

    for warning in warnings:
        print(f"warning: skipped source line: {warning}", file=sys.stderr)

    counts = Counter(str(record["output"]["label"]) for record in selected)
    print(f"wrote: {out.relative_to(ROOT)}")
    print(f"samples: {len(selected)}")
    for label in LABELS:
        print(f"{label}: {counts[label]}")


if __name__ == "__main__":
    main()
