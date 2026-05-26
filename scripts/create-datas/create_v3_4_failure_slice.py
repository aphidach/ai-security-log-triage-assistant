#!/usr/bin/env python3
"""Create the Phase 6 v3.4 boundary failure slice.

This report is a pre-training diagnostic artifact. It reads the v3.3
hard-contrast runtime probe and the hard-contrast source examples, then writes
machine-readable and human-readable failure slices for v3.4 dataset planning.
It intentionally does not read the fixed test split.
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
    / "openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json"
)
SOURCE_SPLIT_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"
OUTPUT_JSON_PATH = ROOT / "reports" / "phase-6-v3-4-boundary-failure-slice.json"
OUTPUT_MD_PATH = ROOT / "reports" / "phase-6-v3-4-boundary-failure-slice.md"

CREATED_DATE = "2026-05-22"

JsonObject = dict[str, Any]


BUCKET_DETAILS: dict[str, dict[str, str]] = {
    "normal_to_bruteforce": {
        "title": "Normal -> brute force",
        "description": "Isolated login failures are being read as repeated password guessing.",
        "inspection_question": "Does the model ignore low counts such as failed_attempts=1 or count=1?",
        "diagnosis": (
            "The model treats failed-login vocabulary as sufficient evidence for brute force "
            "even when the log explicitly shows a single event."
        ),
        "suggested_repair_pattern": (
            "Add brute-force anti-gravity normal examples with failed_attempts=1, count=1, "
            "isolated 4625, and paired burst examples where the count crosses the threshold."
        ),
    },
    "sqli_to_bruteforce": {
        "title": "SQLi -> brute force",
        "description": "SQL injection payloads in login/API contexts are being pulled into auth failure logic.",
        "inspection_question": "Does status/auth context dominate the SQL payload?",
        "diagnosis": (
            "The model notices login/API/status cues before the SQL payload, especially when "
            "the request is blocked with 401, 403, 400, or 500-like status signals."
        ),
        "suggested_repair_pattern": (
            "Add SQLi positives inside login/API/search contexts with quote tautologies, UNION SELECT, "
            "SLEEP, stacked queries, and comment markers, including blocked status codes."
        ),
    },
    "sqli_to_traversal": {
        "title": "SQLi -> traversal",
        "description": "SQL quote/comment syntax is being confused with file/path attack syntax.",
        "inspection_question": "Are quote or comment markers being mistaken for path traversal clues?",
        "diagnosis": (
            "The model treats SQL comment markers and quoted values as a generic injection shape, "
            "then selects directory traversal instead of the SQL-specific label."
        ),
        "suggested_repair_pattern": (
            "Add paired examples contrasting SQL comments such as admin'-- with traversal paths "
            "such as ../../etc/passwd and encoded ../ sequences."
        ),
    },
    "sqli_to_normal_or_port": {
        "title": "SQLi -> normal/port",
        "description": "SQL vocabulary or OR patterns are not always strong enough to hold the SQLi label.",
        "inspection_question": "Is the payload too weak or ambiguous without a clearer SQL boundary?",
        "diagnosis": (
            "The model sometimes treats information_schema or OR payloads as benign search content "
            "or generic probing unless the attack boundary is very explicit."
        ),
        "suggested_repair_pattern": (
            "Add clearer SQLi positives with encoded tautologies, schema discovery in request parameters, "
            "and hard negatives where select/union/sleep/information_schema are benign text."
        ),
    },
    "traversal_boundary_drift": {
        "title": "Traversal boundary drift",
        "description": "Directory traversal examples are spread across normal, SQLi, port scan, and brute force.",
        "inspection_question": "Which non-path cue is distracting from ../, encoded traversal, or sensitive file access?",
        "diagnosis": (
            "Traversal is no longer the primary blocker, but several traversal cases are still "
            "being overruled by status, user-agent, encoding, or generic suspicious cues."
        ),
        "suggested_repair_pattern": (
            "Add traversal positives that keep the sensitive path token prominent, plus hard negatives "
            "where ../ appears in benign normalized documentation paths."
        ),
    },
    "port_to_bruteforce": {
        "title": "Port/recon -> brute force",
        "description": "Reconnaissance signals are being pulled into the over-strong brute-force label.",
        "inspection_question": "Do blocked/attempt/enumeration cues overpower nmap, service enumeration, or port lists?",
        "diagnosis": (
            "The model still uses generic suspicious wording as a shortcut for brute force, even when "
            "the evidence is clearly network reconnaissance."
        ),
        "suggested_repair_pattern": (
            "Add port/recon positives with nmap fingerprint, service enumeration, unique_ports>=10, "
            "horizontal scans, and many hosts/ports, paired with auth-failure negatives."
        ),
    },
    "port_to_normal": {
        "title": "Port/recon -> normal",
        "description": "Horizontal scan evidence is not always enough to beat benign monitoring priors.",
        "inspection_question": "Does the model need a clearer threshold for hosts, ports, or scan window?",
        "diagnosis": (
            "The model underweights horizontal scan and unique host thresholds when the log lacks "
            "strong malicious wording."
        ),
        "suggested_repair_pattern": (
            "Add contrast pairs for inventory/health checks versus horizontal scan, using explicit "
            "unique_hosts and unique_ports thresholds."
        ),
    },
    "other_label_failure": {
        "title": "Other label failure",
        "description": "A label failure outside the primary v3.4 buckets.",
        "inspection_question": "Does this reveal a new boundary not covered by the current repair plan?",
        "diagnosis": "This case should be reviewed manually before adding broad new data.",
        "suggested_repair_pattern": "Do not add generic examples yet; classify the boundary first.",
    },
}

DATASET_IMPLICATIONS = [
    {
        "bucket": "SQLi positives",
        "target": "35-45 examples",
        "details": (
            "Use login/API/search contexts with explicit payloads: quote tautology, UNION SELECT, "
            "SLEEP, information_schema, SQL comment markers, encoded SQLi, and stacked query syntax."
        ),
    },
    {
        "bucket": "SQLi hard negatives",
        "target": "20-30 examples",
        "details": (
            "Use select, union, sleep, schema, and information_schema in documentation, search, "
            "or admin contexts without attack payload boundaries."
        ),
    },
    {
        "bucket": "Port/recon positives",
        "target": "35-45 examples",
        "details": (
            "Use nmap fingerprint, SYN scan detected, service enumeration, horizontal scan, "
            "unique_ports>=10, unique_hosts>=10, and short scan windows."
        ),
    },
    {
        "bucket": "Port/recon hard negatives",
        "target": "20-30 examples",
        "details": (
            "Use authorized inventory, one-port monitoring, health checks, known scanner allowlists, "
            "and low unique port counts."
        ),
    },
    {
        "bucket": "Brute-force anti-gravity negatives",
        "target": "20-30 examples",
        "details": (
            "Use failed, blocked, 401, 403, 4625, or attempt wording without repeated login burst; "
            "pair failed_attempts=1 with failed_attempts>=10."
        ),
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


def bucket_for(expected_label: str, predicted_label: str) -> str:
    if expected_label == "normal" and predicted_label == "failed_login_bruteforce":
        return "normal_to_bruteforce"
    if expected_label == "sql_injection_attempt" and predicted_label == "failed_login_bruteforce":
        return "sqli_to_bruteforce"
    if expected_label == "sql_injection_attempt" and predicted_label == "directory_traversal_attempt":
        return "sqli_to_traversal"
    if expected_label == "sql_injection_attempt" and predicted_label in {"normal", "port_scan_or_recon"}:
        return "sqli_to_normal_or_port"
    if expected_label == "directory_traversal_attempt":
        return "traversal_boundary_drift"
    if expected_label == "port_scan_or_recon" and predicted_label == "failed_login_bruteforce":
        return "port_to_bruteforce"
    if expected_label == "port_scan_or_recon" and predicted_label == "normal":
        return "port_to_normal"
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
        predicted = sample["predicted_label"]
        bucket_key = bucket_for(expected, predicted)
        bucket = BUCKET_DETAILS[bucket_key]
        prediction = sample.get("prediction") or {}
        expected_output = source.get("output") or {}

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
                "expected_is_suspicious": sample.get("expected_is_suspicious"),
                "predicted_is_suspicious": sample.get("predicted_is_suspicious"),
                "expected_evidence": expected_output.get("evidence", []),
                "predicted_evidence": prediction.get("evidence", []),
                "predicted_reason": prediction.get("reason"),
                "evidence_partial_match": sample.get("evidence_partial_match"),
                "severity_correct": sample.get("severity_correct"),
                "is_suspicious_correct": sample.get("is_suspicious_correct"),
                "json_parse_success": sample.get("json_parse_success"),
                "schema_success": sample.get("schema_success"),
                "latency_ms": sample.get("latency_ms"),
                "diagnosis": bucket["diagnosis"],
                "inspection_question": bucket["inspection_question"],
                "suggested_repair_pattern": bucket["suggested_repair_pattern"],
            }
        )
    return failures


def build_bucket_summary(failures: list[JsonObject]) -> list[JsonObject]:
    by_bucket: dict[str, list[JsonObject]] = defaultdict(list)
    for failure in failures:
        by_bucket[failure["failure_bucket"]].append(failure)

    summary: list[JsonObject] = []
    for bucket_key in BUCKET_DETAILS:
        bucket_failures = by_bucket.get(bucket_key, [])
        if not bucket_failures:
            continue
        details = BUCKET_DETAILS[bucket_key]
        expected = Counter(failure["expected_label"] for failure in bucket_failures)
        predicted = Counter(failure["predicted_label"] for failure in bucket_failures)
        summary.append(
            {
                "bucket": bucket_key,
                "title": details["title"],
                "description": details["description"],
                "count": len(bucket_failures),
                "ids": [failure["id"] for failure in bucket_failures],
                "expected_label_counts": dict(sorted(expected.items())),
                "predicted_label_counts": dict(sorted(predicted.items())),
                "inspection_question": details["inspection_question"],
                "diagnosis": details["diagnosis"],
                "suggested_repair_pattern": details["suggested_repair_pattern"],
            }
        )
    return summary


def build_confusion(failures: list[JsonObject]) -> dict[str, dict[str, int]]:
    confusion: dict[str, Counter[str]] = defaultdict(Counter)
    for failure in failures:
        confusion[failure["expected_label"]][failure["predicted_label"]] += 1
    return {
        expected: dict(sorted(predicted_counts.items()))
        for expected, predicted_counts in sorted(confusion.items())
    }


def build_artifact(report: JsonObject, failures: list[JsonObject]) -> JsonObject:
    metrics = report.get("metrics", {})
    first_metadata = {}
    if report.get("samples"):
        first_metadata = compact_metadata(report["samples"][0].get("adapter_metadata"))

    return {
        "artifact": "phase-6-v3-4-boundary-failure-slice",
        "created": CREATED_DATE,
        "purpose": (
            "Identify v3.3 hard-contrast label-boundary failures before creating the v3.4 "
            "boundary repair dataset."
        ),
        "source_report": str(SOURCE_REPORT_PATH.relative_to(ROOT)),
        "source_split": str(SOURCE_SPLIT_PATH.relative_to(ROOT)),
        "fixed_test_split_used": False,
        "run_summary": {
            "sample_count": report.get("sample_count"),
            "label_failure_count": len(failures),
            "metrics": metrics,
            "expected_label_distribution": report.get("expected_label_distribution", {}),
            "predicted_label_distribution": report.get("predicted_label_distribution", {}),
            "counts": report.get("counts", {}),
            "runtime": first_metadata,
        },
        "confusion_failures_only": build_confusion(failures),
        "bucket_summary": build_bucket_summary(failures),
        "failures": failures,
        "dataset_implications": DATASET_IMPLICATIONS,
        "next_step": (
            "Create the v3.4 boundary repair supplement from these buckets, then train and probe "
            "v3.4 on hard-contrast and mini semantic splits before any fixed test comparison."
        ),
        "hold_fixed_test": (
            "data/splits/test.jsonl remains held out and must not be used for selecting repair cases "
            "or tuning prompts/runtime settings."
        ),
    }


def md_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def render_markdown(artifact: JsonObject) -> str:
    summary = artifact["run_summary"]
    metrics = summary["metrics"]
    runtime = summary["runtime"]

    lines: list[str] = [
        "# Phase 6 V3.4 Boundary Failure Slice",
        "",
        "**Summary**",
        "",
        (
            "This report slices the v3.3 temp 0.3 hard-contrast probe by label-boundary failure "
            "so v3.4 data repair can be targeted instead of guessed."
        ),
        "",
        "**Sources**",
        "",
        f"- `{artifact['source_report']}` for v3.3 runtime probe predictions and metrics.",
        f"- `{artifact['source_split']}` for source log lines and expected outputs.",
        "- `docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md` for the v3.4 repair plan.",
        "",
        "**Last updated**",
        "",
        artifact["created"],
        "",
        "## Run Snapshot",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Samples | `{summary['sample_count']}` |",
        f"| Label failures | `{summary['label_failure_count']}` |",
        f"| Label accuracy | `{metrics.get('label_accuracy')}` |",
        f"| JSON parse success | `{metrics.get('json_parse_success_rate')}` |",
        f"| Schema success | `{metrics.get('schema_success_rate')}` |",
        f"| Invalid outputs | `{metrics.get('invalid_output_count')}` |",
        f"| Severity accuracy | `{metrics.get('severity_accuracy')}` |",
        f"| Evidence partial match | `{metrics.get('evidence_partial_match')}` |",
        "",
        "Runtime context:",
        "",
        f"- model: `{runtime.get('model')}`",
        f"- response format: `{runtime.get('response_format_requested')}` / `{runtime.get('response_format_mode')}`",
        f"- prompt version: `{runtime.get('prompt_version')}`",
        f"- request options: `{json.dumps(runtime.get('request_options'), sort_keys=True)}`",
        f"- extra body: `{json.dumps(runtime.get('extra_body'), sort_keys=True)}`",
        "",
        "Expected label distribution:",
        "",
        "```json",
        json.dumps(summary["expected_label_distribution"], indent=2, sort_keys=True),
        "```",
        "",
        "Predicted label distribution:",
        "",
        "```json",
        json.dumps(summary["predicted_label_distribution"], indent=2, sort_keys=True),
        "```",
        "",
        "## Bucket Summary",
        "",
        "| Bucket | Count | IDs | Diagnosis | Repair pattern |",
        "| --- | ---: | --- | --- | --- |",
    ]

    for bucket in artifact["bucket_summary"]:
        ids = ", ".join(f"`{sample_id}`" for sample_id in bucket["ids"])
        lines.append(
            "| "
            + md_escape(bucket["title"])
            + f" | `{bucket['count']}` | "
            + ids
            + " | "
            + md_escape(bucket["diagnosis"])
            + " | "
            + md_escape(bucket["suggested_repair_pattern"])
            + " |"
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

    for failure in artifact["failures"]:
        expected_ev = "; ".join(failure["expected_evidence"])
        predicted_ev = "; ".join(failure["predicted_evidence"])
        lines.append(
            f"| `{failure['id']}` | `{failure['expected_label']}` | `{failure['predicted_label']}` | "
            f"{md_escape(failure['failure_bucket_title'])} | {md_escape(expected_ev)} | "
            f"{md_escape(predicted_ev)} | {md_escape(failure['suggested_repair_pattern'])} |"
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
    for implication in artifact["dataset_implications"]:
        lines.append(
            f"| {md_escape(implication['bucket'])} | {md_escape(implication['target'])} | "
            f"{md_escape(implication['details'])} |"
        )

    lines.extend(
        [
            "",
            "## Hold Fixed Test",
            "",
            artifact["hold_fixed_test"],
            "",
            "## Next Step",
            "",
            artifact["next_step"],
            "",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    report = read_json(SOURCE_REPORT_PATH)
    source_records = read_jsonl_by_id(SOURCE_SPLIT_PATH)
    failures = build_failure_cases(report, source_records)
    artifact = build_artifact(report, failures)

    OUTPUT_JSON_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD_PATH.write_text(render_markdown(artifact), encoding="utf-8")

    print(f"wrote {OUTPUT_JSON_PATH.relative_to(ROOT)}")
    print(f"wrote {OUTPUT_MD_PATH.relative_to(ROOT)}")
    print(f"label failures: {len(failures)}")


if __name__ == "__main__":
    main()
