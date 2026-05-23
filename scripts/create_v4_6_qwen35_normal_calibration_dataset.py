#!/usr/bin/env python3
"""Create Phase 8 v4.6 Qwen3.5 normal/severity calibration data.

The v4.6 supplement starts from the v4.1 Qwen pilot train/validation sources,
adds a normal-heavy calibration train supplement, and creates a separate
non-fixed calibration probe split. It intentionally does not read or modify the
fixed test split.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.unsloth.training_format import format_split  # noqa: E402
from scripts.create_v4_1_sqli_boundary_repair_dataset import (  # noqa: E402
    V4_1_TRAIN_PATH,
    V4_1_VALIDATION_PATH,
)
from scripts.generate_dataset import INSTRUCTION, LABELS, validate_record, write_jsonl  # noqa: E402


SUPPLEMENT_PATH = ROOT / "data" / "generated" / "v4-6-qwen35-normal-severity-calibration-security-triage.jsonl"
TRAIN_PLUS_PATH = ROOT / "data" / "generated" / "train-plus-v4-6-qwen35-normal-severity-calibration.jsonl"
V4_6_TRAIN_PATH = ROOT / "data" / "splits" / "train-v4-6-qwen35-normal-severity-calibration.jsonl"
V4_6_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v4-6-qwen35-normal-severity-calibration.jsonl"
V4_6_PROBE_PATH = ROOT / "data" / "splits" / "v4-6-normal-severity-calibration-probe.jsonl"
HARD_CONTRAST_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"

EXPECTED_TRAIN_SUPPLEMENT_COUNTS = {
    "normal": 72,
    "failed_login_bruteforce": 18,
    "sql_injection_attempt": 6,
    "directory_traversal_attempt": 6,
    "port_scan_or_recon": 18,
}
EXPECTED_PROBE_COUNTS = {
    "normal": 15,
    "failed_login_bruteforce": 4,
    "sql_injection_attempt": 1,
    "directory_traversal_attempt": 1,
    "port_scan_or_recon": 4,
}
EXPECTED_SUPPLEMENT_COUNTS = {
    label: EXPECTED_TRAIN_SUPPLEMENT_COUNTS[label] + EXPECTED_PROBE_COUNTS[label]
    for label in LABELS
}
EXPECTED_V4_6_TRAIN_COUNTS = {
    "normal": 351,
    "failed_login_bruteforce": 154,
    "sql_injection_attempt": 421,
    "directory_traversal_attempt": 197,
    "port_scan_or_recon": 217,
}
EXPECTED_V4_6_VALIDATION_COUNTS = {
    "normal": 30,
    "failed_login_bruteforce": 19,
    "sql_injection_attempt": 16,
    "directory_traversal_attempt": 16,
    "port_scan_or_recon": 19,
}

JsonObject = dict[str, Any]


def load_jsonl(path: Path) -> list[JsonObject]:
    records: list[JsonObject] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_no}: expected JSON object")
        records.append(record)
    return records


def triage_output(
    *,
    label: str,
    severity: str,
    is_suspicious: bool,
    evidence: list[str],
    reason: str,
    recommended_action: str,
) -> JsonObject:
    return {
        "label": label,
        "severity": severity,
        "is_suspicious": is_suspicious,
        "evidence": evidence,
        "reason": reason,
        "recommended_action": recommended_action,
    }


def record(record_id: str, log_line: str, output: JsonObject, *, repair_bucket: str) -> JsonObject:
    return {
        "id": record_id,
        "instruction": INSTRUCTION,
        "input": log_line,
        "output": output,
        "metadata": {
            "phase": "phase-8-v4-6-qwen35-normal-severity-calibration",
            "repair_bucket": repair_bucket,
        },
    }


def make_id(index: int) -> str:
    return f"v4-6-qwen35-cal-{index:06d}"


def _normal_auth_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    templates = [
        ("Failed password for webapp", "failed_attempts=1", "window=none"),
        ("event=login_failed", "failures=1", "window=10m"),
        ("event_id=4625", "status=failed_logon", "repeat_count=1"),
        ("auth failed for user deploy", "repeated=1", "window=none"),
        ("status=401", "request_count=1", "burst=false"),
        ("vpn auth failed", "unique_sources=1", "lockout=false"),
        ("bad password", "attempts=2", "window=24h"),
        ("password_reset_failed", "attempts=1", "user_verified=false"),
        ("login_denied", "failure_count=1", "mfa_challenge=passed_after_retry"),
        ("ssh auth failure", "same_src_repeat=1", "next_login=success"),
        ("service account login failed", "failures=1", "maintenance_window=true"),
        ("expired_password", "retry_count=1", "reset_completed=true"),
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        event, detail, guard = templates[i % len(templates)]
        bucket = "normal_auth_low_volume_probe" if probe else "normal_auth_low_volume_train"
        log_line = (
            f"2026-05-24T00:{i % 60:02d}:01+07:00 auth: user=employee{i % 9} "
            f"src_ip=198.51.110.{20 + i} {event} {detail} {guard} correlation=none"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="normal",
                    severity="low",
                    is_suspicious=False,
                    evidence=[event, detail, guard],
                    reason="The authentication failure is isolated and lacks burst, spray, or lockout evidence.",
                    recommended_action="No immediate action required. Monitor for repeated failures from the same source or account.",
                ),
                repair_bucket=bucket,
            )
        )
        index += 1
    return rows


def _normal_sqli_text_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    queries = [
        "query=union+station+map",
        "query=category=unionized-tools",
        "query=sql-injection-training-notes",
        "query=or-1-equals-1-awareness",
        "query=single-quote escaping guide",
        "query=information-schema lesson",
        "query=drop-table tabletop exercise",
        "query=union-select syntax reference",
        "query=sleep function documentation",
        "query=waitfor delay lab note",
        "query=database error runbook",
        "query=parameterized query tutorial",
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        query = queries[i % len(queries)]
        bucket = "normal_sqli_text_probe" if probe else "normal_sqli_text_train"
        log_line = (
            f"2026-05-24T01:{i % 60:02d}:01+07:00 app=knowledge-base route=/search "
            f"method=GET src_ip=203.0.115.{30 + i} {query} status=200 user_role=analyst "
            f"waf_action=allow"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="normal",
                    severity="low",
                    is_suspicious=False,
                    evidence=[query, "status=200", "waf_action=allow"],
                    reason="The log is a benign knowledge-base search and does not contain an executable SQL injection boundary.",
                    recommended_action="No immediate action required. Continue normal monitoring.",
                ),
                repair_bucket=bucket,
            )
        )
        index += 1
    return rows


def _normal_traversal_text_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    paths = [
        "path=/docs/../guide",
        "path=/static/../static/help.css",
        "path=/training/../training/sql-lab.html",
        "path=/reports/../reports/query-review.pdf",
        "path=/assets/../assets/icon.svg",
        "path=/kb/../kb/password-reset.md",
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        path = paths[i % len(paths)]
        bucket = "normal_traversal_text_probe" if probe else "normal_traversal_text_train"
        log_line = (
            f"2026-05-24T02:{i % 60:02d}:01+07:00 app=docs route=/static method=GET "
            f"src_ip=192.0.4.{40 + i} {path} normalized=true status=200 sensitive_target=false"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="normal",
                    severity="low",
                    is_suspicious=False,
                    evidence=[path, "normalized=true", "sensitive_target=false"],
                    reason="The relative path is normalized within an allowed documentation/static route.",
                    recommended_action="No immediate action required. Continue normal monitoring.",
                ),
                repair_bucket=bucket,
            )
        )
        index += 1
    return rows


def normal_records(start_index: int, *, count: int, probe: bool = False) -> list[JsonObject]:
    auth_count = count // 3 + (1 if count % 3 > 0 else 0)
    sqli_text_count = count // 3 + (1 if count % 3 > 1 else 0)
    traversal_count = count - auth_count - sqli_text_count

    rows: list[JsonObject] = []
    rows.extend(_normal_auth_records(start_index + len(rows), auth_count, probe=probe))
    rows.extend(_normal_sqli_text_records(start_index + len(rows), sqli_text_count, probe=probe))
    rows.extend(_normal_traversal_text_records(start_index + len(rows), traversal_count, probe=probe))
    return rows


def brute_force_medium_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    events = [
        ("Failed password for root", "repeated 9 times in 2 minutes", "single_source=true"),
        ("event=password_guessing", "failures=11", "lockout=true"),
        ("auth failed for user deploy", "repeated=13 window=6m", "same_user=true"),
        ("login_failed", "failures=10", "window=5m"),
        ("vpn auth failed", "failures=8", "window=3m"),
        ("bad password", "failures=12", "window=4m"),
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        event, detail, guard = events[i % len(events)]
        bucket = "bruteforce_medium_probe" if probe else "bruteforce_medium_train"
        log_line = (
            f"2026-05-24T03:{i % 60:02d}:01+07:00 auth: user=target{i % 5} "
            f"src_ip=198.51.111.{50 + i} {event} {detail} {guard}"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="failed_login_bruteforce",
                    severity="medium",
                    is_suspicious=True,
                    evidence=[event, detail],
                    reason="The event shows repeated failed authentication attempts, but the scope is limited.",
                    recommended_action="Review authentication history for the account and source IP before escalating.",
                ),
                repair_bucket=bucket,
            )
        )
        index += 1
    return rows


def port_recon_high_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    signals = [
        ("nmap fingerprint", "probed_ports=80,443,8080,8443"),
        ("SYN scan detected", "ports=80,443,8080"),
        ("horizontal scan", "dst_subnet=192.0.2.0/24", "unique_hosts=18"),
        ("nmap fingerprint", "probed_ports=135,139,445,3389"),
        ("SYN scan detected", "ports=25,110,143,587,993"),
        ("service enumeration", "unique_ports=22", "window=30s"),
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        parts = signals[i % len(signals)]
        signal = parts[0]
        detail = " ".join(parts[1:])
        bucket = "port_recon_high_probe" if probe else "port_recon_high_train"
        log_line = (
            f"2026-05-24T04:{i % 60:02d}:01+07:00 ids: src=203.0.115.{60 + i} "
            f"dst=198.51.112.{80 + i} {signal} {detail} action=blocked"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="port_scan_or_recon",
                    severity="high",
                    is_suspicious=True,
                    evidence=[signal, detail],
                    reason="The event shows broad service or host enumeration consistent with reconnaissance.",
                    recommended_action="Review network telemetry for related scans from the same source.",
                ),
                repair_bucket=bucket,
            )
        )
        index += 1
    return rows


def sqli_guard_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    payloads = [
        "username=admin' OR '1'='1",
        "q=abc'/**/OR/**/'1'='1",
        "id=8 AND SLEEP(5)",
        "q=information_schema.columns",
        "item=5 UNION ALL SELECT null,version()--",
        "filter=1;DROP TABLE sessions--",
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        payload = payloads[i % len(payloads)]
        bucket = "sqli_guard_probe" if probe else "sqli_guard_train"
        log_line = (
            f"2026-05-24T05:{i % 60:02d}:01+07:00 waf: category=sqli "
            f"src=192.0.4.{70 + i} request_payload=\"{payload}\" action=blocked status=403"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="sql_injection_attempt",
                    severity="high",
                    is_suspicious=True,
                    evidence=[payload, "action=blocked"],
                    reason="The request contains a SQL injection boundary and was blocked by the WAF.",
                    recommended_action="Review WAF and application logs for related SQL injection attempts.",
                ),
                repair_bucket=bucket,
            )
        )
        index += 1
    return rows


def traversal_guard_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    payloads = [
        "file=../../../../etc/passwd",
        "download=../../../etc/shadow",
        "file=%2e%2e%2f%2e%2e%2fwindows%2fwin.ini",
        "path=..%2f..%2fvar%2flog%2fauth.log",
        "page=php://filter/convert.base64-encode/resource=index.php",
        "file=../../.env",
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        payload = payloads[i % len(payloads)]
        bucket = "traversal_guard_probe" if probe else "traversal_guard_train"
        log_line = (
            f"2026-05-24T06:{i % 60:02d}:01+07:00 app=files method=GET "
            f"src_ip=203.0.115.{80 + i} {payload} status=403 action=blocked"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="directory_traversal_attempt",
                    severity="high",
                    is_suspicious=True,
                    evidence=[payload, "status=403"],
                    reason="The request contains a traversal sequence targeting a sensitive file path.",
                    recommended_action="Review file-access logs and confirm whether sensitive files were exposed.",
                ),
                repair_bucket=bucket,
            )
        )
        index += 1
    return rows


def build_calibration_records() -> tuple[list[JsonObject], list[JsonObject]]:
    train_records: list[JsonObject] = []
    train_records.extend(normal_records(len(train_records) + 1, count=72))
    train_records.extend(brute_force_medium_records(len(train_records) + 1, count=18))
    train_records.extend(port_recon_high_records(len(train_records) + 1, count=18))
    train_records.extend(sqli_guard_records(len(train_records) + 1, count=6))
    train_records.extend(traversal_guard_records(len(train_records) + 1, count=6))

    probe_records: list[JsonObject] = []
    start = len(train_records) + 1
    probe_records.extend(normal_records(start + len(probe_records), count=15, probe=True))
    probe_records.extend(brute_force_medium_records(start + len(probe_records), count=4, probe=True))
    probe_records.extend(port_recon_high_records(start + len(probe_records), count=4, probe=True))
    probe_records.extend(sqli_guard_records(start + len(probe_records), count=1, probe=True))
    probe_records.extend(traversal_guard_records(start + len(probe_records), count=1, probe=True))
    return train_records, probe_records


def label_counts(records: list[JsonObject]) -> dict[str, int]:
    counts = Counter(str(item["output"]["label"]) for item in records)
    return {label: counts[label] for label in LABELS}


def metadata_counts(records: list[JsonObject]) -> dict[str, int]:
    counts = Counter(str(item.get("metadata", {}).get("repair_bucket", "<missing>")) for item in records)
    return dict(sorted(counts.items()))


def strip_metadata(records: list[JsonObject]) -> list[JsonObject]:
    stripped: list[JsonObject] = []
    for item in records:
        clean = dict(item)
        clean.pop("metadata", None)
        stripped.append(clean)
    return stripped


def validate_records(
    records: list[JsonObject],
    *,
    expected_count: int,
    expected_counts: dict[str, int],
    name: str,
) -> None:
    if len(records) != expected_count:
        raise ValueError(f"{name}: expected {expected_count} records, got {len(records)}")

    ids = [str(item["id"]) for item in records]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{name}: record ids must be unique")

    for item in strip_metadata(records):
        validate_record(item)

    counts = label_counts(records)
    if counts != expected_counts:
        raise ValueError(f"{name}: expected labels {expected_counts}, got {counts}")

    format_split(strip_metadata(records))


def validate_no_hard_contrast_duplicates(records: list[JsonObject]) -> None:
    hard_inputs = {str(item["input"]) for item in load_jsonl(HARD_CONTRAST_PATH)}
    inputs = {str(item["input"]) for item in records}
    duplicates = sorted(inputs & hard_inputs)
    if duplicates:
        raise ValueError(f"v4.6 calibration data duplicates hard-contrast inputs: {duplicates[:3]}")


def validate_no_overlap(*record_groups: list[JsonObject]) -> None:
    seen: set[str] = set()
    for group in record_groups:
        ids = {str(item["id"]) for item in group}
        overlap = seen & ids
        if overlap:
            raise ValueError(f"record id overlap: {sorted(overlap)[:3]}")
        seen |= ids


def build_v4_6_split_records() -> tuple[list[JsonObject], list[JsonObject], list[JsonObject], list[JsonObject]]:
    base_train_records = load_jsonl(V4_1_TRAIN_PATH)
    base_validation_records = load_jsonl(V4_1_VALIDATION_PATH)
    train_supplement_records, probe_records = build_calibration_records()
    supplement_records = [*train_supplement_records, *probe_records]

    train_plus_records = [*base_train_records, *strip_metadata(train_supplement_records)]
    validation_plus_records = [*base_validation_records, *strip_metadata(probe_records)]

    validate_no_hard_contrast_duplicates(supplement_records)
    validate_no_overlap(base_train_records, base_validation_records, train_supplement_records, probe_records)
    validate_records(
        train_supplement_records,
        expected_count=120,
        expected_counts=EXPECTED_TRAIN_SUPPLEMENT_COUNTS,
        name="v4.6 train supplement",
    )
    validate_records(
        probe_records,
        expected_count=25,
        expected_counts=EXPECTED_PROBE_COUNTS,
        name="v4.6 calibration probe",
    )
    validate_records(
        supplement_records,
        expected_count=145,
        expected_counts=EXPECTED_SUPPLEMENT_COUNTS,
        name="v4.6 total supplement",
    )
    validate_records(
        train_plus_records,
        expected_count=1340,
        expected_counts=EXPECTED_V4_6_TRAIN_COUNTS,
        name="v4.6 train",
    )
    validate_records(
        validation_plus_records,
        expected_count=100,
        expected_counts=EXPECTED_V4_6_VALIDATION_COUNTS,
        name="v4.6 validation",
    )

    train_ids = {str(item["id"]) for item in train_plus_records}
    validation_ids = {str(item["id"]) for item in validation_plus_records}
    if train_ids & validation_ids:
        raise ValueError("v4.6 train and validation records overlap")

    return train_plus_records, validation_plus_records, supplement_records, strip_metadata(probe_records)


def main() -> int:
    train_records, validation_records, supplement_records, probe_records = build_v4_6_split_records()
    clean_supplement_records = strip_metadata(supplement_records)

    write_jsonl(SUPPLEMENT_PATH, clean_supplement_records)
    write_jsonl(TRAIN_PLUS_PATH, train_records)
    write_jsonl(V4_6_TRAIN_PATH, train_records)
    write_jsonl(V4_6_VALIDATION_PATH, validation_records)
    write_jsonl(V4_6_PROBE_PATH, probe_records)

    print(f"Wrote {len(clean_supplement_records)} records to {SUPPLEMENT_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_records)} records to {TRAIN_PLUS_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_records)} records to {V4_6_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(validation_records)} records to {V4_6_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(probe_records)} records to {V4_6_PROBE_PATH.relative_to(ROOT)}")
    print(f"Base train source: {V4_1_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Base validation source: {V4_1_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Supplement labels: {dict(sorted(label_counts(clean_supplement_records).items()))}")
    print(f"Supplement buckets: {metadata_counts(supplement_records)}")
    print(f"Train labels: {dict(sorted(label_counts(train_records).items()))}")
    print(f"Validation labels: {dict(sorted(label_counts(validation_records).items()))}")
    print("Fixed test split was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
