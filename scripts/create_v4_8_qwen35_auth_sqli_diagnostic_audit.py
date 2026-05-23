#!/usr/bin/env python3
"""Create the Phase 8 v4.8 Qwen3.5 auth/SQLi diagnostic audit.

The audit reads only non-fixed v4.7 probe reports and the v4.7 probe split.
It does not read the fixed test split, create training data, or change runtime
configuration. Its job is to compare the held v4.7 adapter against the local
heuristic baseline and the currently served base Qwen3.5 diagnostic run before
any v4.8 training data is created.
"""

from __future__ import annotations

import html
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

V4_7_PROBE_PATH = ROOT / "data" / "splits" / "v4-7-auth-sqli-severity-calibration-probe.jsonl"
V4_7_MODEL_REPORT_PATH = (
    ROOT
    / "reports"
    / "openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json"
)
HEURISTIC_REPORT_PATH = ROOT / "reports" / "heuristic-v4-7-auth-sqli-severity-calibration-probe.json"
BASE_MODEL_REPORT_PATH = (
    ROOT
    / "reports"
    / "openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.json"
)
OUTPUT_JSON_PATH = ROOT / "reports" / "phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json"
OUTPUT_MD_PATH = ROOT / "reports" / "phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.md"
OUTPUT_HTML_PATH = ROOT / "reports" / "phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html"

CREATED_DATE = "2026-05-23"

JsonObject = dict[str, Any]


REPORTS = {
    "v4_7_model": V4_7_MODEL_REPORT_PATH,
    "heuristic": HEURISTIC_REPORT_PATH,
    "base_qwen35": BASE_MODEL_REPORT_PATH,
}

REPORT_TITLES = {
    "v4_7_model": "v4.7 trained adapter",
    "heuristic": "heuristic baseline",
    "base_qwen35": "base Qwen3.5",
}

METRIC_KEYS = (
    "label_accuracy",
    "severity_accuracy",
    "is_suspicious_accuracy",
    "evidence_partial_match",
    "json_parse_success_rate",
    "schema_success_rate",
    "invalid_output_count",
    "average_latency_ms",
)

BUCKET_DETAILS: dict[str, dict[str, str]] = {
    "normal_auth_negative": {
        "title": "Normal auth negative",
        "diagnosis": "v4.7 treats benign auth/login vocabulary as enough evidence for brute force.",
        "next_action": "Keep these as paired contrasts; brute force must require repeated attempts, a rate/window, or blocking evidence.",
    },
    "sqli_auth_context": {
        "title": "SQLi inside auth context",
        "diagnosis": "v4.7 underweights SQL payload syntax when the route looks like login or account activity.",
        "next_action": "Make SQL payload tokens in username, email, or query fields own the label over generic auth route context.",
    },
    "bruteforce_medium_severity": {
        "title": "Brute force medium severity",
        "diagnosis": "v4.7 keeps brute-force label recall, but escalates all medium examples to high.",
        "next_action": "Add a medium severity contract: high requires larger volume, spread, privileged target, lockout, or confirmed blocking impact.",
    },
    "port_recon_severity": {
        "title": "Port/recon severity boundary",
        "diagnosis": "v4.7 mostly keeps the recon label, but one medium/high boundary remains unstable.",
        "next_action": "Keep only a small severity pair for recon; do not broaden the recon taxonomy.",
    },
    "directory_traversal_guard": {
        "title": "Directory traversal guard",
        "diagnosis": "v4.7 passes the single traversal guard in this probe.",
        "next_action": "Keep this as a regression guard rather than a main v4.8 data target.",
    },
}


def read_json(path: Path) -> JsonObject:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[JsonObject]:
    records: list[JsonObject] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_no}: JSONL record must be an object")
        if not isinstance(record.get("id"), str):
            raise ValueError(f"{path}:{line_no}: missing string id")
        records.append(record)
    return records


def sample_map(report: JsonObject) -> dict[str, JsonObject]:
    samples: dict[str, JsonObject] = {}
    for sample in report.get("samples", []):
        sample_id = sample.get("id")
        if not isinstance(sample_id, str):
            raise ValueError("report sample is missing string id")
        samples[sample_id] = sample
    return samples


def report_metrics(report: JsonObject) -> JsonObject:
    metrics = report.get("metrics", {})
    return {key: metrics.get(key) for key in METRIC_KEYS}


