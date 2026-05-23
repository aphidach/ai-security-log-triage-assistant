#!/usr/bin/env python3
"""Create the Phase 8 v4.6 Qwen3.5 normal/severity calibration slice.

The slice reads only the v4.5 Qwen LoRA hard-contrast report and the
hard-contrast source split. It does not read the fixed test split.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

V4_5_REPORT_PATH = (
    ROOT
    / "reports"
    / "openai-compatible-vllm-structured-outputs-qwen3.5-8B—v1temp-0-hard-contrast-memorization-probe.json"
)
SOURCE_SPLIT_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"
OUTPUT_JSON_PATH = ROOT / "reports" / "phase-8-v4-6-qwen35-normal-calibration-slice.json"
OUTPUT_MD_PATH = ROOT / "reports" / "phase-8-v4-6-qwen35-normal-calibration-slice.md"

CREATED_DATE = "2026-05-23"

JsonObject = dict[str, Any]


BUCKET_DETAILS: dict[str, dict[str, str]] = {
    "normal_to_bruteforce": {
        "title": "Normal -> brute force",
        "diagnosis": "Single or low-volume auth failures are over-escalated into brute force.",
        "suggested_repair_pattern": (
            "Add normal auth negatives with failures=1-2, no burst window, no repeated source, "
            "and no account lockout."
        ),
    },
    "normal_to_sqli": {
        "title": "Normal -> SQLi",
        "diagnosis": "Benign text containing words like union or SQL training vocabulary is over-alerted.",
        "suggested_repair_pattern": (
            "Add benign documentation/search examples containing SQL words without quote, comment, "
            "tautology, stacked query, or blocked WAF evidence."
        ),
    },
    "normal_to_traversal": {
        "title": "Normal -> traversal",
        "diagnosis": "Normalized relative paths under allowed docs/static routes are over-alerted.",
        "suggested_repair_pattern": (
            "Add normal normalized-path examples where the route is documentation/static content, "
            "status is successful, and no sensitive file target is present."
        ),
    },
    "bruteforce_severity_high": {
        "title": "Brute force severity too high",
        "diagnosis": "Medium brute-force indicators are labelled correctly but escalated to high.",
        "suggested_repair_pattern": (
            "Add medium brute-force positives with repeated failures but limited blast radius, "
            "no admin compromise evidence, and no distributed spray."
        ),
    },
    "port_recon_severity_medium": {
        "title": "Port/recon severity too low",
        "diagnosis": "Clear nmap/SYN/horizontal scan indicators are labelled correctly but lowered to medium.",
        "suggested_repair_pattern": (
            "Add high-severity recon positives with explicit nmap/SYN scan or broad host/port enumeration."
        ),
    },
    "evidence_miss": {
        "title": "Evidence miss",
        "diagnosis": "The label is correct, but evidence is incomplete or does not match the expected substring.",
        "suggested_repair_pattern": "Keep exact evidence substrings short and copied from the log line.",
    },
}


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
        "timeout_seconds": metadata.get("timeout_seconds"),
        "request_options": metadata.get("request_options"),
    }


def bucket_for(sample: JsonObject) -> str | None:
    expected_label = sample["expected_label"]
    predicted_label = sample.get("predicted_label")

    if sample.get("label_correct") is not True:
        if expected_label == "normal" and predicted_label == "failed_login_bruteforce":
            return "normal_to_bruteforce"
        if expected_label == "normal" and predicted_label == "sql_injection_attempt":
            return "normal_to_sqli"
        if expected_label == "normal" and predicted_label == "directory_traversal_attempt":
            return "normal_to_traversal"
        raise ValueError(f"unexpected v4.5 label failure: {sample['id']} {expected_label}->{predicted_label}")

    if sample.get("severity_correct") is not True:
        if expected_label == "failed_login_bruteforce" and sample.get("predicted_severity") == "high":
            return "bruteforce_severity_high"
        if expected_label == "port_scan_or_recon" and sample.get("predicted_severity") == "medium":
            return "port_recon_severity_medium"
        raise ValueError(
            f"unexpected v4.5 severity failure: {sample['id']} "
            f"{sample.get('expected_severity')}->{sample.get('predicted_severity')}"
        )

    if sample.get("evidence_partial_match") is not True:
        return "evidence_miss"

    return None


def build_cases(report: JsonObject, source_records: dict[str, JsonObject]) -> list[JsonObject]:
    cases: list[JsonObject] = []
    for sample in report["samples"]:
        bucket_key = bucket_for(sample)
        if bucket_key is None:
            continue

        source = source_records.get(sample["id"])
        if source is None:
            raise ValueError(f"source split is missing sample id {sample['id']}")
        bucket = BUCKET_DETAILS[bucket_key]
        prediction = sample.get("prediction") or {}
        expected_output = source.get("output") or {}

        cases.append(
            {
                "id": sample["id"],
                "failure_bucket": bucket_key,
                "failure_bucket_title": bucket["title"],
                "input_log": source["input"],
                "expected_label": sample["expected_label"],
                "predicted_label": sample.get("predicted_label"),
                "expected_severity": sample.get("expected_severity"),
                "predicted_severity": sample.get("predicted_severity"),
                "expected_is_suspicious": sample.get("expected_is_suspicious"),
                "predicted_is_suspicious": sample.get("predicted_is_suspicious"),
                "label_correct": sample.get("label_correct"),
                "severity_correct": sample.get("severity_correct"),
                "is_suspicious_correct": sample.get("is_suspicious_correct"),
                "evidence_partial_match": sample.get("evidence_partial_match"),
                "expected_evidence": expected_output.get("evidence", []),
                "predicted_evidence": prediction.get("evidence", []),
                "diagnosis": bucket["diagnosis"],
                "suggested_repair_pattern": bucket["suggested_repair_pattern"],
            }
        )
    return cases


def make_bucket_summary(cases: list[JsonObject]) -> list[JsonObject]:
    counts = Counter(str(case["failure_bucket"]) for case in cases)
    return [
        {
            "bucket": bucket_key,
            "title": BUCKET_DETAILS[bucket_key]["title"],
            "count": counts[bucket_key],
            "ids": [case["id"] for case in cases if case["failure_bucket"] == bucket_key],
            "diagnosis": BUCKET_DETAILS[bucket_key]["diagnosis"],
            "suggested_repair_pattern": BUCKET_DETAILS[bucket_key]["suggested_repair_pattern"],
        }
        for bucket_key in sorted(counts)
    ]


def build_report() -> JsonObject:
    report = read_json(V4_5_REPORT_PATH)
    source_records = read_jsonl_by_id(SOURCE_SPLIT_PATH)
    cases = build_cases(report, source_records)
    label_failures = [case for case in cases if case["label_correct"] is not True]
    severity_failures = [case for case in cases if case["severity_correct"] is not True]
    evidence_failures = [case for case in cases if case["evidence_partial_match"] is not True]

    return {
        "created_date": CREATED_DATE,
        "phase": "phase-8-v4-6",
        "source_report": str(V4_5_REPORT_PATH.relative_to(ROOT)),
        "source_split": str(SOURCE_SPLIT_PATH.relative_to(ROOT)),
        "fixed_test_split_used": False,
        "metrics": report["metrics"],
        "adapter_metadata": compact_metadata(report.get("adapter_metadata")),
        "sample_count": report["sample_count"],
        "label_failure_count": len(label_failures),
        "severity_failure_count": len(severity_failures),
        "severity_only_failure_count": sum(
            1 for case in severity_failures if case["label_correct"] is True
        ),
        "evidence_failure_count": len(evidence_failures),
        "bucket_summary": make_bucket_summary(cases),
        "cases": cases,
        "dataset_implications": [
            {
                "bucket": "normal hard negatives",
                "target": "train-heavy supplement",
                "details": "Repair normal -> brute force, SQLi, and traversal false positives without touching fixed test.",
            },
            {
                "bucket": "severity calibration",
                "target": "medium brute-force and high recon positives",
                "details": "Teach severity boundaries while keeping labels unchanged.",
            },
            {
                "bucket": "suspicious recall guard",
                "target": "small SQLi/traversal positives",
                "details": "Prevent the normal repair from causing a return to suspicious -> normal collapse.",
            },
        ],
    }


def render_markdown(report: JsonObject) -> str:
    lines = [
        "# Phase 8 v4.6 Qwen3.5 Normal Calibration Slice",
        "",
        "This report reads the v4.5 trained-Qwen hard-contrast report and identifies the calibration failures to repair before any fixed split run.",
        "",
        "## Headline",
        "",
        f"- Source report: `{report['source_report']}`",
        f"- Source split: `{report['source_split']}`",
        f"- Fixed test split used: `{str(report['fixed_test_split_used']).lower()}`",
        f"- Label failures: `{report['label_failure_count']}`",
        f"- Severity failures: `{report['severity_failure_count']}`",
        f"- Severity-only failures: `{report['severity_only_failure_count']}`",
        f"- Evidence failures: `{report['evidence_failure_count']}`",
        "",
        "## Bucket Summary",
        "",
        "| Bucket | Count | IDs |",
        "| --- | ---: | --- |",
    ]
    for bucket in report["bucket_summary"]:
        ids = ", ".join(f"`{item}`" for item in bucket["ids"])
        lines.append(f"| {bucket['title']} | `{bucket['count']}` | {ids} |")

    lines.extend(
        [
            "",
            "## Dataset Implications",
            "",
            "| Bucket | Target | Details |",
            "| --- | --- | --- |",
        ]
    )
    for item in report["dataset_implications"]:
        lines.append(f"| {item['bucket']} | {item['target']} | {item['details']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    OUTPUT_JSON_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUT_MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON_PATH.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MD_PATH.relative_to(ROOT)}")
    print(f"Label failures: {report['label_failure_count']}")
    print(f"Severity-only failures: {report['severity_only_failure_count']}")
    print(f"Evidence failures: {report['evidence_failure_count']}")
    print("Fixed test split was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
