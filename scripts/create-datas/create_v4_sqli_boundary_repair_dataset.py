#!/usr/bin/env python3
"""Create Phase 8 v4 SQLi-first boundary repair data.

The v4 supplement is built after Phase 7 held v3.5. It targets SQLi recovery
and quote-heavy structured-output stability first, with small guard sets for
normal-vs-bruteforce, traversal, port/recon, and severity calibration. It does
not read or modify the fixed test split.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.unsloth.training_format import format_split  # noqa: E402
from scripts.create_v3_5_boundary_repair_dataset import (  # noqa: E402
    V3_5_TRAIN_PATH,
    V3_5_VALIDATION_PATH,
    build_v3_5_split_records,
)
from scripts.generate_dataset import INSTRUCTION, LABELS, validate_record, write_jsonl  # noqa: E402


SUPPLEMENT_PATH = ROOT / "data" / "generated" / "v4-sqli-boundary-repair-security-triage.jsonl"
TRAIN_PLUS_PATH = ROOT / "data" / "generated" / "train-plus-v4-sqli-boundary-repair.jsonl"
V4_TRAIN_PATH = ROOT / "data" / "splits" / "train-v4-sqli-boundary-repair.jsonl"
V4_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v4-sqli-boundary-repair.jsonl"

EXPECTED_SUPPLEMENT_COUNTS = {
    "normal": 40,
    "failed_login_bruteforce": 10,
    "sql_injection_attempt": 80,
    "directory_traversal_attempt": 20,
    "port_scan_or_recon": 10,
}
EXPECTED_V4_TRAIN_COUNTS = {
    "normal": 255,
    "failed_login_bruteforce": 130,
    "sql_injection_attempt": 315,
    "directory_traversal_attempt": 175,
    "port_scan_or_recon": 195,
}
EXPECTED_VALIDATION_COUNTS = {label: 15 for label in LABELS}

JsonObject = dict[str, Any]


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
            "phase": "phase-8-v4-sqli-boundary-repair",
            "repair_bucket": repair_bucket,
        },
    }


def make_id(index: int) -> str:
    return f"v4-sqli-{index:06d}"


def sqli_positive_records(start_index: int) -> list[JsonObject]:
    payloads = [
        ("username=admin' OR '1'='1", "quoted OR tautology"),
        ("filter=' OR 'x'='x'--", "quoted tautology with SQL comment"),
        ("q=%27%20OR%201%3D1--", "encoded OR tautology"),
        ("id=7 UNION SELECT username,password FROM users--", "UNION SELECT credential probe"),
        ("id=9 AND SLEEP(5)", "time-delay SLEEP payload"),
        ("id=4;WAITFOR DELAY '0:0:5'--", "WAITFOR time-delay payload"),
        ("sort=name;DROP TABLE audit_log--", "stacked query with destructive verb"),
        ("lookup=information_schema.tables", "database schema discovery"),
        ("email=test@example.com' OR 'a'='a", "email-field tautology"),
        ("token=abc'--", "quote followed by SQL comment marker"),
        ("price=0 OR 1=1", "numeric OR tautology"),
        ("category=books') OR ('1'='1", "parenthesized quote tautology"),
        ('search=" OR "1"="1"', "double-quote tautology"),
        ("account=42' AND 'x'='x", "quoted AND tautology"),
        ("item=5/**/UNION/**/SELECT/**/credit_card", "comment-obfuscated UNION SELECT"),
        ("query=admin%27%29%20OR%20%28%271%27%3D%271", "encoded parenthesized tautology"),
        ("filter=name LIKE '%' OR role='admin'", "SQL predicate injection"),
        ("offset=0;SELECT pg_sleep(5)--", "stacked pg_sleep payload"),
        ("sku=100' UNION ALL SELECT null,version()--", "UNION ALL version probe"),
        ("comment=')/**/OR/**/('a'='a", "comment-obfuscated quote tautology"),
    ]
    contexts = [
        (
            "login",
            "2026-05-22T20:{minute:02d}:01+07:00 app=web route=/login method=POST src_ip=198.51.100.{host} payload=\"{payload}\" status=403 auth_result=blocked",
            "status=403",
        ),
        (
            "api",
            "2026-05-22T20:{minute:02d}:13+07:00 api-gateway method=GET route=/api/search src=203.0.113.{host} raw_query=\"{payload}\" status=400 validation=failed",
            "status=400",
        ),
        (
            "waf",
            "2026-05-22T20:{minute:02d}:25+07:00 waf: rule=sqli src=192.0.2.{host} request_payload=\"{payload}\" status=500 db_error=true",
            "status=500",
        ),
        (
            "reset",
            "2026-05-22T20:{minute:02d}:37+07:00 app=identity route=/reset-password src_ip=198.51.100.{host} form_payload=\"{payload}\" status=401 reset_result=blocked",
            "status=401",
        ),
    ]

    rows: list[JsonObject] = []
    index = start_index
    for payload_index, (payload, reason_suffix) in enumerate(payloads):
        for context_index, (context_name, template, status_evidence) in enumerate(contexts):
            log_line = template.format(
                minute=(payload_index * len(contexts) + context_index) % 60,
                host=30 + index,
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
                    repair_bucket="sqli_quote_boundary_positive",
                )
            )
            index += 1
    return rows


def normal_hard_negative_records(start_index: int) -> list[JsonObject]:
    sql_queries = [
        "query=union-select-cheatsheet",
        "query=information-schema-overview",
        "query=sleep-function-reference",
        "query=waitfor-delay-docs",
        "query=drop-table-training-lab",
        "query=sql-comment-syntax",
        "query=or-condition-tutorial",
        "query=database-schema-review",
        "query=postgres-version-notes",
        "query=mysql-error-reference",
        "query=union-station-map",
        "query=selective-indexing-guide",
        "query=null-value-handling",
        "query=order-by-documentation",
        "query=role-admin-guide",
    ]
    auth_events = [
        ("Failed password", "failed_attempts=1"),
        ("login_failed", "failures=1"),
        ("event_id=4625", "count=1"),
        ("status=401", "request_count=1"),
        ("vpn auth failed", "repeated=1"),
        ("bad password", "unique_passwords=1"),
        ("password_reset_failed", "attempts=1"),
        ("lockout=false", "failed_attempts=2"),
        ("retry allowed", "failures=1"),
        ("status=403", "waf_block=sqli"),
    ]
    relative_paths = [
        "path=docs/../docs/sql-guide.md",
        "path=assets/../assets/logo.png",
        "path=public/../public/robots.txt",
        "path=reports/../reports/monthly.html",
        "path=help/../help/index.html",
        "path=themes/../themes/default.css",
        "path=download/../download/manual.pdf",
        "path=images/../images/banner.jpg",
    ]
    monitoring = [
        ("approved inventory", "unique_ports=2"),
        ("health check", "unique_ports=1"),
        ("allowlisted scanner", "unique_ports=3"),
        ("load balancer probe", "unique_ports=1"),
        ("database readiness probe", "dst_port=5432"),
        ("approved service check", "change_ticket=CHG-4242"),
        ("backup agent connection", "agent=backupd"),
    ]

    rows: list[JsonObject] = []
    index = start_index
    for query_index, query in enumerate(sql_queries):
        log_line = (
            f"2026-05-22T21:{query_index:02d}:01+07:00 app=docs route=/search "
            f"method=GET src_ip=203.0.113.{40 + index} {query} status=200"
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
                    reason="SQL-related words appear in ordinary documentation search without an injection payload boundary.",
                    recommended_action="No immediate action required. Continue normal monitoring.",
                ),
                repair_bucket="sqli_hard_negative_normal",
            )
        )
        index += 1

    for event_index, (event, detail) in enumerate(auth_events):
        log_line = (
            f"2026-05-22T21:{15 + event_index:02d}:01+07:00 auth: user=analyst "
            f"src_ip=198.51.100.{40 + index} {event} {detail} correlation=none"
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

    for path_index, path in enumerate(relative_paths):
        log_line = (
            f"2026-05-22T21:{25 + path_index:02d}:01+07:00 app=docs route=/static "
            f"method=GET src_ip=192.0.2.{40 + index} {path} normalized=true status=200"
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
                    reason="The relative path is normalized inside an allowed static content path.",
                    recommended_action="No immediate action required. Continue normal monitoring.",
                ),
                repair_bucket="traversal_hard_negative_normal",
            )
        )
        index += 1

    for monitor_index, (event, detail) in enumerate(monitoring):
        log_line = (
            f"2026-05-22T21:{33 + monitor_index:02d}:01+07:00 asset-inventory: {event} "
            f"src=monitor-01 dst=203.0.113.{40 + index} {detail} approved=true action=allowed"
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
                    reason="The event is approved low-scope monitoring rather than reconnaissance.",
                    recommended_action="No immediate action required. Continue normal monitoring.",
                ),
                repair_bucket="port_recon_hard_negative_normal",
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
        ("vpn auth failed", "repeated=21", "window=180s"),
        ("bad password", "unique_passwords=14", "window=120s"),
        ("password_reset_failed", "attempts=17", "window=90s"),
        ("lockout=true", "failed_attempts=12", "window=300s"),
        ("spray_detected", "unique_users=19", "window=240s"),
        ("POST /login", "status=401 repeated=22", "user_agent=python-requests"),
    ]

    rows: list[JsonObject] = []
    index = start_index
    for event_index, (event, detail, extra) in enumerate(events):
        log_line = (
            f"2026-05-22T22:{event_index:02d}:01+07:00 auth: user=admin "
            f"src_ip=198.51.100.{50 + index} {event} {detail} {extra}"
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
        ("file=../../../../etc/passwd%00", "null-byte traversal attempt"),
        ("page=php://filter/convert.base64-encode/resource=index.php", "PHP filter file-read wrapper"),
        ("archive=zip://../avatar/target.jpg%23code", "zip wrapper inclusion attempt"),
        ("file=../../.env", "environment file traversal"),
    ]
    contexts = [
        ("files", "2026-05-22T22:{minute:02d}:20+07:00 app=files method=GET src_ip=203.0.113.{host} {payload} status=403 bytes=0", "status=403"),
        ("waf", "2026-05-22T22:{minute:02d}:40+07:00 waf: path_probe src=192.0.2.{host} raw_query=\"{payload}\" action=blocked status=404", "status=404"),
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
        ("banner grab", "banners_requested=true"),
    ]
    contexts = [
        "2026-05-22T23:{minute:02d}:01+07:00 ids: blocked attempt src=198.51.100.{host} dst=203.0.113.{dst} {signal} {detail} window=45s",
        "2026-05-22T23:{minute:02d}:31+07:00 netflow: probe attempt src=192.0.2.{host} dst=198.51.100.{dst} {signal} {detail} packets=148",
    ]

    rows: list[JsonObject] = []
    index = start_index
    for signal_index, (signal, detail) in enumerate(signals):
        for context_index, template in enumerate(contexts):
            log_line = template.format(
                minute=signal_index * len(contexts) + context_index,
                host=70 + index,
                dst=90 + index,
                signal=signal,
                detail=detail,
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


def build_v4_split_records() -> tuple[list[JsonObject], list[JsonObject], list[JsonObject]]:
    v3_5_train_records, validation_records, _v3_5_supplement_records = build_v3_5_split_records()
    supplement_records = build_supplement_records()
    train_plus_records = [*v3_5_train_records, *strip_metadata(supplement_records)]

    validate_records(
        supplement_records,
        expected_count=160,
        expected_counts=EXPECTED_SUPPLEMENT_COUNTS,
        name="v4 SQLi boundary repair supplement",
    )
    validate_records(
        train_plus_records,
        expected_count=1070,
        expected_counts=EXPECTED_V4_TRAIN_COUNTS,
        name="v4 train",
    )
    validate_records(
        validation_records,
        expected_count=75,
        expected_counts=EXPECTED_VALIDATION_COUNTS,
        name="v4 validation",
    )

    train_base_ids = {str(item["id"]) for item in v3_5_train_records}
    validation_ids = {str(item["id"]) for item in validation_records}
    supplement_ids = {str(item["id"]) for item in supplement_records}

    if supplement_ids & train_base_ids:
        raise ValueError("v4 supplement ids overlap v3.5 base train ids")
    if supplement_ids & validation_ids:
        raise ValueError("v4 supplement ids overlap validation ids")

    train_ids = {str(item["id"]) for item in train_plus_records}
    if train_ids & validation_ids:
        raise ValueError("v4 train and validation records overlap")

    return train_plus_records, validation_records, supplement_records


def main() -> int:
    train_plus_records, validation_records, supplement_records = build_v4_split_records()
    clean_supplement_records = strip_metadata(supplement_records)

    write_jsonl(SUPPLEMENT_PATH, clean_supplement_records)
    write_jsonl(TRAIN_PLUS_PATH, train_plus_records)
    write_jsonl(V4_TRAIN_PATH, train_plus_records)
    write_jsonl(V4_VALIDATION_PATH, validation_records)

    print(f"Wrote {len(clean_supplement_records)} records to {SUPPLEMENT_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_plus_records)} records to {TRAIN_PLUS_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_plus_records)} records to {V4_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(validation_records)} records to {V4_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Base train source: {V3_5_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Validation source: {V3_5_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Supplement labels: {dict(sorted(label_counts(clean_supplement_records).items()))}")
    print(f"Supplement buckets: {metadata_counts(supplement_records)}")
    print(f"Train labels: {dict(sorted(label_counts(train_plus_records).items()))}")
    print(f"Validation labels: {dict(sorted(label_counts(validation_records).items()))}")
    print("Fixed test split was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