def bucket_for(record: JsonObject) -> str:
    output = record.get("output", {})
    label = output.get("label") if isinstance(output, dict) else None
    if label == "normal":
        return "normal_auth_negative"
    if label == "sql_injection_attempt":
        return "sqli_auth_context"
    if label == "failed_login_bruteforce":
        return "bruteforce_medium_severity"
    if label == "port_scan_or_recon":
        return "port_recon_severity"
    if label == "directory_traversal_attempt":
        return "directory_traversal_guard"
    raise ValueError(f"unexpected label in v4.7 diagnostic probe: {label!r}")


def predicted_label(sample: JsonObject | None) -> str:
    if not sample:
        return "<missing>"
    label = sample.get("predicted_label")
    return label if isinstance(label, str) else "<invalid>"


def predicted_severity(sample: JsonObject | None) -> str:
    if not sample:
        return "<missing>"
    severity = sample.get("predicted_severity")
    return severity if isinstance(severity, str) else "<invalid>"


def bool_count(samples: list[JsonObject], key: str) -> int:
    return sum(1 for sample in samples if bool(sample.get(key)))


def summarize_bucket(bucket_key: str, records: list[JsonObject], samples_by_report: dict[str, dict[str, JsonObject]]) -> JsonObject:
    ids = [str(record["id"]) for record in records]
    summary: JsonObject = {
        "bucket": bucket_key,
        "title": BUCKET_DETAILS[bucket_key]["title"],
        "sample_count": len(records),
        "ids": ids,
        "diagnosis": BUCKET_DETAILS[bucket_key]["diagnosis"],
        "next_action": BUCKET_DETAILS[bucket_key]["next_action"],
        "reports": {},
    }

    for report_key, samples_by_id in samples_by_report.items():
        bucket_samples = [samples_by_id[sample_id] for sample_id in ids]
        summary["reports"][report_key] = {
            "label_correct": bool_count(bucket_samples, "label_correct"),
            "severity_correct": bool_count(bucket_samples, "severity_correct"),
            "schema_success": bool_count(bucket_samples, "schema_success"),
            "invalid_output": sum(1 for sample in bucket_samples if not bool(sample.get("schema_success"))),
            "predicted_label_distribution": dict(
                sorted(Counter(predicted_label(sample) for sample in bucket_samples).items())
            ),
            "predicted_severity_distribution": dict(
                sorted(Counter(predicted_severity(sample) for sample in bucket_samples).items())
            ),
        }
    return summary


def build_cases(records: list[JsonObject], samples_by_report: dict[str, dict[str, JsonObject]]) -> list[JsonObject]:
    cases: list[JsonObject] = []
    for record in records:
        sample_id = str(record["id"])
        output = record.get("output", {})
        expected_label = output.get("label") if isinstance(output, dict) else None
        expected_severity = output.get("severity") if isinstance(output, dict) else None
        case: JsonObject = {
            "id": sample_id,
            "bucket": bucket_for(record),
            "input": record.get("input", ""),
            "expected_label": expected_label,
            "expected_severity": expected_severity,
            "expected_evidence": output.get("evidence", []) if isinstance(output, dict) else [],
            "reports": {},
        }
        for report_key, samples_by_id in samples_by_report.items():
            sample = samples_by_id[sample_id]
            case["reports"][report_key] = {
                "predicted_label": predicted_label(sample),
                "predicted_severity": predicted_severity(sample),
                "label_correct": bool(sample.get("label_correct")),
                "severity_correct": bool(sample.get("severity_correct")),
                "schema_success": bool(sample.get("schema_success")),
                "evidence_partial_match": bool(sample.get("evidence_partial_match")),
            }
        cases.append(case)
    return cases


def metric_delta(left: JsonObject, right: JsonObject, key: str) -> float | int | None:
    left_value = left.get(key)
    right_value = right.get(key)
    if not isinstance(left_value, (int, float)) or not isinstance(right_value, (int, float)):
        return None
    return round(left_value - right_value, 6)


