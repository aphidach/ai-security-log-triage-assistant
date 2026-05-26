#!/usr/bin/env python3
"""Create Phase 8 v4.1 SQLi-boundary repair data.

The v4.1 supplement is intentionally narrower than v4. It appends a focused
SQLi-boundary set to the existing v4 train split, keeps validation unchanged,
and does not read or modify the fixed test split.
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
from scripts.create_v4_sqli_boundary_repair_dataset import (  # noqa: E402
    V4_TRAIN_PATH,
    V4_VALIDATION_PATH,
)
from scripts.generate_dataset import INSTRUCTION, LABELS, validate_record, write_jsonl  # noqa: E402


SUPPLEMENT_PATH = ROOT / "data" / "generated" / "v4-1-sqli-boundary-repair-security-triage.jsonl"
TRAIN_PLUS_PATH = ROOT / "data" / "generated" / "train-plus-v4-1-sqli-boundary-repair.jsonl"
V4_1_TRAIN_PATH = ROOT / "data" / "splits" / "train-v4-1-sqli-boundary-repair.jsonl"
V4_1_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v4-1-sqli-boundary-repair.jsonl"
HARD_CONTRAST_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"

EXPECTED_SUPPLEMENT_COUNTS = {
    "normal": 24,
    "failed_login_bruteforce": 6,
    "sql_injection_attempt": 100,
    "directory_traversal_attempt": 16,
    "port_scan_or_recon": 4,
}
EXPECTED_V4_1_TRAIN_COUNTS = {
    "normal": 279,
    "failed_login_bruteforce": 136,
    "sql_injection_attempt": 415,
    "directory_traversal_attempt": 191,
    "port_scan_or_recon": 199,
}
EXPECTED_VALIDATION_COUNTS = {label: 15 for label in LABELS}

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
            "phase": "phase-8-v4-1-sqli-boundary-repair",
            "repair_bucket": repair_bucket,
        },
    }


def make_id(index: int) -> str:
    return f"v4-1-sqli-{index:06d}"


def sqli_positive_records(start_index: int) -> list[JsonObject]:
    payloads = [
        ("user=guest OR 1=1", "bare numeric tautology", "sqli_bare_tautology"),
        ("account=42 OR 1=1--", "bare tautology with SQL comment", "sqli_bare_tautology"),
        ("filter=0 OR 1=1 LIMIT 1", "bare tautology with SQL clause", "sqli_bare_tautology"),
        ("page=5 OR TRUE--", "boolean tautology", "sqli_bare_tautology"),
        ("username=admin' OR '1'='1", "quoted OR tautology", "sqli_quoted_tautology"),
        ("login=' OR 'x'='x'--", "quoted tautology with SQL comment", "sqli_quoted_tautology"),
        ("email=test@example.com' OR 'a'='a", "quoted email-field tautology", "sqli_quoted_tautology"),
        ("category=books') OR ('1'='1", "parenthesized quote tautology", "sqli_quoted_tautology"),
        ("name=admin'--", "quote followed by SQL comment", "sqli_comment_boundary"),
        ("token=xyz'/*", "quote followed by block comment opener", "sqli_comment_boundary"),
        ("q=abc'/**/OR/**/'1'='1", "comment-obfuscated tautology", "sqli_comment_boundary"),
        ("ref=17--", "line comment boundary after parameter", "sqli_comment_boundary"),
        ("id=8 AND SLEEP(5)", "MySQL time-delay payload", "sqli_time_delay"),
        ("offset=0;SELECT pg_sleep(5)--", "PostgreSQL time-delay payload", "sqli_time_delay"),
        ("id=11;WAITFOR DELAY '0:0:5'--", "SQL Server time-delay payload", "sqli_time_delay"),
        ("sort=name AND benchmark(5000000,md5(1))", "CPU-delay SQL payload", "sqli_time_delay"),
        ("q=information_schema.columns", "database schema discovery", "sqli_schema_discovery"),
        ("table=sqlite_master", "SQLite schema discovery", "sqli_schema_discovery"),
        ("catalog=pg_catalog.pg_tables", "PostgreSQL catalog discovery", "sqli_schema_discovery"),
        ("lookup=sys.objects", "SQL Server object catalog discovery", "sqli_schema_discovery"),
        ("filter=1;DROP TABLE sessions--", "stacked destructive query", "sqli_stacked_query"),
        ("report=0;SELECT password FROM users--", "stacked SELECT credential probe", "sqli_stacked_query"),
        ("sku=100' UNION SELECT username,password FROM users--", "UNION SELECT credential probe", "sqli_stacked_query"),
        ("item=5 UNION ALL SELECT null,version()--", "UNION ALL version probe", "sqli_stacked_query"),
        ("query=%27%20OR%201%3D1--", "encoded quoted tautology", "sqli_encoded_boundary"),
    ]
    contexts = [
        (
            "login",
            "2026-05-23T00:{minute:02d}:01+07:00 app=web route=/login method=POST src_ip=198.51.101.{host} payload=\"{payload}\" status=403 decision=blocked",
            "status=403",
        ),
        (
            "api",
            "2026-05-23T00:{minute:02d}:13+07:00 api-gateway method=GET route=/api/search src=203.0.114.{host} raw_query=\"{payload}\" status=400 validation=failed",
            "status=400",
        ),
        (
            "waf",
            "2026-05-23T00:{minute:02d}:25+07:00 waf: category=sqli src=192.0.3.{host} request_payload=\"{payload}\" status=500 upstream_ms=5200",
            "status=500",
        ),
        (
            "report",
            "2026-05-23T00:{minute:02d}:37+07:00 app=reports route=/export method=GET src_ip=198.51.102.{host} query_string=\"{payload}\" status=401 db_guard=blocked",
            "status=401",
        ),
    ]

    rows: list[JsonObject] = []
    index = start_index
    for payload_index, (payload, reason_suffix, repair_bucket) in enumerate(payloads):
        for context_index, (context_name, template, status_evidence) in enumerate(contexts):
            log_line = template.format(
                minute=(payload_index * len(contexts) + context_index) % 60,
                host=20 + index,
                payload=payload,
            )
            rows.append(
                record(
                    make_id(index),
                    log_line,
                    triage_output(
                        label="sql_injection_attempt",
                        severity="high",
                        is_suspicious=True,
                        evidence=[payload, status_evidence],
                        reason=f"The {context_name} request contains a SQL injection {reason_suffix}.",
                        recommended_action="Review WAF and application logs, then check whether the request reached database-backed code.",
                    ),
                    repair_bucket=repair_bucket,
                )
            )
            index += 1
    return rows


def normal_hard_negative_records(start_index: int) -> list[JsonObject]:
    sql_searches = [
        "query=or-1-equals-1-training-note",
        "query=single-quote-sql-comment-guide",
        "query=sleep-function-documentation",
        "query=waitfor-delay-reference",
        "query=information-schema-cheatsheet",
        "query=sqlite-master-migration-doc",
        "query=pg-catalog-table-list",
        "query=drop-table-safe-lab",
        "query=union-select-example-doc",
        "query=sql-injection-awareness",
        "query=parameterized-query-tutorial",
        "query=database-error-playbook",
    ]
    auth_events = [
        ("Failed password", "failed_attempts=1"),
        ("login_failed", "failures=1"),
        ("event_id=4625", "count=1"),
        ("status=401", "request_count=1"),
        ("vpn auth failed", "repeated=1"),
        ("bad password", "unique_passwords=1"),
        ("lockout=false", "failed_attempts=2"),
        ("password_reset_failed", "attempts=1"),
    ]
    normalized_paths = [
        "path=docs/../docs/sql-safety.md",
        "path=training/../training/injection-lab.html",
        "path=assets/../assets/sql-icon.svg",
        "path=reports/../reports/query-review.pdf",
    ]

    rows: list[JsonObject] = []
    index = start_index
    for query_index, query in enumerate(sql_searches):
        log_line = (
            f"2026-05-23T01:{query_index:02d}:01+07:00 app=knowledge-base route=/search "
            f"method=GET src_ip=203.0.114.{40 + index} {query} status=200 user_role=analyst"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="normal",
                    severity="low",
                    is_suspicious=False,
                    evidence=[query, "status=200"],
                    reason="SQL-related words appear in an ordinary documentation search without an injection boundary.",
                    recommended_action="No immediate action required. Continue normal monitoring.",
                ),
                repair_bucket="sqli_hard_negative_normal",
            )
        )
        index += 1

    for event_index, (event, detail) in enumerate(auth_events):
        log_line = (
            f"2026-05-23T01:{12 + event_index:02d}:01+07:00 auth: user=developer "
            f"src_ip=198.51.101.{40 + index} {event} {detail} correlation=none window=none"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="normal",
                    severity="low",
                    is_suspicious=False,
                    evidence=[event, detail],
                    reason="The event is below the repeated-failure threshold and has no correlation evidence.",
                    recommended_action="Monitor for repeated failures from the same source before escalating.",
                ),
                repair_bucket="bruteforce_antigravity_normal",
            )
        )
        index += 1

    for path_index, path in enumerate(normalized_paths):
        log_line = (
            f"2026-05-23T01:{20 + path_index:02d}:01+07:00 app=knowledge-base route=/static "
            f"method=GET src_ip=192.0.3.{40 + index} {path} normalized=true status=200"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="normal",
                    severity="low",
                    is_suspicious=False,
                    evidence=[path, "normalized=true"],
                    reason="The relative path is normalized inside an allowed static documentation path.",
                    recommended_action="No immediate action required. Continue normal monitoring.",
                ),
                repair_bucket="traversal_hard_negative_normal",
            )
        )
        index += 1

    return rows


def brute_threshold_positive_records(start_index: int) -> list[JsonObject]:
    events = [
        ("Failed password", "failed_attempts=18", "window=120s"),
        ("login_failed", "failures=16", "window=90s"),
        ("event_id=4625", "count=24", "window=300s"),
        ("status=401", "request_count=31", "window=60s"),
        ("spray_detected", "unique_users=21", "window=240s"),
        ("bad password", "unique_passwords=14", "window=120s"),
    ]

    rows: list[JsonObject] = []
    index = start_index
    for event_index, (event, detail, extra) in enumerate(events):
        log_line = (
            f"2026-05-23T02:{event_index:02d}:01+07:00 auth: user=admin "
            f"src_ip=198.51.101.{50 + index} {event} {detail} {extra}"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="failed_login_bruteforce",
                    severity="medium",
                    is_suspicious=True,
                    evidence=[event, detail, extra],
                    reason="The log shows repeated authentication failures within a short window.",
                    recommended_action="Check whether the target account was locked and review related endpoint events.",
                ),
                repair_bucket="bruteforce_threshold_positive_guard",
            )
        )
        index += 1
    return rows


def traversal_positive_records(start_index: int) -> list[JsonObject]:
    payloads = [
        ("file=../../../../etc/passwd", "Unix password file traversal"),
        ("download=../../../etc/shadow", "Unix shadow file traversal"),
        ("file=%2e%2e%2f%2e%2e%2fwindows%2fwin.ini", "encoded Windows traversal"),
        ("path=..%2f..%2fvar%2flog%2fauth.log", "encoded traversal to auth logs"),
        ("include=../../secrets.yml", "secrets file traversal"),
        ("template=../../WEB-INF/web.xml", "Java web descriptor traversal"),
        ("page=php://filter/convert.base64-encode/resource=index.php", "PHP filter file-read wrapper"),
        ("file=../../.env", "environment file traversal"),
    ]
    contexts = [
        (
            "files",
            "2026-05-23T02:{minute:02d}:20+07:00 app=files method=GET src_ip=203.0.114.{host} {payload} status=403 bytes=0",
            "status=403",
        ),
        (
            "waf",
            "2026-05-23T02:{minute:02d}:40+07:00 waf: path_probe src=192.0.3.{host} raw_query=\"{payload}\" action=blocked status=404",
            "status=404",
        ),
    ]

    rows: list[JsonObject] = []
    index = start_index
    for payload_index, (payload, reason_suffix) in enumerate(payloads):
        for context_index, (context_name, template, status_evidence) in enumerate(contexts):
            log_line = template.format(
                minute=(payload_index * len(contexts) + context_index) % 60,
                host=60 + index,
                payload=payload,
            )
            rows.append(
                record(
                    make_id(index),
                    log_line,
                    triage_output(
                        label="directory_traversal_attempt",
                        severity="high",
                        is_suspicious=True,
                        evidence=[payload, status_evidence],
                        reason=f"The {context_name} request contains a {reason_suffix}.",
                        recommended_action="Review web server file-access logs and verify whether sensitive files were exposed.",
                    ),
                    repair_bucket="traversal_positive_guard",
                )
            )
            index += 1
    return rows


def port_positive_records(start_index: int) -> list[JsonObject]:
    signals = [
        ("nmap fingerprint", "probed_ports=22,80,443,3306,8080"),
        ("service enumeration", "unique_ports=12"),
        ("horizontal scan", "unique_hosts=24"),
        ("SYN scan detected", "unique_ports=18"),
    ]

    rows: list[JsonObject] = []
    index = start_index
    for signal_index, (signal, detail) in enumerate(signals):
        log_line = (
            f"2026-05-23T03:{signal_index:02d}:01+07:00 ids: blocked attempt "
            f"src=198.51.101.{70 + index} dst=203.0.114.{90 + index} {signal} {detail} window=45s"
        )
        rows.append(
            record(
                make_id(index),
                log_line,
                triage_output(
                    label="port_scan_or_recon",
                    severity="high" if signal in {"nmap fingerprint", "SYN scan detected"} else "medium",
                    is_suspicious=True,
                    evidence=[signal, detail],
                    reason="The event shows reconnaissance across services or hosts rather than an authentication burst.",
                    recommended_action="Review network logs for additional reconnaissance from the source IP.",
                ),
                repair_bucket="port_recon_positive_guard",
            )
        )
        index += 1
    return rows


def build_supplement_records() -> list[JsonObject]:
    records: list[JsonObject] = []
    for builder in (
        sqli_positive_records,
        normal_hard_negative_records,
        brute_threshold_positive_records,
        traversal_positive_records,
        port_positive_records,
    ):
        records.extend(builder(len(records) + 1))
    return records


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


def validate_no_hard_contrast_duplicates(supplement_records: list[JsonObject]) -> None:
    hard_inputs = {str(item["input"]) for item in load_jsonl(HARD_CONTRAST_PATH)}
    supplement_inputs = {str(item["input"]) for item in supplement_records}
    duplicates = sorted(supplement_inputs & hard_inputs)
    if duplicates:
        raise ValueError(f"v4.1 supplement duplicates hard-contrast inputs: {duplicates[:3]}")


def build_v4_1_split_records() -> tuple[list[JsonObject], list[JsonObject], list[JsonObject]]:
    v4_train_records = load_jsonl(V4_TRAIN_PATH)
    validation_records = load_jsonl(V4_VALIDATION_PATH)
    supplement_records = build_supplement_records()
    clean_supplement_records = strip_metadata(supplement_records)
    train_plus_records = [*v4_train_records, *clean_supplement_records]

    validate_no_hard_contrast_duplicates(supplement_records)
    validate_records(
        supplement_records,
        expected_count=150,
        expected_counts=EXPECTED_SUPPLEMENT_COUNTS,
        name="v4.1 SQLi boundary repair supplement",
    )
    validate_records(
        train_plus_records,
        expected_count=1220,
        expected_counts=EXPECTED_V4_1_TRAIN_COUNTS,
        name="v4.1 train",
    )
    validate_records(
        validation_records,
        expected_count=75,
        expected_counts=EXPECTED_VALIDATION_COUNTS,
        name="v4.1 validation",
    )

    train_base_ids = {str(item["id"]) for item in v4_train_records}
    validation_ids = {str(item["id"]) for item in validation_records}
    supplement_ids = {str(item["id"]) for item in supplement_records}

    if supplement_ids & train_base_ids:
        raise ValueError("v4.1 supplement ids overlap v4 base train ids")
    if supplement_ids & validation_ids:
        raise ValueError("v4.1 supplement ids overlap validation ids")

    train_ids = {str(item["id"]) for item in train_plus_records}
    if train_ids & validation_ids:
        raise ValueError("v4.1 train and validation records overlap")

    return train_plus_records, validation_records, supplement_records


def main() -> int:
    train_plus_records, validation_records, supplement_records = build_v4_1_split_records()
    clean_supplement_records = strip_metadata(supplement_records)

    write_jsonl(SUPPLEMENT_PATH, clean_supplement_records)
    write_jsonl(TRAIN_PLUS_PATH, train_plus_records)
    write_jsonl(V4_1_TRAIN_PATH, train_plus_records)
    write_jsonl(V4_1_VALIDATION_PATH, validation_records)

    print(f"Wrote {len(clean_supplement_records)} records to {SUPPLEMENT_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_plus_records)} records to {TRAIN_PLUS_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_plus_records)} records to {V4_1_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(validation_records)} records to {V4_1_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Base train source: {V4_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Validation source: {V4_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Supplement labels: {dict(sorted(label_counts(clean_supplement_records).items()))}")
    print(f"Supplement buckets: {metadata_counts(supplement_records)}")
    print(f"Train labels: {dict(sorted(label_counts(train_plus_records).items()))}")
    print(f"Validation labels: {dict(sorted(label_counts(validation_records).items()))}")
    print("Fixed test split was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
