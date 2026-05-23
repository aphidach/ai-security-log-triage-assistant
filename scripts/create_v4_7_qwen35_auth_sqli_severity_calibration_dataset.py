#!/usr/bin/env python3
"""Create Phase 8 v4.7 Qwen3.5 auth/SQLi/severity calibration data.

The v4.7 supplement starts from the v4.6 Qwen train/validation splits, adds a
narrow train-only calibration supplement, and creates a separate non-fixed
calibration probe split. It intentionally does not read or modify the fixed test
split.
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
from scripts.create_v4_6_qwen35_normal_calibration_dataset import (  # noqa: E402
    V4_6_TRAIN_PATH,
    V4_6_VALIDATION_PATH,
)
from scripts.generate_dataset import INSTRUCTION, LABELS, validate_record, write_jsonl  # noqa: E402


SUPPLEMENT_PATH = ROOT / "data" / "generated" / "v4-7-qwen35-auth-sqli-severity-calibration-security-triage.jsonl"
TRAIN_PLUS_PATH = ROOT / "data" / "generated" / "train-plus-v4-7-qwen35-auth-sqli-severity-calibration.jsonl"
V4_7_TRAIN_PATH = ROOT / "data" / "splits" / "train-v4-7-qwen35-auth-sqli-severity-calibration.jsonl"
V4_7_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v4-7-qwen35-auth-sqli-severity-calibration.jsonl"
V4_7_PROBE_PATH = ROOT / "data" / "splits" / "v4-7-auth-sqli-severity-calibration-probe.jsonl"
HARD_CONTRAST_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"

EXPECTED_TRAIN_SUPPLEMENT_COUNTS = {
    "normal": 54,
    "failed_login_bruteforce": 32,
    "sql_injection_attempt": 18,
    "directory_traversal_attempt": 8,
    "port_scan_or_recon": 8,
}
EXPECTED_PROBE_COUNTS = {
    "normal": 15,
    "failed_login_bruteforce": 7,
    "sql_injection_attempt": 5,
    "directory_traversal_attempt": 1,
    "port_scan_or_recon": 2,
}
EXPECTED_SUPPLEMENT_COUNTS = {
    label: EXPECTED_TRAIN_SUPPLEMENT_COUNTS[label] + EXPECTED_PROBE_COUNTS[label]
    for label in LABELS
}
EXPECTED_V4_7_TRAIN_COUNTS = {
    "normal": 405,
    "failed_login_bruteforce": 186,
    "sql_injection_attempt": 439,
    "directory_traversal_attempt": 205,
    "port_scan_or_recon": 225,
}
EXPECTED_V4_7_VALIDATION_COUNTS = {
    "normal": 45,
    "failed_login_bruteforce": 26,
    "sql_injection_attempt": 21,
    "directory_traversal_attempt": 17,
    "port_scan_or_recon": 21,
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
            "phase": "phase-8-v4-7-qwen35-auth-sqli-severity-calibration",
            "repair_bucket": repair_bucket,
        },
    }


def make_id(index: int) -> str:
    return f"v4-7-qwen35-cal-{index:06d}"


def normal_auth_boundary_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    templates = [
        ("Failed password for webapp", "failed_attempts=1", "window=none outcome=success_on_next_try"),
        ("event=login_failed", "failures=1", "window=10m outcome=allowed_retry"),
        ("event_id=4625", "count=1 status=failed_logon", "repeat_count=1 lockout=false"),
        ("ssh auth failure", "same_src_repeat=1", "next_login=success"),
        ("vpn auth failed", "failures=1", "mfa_challenge=passed_after_retry"),
        ("login_denied", "failure_count=1", "risk_score=low"),
        ("bad password", "attempts=2", "window=24h lockout=false"),
        ("service account login failed", "failures=1", "maintenance_window=true"),
        ("expired_password", "retry_count=1", "reset_completed=true"),
        ("password_reset_failed", "attempts=1", "user_verified=false"),
        ("status=401", "request_count=1", "burst=false"),
        ("sso login_failed", "failures=1", "device_trust=known"),
        ("kerberos preauth failed", "count=1", "followup_success=true"),
        ("pam_unix authentication failure", "attempts=1", "interactive_user=true"),
        ("radius auth reject", "reject_count=1", "next_attempt=success"),
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        event, volume, guard = templates[i % len(templates)]
        bucket = "normal_auth_boundary_probe" if probe else "normal_auth_boundary_train"
        log_line = (
            f"2026-05-25T00:{i % 60:02d}:01+07:00 auth: user=employee{i % 11} "
            f"src_ip=198.51.130.{20 + i} {event} {volume} {guard} "
            f"correlation=none distributed=false"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="normal",
                    severity="low",
                    is_suspicious=False,
                    evidence=[event, volume, guard],
                    reason="The authentication signal is isolated or resolved and lacks brute-force volume or scope.",
                    recommended_action="No immediate action required. Monitor for repeated failures from the same source or account.",
                ),
                repair_bucket=bucket,
            )
        )
        index += 1
    return rows


def brute_force_medium_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    templates = [
        ("Failed password for root", "repeated 9 times in 2 minutes", "single_source=true unique_accounts=1"),
        ("event=password_guessing", "failures=11 window=5m", "lockout=true distributed=false"),
        ("auth failed for user deploy", "repeated=13 window=6m", "same_user=true no_successful_login=true"),
        ("login_failed", "failures=10 window=5m", "unique_accounts=1 source_count=1"),
        ("vpn auth failed", "failures=8 window=3m", "same_user=true mfa_bypass=false"),
        ("bad password", "failures=12 window=4m", "single_source=true no_admin_user=true"),
        ("event=login_failed", "failures=14 window=8m", "target_scope=one_account distributed=false"),
        ("ssh password failure", "repeated=7 window=90s", "source_count=1 unique_users=1"),
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        event, volume, scope = templates[i % len(templates)]
        bucket = "bruteforce_medium_probe" if probe else "bruteforce_medium_train"
        log_line = (
            f"2026-05-25T01:{i % 60:02d}:01+07:00 auth: user=target{i % 7} "
            f"src_ip=198.51.131.{40 + i} {event} {volume} {scope}"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="failed_login_bruteforce",
                    severity="medium",
                    is_suspicious=True,
                    evidence=[event, volume, scope],
                    reason="The event shows repeated failed authentication attempts, but the scope is limited.",
                    recommended_action="Review authentication history for the account and source IP before escalating.",
                ),
                repair_bucket=bucket,
            )
        )
        index += 1
    return rows


def sqli_auth_context_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    payloads = [
        "username=' OR '1'='1",
        "login=admin'/**/OR/**/'1'='1",
        "user=admin') OR ('1'='1",
        "account=admin%27%20OR%201%3D1--",
        "username=admin' UNION SELECT password FROM users--",
        "session_lookup=1 AND SLEEP(5)",
        "email=test@example.com' OR 1=1--",
        "auth_param=1;DROP TABLE sessions--",
        "login_id=5 UNION ALL SELECT null,version()--",
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        payload = payloads[i % len(payloads)]
        bucket = "sqli_auth_context_probe" if probe else "sqli_auth_context_train"
        log_line = (
            f"2026-05-25T02:{i % 60:02d}:01+07:00 app=web route=/login method=POST "
            f"src_ip=192.0.6.{60 + i} request_payload=\"{payload}\" "
            f"auth_result=blocked status=403 failure_count=0"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="sql_injection_attempt",
                    severity="high",
                    is_suspicious=True,
                    evidence=[payload, "status=403"],
                    reason="The login request contains a SQL injection payload rather than repeated authentication failures.",
                    recommended_action="Review WAF and application logs for related SQL injection attempts from the source.",
                ),
                repair_bucket=bucket,
            )
        )
        index += 1
    return rows


def port_recon_medium_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    templates = [
        ("blocked recon", "tcp_flags=SYN unique_ports=5", "dst_hosts=1 action=blocked"),
        ("sequential connection attempts", "unique_ports=4", "window=20s action=blocked"),
        ("service enumeration", "banners_requested=true unique_ports=5", "dst_hosts=1"),
        ("netflow probe burst", "unique_ports=6", "bytes_out=small duration=15s"),
        ("firewall denied probe", "ports=22,80,443,8080", "src_role=internal_workstation"),
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        signal, detail, scope = templates[i % len(templates)]
        bucket = "port_recon_medium_probe" if probe else "port_recon_medium_train"
        log_line = (
            f"2026-05-25T03:{i % 60:02d}:01+07:00 firewall: src=10.0.4.{70 + i} "
            f"dst=198.51.132.{80 + i} {signal} {detail} {scope}"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="port_scan_or_recon",
                    severity="medium",
                    is_suspicious=True,
                    evidence=[signal, detail],
                    reason="The event shows limited reconnaissance that was blocked or narrow in scope.",
                    recommended_action="Review network telemetry for repeated reconnaissance from the same source.",
                ),
                repair_bucket=bucket,
            )
        )
        index += 1
    return rows


def traversal_exact_evidence_records(start_index: int, count: int, *, probe: bool = False) -> list[JsonObject]:
    payloads = [
        "file=../../../../etc/passwd",
        "download=../../../etc/shadow",
        "path=..%2f..%2fvar%2flog%2fauth.log",
        "file=%2e%2e%2f%2e%2e%2fwindows%2fwin.ini",
        "page=php://filter/convert.base64-encode/resource=index.php",
        "file=../../.env",
        "template=../../../../proc/self/environ",
        "include=..%2f..%2f..%2fetc%2fhosts",
    ]
    rows: list[JsonObject] = []
    index = start_index
    for i in range(count):
        payload = payloads[i % len(payloads)]
        bucket = "traversal_exact_evidence_probe" if probe else "traversal_exact_evidence_train"
        log_line = (
            f"2026-05-25T04:{i % 60:02d}:01+07:00 app=files method=GET "
            f"src_ip=203.0.116.{80 + i} {payload} status=403 action=blocked"
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
    train_records.extend(normal_auth_boundary_records(len(train_records) + 1, count=54))
    train_records.extend(brute_force_medium_records(len(train_records) + 1, count=32))
    train_records.extend(sqli_auth_context_records(len(train_records) + 1, count=18))
    train_records.extend(port_recon_medium_records(len(train_records) + 1, count=8))
    train_records.extend(traversal_exact_evidence_records(len(train_records) + 1, count=8))

    probe_records: list[JsonObject] = []
    start = len(train_records) + 1
    probe_records.extend(normal_auth_boundary_records(start + len(probe_records), count=15, probe=True))
    probe_records.extend(brute_force_medium_records(start + len(probe_records), count=7, probe=True))
    probe_records.extend(sqli_auth_context_records(start + len(probe_records), count=5, probe=True))
    probe_records.extend(port_recon_medium_records(start + len(probe_records), count=2, probe=True))
    probe_records.extend(traversal_exact_evidence_records(start + len(probe_records), count=1, probe=True))
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
        raise ValueError(f"v4.7 calibration data duplicates hard-contrast inputs: {duplicates[:3]}")


def validate_no_overlap(*record_groups: list[JsonObject]) -> None:
    seen: set[str] = set()
    for group in record_groups:
        ids = {str(item["id"]) for item in group}
        overlap = seen & ids
        if overlap:
            raise ValueError(f"record id overlap: {sorted(overlap)[:3]}")
        seen |= ids


def build_v4_7_split_records() -> tuple[list[JsonObject], list[JsonObject], list[JsonObject], list[JsonObject]]:
    base_train_records = load_jsonl(V4_6_TRAIN_PATH)
    base_validation_records = load_jsonl(V4_6_VALIDATION_PATH)
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
        name="v4.7 train supplement",
    )
    validate_records(
        probe_records,
        expected_count=30,
        expected_counts=EXPECTED_PROBE_COUNTS,
        name="v4.7 calibration probe",
    )
    validate_records(
        supplement_records,
        expected_count=150,
        expected_counts=EXPECTED_SUPPLEMENT_COUNTS,
        name="v4.7 total supplement",
    )
    validate_records(
        train_plus_records,
        expected_count=1460,
        expected_counts=EXPECTED_V4_7_TRAIN_COUNTS,
        name="v4.7 train",
    )
    validate_records(
        validation_plus_records,
        expected_count=130,
        expected_counts=EXPECTED_V4_7_VALIDATION_COUNTS,
        name="v4.7 validation",
    )

    train_ids = {str(item["id"]) for item in train_plus_records}
    validation_ids = {str(item["id"]) for item in validation_plus_records}
    if train_ids & validation_ids:
        raise ValueError("v4.7 train and validation records overlap")

    return train_plus_records, validation_plus_records, supplement_records, strip_metadata(probe_records)


def main() -> int:
    train_records, validation_records, supplement_records, probe_records = build_v4_7_split_records()
    clean_supplement_records = strip_metadata(supplement_records)

    write_jsonl(SUPPLEMENT_PATH, clean_supplement_records)
    write_jsonl(TRAIN_PLUS_PATH, train_records)
    write_jsonl(V4_7_TRAIN_PATH, train_records)
    write_jsonl(V4_7_VALIDATION_PATH, validation_records)
    write_jsonl(V4_7_PROBE_PATH, probe_records)

    print(f"Wrote {len(clean_supplement_records)} records to {SUPPLEMENT_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_records)} records to {TRAIN_PLUS_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_records)} records to {V4_7_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(validation_records)} records to {V4_7_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(probe_records)} records to {V4_7_PROBE_PATH.relative_to(ROOT)}")
    print(f"Base train source: {V4_6_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Base validation source: {V4_6_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Supplement labels: {dict(sorted(label_counts(clean_supplement_records).items()))}")
    print(f"Supplement buckets: {metadata_counts(supplement_records)}")
    print(f"Train labels: {dict(sorted(label_counts(train_records).items()))}")
    print(f"Validation labels: {dict(sorted(label_counts(validation_records).items()))}")
    print("Fixed test split was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
