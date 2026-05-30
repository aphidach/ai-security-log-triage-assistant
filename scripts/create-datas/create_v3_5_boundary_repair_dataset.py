#!/usr/bin/env python3
"""Create Phase 6 v3.5 boundary repair data without fixed-test use.

The v3.5 supplement is built from the v3.4 temperature=0 failure slice. It
targets SQLi recovery, traversal recovery, JSON-escape stress cases, and
brute-force anti-gravity. No new brute-force positives are added because v3.4
already has perfect brute-force recall on the hard-contrast canary.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.unsloth.training_format import format_split  # noqa: E402
from scripts.create_v3_4_boundary_repair_dataset import (  # noqa: E402
    V3_4_TRAIN_PATH,
    V3_4_VALIDATION_PATH,
    build_v3_4_split_records,
)
from scripts.generate_dataset import INSTRUCTION, LABELS, validate_record, write_jsonl  # noqa: E402


SUPPLEMENT_PATH = ROOT / "data" / "generated" / "v3-5-boundary-repair-security-triage.jsonl"
TRAIN_PLUS_PATH = ROOT / "data" / "generated" / "train-plus-v3-5-boundary-repair.jsonl"
V3_5_TRAIN_PATH = ROOT / "data" / "splits" / "train-v3-5-boundary-repair.jsonl"
V3_5_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v3-5-boundary-repair.jsonl"

EXPECTED_SUPPLEMENT_COUNTS = {
    "normal": 45,
    "failed_login_bruteforce": 0,
    "sql_injection_attempt": 75,
    "directory_traversal_attempt": 55,
    "port_scan_or_recon": 25,
}
EXPECTED_V3_5_TRAIN_COUNTS = {
    "normal": 215,
    "failed_login_bruteforce": 120,
    "sql_injection_attempt": 235,
    "directory_traversal_attempt": 155,
    "port_scan_or_recon": 185,
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
            "phase": "phase-6-v3-5-boundary-repair",
            "repair_bucket": repair_bucket,
        },
    }


def make_id(index: int) -> str:
    return f"v3-5-boundary-{index:06d}"


def sqli_positive_records(start_index: int) -> list[JsonObject]:
    payloads = [
        ("username=admin' OR '1'='1", "quoted OR tautology"),
        ("user=1' or '1'='1'))/*", "quote tautology with comment close"),
        ('q=" OR "1"="1', "double-quote tautology"),
        ("id=1 OR 1=1", "numeric OR tautology"),
        ("id=10 AND 1=1", "numeric AND tautology"),
        ("id=9 AND SLEEP(5)", "time delay SLEEP payload"),
        ("id=4;WAITFOR DELAY '0:0:5'--", "time delay WAITFOR payload"),
        ("filter=1;DROP TABLE audit_log--", "stacked query with SQL comment"),
        ("sort=name UNION SELECT password FROM users--", "UNION SELECT credential probe"),
        ("q=information_schema.tables", "database metadata discovery"),
        ("search=%27%20OR%20%271%27%3D%271--", "encoded quote tautology"),
        ("account=42' AND 'x'='x", "quoted AND tautology"),
        ("email=test@example.com' OR 'a'='a", "email field tautology"),
        ("token=abc'--", "SQL comment marker after quoted value"),
        ("uri=/product?id=99999 UNION SELECT 1,null,null--", "UNION column probe"),
    ]
    contexts = [
        ("login", "2026-05-22T16:{minute:02d}:01+07:00 app=web route=/login method=POST src_ip=198.51.100.{host} {payload} status=403 auth_result=blocked"),
        ("api", "2026-05-22T16:{minute:02d}:13+07:00 api-gateway method=GET route=/api/items src=203.0.113.{host} {payload} status=400 validation=failed"),
        ("search", '192.0.2.{host} - - [22/May/2026:16:{minute:02d}:25 +0700] "GET /search?{payload} HTTP/1.1" 500 912 "-" "Mozilla/5.0"'),
        ("reset", "2026-05-22T16:{minute:02d}:37+07:00 app=identity route=/reset-password src_ip=198.51.100.{host} {payload} status=401 reset_result=blocked"),
        ("waf", "2026-05-22T16:{minute:02d}:49+07:00 waf: blocked request src=203.0.113.{host} raw=\"{payload}\" rule=sqli status=403"),
    ]

    rows: list[JsonObject] = []
    index = start_index
    for payload_index, (payload, reason_suffix) in enumerate(payloads):
        for context_index, (context_name, template) in enumerate(contexts):
            status_evidence = "500" if " 500 " in template else "status=403" if "status=403" in template else "status=400" if "status=400" in template else "status=401"
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
                        label="sql_injection_attempt",
                        severity="high",
                        is_suspicious=True,
                        evidence=[payload, status_evidence],
                        reason=f"The {context_name} request contains a SQL injection {reason_suffix}.",
                        recommended_action="Review web application and WAF logs, then check whether the request reached database-backed code.",
                    ),
                    repair_bucket="sqli_positive_boundary",
                )
            )
            index += 1
    return rows


def traversal_positive_records(start_index: int) -> list[JsonObject]:
    payloads = [
        ("file=../config.yml", "relative traversal to a config file"),
        ("file=../../../../etc/passwd", "Unix password file traversal"),
        ("download=../../../etc/shadow", "Unix shadow file traversal"),
        ("file=%2e%2e%2f%2e%2e%2fwindows%2fwin.ini", "encoded Windows traversal"),
        ("path=..%2f..%2fvar%2flog%2fauth.log", "encoded traversal to auth logs"),
        ("include=../../secrets.yml", "traversal to secrets file"),
        ("template=../../WEB-INF/web.xml", "Java web descriptor traversal"),
        ("file=../../../../etc/passwd%00", "null-byte traversal attempt"),
        ("page=php://filter/convert.base64-encode/resource=index.php", "PHP filter file-read wrapper"),
        ("archive=zip://../avatar/target.jpg%23code", "zip wrapper inclusion attempt"),
        ("file=../../.env", "environment file traversal"),
    ]
    contexts = [
        ("blocked", "2026-05-22T17:{minute:02d}:01+07:00 app=files method=GET src_ip=198.51.100.{host} {payload} status=403 bytes=0"),
        ("curl", '203.0.113.{host} - - [22/May/2026:17:{minute:02d}:13 +0700] "GET /download?{payload} HTTP/1.1" 404 0 "-" "curl/8.1"'),
        ("scanner", "2026-05-22T17:{minute:02d}:25+07:00 waf: path_probe src=192.0.2.{host} {payload} action=blocked status=401"),
        ("encoded", "2026-05-22T17:{minute:02d}:37+07:00 reverse-proxy request_id=trav-{host} raw_query=\"{payload}\" normalized_path=/blocked status=403"),
        ("backup", "2026-05-22T17:{minute:02d}:49+07:00 app=backup route=/restore src_ip=198.51.100.{host} {payload} user_agent=Mozilla status=403"),
    ]

    rows: list[JsonObject] = []
    index = start_index
    for payload_index, (payload, reason_suffix) in enumerate(payloads):
        for context_index, (context_name, template) in enumerate(contexts):
            status_evidence = "404" if " 404 " in template else "status=401" if "status=401" in template else "status=403"
            log_line = template.format(
                minute=(payload_index * len(contexts) + context_index) % 60,
                host=70 + index,
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
                    repair_bucket="traversal_positive_boundary",
                )
            )
            index += 1
    return rows


def sqli_hard_negative_normal_records(start_index: int) -> list[JsonObject]:
    queries = [
        "query=selective-indexing-guide",
        "query=union-station-map",
        "query=sleep-tracking-tips",
        "query=information_schema-overview",
        "query=schema-migration-checklist",
        "query=or-logic-tutorial",
        "query=drop-table-exercise-docs",
        "query=sql-comment-syntax-lesson",
        "query=waitfor-delay-documentation",
        "query=union-select-committee-minutes",
        "query=order-by-documentation",
        "query=null-value-handling",
        "query=postgres-version-notes",
        "query=mysql-error-reference",
        "query=database-schema-review",
    ]

    rows: list[JsonObject] = []
    index = start_index
    for query_index, query in enumerate(queries):
        log_line = (
            f"2026-05-22T18:{query_index:02d}:01+07:00 app=docs route=/search "
            f"method=GET src_ip=203.0.113.{80 + index} {query} status=200"
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
    return rows


def traversal_hard_negative_normal_records(start_index: int) -> list[JsonObject]:
    paths = [
        "path=docs/../docs/install.md",
        "path=assets/../assets/logo.png",
        "path=reports/../reports/daily.html",
        "path=help/../help/index.html",
        "path=public/../public/robots.txt",
        "path=themes/../themes/default.css",
        "path=images/../images/banner.jpg",
        "path=backup/../backup/readme.txt",
        "path=kb/../kb/sql-guide.md",
        "path=download/../download/manual.pdf",
    ]

    rows: list[JsonObject] = []
    index = start_index
    for path_index, path in enumerate(paths):
        log_line = (
            f"2026-05-22T18:{20 + path_index:02d}:01+07:00 app=docs route=/static "
            f"method=GET src_ip=198.51.100.{80 + index} {path} normalized=true status=200"
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
                    reason="The relative path is normalized inside an allowed documentation/static path.",
                    recommended_action="No immediate action required. Continue normal monitoring.",
                ),
                repair_bucket="traversal_hard_negative_normal",
            )
        )
        index += 1
    return rows


def brute_antigravity_normal_records(start_index: int) -> list[JsonObject]:
    low_signal_events = [
        ("Failed password", "failed_attempts=1", "A single SSH failed password is not brute force."),
        ("event_id=4625", "count=1", "A single Windows failed logon event is not a burst."),
        ("login_failed", "failures=1", "One application login failure is not repeated guessing."),
        ("status=401", "request_count=1", "A single 401 response is not an authentication burst."),
        ("status=403", "waf_block=sqli", "A WAF block for SQLi is not brute force."),
        ("password_reset_failed", "attempts=1", "One password reset validation failure is not guessing."),
        ("vpn auth failed", "repeated=1", "One VPN authentication failure is not brute force."),
        ("lockout=false", "failed_attempts=2", "Two failures without lockout are below the brute-force threshold."),
        ("retry allowed", "failures=1", "A normal allowed retry is not an attack pattern."),
        ("bad password", "unique_passwords=1", "One bad password does not show password spraying."),
    ]

    rows: list[JsonObject] = []
    index = start_index
    for event_index, (event, detail, reason) in enumerate(low_signal_events):
        log_line = (
            f"2026-05-22T18:{35 + event_index:02d}:01+07:00 auth: target_user=analyst "
            f"src_ip=203.0.113.{80 + index} {event} {detail} correlation=none"
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
                    reason=reason,
                    recommended_action="Monitor for repeated failures from the same source before escalating.",
                ),
                repair_bucket="bruteforce_antigravity_normal",
            )
        )
        index += 1
    return rows


def port_hard_negative_normal_records(start_index: int) -> list[JsonObject]:
    events = [
        ("approved inventory", "unique_ports=2", "approved=true"),
        ("health check", "unique_ports=1", "monitoring=true"),
        ("allowlisted scanner", "unique_ports=3", "allowlist=asset-inventory"),
        ("one-port monitoring", "unique_ports=1", "dst_port=9100"),
        ("load balancer probe", "unique_ports=1", "pool=web"),
        ("backup agent connection", "unique_ports=1", "agent=backupd"),
        ("database readiness probe", "unique_ports=1", "dst_port=5432"),
        ("authorized vulnerability scan", "unique_ports=4", "scanner=approved"),
        ("approved service check", "unique_ports=2", "change_ticket=CHG-2241"),
        ("known TLS fingerprint", "dst_port=443", "signature=ja3_known_client"),
    ]

    rows: list[JsonObject] = []
    index = start_index
    for event_index, (event, detail, extra) in enumerate(events):
        log_line = (
            f"2026-05-22T18:{45 + event_index:02d}:01+07:00 asset-inventory: {event} "
            f"src=monitor-01 dst=192.0.2.{80 + index} {detail} {extra} action=allowed"
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
                    reason="The event is an approved or low-scope monitoring activity, not reconnaissance.",
                    recommended_action="No immediate action required. Continue normal monitoring.",
                ),
                repair_bucket="port_recon_hard_negative_normal",
            )
        )
        index += 1
    return rows


def port_positive_records(start_index: int) -> list[JsonObject]:
    signals = [
        ("nmap fingerprint", "probed_ports=22,80,443,3306,8080", "Nmap-style fingerprinting across services."),
        ("service enumeration", "unique_ports=12", "Service enumeration across many ports."),
        ("horizontal scan", "unique_hosts=24", "Horizontal scan across many hosts."),
        ("SYN scan detected", "unique_ports=18", "SYN scan across a high number of ports."),
        ("banner grab", "banners_requested=true", "Banner collection during service enumeration."),
    ]
    contexts = [
        "2026-05-22T19:{minute:02d}:01+07:00 ids: blocked attempt src=198.51.100.{host} dst=203.0.113.{dst} {signal} {detail} window=45s",
        "2026-05-22T19:{minute:02d}:13+07:00 firewall: repeated attempt src=203.0.113.{host} dst=192.0.2.{dst} {signal} {detail} packets=148",
        "2026-05-22T19:{minute:02d}:25+07:00 netflow: probe attempt src=192.0.2.{host} dst=198.51.100.{dst} {signal} {detail} window=60s",
        "2026-05-22T19:{minute:02d}:37+07:00 siem: recon_alert blocked=true src=198.51.100.{host} target=192.0.2.{dst} {signal} {detail}",
        "2026-05-22T19:{minute:02d}:49+07:00 ids: generic attempt wording src=203.0.113.{host} dst=198.51.100.{dst} {signal} {detail}",
    ]

    rows: list[JsonObject] = []
    index = start_index
    for signal_index, (signal, detail, reason_suffix) in enumerate(signals):
        for context_index, template in enumerate(contexts):
            host_octet = 30 + (index % 180)
            dst_octet = 40 + (index % 180)
            log_line = template.format(
                minute=signal_index * len(contexts) + context_index,
                host=host_octet,
                dst=dst_octet,
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
                        reason=f"The event shows {reason_suffix} Blocked/attempt wording does not make it a login brute force event.",
                        recommended_action="Review network logs for additional reconnaissance from the source IP.",
                    ),
                    repair_bucket="port_recon_positive_boundary",
                )
            )
            index += 1
    return rows


def build_supplement_records() -> list[JsonObject]:
    records: list[JsonObject] = []
    for builder in (
        sqli_positive_records,
        traversal_positive_records,
        sqli_hard_negative_normal_records,
        traversal_hard_negative_normal_records,
        brute_antigravity_normal_records,
        port_hard_negative_normal_records,
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


def build_v3_5_split_records() -> tuple[list[JsonObject], list[JsonObject], list[JsonObject]]:
    v3_4_train_records, validation_records, _v3_4_supplement_records = build_v3_4_split_records()
    supplement_records = build_supplement_records()
    train_plus_records = [*v3_4_train_records, *strip_metadata(supplement_records)]

    validate_records(
        supplement_records,
        expected_count=200,
        expected_counts=EXPECTED_SUPPLEMENT_COUNTS,
        name="v3.5 boundary repair supplement",
    )
    validate_records(
        train_plus_records,
        expected_count=910,
        expected_counts=EXPECTED_V3_5_TRAIN_COUNTS,
        name="v3.5 train",
    )
    validate_records(
        validation_records,
        expected_count=75,
        expected_counts=EXPECTED_VALIDATION_COUNTS,
        name="v3.5 validation",
    )

    train_base_ids = {str(item["id"]) for item in v3_4_train_records}
    validation_ids = {str(item["id"]) for item in validation_records}
    supplement_ids = {str(item["id"]) for item in supplement_records}

    if supplement_ids & train_base_ids:
        raise ValueError("v3.5 supplement ids overlap v3.4 base train ids")
    if supplement_ids & validation_ids:
        raise ValueError("v3.5 supplement ids overlap validation ids")

    train_ids = {str(item["id"]) for item in train_plus_records}
    if train_ids & validation_ids:
        raise ValueError("v3.5 train and validation records overlap")

    return train_plus_records, validation_records, supplement_records


def main() -> int:
    train_plus_records, validation_records, supplement_records = build_v3_5_split_records()
    clean_supplement_records = strip_metadata(supplement_records)

    write_jsonl(SUPPLEMENT_PATH, clean_supplement_records)
    write_jsonl(TRAIN_PLUS_PATH, train_plus_records)
    write_jsonl(V3_5_TRAIN_PATH, train_plus_records)
    write_jsonl(V3_5_VALIDATION_PATH, validation_records)

    print(f"Wrote {len(clean_supplement_records)} records to {SUPPLEMENT_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_plus_records)} records to {TRAIN_PLUS_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_plus_records)} records to {V3_5_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(validation_records)} records to {V3_5_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Base train source: {V3_4_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Validation source: {V3_4_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Supplement labels: {dict(sorted(label_counts(clean_supplement_records).items()))}")
    print(f"Supplement buckets: {metadata_counts(supplement_records)}")
    print(f"Train labels: {dict(sorted(label_counts(train_plus_records).items()))}")
    print(f"Validation labels: {dict(sorted(label_counts(validation_records).items()))}")
    print("Fixed test split was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
