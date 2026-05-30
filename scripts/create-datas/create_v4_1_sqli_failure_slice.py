#!/usr/bin/env python3
"""Create the Phase 8 v4.1 SQLi boundary failure slice.

This report is a v4.1 planning artifact. It reads only the v4 hard-contrast
temperature=0 and temperature=0.3 reports plus the hard-contrast source split.
It intentionally does not read the fixed test split.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

TEMP_0_REPORT_PATH = (
    ROOT
    / "reports"
    / "phase-8"
    / "openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json"
)
TEMP_0_3_REPORT_PATH = (
    ROOT
    / "reports"
    / "phase-8"
    / "openai-compatible-vllm-structured-outputs-v4-temp-03-2048-hard-contrast-memorization-probe.json"
)
SOURCE_SPLIT_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"
OUTPUT_JSON_PATH = ROOT / "reports" / "phase-8" / "phase-8-v4-1-sqli-boundary-failure-slice.json"
OUTPUT_MD_PATH = ROOT / "reports" / "phase-8" / "phase-8-v4-1-sqli-boundary-failure-slice.md"

CREATED_DATE = "2026-05-22"

JsonObject = dict[str, Any]


BUCKET_DETAILS: dict[str, dict[str, str]] = {
    "normal_to_bruteforce": {
        "title": "Normal -> brute force",
        "diagnosis": "Single or isolated failed-auth events still look too much like threshold-based attacks.",
        "suggested_repair_pattern": (
            "Add normal auth negatives with failed_attempts=1, count=1, correlation=none, "
            "lockout=false, and no short burst window."
        ),
    },
    "sqli_to_normal": {
        "title": "SQLi -> normal",
        "diagnosis": "Schema-discovery SQLi can be mistaken for ordinary documentation or search traffic.",
        "suggested_repair_pattern": (
            "Add SQLi positives for information_schema, sqlite_master, pg_catalog, blocked status, "
            "and database-backed routes, paired with benign SQL documentation searches."
        ),
    },
    "sqli_to_port": {
        "title": "SQLi -> port/recon",
        "diagnosis": "Time-delay/API error SQLi can drift into generic reconnaissance.",
        "suggested_repair_pattern": (
            "Add SLEEP, pg_sleep, WAITFOR, and upstream latency SQLi positives without port/host "
            "enumeration cues."
        ),
    },
    "sqli_to_traversal": {
        "title": "SQLi -> traversal",
        "diagnosis": "SQL quote/comment boundaries are still confused with file-read or traversal signals.",
        "suggested_repair_pattern": (
            "Add close SQLi-vs-traversal contrasts: SQL comments, quotes, tautologies, stacked "
            "queries, and schema names versus ../, /etc/passwd, win.ini, .env, and wrappers."
        ),
    },
    "sqli_to_invalid": {
        "title": "SQLi -> invalid",
        "diagnosis": "Quote-heavy SQLi can still stress structured output if it reappears.",
        "suggested_repair_pattern": "Keep SQLi evidence short, exact, and JSON-escaped in training targets.",
    },
    "other_label_failure": {
        "title": "Other label failure",
        "diagnosis": "A label failure outside the v4.1 SQLi-first repair scope.",
        "suggested_repair_pattern": "Review manually before broadening the v4.1 supplement.",
    },
}


DATASET_IMPLICATIONS = [
    {
        "bucket": "SQLi positives",
        "target": "100 examples",
        "details": (
            "Overweight bare and quoted tautologies, SQL comments, SLEEP/pg_sleep/WAITFOR, "
            "information_schema/sqlite_master/pg_catalog, and stacked queries."
        ),
    },
    {
        "bucket": "Normal hard negatives",
        "target": "24 examples",
        "details": "Keep normal guard examples focused on benign SQL searches and single auth failures.",
    },
    {
        "bucket": "Brute-force positives",
        "target": "6 examples",
        "details": "Preserve threshold ownership with repeated failures, short windows, and spray cues.",
    },
    {
        "bucket": "Traversal positives",
        "target": "16 examples",
        "details": "Keep true traversal/file-read tokens clearly separate from SQL comment syntax.",
    },
    {
        "bucket": "Port/recon positives",
        "target": "4 examples",
        "details": "Use only clear service/host enumeration cues as a small recall guard.",
    },
]


PROBES = {
    "temp_0": TEMP_0_REPORT_PATH,
    "temp_0_3": TEMP_0_3_REPORT_PATH,
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
    if expected_label == "sql_injection_attempt" and predicted_label == "port_scan_or_recon":
        return "sqli_to_port"
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


def build_failure_cases(
    report: JsonObject,
    source_records: dict[str, JsonObject],
    *,
    probe_key: str,
) -> list[JsonObject]:
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
                "probe": probe_key,
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


def build_probe_summary(
    probe_key: str,
    report_path: Path,
    source_records: dict[str, JsonObject],
) -> JsonObject:
    report = read_json(report_path)
    failure_cases = build_failure_cases(report, source_records, probe_key=probe_key)
    expected_distribution = Counter(str(item["expected_label"]) for item in report["samples"])
    predicted_distribution = Counter(normalized_predicted_label(item) for item in report["samples"])

    return {
        "source_report_path": str(report_path.relative_to(ROOT)),
        "metrics": report.get("metrics", {}),
        "runtime_context": compact_metadata(report.get("adapter_metadata")),
        "sample_count": len(report["samples"]),
        "label_failure_count": len(failure_cases),
        "expected_label_distribution": dict(sorted(expected_distribution.items())),
        "predicted_label_distribution": dict(sorted(predicted_distribution.items())),
        "bucket_summary": make_bucket_summary(failure_cases),
        "failure_cases": failure_cases,
    }


def build_union_failure_cases(
    probe_summaries: dict[str, JsonObject],
    source_records: dict[str, JsonObject],
) -> list[JsonObject]:
    by_id: dict[str, dict[str, JsonObject]] = defaultdict(dict)
    for probe_key, summary in probe_summaries.items():
        for case in summary["failure_cases"]:
            by_id[str(case["id"])][probe_key] = case

    union_cases: list[JsonObject] = []
    for sample_id in sorted(by_id):
        source = source_records[sample_id]
        expected_output = source.get("output") or {}
        union_cases.append(
            {
                "id": sample_id,
                "input_log": source["input"],
                "expected_label": expected_output.get("label"),
                "expected_severity": expected_output.get("severity"),
                "expected_evidence": expected_output.get("evidence", []),
                "probe_predictions": {
                    probe_key: {
                        "failure_bucket": case["failure_bucket"],
                        "predicted_label": case["predicted_label"],
                        "predicted_severity": case["predicted_severity"],
                    }
                    for probe_key, case in sorted(by_id[sample_id].items())
                },
            }
        )
    return union_cases


def build_report() -> JsonObject:
    source_records = read_jsonl_by_id(SOURCE_SPLIT_PATH)
    probe_summaries = {
        probe_key: build_probe_summary(probe_key, report_path, source_records)
        for probe_key, report_path in PROBES.items()
    }
    union_failure_cases = build_union_failure_cases(probe_summaries, source_records)
    union_failure_ids = [case["id"] for case in union_failure_cases]

    return {
        "summary": (
            "v4.1 slices the v4 hard-contrast failures at temp 0 and temp 0.3 so the next "
            "repair can focus narrowly on SQLi boundaries, especially SQLi mistaken for traversal, "
            "without using the fixed test split."
        ),
        "created_date": CREATED_DATE,
        "source_split_path": str(SOURCE_SPLIT_PATH.relative_to(ROOT)),
        "fixed_test_split_used": False,
        "probe_summaries": probe_summaries,
        "union_label_failure_count": len(union_failure_cases),
        "union_failure_ids": union_failure_ids,
        "union_failure_cases": union_failure_cases,
        "dataset_implications": DATASET_IMPLICATIONS,
        "next_step": (
            "Create the v4.1 SQLi-boundary supplement on top of the v4 train split, then train "
            "from the base LFM2-350M model and run hard-contrast probes before any mini semantic eval."
        ),
    }


def md_table_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value).replace("\n", " ") for value in values) + " |"


def write_markdown(report: JsonObject) -> None:
    lines: list[str] = [
        "# Phase 8 V4.1 SQLi Boundary Failure Slice",
        "",
        "**Summary**",
        "",
        str(report["summary"]),
        "",
        "**Sources**",
        "",
        f"- `{report['probe_summaries']['temp_0']['source_report_path']}` for v4 temp 0 failures.",
        f"- `{report['probe_summaries']['temp_0_3']['source_report_path']}` for v4 temp 0.3 failures.",
        f"- `{report['source_split_path']}` for source log lines and expected outputs.",
        "- `docs/output-structure-fix/phase-8-v4-sqli-boundary-repair-plan.md` for v4 hold context.",
        "",
        "**Last updated**",
        "",
        str(report["created_date"]),
        "",
        "## Probe Snapshots",
        "",
        "| Probe | Samples | Label failures | Label accuracy | JSON/schema | Invalid | SQLi predicted traversal |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for probe_key, summary in report["probe_summaries"].items():
        buckets = {bucket["bucket"]: bucket["count"] for bucket in summary["bucket_summary"]}
        metrics = summary["metrics"]
        lines.append(
            md_table_row(
                [
                    f"`{probe_key}`",
                    f"`{summary['sample_count']}`",
                    f"`{summary['label_failure_count']}`",
                    f"`{metrics.get('label_accuracy')}`",
                    f"`{metrics.get('json_parse_success_rate')} / {metrics.get('schema_success_rate')}`",
                    f"`{metrics.get('invalid_output_count')}`",
                    f"`{buckets.get('sqli_to_traversal', 0)}`",
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Bucket Summary",
            "",
        ]
    )

    for probe_key, summary in report["probe_summaries"].items():
        lines.extend(
            [
                f"### `{probe_key}`",
                "",
                "| Bucket | Count | IDs | Diagnosis | Repair pattern |",
                "| --- | ---: | --- | --- | --- |",
            ]
        )
        for bucket in summary["bucket_summary"]:
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
        lines.append("")

    lines.extend(
        [
            "## Union Failures",
            "",
            f"Union failure ids: {', '.join(f'`{item}`' for item in report['union_failure_ids'])}",
            "",
            "| ID | Expected | Evidence | Probe predictions |",
            "| --- | --- | --- | --- |",
        ]
    )
    for case in report["union_failure_cases"]:
        predictions = "; ".join(
            f"{probe}: {prediction['predicted_label']} ({prediction['failure_bucket']})"
            for probe, prediction in case["probe_predictions"].items()
        )
        lines.append(
            md_table_row(
                [
                    f"`{case['id']}`",
                    f"`{case['expected_label']}`",
                    "; ".join(str(item) for item in case["expected_evidence"]),
                    predictions,
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
            "`data/splits/test.jsonl` must not be used for selecting v4.1 repair cases or tuning prompts/runtime settings.",
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