def build_report() -> JsonObject:
    records = read_jsonl(V4_7_PROBE_PATH)
    reports = {key: read_json(path) for key, path in REPORTS.items()}
    samples_by_report = {key: sample_map(report) for key, report in reports.items()}

    record_ids = [str(record["id"]) for record in records]
    for report_key, samples_by_id in samples_by_report.items():
        missing = sorted(set(record_ids) - set(samples_by_id))
        extra = sorted(set(samples_by_id) - set(record_ids))
        if missing or extra:
            raise ValueError(f"{report_key} sample IDs do not match probe; missing={missing}, extra={extra}")

    records_by_bucket: dict[str, list[JsonObject]] = {bucket: [] for bucket in BUCKET_DETAILS}
    for record in records:
        records_by_bucket[bucket_for(record)].append(record)

    metrics = {key: report_metrics(report) for key, report in reports.items()}
    cases = build_cases(records, samples_by_report)

    return {
        "diagnostic_type": "v4_8_auth_sqli_severity_diagnostic_audit",
        "created_date": CREATED_DATE,
        "fixed_test_split_used": False,
        "training_artifacts_created": False,
        "source_probe": str(V4_7_PROBE_PATH.relative_to(ROOT)),
        "source_reports": {key: str(path.relative_to(ROOT)) for key, path in REPORTS.items()},
        "output_reports": {
            "json": str(OUTPUT_JSON_PATH.relative_to(ROOT)),
            "markdown": str(OUTPUT_MD_PATH.relative_to(ROOT)),
            "html": str(OUTPUT_HTML_PATH.relative_to(ROOT)),
        },
        "comparator_status": {
            "v4_6_on_v4_7_probe": {
                "status": "blocked_not_served",
                "requested_alias": "qwen3.6-8B-triage-v2",
                "observed_served_model_ids": ["unsloth/Qwen3.5-0.8B", "qwen3.6-8B-triage-v3"],
                "note": "Endpoint inventory on 2026-05-23 did not expose the v4.6 alias, so the audit uses heuristic and base Qwen3.5 comparators first.",
            }
        },
        "headline_metrics": metrics,
        "metric_deltas": {
            "v4_7_model_minus_heuristic": {
                key: metric_delta(metrics["v4_7_model"], metrics["heuristic"], key) for key in METRIC_KEYS
            },
            "v4_7_model_minus_base_qwen35": {
                key: metric_delta(metrics["v4_7_model"], metrics["base_qwen35"], key) for key in METRIC_KEYS
            },
        },
        "bucket_summary": [
            summarize_bucket(bucket, records_by_bucket[bucket], samples_by_report)
            for bucket in BUCKET_DETAILS
        ],
        "cases": cases,
        "recommended_v4_8_gates": {
            "calibration_label_accuracy": ">= 0.85",
            "normal_auth_label_correct": ">= 13/15",
            "sqli_auth_context_label_correct": ">= 4/5",
            "bruteforce_medium_severity_correct": ">= 5/7",
            "hard_contrast_label_accuracy": ">= 0.92",
            "json_schema": "1.0 / 1.0",
            "invalid_output_count": "0",
        },
        "decision": {
            "status": "prepare_v4_8_diagnostic_first",
            "fixed_split": "closed",
            "training": "not_started",
            "summary": (
                "v4.7 stays held. The next action is a small v4.8 paired-contrast repair after "
                "this diagnostic audit, not a broad dataset expansion or fixed-split run."
            ),
        },
    }


def markdown_metrics_table(report: JsonObject) -> list[str]:
    lines = [
        "| Comparator | Label | Severity | Suspicious | Evidence | JSON/schema | Invalid | Avg latency |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key in ("v4_7_model", "heuristic", "base_qwen35"):
        metrics = report["headline_metrics"][key]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{REPORT_TITLES[key]}`",
                    f"`{metrics['label_accuracy']}`",
                    f"`{metrics['severity_accuracy']}`",
                    f"`{metrics['is_suspicious_accuracy']}`",
                    f"`{metrics['evidence_partial_match']}`",
                    f"`{metrics['json_parse_success_rate']} / {metrics['schema_success_rate']}`",
                    f"`{metrics['invalid_output_count']}`",
                    f"`{metrics['average_latency_ms']}`",
                ]
            )
            + " |"
        )
    return lines


def markdown_bucket_table(report: JsonObject) -> list[str]:
    lines = [
        "| Bucket | Samples | v4.7 label/severity | Heuristic label/severity | Base label/severity | Diagnostic read |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for bucket in report["bucket_summary"]:
        reports = bucket["reports"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{bucket['bucket']}`",
                    f"`{bucket['sample_count']}`",
                    f"`{reports['v4_7_model']['label_correct']}/{bucket['sample_count']} / {reports['v4_7_model']['severity_correct']}/{bucket['sample_count']}`",
                    f"`{reports['heuristic']['label_correct']}/{bucket['sample_count']} / {reports['heuristic']['severity_correct']}/{bucket['sample_count']}`",
                    f"`{reports['base_qwen35']['label_correct']}/{bucket['sample_count']} / {reports['base_qwen35']['severity_correct']}/{bucket['sample_count']}`",
                    bucket["diagnosis"],
                ]
            )
            + " |"
        )
    return lines


