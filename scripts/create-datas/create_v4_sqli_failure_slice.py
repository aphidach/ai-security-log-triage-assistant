#!/usr/bin/env python3
"""Create the Phase 8 v4 SQLi boundary failure slice.

This report is a pre-training diagnostic artifact. It reads the v3.5
temperature=0, 2048-token hard-contrast probe and the hard-contrast source
examples, then writes machine-readable and human-readable failure slices for
v4 dataset planning. It intentionally does not read the fixed test split.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

SOURCE_REPORT_PATH = (
    ROOT
    / "reports"
    / "phase-6"
    / "openai-compatible-vllm-structured-outputs-v3-5-temp-0-2048-hard-contrast-memorization-probe.json"
)
SOURCE_SPLIT_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"
OUTPUT_JSON_PATH = ROOT / "reports" / "phase-8" / "phase-8-v4-sqli-boundary-failure-slice.json"
OUTPUT_MD_PATH = ROOT / "reports" / "phase-8" / "phase-8-v4-sqli-boundary-failure-slice.md"

CREATED_DATE = "2026-05-22"

JsonObject = dict[str, Any]


BUCKET_DETAILS: dict[str, dict[str, str]] = {
    "normal_to_bruteforce": {
        "title": "Normal -> brute force",
        "diagnosis": "Single failed-login or low-signal auth events can still be escalated.",
        "suggested_repair_pattern": (
            "Add normal guard examples with failed_attempts=1, repeated=1, count=1, "
            "lockout=false, correlation=none, and no burst window."
        ),
    },
    "sqli_to_invalid": {
        "title": "SQLi -> invalid",
        "diagnosis": "Quote-heavy SQLi evidence can still break deterministic structured output.",
        "suggested_repair_pattern": (
            "Add quote-heavy SQLi positives with evidence substrings that require JSON escaping, "
            "but keep each evidence item short and exact."
        ),
    },
    "sqli_to_normal": {
        "title": "SQLi -> normal",
        "diagnosis": "SQL vocabulary or schema discovery can be underweighted in routine-looking logs.",
        "suggested_repair_pattern": (
            "Add SQLi positives with information_schema, encoded tautologies, and SQL comments, "
            "paired with benign SQL documentation/search hard negatives."
        ),
    },
    "sqli_to_traversal": {
        "title": "SQLi -> traversal",
        "diagnosis": "SQL quote/comment syntax is still confused with path traversal/file-read syntax.",
        "suggested_repair_pattern": (
            "Add SQLi-vs-traversal contrast examples where SQL comment markers, UNION, SLEEP, "
            "WAITFOR, and encoded quotes are separate from ../, /etc/passwd, and php://filter."
        ),
    },
    "other_label_failure": {
        "title": "Other label failure",
        "diagnosis": "A label failure outside the planned v4 SQLi-first buckets.",
        "suggested_repair_pattern": "Review manually before broadening the v4 scope.",
    },
}


DATASET_IMPLICATIONS = [
    {
        "bucket": "SQLi positives",
        "target": "80 examples",
        "details": (
            "Emphasize quote-heavy payloads, SQL comments, UNION SELECT, SLEEP/WAITFOR, "
            "information_schema, encoded tautologies, and status/severity cues."
        ),
    },
    {
        "bucket": "Normal hard negatives",
        "target": "40 examples",
        "details": (
            "Cover benign SQL documentation/search terms, single auth failures, normalized relative "
            "paths, and approved low-scope monitoring."
        ),
    },
    {
        "bucket": "Brute-force positives",
        "target": "10 examples",
        "details": "Keep a small guard set for repeated failures so anti-gravity examples do not erase recall.",
    },
    {
        "bucket": "Traversal positives",
        "target": "20 examples",
        "details": "Keep traversal token ownership clear with ../, encoded traversal, sensitive files, and wrappers.",
    },
    {
        "bucket": "Port/recon positives",
        "target": "10 examples",
        "details": "Keep recon recall guarded with unique port/host thresholds and scanner signatures.",
    },
]


def read_json(path: Path) -> JsonObject:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl_by_id(path: Path) -> dict[str, JsonObject]:
    records: dict[str, JsonObject] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        record_id = record.get("id")
        if not isinstance(record_id, str):
            raise ValueError(f"{path}:{line_no}: missing string id")
        if record_id in records:
            raise ValueError(f"{path}:{line_no}: duplicate id {record_id}")
        records[record_id] = record
    return records


def normalized_predicted_label(sample: JsonObject) -> str:
    predicted = sample.get("predicted_label")
    return predicted if isinstance(predicted, str) else "<invalid>"


def bucket_for(expected_label: str, predicted_label: str) -> str:
    if expected_label == "normal" and predicted_label == "failed_login_bruteforce":
        return "normal_to_bruteforce"
    if expected_label == "sql_injection_attempt" and predicted_label == "<invalid>":
        return "sqli_to_invalid"
    if expected_label == "sql_injection_attempt" and predicted_label == "normal":
        return "sqli_to_normal"
    if expected_label == "sql_injection_attempt" and predicted_label == "directory_traversal_attempt":
        return "sqli_to_traversal"
    return "other_label_failure"


def compact_metadata(metadata: JsonObject | None) -> JsonObject:
    if not isinstance(metadata, dict):
        return {}
    return {
        "model": metadata.get("model"),
        "base_url": metadata.get("base_url"),
        "config_path": metadata.get("config_path"),
        "response_format_requested": metadata.get("response_format_requested"),
        "response_format_mode": metadata.get("response_format_mode"),
        "prompt_version": metadata.get("prompt_version"),
        "max_tokens": metadata.get("max_tokens"),
        "max_retries": metadata.get("max_retries"),
        "request_options": metadata.get("request_options"),
        "extra_body": metadata.get("extra_body"),
    }


def build_failure_cases(report: JsonObject, source_records: dict[str, JsonObject]) -> list[JsonObject]:
    failures: list[JsonObject] = []
    for sample in report["samples"]:
        if sample.get("label_correct") is True:
            continue

        sample_id = sample["id"]
        source = source_records.get(sample_id)
        if source is None:
            raise ValueError(f"source split is missing sample id {sample_id}")

        expected = sample["expected_label"]
        predicted = normalized_predicted_label(sample)
        bucket_key = bucket_for(expected, predicted)
        bucket = BUCKET_DETAILS[bucket_key]
        expected_output = source.get("output") or {}
        prediction = sample.get("prediction") or {}

        failures.append(
            {
                "id": sample_id,
                "failure_bucket": bucket_key,
                "failure_bucket_title": bucket["title"],
                "input_log": source["input"],
                "expected_label": expected,
                "predicted_label": predicted,
                "expected_severity": sample.get("expected_severity"),
                "predicted_severity": sample.get("predicted_severity"),
                "json_parse_success": sample.get("json_parse_success"),
                "schema_success": sample.get("schema_success"),
                "expected_evidence": expected_output.get("evidence", []),
                "predicted_evidence": prediction.get("evidence", []),
                "diagnosis": bucket["diagnosis"],
                "suggested_repair_pattern": bucket["suggested_repair_pattern"],
                "raw_prediction_prefix": str(sample.get("raw_prediction", ""))[:160],
            }
        )
    return failures


def make_bucket_summary(failure_cases: list[JsonObject]) -> list[JsonObject]:
    by_bucket: dict[str, list[JsonObject]] = defaultdict(list)
    for item in failure_cases:
        by_bucket[str(item["failure_bucket"])].append(item)

    summary: list[JsonObject] = []
    for bucket_key, cases in sorted(by_bucket.items()):
        bucket = BUCKET_DETAILS[bucket_key]
        summary.append(
            {
                "bucket": bucket_key,
                "title": bucket["title"],
                "count": len(cases),
                "ids": [case["id"] for case in cases],
                "diagnosis": bucket["diagnosis"],
                "suggested_repair_pattern": bucket["suggested_repair_pattern"],
            }
        )
    return summary


def build_report() -> JsonObject:
    report = read_json(SOURCE_REPORT_PATH)
    source_records = read_jsonl_by_id(SOURCE_SPLIT_PATH)
    failure_cases = build_failure_cases(report, source_records)
    bucket_summary = make_bucket_summary(failure_cases)

    expected_distribution = Counter(str(item["expected_label"]) for item in report["samples"])
    predicted_distribution = Counter(normalized_predicted_label(item) for item in report["samples"])

    return {
        "summary": (
            "v4 slices the v3.5 temperature=0 2048-token hard-contrast failures so the next "
            "repair can target SQLi/quote boundaries while preserving normal/brute-force guards "
            "without using the fixed test split."
        ),
        "created_date": CREATED_DATE,
        "source_report_path": str(SOURCE_REPORT_PATH.relative_to(ROOT)),
        "source_split_path": str(SOURCE_SPLIT_PATH.relative_to(ROOT)),
        "fixed_test_split_used": False,
        "metrics": report.get("metrics", {}),
        "runtime_context": compact_metadata(report.get("adapter_metadata")),
        "sample_count": len(report["samples"]),
        "label_failure_count": len(failure_cases),
        "expected_label_distribution": dict(sorted(expected_distribution.items())),
        "predicted_label_distribution": dict(sorted(predicted_distribution.items())),
        "bucket_summary": bucket_summary,
        "failure_cases": failure_cases,
        "dataset_implications": DATASET_IMPLICATIONS,
        "next_step": (
            "Create the v4 SQLi-first supplement from these buckets, then train and probe v4 on "
            "hard-contrast before any mini semantic or future fixed comparison."
        ),
    }


def md_table_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value).replace("\n", " ") for value in values) + " |"


def write_markdown(report: JsonObject) -> None:
    lines: list[str] = [
        "# Phase 8 V4 SQLi Boundary Failure Slice",
        "",
        "**Summary**",
        "",
        str(report["summary"]),
        "",
        "**Sources**",
        "",
        f"- `{report['source_report_path']}` for v3.5 temp 0 2048 runtime probe predictions and metrics.",
        f"- `{report['source_split_path']}` for source log lines and expected outputs.",
        "- `docs/output-structure-fix/phase-6-v3-5-boundary-repair-plan.md` for v3.5 closure context.",
        "- `reports/phase-7/comparison.md` for Phase 7 historical context, not tuning examples.",
        "",
        "**Last updated**",
        "",
        str(report["created_date"]),
        "",
        "## Run Snapshot",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        md_table_row(["Samples", f"`{report['sample_count']}`"]),
        md_table_row(["Label failures", f"`{report['label_failure_count']}`"]),
        md_table_row(["Label accuracy", f"`{report['metrics'].get('label_accuracy')}`"]),
        md_table_row(["JSON parse success", f"`{report['metrics'].get('json_parse_success_rate')}`"]),
        md_table_row(["Schema success", f"`{report['metrics'].get('schema_success_rate')}`"]),
        md_table_row(["Invalid outputs", f"`{report['metrics'].get('invalid_output_count')}`"]),
        md_table_row(["Severity accuracy", f"`{report['metrics'].get('severity_accuracy')}`"]),
        md_table_row(["Evidence partial match", f"`{report['metrics'].get('evidence_partial_match')}`"]),
        "",
        "Expected label distribution:",
        "",
        "```json",
        json.dumps(report["expected_label_distribution"], indent=2, sort_keys=True),
        "```",
        "",
        "Predicted label distribution:",
        "",
        "```json",
        json.dumps(report["predicted_label_distribution"], indent=2, sort_keys=True),
        "```",
        "",
        "## Bucket Summary",
        "",
        "| Bucket | Count | IDs | Diagnosis | Repair pattern |",
        "| --- | ---: | --- | --- | --- |",
    ]

    for bucket in report["bucket_summary"]:
        lines.append(
            md_table_row(
                [
                    bucket["title"],
                    f"`{bucket['count']}`",
                    ", ".join(f"`{item}`" for item in bucket["ids"]),
                    bucket["diagnosis"],
                    bucket["suggested_repair_pattern"],
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Failure Cases",
            "",
            "| ID | Expected | Predicted | Bucket | Expected evidence | Predicted evidence | Repair cue |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    for case in report["failure_cases"]:
        lines.append(
            md_table_row(
                [
                    f"`{case['id']}`",
                    f"`{case['expected_label']}`",
                    f"`{case['predicted_label']}`",
                    case["failure_bucket_title"],
                    "; ".join(str(item) for item in case["expected_evidence"]),
                    "; ".join(str(item) for item in case["predicted_evidence"]),
                    case["suggested_repair_pattern"],
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Dataset Implications",
            "",
            "| Bucket | Target | Details |",
            "| --- | ---: | --- |",
        ]
    )
    for item in report["dataset_implications"]:
        lines.append(md_table_row([item["bucket"], item["target"], item["details"]]))

    lines.extend(
        [
            "",
            "## Hold Fixed Test",
            "",
            "`data/splits/test.jsonl` must not be used for selecting v4 repair cases or tuning prompts/runtime settings.",
            "",
            "## Next Step",
            "",
            str(report["next_step"]),
        ]
    )

    OUTPUT_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    OUTPUT_JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print(f"Wrote {OUTPUT_JSON_PATH.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MD_PATH.relative_to(ROOT)}")
    print("Fixed test split was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
