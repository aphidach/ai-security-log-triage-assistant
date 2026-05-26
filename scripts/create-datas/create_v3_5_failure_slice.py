#!/usr/bin/env python3
"""Create the Phase 6 v3.5 boundary failure slice.

This report is a pre-training diagnostic artifact. It reads the v3.4
temperature=0 hard-contrast probe and the hard-contrast source examples, then
writes machine-readable and human-readable failure slices for v3.5 dataset
planning. It intentionally does not read the fixed test split.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SOURCE_REPORT_PATH = (
    ROOT
    / "reports"
    / "openai-compatible-vllm-structured-outputs-v3-4-temp-0-hard-contrast-memorization-probe.json"
)
SOURCE_SPLIT_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"
OUTPUT_JSON_PATH = ROOT / "reports" / "phase-6-v3-5-boundary-failure-slice.json"
OUTPUT_MD_PATH = ROOT / "reports" / "phase-6-v3-5-boundary-failure-slice.md"

CREATED_DATE = "2026-05-22"

JsonObject = dict[str, Any]


BUCKET_DETAILS: dict[str, dict[str, str]] = {
    "normal_to_bruteforce": {
        "title": "Normal -> brute force",
        "diagnosis": "Single failed-login events are still being treated as repeated guessing.",
        "suggested_repair_pattern": (
            "Add anti-gravity normal examples with failed_attempts=1, count=1, isolated 4625, "
            "single 401/403 responses, and no burst/correlation evidence."
        ),
    },
    "sqli_to_bruteforce": {
        "title": "SQLi -> brute force",
        "diagnosis": "Login/API/status context still overrules clear SQL injection payloads.",
        "suggested_repair_pattern": (
            "Add SQLi positives in login, API, search, and reset-password contexts with 401/403/400/500 "
            "status codes, keeping quote tautologies, UNION, SLEEP/WAITFOR, stacked queries, "
            "and comment markers prominent."
        ),
    },
    "sqli_to_invalid": {
        "title": "SQLi -> invalid",
        "diagnosis": "Quote-heavy SQLi evidence can still break JSON generation despite structured outputs.",
        "suggested_repair_pattern": (
            "Add quote-heavy SQLi examples and keep evidence as short exact substrings that require "
            "JSON escaping, then probe structured-output enforcement on the same shape."
        ),
    },
    "sqli_to_normal": {
        "title": "SQLi -> normal",
        "diagnosis": "Schema-discovery or SQL vocabulary is still underweighted in request-parameter context.",
        "suggested_repair_pattern": (
            "Add information_schema and encoded SQLi positives paired with benign documentation/search "
            "hard negatives that contain SQL words without payload boundaries."
        ),
    },
    "sqli_to_traversal": {
        "title": "SQLi -> traversal",
        "diagnosis": "SQL quote/comment syntax is still confused with file/path injection syntax.",
        "suggested_repair_pattern": (
            "Add contrast pairs where SQL comment markers such as admin'-- are adjacent to traversal "
            "paths such as ../../etc/passwd and encoded ../ sequences."
        ),
    },
    "traversal_to_normal": {
        "title": "Traversal -> normal",
        "diagnosis": "Sensitive path traversal tokens are underweighted when the log looks routine.",
        "suggested_repair_pattern": (
            "Add traversal positives with ../, encoded traversal, /etc/passwd, /etc/shadow, win.ini, "
            "secrets.yml, %00, and php://filter while preserving benign relative-path hard negatives."
        ),
    },
    "traversal_to_port": {
        "title": "Traversal -> port/recon",
        "diagnosis": "Status, user-agent, curl, and generic probing cues distract from traversal paths.",
        "suggested_repair_pattern": (
            "Add traversal positives with distracting curl/scanner-like user agents and blocked/404 "
            "status codes, keeping the sensitive path token prominent."
        ),
    },
    "traversal_to_bruteforce": {
        "title": "Traversal -> brute force",
        "diagnosis": "Status/blocking cues can still trigger the over-strong brute-force label.",
        "suggested_repair_pattern": (
            "Add traversal positives with 401/403/blocked wording and no authentication burst evidence."
        ),
    },
    "port_to_bruteforce": {
        "title": "Port/recon -> brute force",
        "diagnosis": "Reconnaissance signals are still pulled into brute force when wording is generic.",
        "suggested_repair_pattern": (
            "Add port/recon positives with nmap fingerprint, service enumeration, horizontal scan, "
            "unique_hosts/unique_ports thresholds, and blocked/attempt wording."
        ),
    },
    "other_label_failure": {
        "title": "Other label failure",
        "diagnosis": "A label failure outside the primary v3.5 repair buckets.",
        "suggested_repair_pattern": "Review manually before adding broad new data.",
    },
}


DATASET_IMPLICATIONS = [
    {
        "bucket": "SQLi positives",
        "target": "75 examples",
        "details": (
            "Use login/API/search/reset contexts with 401/403/400/500, quote tautologies, UNION SELECT, "
            "SLEEP/WAITFOR, stacked queries, comment markers, encoded payloads, and quote-heavy evidence."
        ),
    },
    {
        "bucket": "Traversal positives",
        "target": "55 examples",
        "details": (
            "Use ../, encoded %2e%2e, /etc/passwd, /etc/shadow, win.ini, secrets.yml, %00, "
            "php://filter, and distracting status/user-agent cues."
        ),
    },
    {
        "bucket": "Normal hard negatives",
        "target": "45 examples",
        "details": (
            "Use single auth failures, isolated 4625, benign SQL docs/search terms, benign relative paths, "
            "allowlisted inventory, and low-scope monitoring."
        ),
    },
    {
        "bucket": "Port/recon positives",
        "target": "25 examples",
        "details": (
            "Use nmap fingerprint, service enumeration, horizontal scan, unique_hosts/unique_ports, "
            "and blocked/attempt wording that should not become brute force."
        ),
    },
    {
        "bucket": "No new brute-force positives",
        "target": "0 examples",
        "details": "v3.5 should reduce brute-force gravity rather than further strengthening the label.",
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
    if expected_label == "sql_injection_attempt" and predicted_label == "failed_login_bruteforce":
        return "sqli_to_bruteforce"
    if expected_label == "sql_injection_attempt" and predicted_label == "<invalid>":
        return "sqli_to_invalid"
    if expected_label == "sql_injection_attempt" and predicted_label == "normal":
        return "sqli_to_normal"
    if expected_label == "sql_injection_attempt" and predicted_label == "directory_traversal_attempt":
        return "sqli_to_traversal"
    if expected_label == "directory_traversal_attempt" and predicted_label == "normal":
        return "traversal_to_normal"
    if expected_label == "directory_traversal_attempt" and predicted_label == "port_scan_or_recon":
        return "traversal_to_port"
    if expected_label == "directory_traversal_attempt" and predicted_label == "failed_login_bruteforce":
        return "traversal_to_bruteforce"
    if expected_label == "port_scan_or_recon" and predicted_label == "failed_login_bruteforce":
        return "port_to_bruteforce"
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
            "v3.5 slices the v3.4 temperature=0 hard-contrast failures so the next repair can target "
            "SQLi, traversal, invalid JSON, and brute-force gravity without using the fixed test split."
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
            "Create the v3.5 boundary repair supplement from these buckets, then train and probe v3.5 "
            "on hard-contrast before any mini semantic or fixed test comparison."
        ),
    }


def md_table_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value).replace("\n", " ") for value in values) + " |"


def write_markdown(report: JsonObject) -> None:
    lines: list[str] = [
        "# Phase 6 V3.5 Boundary Failure Slice",
        "",
        "**Summary**",
        "",
        str(report["summary"]),
        "",
        "**Sources**",
        "",
        f"- `{report['source_report_path']}` for v3.4 temp 0 runtime probe predictions and metrics.",
        f"- `{report['source_split_path']}` for source log lines and expected outputs.",
        "- `docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md` for the v3.4 result and v3.5 decision context.",
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
            "`data/splits/test.jsonl` remains held out and must not be used for selecting v3.5 repair cases or tuning prompts/runtime settings.",
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
