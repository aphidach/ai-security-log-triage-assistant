#!/usr/bin/env python3
"""Create the Phase 8 v4.2 SQLi priority prompt diagnostic slice.

This report is a v4.2 planning artifact. It reads only the v4.1 hard-contrast
temperature=0 and temperature=0.3 reports plus the hard-contrast source split.
It intentionally does not read the fixed test split or create training data.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

TEMP_0_REPORT_PATH = (
    ROOT
    / "reports"
    / "openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.json"
)
TEMP_0_3_REPORT_PATH = (
    ROOT
    / "reports"
    / "openai-compatible-vllm-structured-outputs-v4-1-temp-03-2048-hard-contrast-memorization-probe.json"
)
SOURCE_SPLIT_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"
OUTPUT_JSON_PATH = ROOT / "reports" / "phase-8-v4-2-sqli-priority-diagnostic-slice.json"
OUTPUT_MD_PATH = ROOT / "reports" / "phase-8-v4-2-sqli-priority-diagnostic-slice.md"

CREATED_DATE = "2026-05-22"

JsonObject = dict[str, Any]


BUCKET_DETAILS: dict[str, dict[str, str]] = {
    "normal_to_bruteforce": {
        "title": "Normal -> brute force",
        "diagnosis": "Single failed-auth events are still over-escalated without repeated attempts or short-window volume.",
        "prompt_repair_pattern": (
            "State that brute force needs repeated failures, a short window, many users, or many passwords; "
            "single failed logons remain normal monitoring cases."
        ),
    },
    "sqli_to_normal": {
        "title": "SQLi -> normal",
        "diagnosis": "Database schema-discovery tokens can still be treated as ordinary search traffic.",
        "prompt_repair_pattern": (
            "Give SQLi priority to information_schema, sqlite_master, and pg_catalog when they appear in "
            "request, query, body, search, or API fields."
        ),
    },
    "sqli_to_port": {
        "title": "SQLi -> port/recon",
        "diagnosis": "Time-delay SQLi can drift into generic reconnaissance when the log includes API errors or latency.",
        "prompt_repair_pattern": (
            "State that SLEEP, pg_sleep, and WAITFOR DELAY are SQLi timing payloads unless explicit host, "
            "port, scan, or service-enumeration evidence is present."
        ),
    },
    "sqli_to_traversal": {
        "title": "SQLi -> traversal",
        "diagnosis": "SQL comments, stacked queries, and destructive SQL verbs can still be confused with file/path access.",
        "prompt_repair_pattern": (
            "State that SQL comments and ;DROP TABLE / ;SELECT should stay SQLi unless traversal tokens such as ../, "
            "/etc/passwd, win.ini, .env, WEB-INF, or php://filter are present."
        ),
    },
    "sqli_to_invalid": {
        "title": "SQLi -> invalid",
        "diagnosis": "Quote-heavy SQLi can stress structured output if it reappears.",
        "prompt_repair_pattern": "Keep SQLi evidence short, exact, and copied from the input.",
    },
    "other_label_failure": {
        "title": "Other label failure",
        "diagnosis": "A label failure outside the v4.2 SQLi-priority diagnostic scope.",
        "prompt_repair_pattern": "Review manually before broadening v4.2 beyond prompt priority.",
    },
}


PROMPT_DIAGNOSTIC_RULES = [
    {
        "rule": "SQLi priority",
        "details": (
            "Prioritize SQLi when SQL tokens appear in request/query/body/login fields: OR 1=1, quoted "
            "tautologies, SQL comments, SLEEP/pg_sleep/WAITFOR DELAY, information_schema/sqlite_master/"
            "pg_catalog, ;DROP TABLE, and ;SELECT."
        ),
    },
    {
        "rule": "Traversal guard",
        "details": "Traversal still needs file/path access cues such as ../, encoded traversal, /etc/passwd, win.ini, .env, WEB-INF, or php://filter.",
    },
    {
        "rule": "Bruteforce guard",
        "details": "Brute force still needs repeated failures, a short window, or many users/passwords.",
    },
    {
        "rule": "Recon guard",
        "details": "Recon still needs explicit scan, probing, enumeration, host, service, nmap, SYN scan, or multi-port evidence.",
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
                "prompt_repair_pattern": bucket["prompt_repair_pattern"],
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
                "prompt_repair_pattern": bucket["prompt_repair_pattern"],
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
            "v4.2 slices the v4.1 hard-contrast label failures so the next repair can test "
            "SQLi label-priority prompt rules without adding training data or using the fixed test split."
        ),
        "created_date": CREATED_DATE,
        "diagnostic_type": "prompt_priority",
        "source_split_path": str(SOURCE_SPLIT_PATH.relative_to(ROOT)),
        "fixed_test_split_used": False,
        "training_artifacts_created": False,
        "probe_summaries": probe_summaries,
        "union_label_failure_count": len(union_failure_cases),
        "union_failure_ids": union_failure_ids,
        "union_failure_cases": union_failure_cases,
        "prompt_diagnostic_rules": PROMPT_DIAGNOSTIC_RULES,
        "next_step": (
            "Run hard-contrast probes against alias lfm2-security-triage-v4-1 with "
            "OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.2-sqli-priority before any mini semantic eval."
        ),
    }


def md_table_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value).replace("\n", " ") for value in values) + " |"


def write_markdown(report: JsonObject) -> None:
    lines: list[str] = [
        "# Phase 8 V4.2 SQLi Priority Diagnostic Slice",
        "",
        "**Summary**",
        "",
        str(report["summary"]),
        "",
        "**Sources**",
        "",
        f"- `{report['probe_summaries']['temp_0']['source_report_path']}` for v4.1 temp 0 failures.",
        f"- `{report['probe_summaries']['temp_0_3']['source_report_path']}` for v4.1 temp 0.3 failures.",
        f"- `{report['source_split_path']}` for source log lines and expected outputs.",
        "- `docs/output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan.md` for v4.1 hold context.",
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

    lines.extend(["", "## Bucket Summary", ""])

    for probe_key, summary in report["probe_summaries"].items():
        lines.extend(
            [
                f"### `{probe_key}`",
                "",
                "| Bucket | Count | IDs | Diagnosis | Prompt repair pattern |",
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
                        bucket["prompt_repair_pattern"],
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
            "## Prompt Diagnostic Rules",
            "",
            "| Rule | Details |",
            "| --- | --- |",
        ]
    )
    for item in report["prompt_diagnostic_rules"]:
        lines.append(md_table_row([item["rule"], item["details"]]))

    lines.extend(
        [
            "",
            "## Hold Fixed Test",
            "",
            "`data/splits/test.jsonl` must not be used for selecting v4.2 prompt rules or tuning runtime settings.",
            "",
            "## No Training Artifacts",
            "",
            "v4.2 does not create supplement data, train/validation splits, a LoRA config, or train allowlist entries.",
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
    print("No training artifacts were created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