def write_json_report(report: JsonObject) -> None:
    OUTPUT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown_report(report: JsonObject) -> None:
    blocked = report["comparator_status"]["v4_6_on_v4_7_probe"]
    lines = [
        "# Phase 8 V4.8 Qwen3.5 Auth/SQLi Diagnostic Audit",
        "",
        f"- Created: `{report['created_date']}`",
        f"- Source probe: `{report['source_probe']}`",
        "- Fixed split used: `false`",
        "- Training artifacts created: `false`",
        "- Decision: `prepare_v4_8_diagnostic_first`; fixed split remains closed.",
        "",
        "## Comparator Status",
        "",
        f"- v4.6 on v4.7 probe: `{blocked['status']}` because alias `{blocked['requested_alias']}` was not in the observed served model list.",
        f"- Observed served model IDs: `{', '.join(blocked['observed_served_model_ids'])}`",
        "",
        "## Headline Metrics",
        "",
        *markdown_metrics_table(report),
        "",
        "## Bucket Summary",
        "",
        *markdown_bucket_table(report),
        "",
        "## Recommended V4.8 Gate",
        "",
    ]
    for key, value in report["recommended_v4_8_gates"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(
        [
            "",
            "## Source Reports",
            "",
        ]
    )
    for key, path in report["source_reports"].items():
        lines.append(f"- `{key}`: `{path}`")

    OUTPUT_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def html_escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def write_html_report(report: JsonObject) -> None:
    metrics_rows = []
    for key in ("v4_7_model", "heuristic", "base_qwen35"):
        metrics = report["headline_metrics"][key]
        metrics_rows.append(
            "<tr>"
            f"<td>{html_escape(REPORT_TITLES[key])}</td>"
            f"<td>{html_escape(metrics['label_accuracy'])}</td>"
            f"<td>{html_escape(metrics['severity_accuracy'])}</td>"
            f"<td>{html_escape(metrics['is_suspicious_accuracy'])}</td>"
            f"<td>{html_escape(metrics['evidence_partial_match'])}</td>"
            f"<td>{html_escape(metrics['json_parse_success_rate'])} / {html_escape(metrics['schema_success_rate'])}</td>"
            f"<td>{html_escape(metrics['invalid_output_count'])}</td>"
            f"<td>{html_escape(metrics['average_latency_ms'])}</td>"
            "</tr>"
        )

    bucket_rows = []
    for bucket in report["bucket_summary"]:
        reports = bucket["reports"]
        count = bucket["sample_count"]
        bucket_rows.append(
            "<tr>"
            f"<td><code>{html_escape(bucket['bucket'])}</code><span>{html_escape(bucket['title'])}</span></td>"
            f"<td>{html_escape(count)}</td>"
            f"<td>{html_escape(reports['v4_7_model']['label_correct'])}/{count}<small>label</small><br>{html_escape(reports['v4_7_model']['severity_correct'])}/{count}<small>severity</small></td>"
            f"<td>{html_escape(reports['heuristic']['label_correct'])}/{count}<small>label</small><br>{html_escape(reports['heuristic']['severity_correct'])}/{count}<small>severity</small></td>"
            f"<td>{html_escape(reports['base_qwen35']['label_correct'])}/{count}<small>label</small><br>{html_escape(reports['base_qwen35']['severity_correct'])}/{count}<small>severity</small></td>"
            f"<td>{html_escape(bucket['next_action'])}</td>"
            "</tr>"
        )

    case_rows = []
    for case in report["cases"]:
        v47 = case["reports"]["v4_7_model"]
        heuristic = case["reports"]["heuristic"]
        case_rows.append(
            "<tr>"
            f"<td><code>{html_escape(case['id'])}</code></td>"
            f"<td><code>{html_escape(case['bucket'])}</code></td>"
            f"<td>{html_escape(case['expected_label'])}<br><small>{html_escape(case['expected_severity'])}</small></td>"
            f"<td>{html_escape(v47['predicted_label'])}<br><small>{html_escape(v47['predicted_severity'])}</small></td>"
            f"<td>{html_escape(heuristic['predicted_label'])}<br><small>{html_escape(heuristic['predicted_severity'])}</small></td>"
            "</tr>"
        )

    blocked = report["comparator_status"]["v4_6_on_v4_7_probe"]
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Phase 8 v4.8 Qwen3.5 Diagnostic Audit</title>
  <style>
    :root {{
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #18202a;
      --muted: #5b6572;
      --line: #d9dee7;
      --accent: #176b87;
      --hold: #a33d2a;
      --ok: #197046;
      --warn: #9a6a00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 32px max(24px, calc((100vw - 1120px) / 2)) 24px;
      background: #ffffff;
      border-bottom: 1px solid var(--line);
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 24px;
    }}
    h1, h2 {{ margin: 0; letter-spacing: 0; }}
    h1 {{ font-size: clamp(28px, 4vw, 44px); line-height: 1.05; max-width: 900px; }}
    h2 {{ font-size: 18px; margin-top: 28px; margin-bottom: 12px; }}
    p {{ margin: 8px 0 0; color: var(--muted); max-width: 900px; }}
    .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 4px 10px;
      border: 1px solid var(--line);
      background: #f9fbfc;
      color: var(--muted);
      font-weight: 650;
      margin-bottom: 14px;
    }}
    .decision {{
      margin-top: 18px;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 14px;
      min-height: 88px;
    }}
    .metric strong {{ display: block; font-size: 24px; line-height: 1.1; }}
    .metric span {{ color: var(--muted); }}
    .hold strong {{ color: var(--hold); }}
    .warn strong {{ color: var(--warn); }}
    .ok strong {{ color: var(--ok); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
    }}
    th, td {{
      text-align: left;
      vertical-align: top;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .02em;
      background: #fbfcfd;
    }}
    td span, small {{
      display: block;
      color: var(--muted);
      font-size: 12px;
    }}
    code {{
      font: 12px/1.4 "SFMono-Regular", Consolas, monospace;
      background: #eef3f6;
      padding: 1px 4px;
    }}
    .note {{
      border-left: 4px solid var(--accent);
      background: #eef7fa;
      padding: 12px 14px;
      margin: 12px 0 20px;
      color: var(--ink);
    }}
    @media (max-width: 760px) {{
      .decision {{ grid-template-columns: 1fr; }}
      table {{ display: block; overflow-x: auto; }}
      th, td {{ min-width: 140px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="pill">Created {html_escape(report['created_date'])}</div>
    <h1>Phase 8 v4.8 Qwen3.5 Diagnostic Audit</h1>
    <p>v4.7 stays held. This report compares the held adapter against heuristic and base Qwen3.5 runs on the same non-fixed auth/SQLi/severity probe before any v4.8 training work.</p>
    <div class="decision">
      <div class="metric hold"><strong>Hold</strong><span>fixed split remains closed</span></div>
      <div class="metric warn"><strong>{html_escape(report['headline_metrics']['v4_7_model']['label_accuracy'])}</strong><span>v4.7 calibration label accuracy</span></div>
      <div class="metric ok"><strong>{html_escape(report['headline_metrics']['heuristic']['label_accuracy'])}</strong><span>heuristic label accuracy on same probe</span></div>
    </div>
  </header>
  <main>
    <h2>Comparator Status</h2>
    <div class="note">v4.6 comparator is <code>{html_escape(blocked['status'])}</code>: alias <code>{html_escape(blocked['requested_alias'])}</code> was not in the observed served models. Observed: <code>{html_escape(', '.join(blocked['observed_served_model_ids']))}</code>.</div>

    <h2>Headline Metrics</h2>
    <table>
      <thead><tr><th>Comparator</th><th>Label</th><th>Severity</th><th>Suspicious</th><th>Evidence</th><th>JSON/schema</th><th>Invalid</th><th>Avg latency ms</th></tr></thead>
      <tbody>{''.join(metrics_rows)}</tbody>
    </table>

    <h2>Bucket Summary</h2>
    <table>
      <thead><tr><th>Bucket</th><th>Samples</th><th>v4.7</th><th>Heuristic</th><th>Base</th><th>V4.8 action</th></tr></thead>
      <tbody>{''.join(bucket_rows)}</tbody>
    </table>

    <h2>Case Matrix</h2>
    <table>
      <thead><tr><th>ID</th><th>Bucket</th><th>Expected</th><th>v4.7 predicted</th><th>Heuristic predicted</th></tr></thead>
      <tbody>{''.join(case_rows)}</tbody>
    </table>
  </main>
</body>
</html>
"""
    OUTPUT_HTML_PATH.write_text(html_text, encoding="utf-8")


def main() -> int:
    report = build_report()
    write_json_report(report)
    write_markdown_report(report)
    write_html_report(report)
    print(f"wrote {OUTPUT_JSON_PATH.relative_to(ROOT)}")
    print(f"wrote {OUTPUT_MD_PATH.relative_to(ROOT)}")
    print(f"wrote {OUTPUT_HTML_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
