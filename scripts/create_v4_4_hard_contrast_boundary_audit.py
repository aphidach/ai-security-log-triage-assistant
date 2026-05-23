#!/usr/bin/env python3
"""Create the Phase 8 v4.4 hard-contrast boundary audit.

This audit reads only the v4.3 Qwen3.5 hard-contrast reports and the
hard-contrast source split. It intentionally does not read the fixed test split,
create training data, or change model/runtime configuration.
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
    / "openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.json"
)
TEMP_0_3_REPORT_PATH = (
    ROOT
    / "reports"
    / "openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.json"
)
SOURCE_SPLIT_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"
OUTPUT_JSON_PATH = ROOT / "reports" / "phase-8-v4-4-hard-contrast-boundary-audit.json"
OUTPUT_MD_PATH = ROOT / "reports" / "phase-8-v4-4-hard-contrast-boundary-audit.md"

CREATED_DATE = "2026-05-23"

JsonObject = dict[str, Any]


BUCKET_DETAILS: dict[str, dict[str, str]] = {
    "normal_auth_negative_to_bruteforce": {
        "title": "Normal auth negative -> brute force",
        "diagnosis": "Single failed-auth negatives are still close to brute-force wording.",
        "boundary_read": "This is a small guardrail issue, not the main v4.4 blocker.",
        "next_action": "Keep the single-attempt threshold wording in future prompt/data audits.",
    },
    "bruteforce_to_normal": {
        "title": "Brute force -> normal",
        "diagnosis": "A failed-login positive without enough repeated-attempt framing can be undercalled.",
        "boundary_read": "This is secondary because failed_login_bruteforce recall remains 9/10.",
        "next_action": "Review the one missed brute-force case after suspicious-to-normal collapse is handled.",
    },
    "sqli_tautology_to_normal": {
        "title": "SQLi tautology -> normal",
        "diagnosis": "Classic OR/quote tautology cues are seen but treated as ordinary login/search traffic.",
        "boundary_read": "The model notices text fragments but does not attach the security meaning strongly enough.",
        "next_action": "If using prompt/data repair later, make SQL tautology cues explicit positives even inside normal-looking routes.",
    },
    "sqli_schema_to_normal": {
        "title": "SQLi schema discovery -> normal",
        "diagnosis": "information_schema-style schema discovery is interpreted as benign database/search activity.",
        "boundary_read": "The label boundary needs to say schema names in request/query fields are suspicious.",
        "next_action": "Pair benign SQL documentation searches against malicious request-field schema discovery.",
    },
    "sqli_timing_to_normal": {
        "title": "SQLi timing -> normal",
        "diagnosis": "SLEEP/latency cues are interpreted as backend processing rather than timing SQLi.",
        "boundary_read": "The model needs an explicit security mapping from timing functions to SQLi.",
        "next_action": "Use SLEEP/pg_sleep/WAITFOR cases only as SQLi positives unless host/port scan evidence is present.",
    },
    "sqli_login_payload_to_bruteforce": {
        "title": "SQLi login payload -> brute force",
        "diagnosis": "Login-form SQLi payloads drift into failed-login brute-force because the route/status dominates the payload.",
        "boundary_read": "This is older Phase 8 gravity in a smaller form; route context is overpowering payload semantics.",
        "next_action": "Teach that SQL payload syntax inside username/email fields owns the label over generic login failure wording.",
    },
    "traversal_to_normal": {
        "title": "Traversal -> normal",
        "diagnosis": "Traversal tokens are recognized but reframed as common or legitimate file access behavior.",
        "boundary_read": "This is a security-semantics miss, not an evidence extraction miss.",
        "next_action": "Keep traversal cues as suspicious even when the HTTP status is 403/404 or the route is a normal file endpoint.",
    },
    "recon_to_normal": {
        "title": "Recon -> normal",
        "diagnosis": "Nmap, service enumeration, sequential connection attempts, and unique_ports are called routine operations.",
        "boundary_read": "The model treats SOC/security-tool vocabulary as benign admin activity by default.",
        "next_action": "Require recon labels for explicit scan/probe/enumeration tokens unless the log states approved/internal testing.",
    },
    "other_label_failure": {
        "title": "Other label failure",
        "diagnosis": "A label failure outside the named v4.4 boundary buckets.",
        "boundary_read": "Review manually before creating any repair data.",
        "next_action": "Do not broaden the taxonomy; classify the case before deciding on data or prompt repair.",
    },
}


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


def bucket_for(expected_label: str, predicted_label: str, input_log: str) -> str:
    lowered_log = input_log.lower()
    if expected_label == "normal" and predicted_label == "failed_login_bruteforce":
        return "normal_auth_negative_to_bruteforce"
    if expected_label == "failed_login_bruteforce" and predicted_label == "normal":
        return "bruteforce_to_normal"
    if expected_label == "sql_injection_attempt" and predicted_label == "failed_login_bruteforce":
        return "sqli_login_payload_to_bruteforce"
    if expected_label == "sql_injection_attempt" and predicted_label == "normal":
        if any(token in lowered_log for token in ("sleep(", "pg_sleep", "waitfor")):
            return "sqli_timing_to_normal"
        if any(token in lowered_log for token in ("information_schema", "sqlite_master", "pg_catalog")):
            return "sqli_schema_to_normal"
        return "sqli_tautology_to_normal"
    if expected_label == "directory_traversal_attempt" and predicted_label == "normal":
        return "traversal_to_normal"
    if expected_label == "port_scan_or_recon" and predicted_label == "normal":
        return "recon_to_normal"
    return "other_label_failure"


def build_failure_cases(
    report: JsonObject,
    source_records: dict[str, JsonObject],
    *,
    probe_key: str,
) -> list[JsonObject]:
    failures: list[JsonObject] = []
    for sample in report["samples"]:
        expected = sample["expected_label"]
        predicted = normalized_predicted_label(sample)
        if expected == predicted:
            continue

        sample_id = sample["id"]
        source = source_records.get(sample_id)
        if source is None:
            raise ValueError(f"source split is missing sample id {sample_id}")

        input_log = source["input"]
        bucket_key = bucket_for(expected, predicted, input_log)
        bucket = BUCKET_DETAILS[bucket_key]
        expected_output = source.get("output") or {}
        prediction = sample.get("prediction") or {}

        failures.append(
            {
                "id": sample_id,
                "probe": probe_key,
                "failure_bucket": bucket_key,
                "failure_bucket_title": bucket["title"],
                "input_log": input_log,
                "expected_label": expected,
                "predicted_label": predicted,
                "expected_severity": sample.get("expected_severity"),
                "predicted_severity": sample.get("predicted_severity"),
                "expected_is_suspicious": sample.get("expected_is_suspicious"),
                "predicted_is_suspicious": sample.get("predicted_is_suspicious"),
                "json_parse_success": sample.get("json_parse_success"),
                "schema_success": sample.get("schema_success"),
                "expected_evidence": expected_output.get("evidence", []),
                "predicted_evidence": prediction.get("evidence", []),
                "predicted_reason": prediction.get("reason"),
                "diagnosis": bucket["diagnosis"],
                "boundary_read": bucket["boundary_read"],
                "next_action": bucket["next_action"],
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
                "boundary_read": bucket["boundary_read"],
                "next_action": bucket["next_action"],
            }
        )
    return summary


def count_key_cases(failure_cases: list[JsonObject]) -> JsonObject:
    suspicious_to_normal = [
        item
        for item in failure_cases
        if item["expected_label"]
        in {
            "sql_injection_attempt",
            "directory_traversal_attempt",
            "port_scan_or_recon",
        }
        and item["predicted_label"] == "normal"
    ]
    return {
        "sqli_traversal_recon_to_normal_count": len(suspicious_to_normal),
        "sqli_traversal_recon_to_normal_ids": [item["id"] for item in suspicious_to_normal],
    }


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
        "key_case_counts": count_key_cases(failure_cases),
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
        first_case = next(iter(by_id[sample_id].values()))
        union_cases.append(
            {
                "id": sample_id,
                "input_log": source["input"],
                "expected_label": expected_output.get("label"),
                "expected_severity": expected_output.get("severity"),
                "expected_evidence": expected_output.get("evidence", []),
                "primary_failure_bucket": first_case["failure_bucket"],
                "primary_failure_bucket_title": first_case["failure_bucket_title"],
                "probe_predictions": {
                    probe_key: {
                        "failure_bucket": case["failure_bucket"],
                        "predicted_label": case["predicted_label"],
                        "predicted_severity": case["predicted_severity"],
                        "predicted_is_suspicious": case["predicted_is_suspicious"],
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

    failure_sets = {
        probe_key: {case["id"] for case in summary["failure_cases"]}
        for probe_key, summary in probe_summaries.items()
    }
    persistent_ids = sorted(set.intersection(*failure_sets.values()))
    union_ids = [case["id"] for case in union_failure_cases]

    return {
        "summary": (
            "v4.4 audits the v4.3 Qwen3.5 hard-contrast failures. The model keeps "
            "JSON/schema reliability but collapses many suspicious SQLi, traversal, "
            "and recon records into normal."
        ),
        "created_date": CREATED_DATE,
        "diagnostic_type": "hard_contrast_boundary_audit",
        "source_split_path": str(SOURCE_SPLIT_PATH.relative_to(ROOT)),
        "fixed_test_split_used": False,
        "training_artifacts_created": False,
        "probe_summaries": probe_summaries,
        "union_label_failure_count": len(union_failure_cases),
        "persistent_label_failure_count": len(persistent_ids),
        "union_failure_ids": union_ids,
        "persistent_failure_ids": persistent_ids,
        "union_failure_cases": union_failure_cases,
        "boundary_decision": (
            "Do not train from this result yet. The next useful evidence is either a "
            "candidate with stronger security-log semantics or a deliberately scoped "
            "prompt/data boundary repair based on the suspicious-to-normal buckets."
        ),
        "recommended_next_step": (
            "Keep fixed test closed, keep Qwen3.5-0.8B held, and choose between another "
            "capacity candidate and a small boundary-repair prompt/data experiment."
        ),
    }


def md_table_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value).replace("\n", " ") for value in values) + " |"


def format_ids(ids: list[str]) -> str:
    return ", ".join(f"`{item}`" for item in ids)


def write_markdown(report: JsonObject) -> None:
    lines: list[str] = [
        "# Phase 8 V4.4 Hard-Contrast Boundary Audit",
        "",
        "**Summary**",
        "",
        str(report["summary"]),
        "",
        "**Sources**",
        "",
        f"- `{report['probe_summaries']['temp_0']['source_report_path']}` for Qwen3.5 temp 0 hard-contrast failures.",
        f"- `{report['probe_summaries']['temp_0_3']['source_report_path']}` for Qwen3.5 temp 0.3 hard-contrast failures.",
        f"- `{report['source_split_path']}` for source log lines and expected outputs.",
        "- `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md` for the v4.3 hold decision.",
        "",
        "**Last updated**",
        "",
        str(report["created_date"]),
        "",
        "## Probe Snapshots",
        "",
        "| Probe | Samples | Label failures | Persistent? | Label accuracy | JSON/schema | Invalid | SQLi/traversal/recon -> normal |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    persistent = set(report["persistent_failure_ids"])
    for probe_key, summary in report["probe_summaries"].items():
        failures = {case["id"] for case in summary["failure_cases"]}
        metrics = summary["metrics"]
        lines.append(
            md_table_row(
                [
                    f"`{probe_key}`",
                    f"`{summary['sample_count']}`",
                    f"`{summary['label_failure_count']}`",
                    f"`{len(failures & persistent)}`",
                    f"`{metrics.get('label_accuracy')}`",
                    f"`{metrics.get('json_parse_success_rate')} / {metrics.get('schema_success_rate')}`",
                    f"`{metrics.get('invalid_output_count')}`",
                    f"`{summary['key_case_counts']['sqli_traversal_recon_to_normal_count']}`",
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Boundary Read",
            "",
            f"- Union label failures: `{report['union_label_failure_count']}` IDs.",
            f"- Persistent failures across both probes: `{report['persistent_label_failure_count']}` IDs.",
            "- Main failure family: suspicious SQLi/traversal/recon examples are classified as `normal` while JSON/schema stay perfect.",
            "- Temp `0.3` adds one extra failure (`v3-hard-000024`) and does not change the core failure shape.",
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
                "| Bucket | Count | IDs | Boundary read | Next action |",
                "| --- | ---: | --- | --- | --- |",
            ]
        )
        for bucket in summary["bucket_summary"]:
            lines.append(
                md_table_row(
                    [
                        bucket["title"],
                        f"`{bucket['count']}`",
                        format_ids(bucket["ids"]),
                        bucket["boundary_read"],
                        bucket["next_action"],
                    ]
                )
            )
        lines.append("")

    lines.extend(
        [
            "## Union Failures",
            "",
            f"Union failure ids: {format_ids(report['union_failure_ids'])}",
            "",
            "| ID | Expected | Evidence | Temp 0 | Temp 0.3 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for case in report["union_failure_cases"]:
        temp_0 = case["probe_predictions"].get("temp_0")
        temp_0_3 = case["probe_predictions"].get("temp_0_3")
        lines.append(
            md_table_row(
                [
                    f"`{case['id']}`",
                    f"`{case['expected_label']}`",
                    "; ".join(str(item) for item in case["expected_evidence"]),
                    temp_0["predicted_label"] if temp_0 else "pass",
                    temp_0_3["predicted_label"] if temp_0_3 else "pass",
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            str(report["boundary_decision"]),
            "",
            "## Next Step",
            "",
            str(report["recommended_next_step"]),
            "",
            "## Hold Fixed Test",
            "",
            "`data/splits/test.jsonl` was not read and must stay closed for this boundary audit.",
            "",
            "## No Training Artifacts",
            "",
            "v4.4 creates only audit reports. It does not create supplement data, train/validation splits, a LoRA config, or train allowlist entries.",
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
