#!/usr/bin/env python3
"""Create the Phase 8 v4.7 Qwen3.5 auth/SQLi/severity calibration slice.

The slice reads only v4.6 non-fixed probe reports. It does not read the fixed
test split.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

V4_6_HARD_REPORT_PATH = (
    ROOT
    / "reports"
    / "openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.json"
)
V4_6_CALIBRATION_REPORT_PATH = (
    ROOT
    / "reports"
    / "openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json"
)
OUTPUT_JSON_PATH = ROOT / "reports" / "phase-8-v4-7-qwen35-auth-sqli-severity-calibration-slice.json"
OUTPUT_MD_PATH = ROOT / "reports" / "phase-8-v4-7-qwen35-auth-sqli-severity-calibration-slice.md"

CREATED_DATE = "2026-05-23"

JsonObject = dict[str, Any]


BUCKET_ORDER = [
    "normal_to_bruteforce",
    "sqli_to_bruteforce",
    "bruteforce_medium_to_high",
    "port_recon_medium_to_high",
    "traversal_evidence_miss",
]

BUCKET_DETAILS: dict[str, dict[str, str]] = {
    "normal_to_bruteforce": {
        "title": "Normal -> brute force",
        "diagnosis": "Single or low-volume auth failures are still over-alerted as brute force.",
        "suggested_repair_pattern": (
            "Add benign auth negatives with failures=1-2, allowed retry or later success, "
            "and no burst, spray, lockout, or distributed-source evidence."
        ),
    },
    "sqli_to_bruteforce": {
        "title": "SQLi -> brute force",
        "diagnosis": "SQL injection payloads on login/auth routes are misread as authentication brute force.",
        "suggested_repair_pattern": (
            "Add SQLi positives in login/auth contexts where the decisive evidence is tautology, "
            "UNION, stacked query, or time-delay payload rather than failure counts."
        ),
    },
    "bruteforce_medium_to_high": {
        "title": "Brute force medium -> high",
        "diagnosis": "Medium brute-force indicators are labelled correctly but severity is escalated to high.",
        "suggested_repair_pattern": (
            "Add medium brute-force positives with repeated failures but limited scope, "
            "single source/account, and no confirmed compromise or distributed spray."
        ),
    },
    "port_recon_medium_to_high": {
        "title": "Port/recon medium -> high",
        "diagnosis": "Limited blocked reconnaissance is labelled correctly but severity is escalated to high.",
        "suggested_repair_pattern": (
            "Add medium port/recon positives with few ports or blocked limited scans, "
            "contrasted against broader high-severity recon already learned in v4.6."
        ),
    },
    "traversal_evidence_miss": {
        "title": "Traversal evidence miss",
        "diagnosis": "Directory traversal label and severity are correct, but evidence matching misses an exact substring.",
        "suggested_repair_pattern": "Add traversal positives with short exact evidence substrings copied from the log line.",
    },
}


def read_json(path: Path) -> JsonObject:
    return json.loads(path.read_text(encoding="utf-8"))


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


def bucket_for(sample: JsonObject) -> str:
    expected = sample.get("expected") or {}
    prediction = sample.get("prediction") or {}
    expected_label = expected.get("label")
    predicted_label = prediction.get("label")
    expected_severity = expected.get("severity")
    predicted_severity = prediction.get("severity")
    failure_reasons = set(sample.get("failure_reasons") or [])

    if "label_mismatch" in failure_reasons:
        if expected_label == "normal" and predicted_label == "failed_login_bruteforce":
            return "normal_to_bruteforce"
        if expected_label == "sql_injection_attempt" and predicted_label == "failed_login_bruteforce":
            return "sqli_to_bruteforce"
        raise ValueError(f"unexpected v4.6 label failure: {sample['id']} {expected_label}->{predicted_label}")

    if "severity_mismatch" in failure_reasons:
        if (
            expected_label == "failed_login_bruteforce"
            and expected_severity == "medium"
            and predicted_severity == "high"
        ):
            return "bruteforce_medium_to_high"
        if (
            expected_label == "port_scan_or_recon"
            and expected_severity == "medium"
            and predicted_severity == "high"
        ):
            return "port_recon_medium_to_high"
        raise ValueError(
            f"unexpected v4.6 severity failure: {sample['id']} "
            f"{expected_label} {expected_severity}->{predicted_severity}"
        )

    if "evidence_partial_mismatch" in failure_reasons:
        if expected_label == "directory_traversal_attempt":
            return "traversal_evidence_miss"
        raise ValueError(f"unexpected v4.6 evidence failure: {sample['id']} {expected_label}")

    raise ValueError(f"could not bucket v4.6 failure: {sample['id']} {sample.get('failure_reasons')}")


def case_from_sample(sample: JsonObject, *, source_report: Path, probe_name: str) -> JsonObject:
    bucket_key = bucket_for(sample)
    bucket = BUCKET_DETAILS[bucket_key]
    expected = sample.get("expected") or {}
    prediction = sample.get("prediction") or {}

    return {
        "id": sample["id"],
        "source_probe": probe_name,
        "source_report": str(source_report.relative_to(ROOT)),
        "failure_bucket": bucket_key,
        "failure_bucket_title": bucket["title"],
        "input_log": sample["input"],
        "expected_label": expected.get("label"),
        "predicted_label": prediction.get("label"),
        "expected_severity": expected.get("severity"),
        "predicted_severity": prediction.get("severity"),
        "expected_is_suspicious": expected.get("is_suspicious"),
        "predicted_is_suspicious": prediction.get("is_suspicious"),
        "failure_reasons": sample.get("failure_reasons", []),
        "expected_evidence": expected.get("evidence", []),
        "predicted_evidence": prediction.get("evidence", []),
        "diagnosis": bucket["diagnosis"],
        "suggested_repair_pattern": bucket["suggested_repair_pattern"],
    }


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
        for bucket_key in BUCKET_ORDER
        if counts[bucket_key]
    ]


def build_cases() -> list[JsonObject]:
    reports = [
        ("v4.6 hard-contrast", V4_6_HARD_REPORT_PATH),
        ("v4.6 calibration probe", V4_6_CALIBRATION_REPORT_PATH),
    ]
    cases: list[JsonObject] = []
    for probe_name, report_path in reports:
        report = read_json(report_path)
        for sample in report.get("failures", []):
            cases.append(case_from_sample(sample, source_report=report_path, probe_name=probe_name))
    return cases


def build_report() -> JsonObject:
    hard_report = read_json(V4_6_HARD_REPORT_PATH)
    calibration_report = read_json(V4_6_CALIBRATION_REPORT_PATH)
    cases = build_cases()
    bucket_counts = Counter(str(case["failure_bucket"]) for case in cases)

    return {
        "created_date": CREATED_DATE,
        "phase": "phase-8-v4-7",
        "source_reports": [
            str(V4_6_HARD_REPORT_PATH.relative_to(ROOT)),
            str(V4_6_CALIBRATION_REPORT_PATH.relative_to(ROOT)),
        ],
        "fixed_test_split_used": False,
        "source_metrics": {
            "v4_6_hard_contrast": hard_report["metrics"],
            "v4_6_calibration_probe": calibration_report["metrics"],
        },
        "adapter_metadata": {
            "v4_6_hard_contrast": compact_metadata(hard_report.get("adapter_metadata")),
            "v4_6_calibration_probe": compact_metadata(calibration_report.get("adapter_metadata")),
        },
        "case_count": len(cases),
        "bucket_counts": {bucket: bucket_counts[bucket] for bucket in BUCKET_ORDER},
        "bucket_summary": make_bucket_summary(cases),
        "cases": cases,
        "dataset_implications": [
            {
                "bucket": "auth normal hard negatives",
                "target": "train-heavy supplement and 15-record probe holdout",
                "details": "Repair benign auth failures that resemble brute force but lack volume or scope.",
            },
            {
                "bucket": "SQLi auth-context positives",
                "target": "SQLi guard supplement and 5-record probe holdout",
                "details": "Preserve SQLi recall on login/auth routes where auth vocabulary is present.",
            },
            {
                "bucket": "medium severity boundaries",
                "target": "brute-force and limited port/recon calibration examples",
                "details": "Teach that limited repeated auth failures and small blocked recon do not automatically become high.",
            },
            {
                "bucket": "exact traversal evidence",
                "target": "short copied evidence substrings",
                "details": "Repair traversal evidence partial-match behavior without changing label taxonomy.",
            },
        ],
    }


def render_markdown(report: JsonObject) -> str:
    lines = [
        "# Phase 8 v4.7 Qwen3.5 Auth/SQLi/Severity Calibration Slice",
        "",
        "This report reads the v4.6 non-fixed probe outputs and identifies the remaining failures to repair before any fixed split run.",
        "",
        "## Headline",
        "",
        f"- Source reports: `{report['source_reports'][0]}`, `{report['source_reports'][1]}`",
        "- Fixed test split used: `false`",
        f"- Failure cases: `{report['case_count']}`",
        "",
        "## Bucket Summary",
        "",
        "| Bucket | Count | IDs |",
        "| --- | ---: | --- |",
    ]
    for bucket in report["bucket_summary"]:
        ids = ", ".join(f"`{case_id}`" for case_id in bucket["ids"])
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
    for implication in report["dataset_implications"]:
        lines.append(f"| {implication['bucket']} | {implication['target']} | {implication['details']} |")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    OUTPUT_JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD_PATH.write_text(render_markdown(report), encoding="utf-8")

    print(f"Wrote {OUTPUT_JSON_PATH.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MD_PATH.relative_to(ROOT)}")
    print(f"Failure cases: {report['case_count']}")
    print(f"Bucket counts: {report['bucket_counts']}")
    print("Fixed test split was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
