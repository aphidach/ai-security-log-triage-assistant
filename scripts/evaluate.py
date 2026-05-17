#!/usr/bin/env python3
"""Evaluate triage adapters against a fixed JSONL split."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.baseline_heuristic import analyze_log  # noqa: E402


DEFAULT_SPLIT_PATH = ROOT / "data" / "splits" / "test.jsonl"
DEFAULT_SCHEMA_PATH = ROOT / "data" / "schemas" / "triage-output.schema.json"
DEFAULT_JSON_REPORT_PATH = ROOT / "reports" / "baseline-eval.json"
DEFAULT_MARKDOWN_REPORT_PATH = ROOT / "reports" / "comparison.md"


JsonObject = dict[str, Any]


def load_jsonl(path: Path) -> list[JsonObject]:
    records: list[JsonObject] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSONL record: {exc}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"{path}:{line_number}: JSONL record must be an object")
        records.append(item)
    return records


def load_schema(path: Path) -> JsonObject:
    schema = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(schema, dict):
        raise ValueError(f"{path}: schema must be a JSON object")
    return schema


def run_adapter(adapter: str, log_line: str) -> Any:
    if adapter == "heuristic":
        return analyze_log(log_line)
    raise ValueError(f"Unsupported adapter: {adapter}")


def parse_prediction(raw_prediction: Any) -> tuple[JsonObject | None, bool, str | None]:
    if isinstance(raw_prediction, dict):
        return raw_prediction, True, None

    if isinstance(raw_prediction, str):
        try:
            parsed = json.loads(raw_prediction)
        except json.JSONDecodeError as exc:
            return None, False, str(exc)
        if not isinstance(parsed, dict):
            return None, False, "parsed JSON is not an object"
        return parsed, True, None

    return None, False, f"prediction is {type(raw_prediction).__name__}, not dict or JSON string"


def validate_schema(output: Any, schema: JsonObject) -> list[str]:
    if not isinstance(output, dict):
        return ["output must be an object"]

    errors: list[str] = []
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})

    missing = sorted(required - set(output))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    if schema.get("additionalProperties") is False:
        extra = sorted(set(output) - set(properties))
        if extra:
            errors.append(f"unexpected fields: {', '.join(extra)}")

    label = output.get("label")
    label_enum = properties.get("label", {}).get("enum", [])
    if not isinstance(label, str):
        errors.append("label must be a string")
    elif label not in label_enum:
        errors.append(f"label must be one of: {', '.join(label_enum)}")

    severity = output.get("severity")
    severity_enum = properties.get("severity", {}).get("enum", [])
    if not isinstance(severity, str):
        errors.append("severity must be a string")
    elif severity not in severity_enum:
        errors.append(f"severity must be one of: {', '.join(severity_enum)}")

    if not isinstance(output.get("is_suspicious"), bool):
        errors.append("is_suspicious must be a boolean")

    evidence = output.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be an array")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, str) or not item:
                errors.append(f"evidence[{index}] must be a non-empty string")

    for field in ("reason", "recommended_action"):
        value = output.get(field)
        if not isinstance(value, str) or not value:
            errors.append(f"{field} must be a non-empty string")

    return errors


def evidence_partial_match(predicted: JsonObject, expected: JsonObject) -> bool:
    predicted_evidence = predicted.get("evidence")
    expected_evidence = expected.get("evidence")
    if not isinstance(predicted_evidence, list) or not isinstance(expected_evidence, list):
        return False
    if not expected_evidence:
        return not predicted_evidence

    predicted_items = [str(item).lower() for item in predicted_evidence if isinstance(item, str) and item]
    expected_items = [str(item).lower() for item in expected_evidence if isinstance(item, str) and item]
    for predicted_item in predicted_items:
        for expected_item in expected_items:
            if predicted_item in expected_item or expected_item in predicted_item:
                return True
    return False


def rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def round_latency(value: float) -> float:
    return round(value, 6)


def json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
    except TypeError:
        return repr(value)
    return value


def evaluate_record(item: JsonObject, adapter: str, schema: JsonObject) -> JsonObject:
    record_id = str(item.get("id", "<missing>"))
    expected = item.get("output", {})
    if not isinstance(expected, dict):
        expected = {}

    start = time.perf_counter()
    raw_prediction: Any = None
    adapter_error: str | None = None
    try:
        raw_prediction = run_adapter(adapter, str(item.get("input", "")))
    except Exception as exc:  # pragma: no cover - defensive path for future adapters.
        adapter_error = f"{type(exc).__name__}: {exc}"
    latency_ms = (time.perf_counter() - start) * 1000

    if adapter_error:
        prediction, parse_success, parse_error = None, False, adapter_error
    else:
        prediction, parse_success, parse_error = parse_prediction(raw_prediction)

    schema_errors = validate_schema(prediction, schema) if parse_success else []
    schema_success = parse_success and not schema_errors
    prediction_for_compare = prediction if isinstance(prediction, dict) else {}

    label_correct = schema_success and prediction_for_compare.get("label") == expected.get("label")
    severity_correct = schema_success and prediction_for_compare.get("severity") == expected.get("severity")
    evidence_match = schema_success and evidence_partial_match(prediction_for_compare, expected)

    failure_reasons: list[str] = []
    if not parse_success:
        failure_reasons.append(f"json_parse_failed: {parse_error}")
    if parse_success and schema_errors:
        failure_reasons.extend(f"schema_failed: {error}" for error in schema_errors)
    if not label_correct:
        failure_reasons.append("label_mismatch")
    if not severity_correct:
        failure_reasons.append("severity_mismatch")
    if not evidence_match:
        failure_reasons.append("evidence_partial_mismatch")

    return {
        "id": record_id,
        "input": item.get("input", ""),
        "expected": expected,
        "prediction": prediction,
        "raw_prediction": json_safe(raw_prediction),
        "latency_ms": round_latency(latency_ms),
        "json_parse_success": parse_success,
        "schema_success": schema_success,
        "schema_errors": schema_errors,
        "label_correct": label_correct,
        "severity_correct": severity_correct,
        "evidence_partial_match": evidence_match,
        "failure_reasons": failure_reasons,
    }


def build_report(records: list[JsonObject], adapter: str, split_path: Path, schema_path: Path, schema: JsonObject) -> JsonObject:
    results = [evaluate_record(item, adapter, schema) for item in records]
    sample_count = len(results)

    parse_success_count = sum(bool(item["json_parse_success"]) for item in results)
    schema_success_count = sum(bool(item["schema_success"]) for item in results)
    label_correct_count = sum(bool(item["label_correct"]) for item in results)
    severity_correct_count = sum(bool(item["severity_correct"]) for item in results)
    evidence_match_count = sum(bool(item["evidence_partial_match"]) for item in results)
    invalid_output_count = sample_count - schema_success_count
    average_latency_ms = round_latency(sum(float(item["latency_ms"]) for item in results) / sample_count) if sample_count else 0.0

    expected_labels = Counter(str(item.get("output", {}).get("label", "<missing>")) for item in records)
    predicted_labels = Counter(
        str(item["prediction"].get("label", "<invalid>")) if isinstance(item.get("prediction"), dict) else "<invalid>"
        for item in results
    )

    failures = [
        {
            "id": item["id"],
            "failure_reasons": item["failure_reasons"],
            "input": item["input"],
            "expected": item["expected"],
            "prediction": item["prediction"],
            "schema_errors": item["schema_errors"],
            "latency_ms": item["latency_ms"],
        }
        for item in results
        if item["failure_reasons"]
    ]
    samples = [
        {
            "id": item["id"],
            "expected_label": item["expected"].get("label"),
            "predicted_label": item["prediction"].get("label") if isinstance(item["prediction"], dict) else None,
            "expected_severity": item["expected"].get("severity"),
            "predicted_severity": item["prediction"].get("severity") if isinstance(item["prediction"], dict) else None,
            "json_parse_success": item["json_parse_success"],
            "schema_success": item["schema_success"],
            "label_correct": item["label_correct"],
            "severity_correct": item["severity_correct"],
            "evidence_partial_match": item["evidence_partial_match"],
            "latency_ms": item["latency_ms"],
            "schema_errors": item["schema_errors"],
            "raw_prediction": item["raw_prediction"],
            "prediction": item["prediction"],
        }
        for item in results
    ]

    return {
        "adapter": adapter,
        "split": str(split_path.relative_to(ROOT) if split_path.is_relative_to(ROOT) else split_path),
        "schema": str(schema_path.relative_to(ROOT) if schema_path.is_relative_to(ROOT) else schema_path),
        "sample_count": sample_count,
        "metrics": {
            "label_accuracy": rate(label_correct_count, sample_count),
            "json_parse_success_rate": rate(parse_success_count, sample_count),
            "schema_success_rate": rate(schema_success_count, sample_count),
            "severity_accuracy": rate(severity_correct_count, sample_count),
            "evidence_partial_match": rate(evidence_match_count, sample_count),
            "average_latency_ms": average_latency_ms,
            "invalid_output_count": invalid_output_count,
        },
        "counts": {
            "label_correct": label_correct_count,
            "json_parse_success": parse_success_count,
            "schema_success": schema_success_count,
            "severity_correct": severity_correct_count,
            "evidence_partial_match": evidence_match_count,
            "invalid_output": invalid_output_count,
            "failure": len(failures),
        },
        "expected_label_distribution": dict(sorted(expected_labels.items())),
        "predicted_label_distribution": dict(sorted(predicted_labels.items())),
        "samples": samples,
        "failures": failures,
    }


def write_json_report(report: JsonObject, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown_report(report: JsonObject, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metrics = report["metrics"]
    lines = [
        "# Baseline Evaluation Report",
        "",
        f"- Adapter: `{report['adapter']}`",
        f"- Split: `{report['split']}`",
        f"- Schema: `{report['schema']}`",
        f"- Samples: `{report['sample_count']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key in (
        "label_accuracy",
        "json_parse_success_rate",
        "schema_success_rate",
        "severity_accuracy",
        "evidence_partial_match",
        "average_latency_ms",
        "invalid_output_count",
    ):
        lines.append(f"| `{key}` | `{metrics[key]}` |")

    lines.extend(
        [
            "",
            "## Failure Summary",
            "",
            f"- Failure cases: `{len(report['failures'])}`",
            f"- Invalid outputs: `{metrics['invalid_output_count']}`",
        ]
    )

    if report["failures"]:
        lines.extend(["", "## Failure Cases", ""])
        for failure in report["failures"][:20]:
            expected_label = failure["expected"].get("label", "<missing>")
            predicted = failure["prediction"] or {}
            predicted_label = predicted.get("label", "<invalid>") if isinstance(predicted, dict) else "<invalid>"
            lines.append(f"- `{failure['id']}` expected `{expected_label}`, predicted `{predicted_label}`")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_summary(report: JsonObject, json_report_path: Path | None, markdown_report_path: Path | None) -> None:
    metrics = report["metrics"]
    print(f"adapter: {report['adapter']}")
    print(f"split: {report['split']}")
    print(f"samples: {report['sample_count']}")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    if json_report_path:
        print(f"json_report: {json_report_path}")
    if markdown_report_path:
        print(f"markdown_report: {markdown_report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a security log triage adapter against a JSONL split.")
    parser.add_argument("--adapter", default="heuristic", choices=["heuristic"], help="Adapter to evaluate.")
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT_PATH, help="JSONL split to evaluate.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH, help="Triage output JSON Schema path.")
    parser.add_argument("--out", type=Path, default=DEFAULT_JSON_REPORT_PATH, help="JSON report output path.")
    parser.add_argument(
        "--comparison-out",
        type=Path,
        default=DEFAULT_MARKDOWN_REPORT_PATH,
        help="Markdown comparison report output path.",
    )
    parser.add_argument("--no-write", action="store_true", help="Run evaluation without writing report files.")
    args = parser.parse_args()

    records = load_jsonl(args.split)
    schema = load_schema(args.schema)
    report = build_report(records, args.adapter, args.split, args.schema, schema)

    json_report_path = None if args.no_write else args.out
    markdown_report_path = None if args.no_write else args.comparison_out
    if json_report_path:
        write_json_report(report, json_report_path)
    if markdown_report_path:
        write_markdown_report(report, markdown_report_path)

    print_summary(report, json_report_path, markdown_report_path)


if __name__ == "__main__":
    main()
