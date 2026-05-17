#!/usr/bin/env python3
"""Evaluate triage adapters against a fixed JSONL split."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, TextIO


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.baseline_heuristic import analyze_log  # noqa: E402
from scripts.model_adapters import (  # noqa: E402
    AdapterResult,
    FineTuneAdapter,
    OpenAICompatibleAdapter,
    TriageModelAdapter,
)


DEFAULT_SPLIT_PATH = ROOT / "data" / "splits" / "test.jsonl"
DEFAULT_SCHEMA_PATH = ROOT / "data" / "schemas" / "triage-output.schema.json"
DEFAULT_JSON_REPORT_PATH = ROOT / "reports" / "baseline-eval.json"
DEFAULT_MARKDOWN_REPORT_PATH = ROOT / "reports" / "comparison.md"
ADAPTER_CHOICES = ("heuristic", "openai-compatible", "openai-finetune")


JsonObject = dict[str, Any]
MappingStringAny = dict[str, Any]


class ProgressReporter:
    def __init__(self, *, total: int, adapter_name: str, enabled: bool, stream: TextIO = sys.stderr) -> None:
        self.total = total
        self.adapter_name = adapter_name
        self.enabled = enabled
        self.stream = stream
        self.started_at = time.perf_counter()
        self.one_line = stream.isatty()

    def start(self) -> None:
        self.update(0)

    def update(self, completed: int, current_id: str | None = None) -> None:
        if not self.enabled:
            return

        percent = 100 if self.total == 0 else int((completed / self.total) * 100)
        elapsed_seconds = time.perf_counter() - self.started_at
        line = (
            f"progress: {progress_bar(percent)} {percent:3d}% "
            f"({completed}/{self.total}) adapter={self.adapter_name} "
            f"elapsed={elapsed_seconds:.1f}s"
        )
        if current_id:
            line = f"{line} current={current_id}"

        prefix = "\r" if self.one_line else ""
        end = "" if self.one_line else "\n"
        padding = " " * 8 if self.one_line else ""
        print(f"{prefix}{line}{padding}", end=end, file=self.stream, flush=True)

    def finish(self) -> None:
        if self.enabled and self.one_line:
            print(file=self.stream, flush=True)


class HeuristicAdapter:
    name = "heuristic"

    def analyze(self, log_line: str) -> AdapterResult:
        start = time.perf_counter()
        try:
            raw_output = analyze_log(log_line)
        except Exception as exc:  # pragma: no cover - defensive path for future rule changes.
            return AdapterResult(
                raw_output=None,
                latency_ms=round_latency((time.perf_counter() - start) * 1000),
                error=f"{type(exc).__name__}: {exc}",
                metadata={"adapter": self.name},
            )
        return AdapterResult(
            raw_output=raw_output,
            latency_ms=round_latency((time.perf_counter() - start) * 1000),
            error=None,
            metadata={"adapter": self.name},
        )


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


def create_adapter(name: str) -> TriageModelAdapter:
    if name == "heuristic":
        return HeuristicAdapter()
    if name == "openai-compatible":
        return OpenAICompatibleAdapter()
    if name == "openai-finetune":
        return FineTuneAdapter()
    raise ValueError(f"Unsupported adapter: {name}")


def default_json_report_path(adapter_name: str) -> Path:
    if adapter_name == "heuristic":
        return DEFAULT_JSON_REPORT_PATH
    return ROOT / "reports" / f"{adapter_name}-eval.json"


def default_markdown_report_path(adapter_name: str) -> Path:
    if adapter_name == "heuristic":
        return DEFAULT_MARKDOWN_REPORT_PATH
    return ROOT / "reports" / f"{adapter_name}-eval.md"


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


def progress_bar(percent: int, width: int = 24) -> str:
    bounded_percent = max(0, min(100, percent))
    filled = round(width * bounded_percent / 100)
    return f"[{'#' * filled}{'-' * (width - filled)}]"


def json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
    except TypeError:
        return repr(value)
    return value


def stable_adapter_metadata(metadata: MappingStringAny) -> JsonObject:
    return {
        key: value
        for key, value in metadata.items()
        if key not in {"response_metadata", "usage_metadata"}
    }


def evaluate_record(item: JsonObject, adapter: TriageModelAdapter, schema: JsonObject) -> JsonObject:
    record_id = str(item.get("id", "<missing>"))
    expected = item.get("output", {})
    if not isinstance(expected, dict):
        expected = {}

    adapter_result: AdapterResult | None = None
    adapter_error: str | None = None
    try:
        adapter_result = adapter.analyze(str(item.get("input", "")))
    except Exception as exc:  # pragma: no cover - defensive path for future adapters.
        adapter_error = f"{type(exc).__name__}: {exc}"

    if adapter_result is None:
        raw_prediction: Any = None
        latency_ms = 0.0
        adapter_metadata: MappingStringAny = {"adapter": adapter.name}
    else:
        raw_prediction = adapter_result.raw_output
        latency_ms = adapter_result.latency_ms
        adapter_error = adapter_result.error
        adapter_metadata = dict(adapter_result.metadata)

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
    if adapter_error:
        failure_reasons.append(f"adapter_error: {adapter_error}")
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
        "adapter_error": adapter_error,
        "adapter_metadata": json_safe(adapter_metadata),
        "json_parse_success": parse_success,
        "schema_success": schema_success,
        "schema_errors": schema_errors,
        "label_correct": label_correct,
        "severity_correct": severity_correct,
        "evidence_partial_match": evidence_match,
        "failure_reasons": failure_reasons,
    }


def build_report(
    records: list[JsonObject],
    adapter: TriageModelAdapter,
    split_path: Path,
    schema_path: Path,
    schema: JsonObject,
    *,
    show_progress: bool = True,
) -> JsonObject:
    progress = ProgressReporter(total=len(records), adapter_name=adapter.name, enabled=show_progress)
    progress.start()
    results: list[JsonObject] = []
    for index, item in enumerate(records, start=1):
        record_id = str(item.get("id", f"record-{index}"))
        if progress.one_line:
            progress.update(index - 1, current_id=record_id)
        results.append(evaluate_record(item, adapter, schema))
        progress.update(index, current_id=record_id)
    progress.finish()

    sample_count = len(results)
    adapter_name = adapter.name
    adapter_metadata = {"adapter": adapter_name}
    if results:
        first_metadata = results[0].get("adapter_metadata", {})
        if isinstance(first_metadata, dict):
            adapter_metadata = stable_adapter_metadata(first_metadata)

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
            "adapter_error": item["adapter_error"],
            "adapter_metadata": item["adapter_metadata"],
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
            "adapter_error": item["adapter_error"],
            "adapter_metadata": item["adapter_metadata"],
            "schema_errors": item["schema_errors"],
            "raw_prediction": item["raw_prediction"],
            "prediction": item["prediction"],
        }
        for item in results
    ]

    return {
        "adapter": adapter_name,
        "adapter_metadata": adapter_metadata,
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
        "# Triage Adapter Evaluation Report",
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
    parser.add_argument("--adapter", default="heuristic", choices=ADAPTER_CHOICES, help="Adapter to evaluate.")
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT_PATH, help="JSONL split to evaluate.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH, help="Triage output JSON Schema path.")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="JSON report output path. Defaults to reports/<adapter>-eval.json.",
    )
    parser.add_argument(
        "--comparison-out",
        type=Path,
        default=None,
        help="Markdown report output path. Defaults to reports/<adapter>-eval.md.",
    )
    parser.add_argument("--no-write", action="store_true", help="Run evaluation without writing report files.")
    parser.add_argument("--no-progress", action="store_true", help="Hide per-record progress output.")
    args = parser.parse_args()

    records = load_jsonl(args.split)
    schema = load_schema(args.schema)
    adapter = create_adapter(args.adapter)
    report = build_report(records, adapter, args.split, args.schema, schema, show_progress=not args.no_progress)

    json_report_path = None if args.no_write else args.out or default_json_report_path(args.adapter)
    markdown_report_path = None if args.no_write else args.comparison_out or default_markdown_report_path(args.adapter)
    if json_report_path:
        write_json_report(report, json_report_path)
    if markdown_report_path:
        write_markdown_report(report, markdown_report_path)

    print_summary(report, json_report_path, markdown_report_path)


if __name__ == "__main__":
    main()
