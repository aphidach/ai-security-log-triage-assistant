#!/usr/bin/env python3
"""Create Phase 6 v3.3 targeted training split files without fixed-test use."""

from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.create_v3_1_training_split import (  # noqa: E402
    V3_1_TRAIN_PATH,
    V3_1_VALIDATION_PATH,
    build_v3_1_split_records,
)
from scripts.generate_dataset import INSTRUCTION, LABELS, validate_record, write_jsonl  # noqa: E402
from ml.unsloth.training_format import format_split  # noqa: E402


TARGETED_PATH = ROOT / "data" / "generated" / "v3-3-targeted-hard-contrast-security-triage.jsonl"
TRAIN_PLUS_PATH = ROOT / "data" / "generated" / "train-plus-v3-3-targeted-hard-contrast.jsonl"
V3_3_TRAIN_PATH = ROOT / "data" / "splits" / "train-v3-3-targeted-hard-contrast.jsonl"
V3_3_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v3-3-targeted-hard-contrast.jsonl"

TARGETED_WEIGHTED_PREFIX = "v3-3-target-weighted-"
TARGETED_LABEL_WEIGHTS = {
    "normal": 1,
    "sql_injection_attempt": 2,
    "port_scan_or_recon": 2,
}
EXPECTED_TARGETED_COUNTS = {
    "normal": 10,
    "failed_login_bruteforce": 0,
    "sql_injection_attempt": 10,
    "directory_traversal_attempt": 0,
    "port_scan_or_recon": 10,
}
EXPECTED_WEIGHTED_TARGETED_COUNTS = {
    "normal": 10,
    "failed_login_bruteforce": 0,
    "sql_injection_attempt": 20,
    "directory_traversal_attempt": 0,
    "port_scan_or_recon": 20,
}
EXPECTED_V3_3_TRAIN_COUNTS = {
    "normal": 110,
    "failed_login_bruteforce": 100,
    "sql_injection_attempt": 120,
    "directory_traversal_attempt": 100,
    "port_scan_or_recon": 120,
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


def record(record_id: str, log_line: str, output: JsonObject) -> JsonObject:
    return {
        "id": record_id,
        "instruction": INSTRUCTION,
        "input": log_line,
        "output": output,
    }


def normal_targeted_records() -> list[JsonObject]:
    rows = [
        (
            "v3-3-target-000001",
            '198.51.100.18 - - [21/May/2026:09:00:01 +0700] "GET /docs/sql/quote-handling?example=single-quote HTTP/1.1" 200 2144 "-" "Mozilla/5.0"',
            ["/docs/sql/quote-handling?example=single-quote", "200"],
            "This is a documentation request about quotes, not a SQL injection payload.",
        ),
        (
            "v3-3-target-000002",
            '203.0.113.18 - - [21/May/2026:09:02:01 +0700] "GET /search?q=tautology+lesson+or+one+equals+one HTTP/1.1" 200 1201 "-" "Mozilla/5.0"',
            ["/search?q=tautology+lesson+or+one+equals+one", "200"],
            "The query discusses tautology as ordinary text and lacks SQL operators.",
        ),
        (
            "v3-3-target-000003",
            '192.0.2.18 - - [21/May/2026:09:04:01 +0700] "GET /news?topic=Union+Select+Committee+minutes HTTP/1.1" 200 1878 "-" "Mozilla/5.0"',
            ["/news?topic=Union+Select+Committee+minutes", "200"],
            "Union Select appears as a normal phrase, not a UNION SELECT SQL clause.",
        ),
        (
            "v3-3-target-000004",
            '198.51.100.19 - - [21/May/2026:09:06:01 +0700] "GET /search?q=sleep+function+documentation HTTP/1.1" 200 1764 "-" "Mozilla/5.0"',
            ["/search?q=sleep+function+documentation", "200"],
            "The word sleep is part of a documentation search, not a timing payload.",
        ),
        (
            "v3-3-target-000005",
            '203.0.113.19 - - [21/May/2026:09:08:01 +0700] "GET /docs/database/information_schema_overview HTTP/1.1" 200 2239 "-" "Mozilla/5.0"',
            ["/docs/database/information_schema_overview", "200"],
            "The request is for database documentation and does not probe application data.",
        ),
        (
            "v3-3-target-000006",
            "2026-05-21T09:10:01+07:00 api=learning route=/training/sql-basics query=topic=selective-indexing src_ip=192.0.2.19 status=200",
            ["query=topic=selective-indexing", "status=200"],
            "The query value is normal training content and contains no injection syntax.",
        ),
        (
            "v3-3-target-000007",
            "2026-05-21T09:12:01+07:00 netflow: allowed monitoring check src=198.51.100.20 dst=192.0.2.20 dst_ports=443 unique_ports=1 window=60s",
            ["allowed monitoring check", "unique_ports=1"],
            "A single allowed monitoring check to one port is not reconnaissance.",
        ),
        (
            "v3-3-target-000008",
            "2026-05-21T09:14:01+07:00 asset-inventory: approved service enumeration job src=monitor-01 dst=192.0.2.21 unique_ports=2 banners_requested=false status=completed",
            ["approved service enumeration job", "banners_requested=false", "status=completed"],
            "This is an approved inventory job with limited ports and no banner collection.",
        ),
        (
            "v3-3-target-000009",
            "2026-05-21T09:16:01+07:00 ids: TLS fingerprint observed src=203.0.113.20 dst=192.0.2.22 dst_port=443 signature=ja3_known_client",
            ["TLS fingerprint observed", "signature=ja3_known_client"],
            "A known TLS client fingerprint on one service is not an Nmap scan.",
        ),
        (
            "v3-3-target-000010",
            "2026-05-21T09:18:01+07:00 firewall: allowed tcp connection src=198.51.100.21 dst=192.0.2.23 dst_ports=22 unique_ports=1 tcp_flags=SYN,ACK",
            ["allowed tcp connection", "unique_ports=1", "tcp_flags=SYN,ACK"],
            "The event shows one established connection, not a SYN scan across services.",
        ),
    ]
    return [
        record(
            row_id,
            log_line,
            triage_output(
                label="normal",
                severity="low",
                is_suspicious=False,
                evidence=evidence,
                reason=reason,
                recommended_action="No immediate action required. Continue normal monitoring.",
            ),
        )
        for row_id, log_line, evidence, reason in rows
    ]


def sql_injection_targeted_records() -> list[JsonObject]:
    rows = [
        (
            "v3-3-target-000011",
            "2026-05-21T10:00:01+07:00 app=web route=/login method=POST src_ip=198.51.100.31 username=admin' OR '1'='1 status=403",
            ["username=admin' OR '1'='1", "status=403"],
            "The login field contains a quoted OR tautology.",
        ),
        (
            "v3-3-target-000012",
            '203.0.113.31 - - [21/May/2026:10:02:01 +0700] "GET /search?q=%27%20OR%201%3D1-- HTTP/1.1" 400 622 "-" "sqlmap/1.8"',
            ["q=%27%20OR%201%3D1--", "sqlmap/1.8"],
            "The encoded query contains an OR tautology and SQL comment marker.",
        ),
        (
            "v3-3-target-000013",
            '192.0.2.31 - - [21/May/2026:10:04:01 +0700] "GET /products?id=5 UNION SELECT username,password FROM users-- HTTP/1.1" 500 911 "-" "Mozilla/5.0"',
            ["UNION SELECT username,password FROM users--", "500"],
            "The request includes a UNION SELECT statement against user data.",
        ),
        (
            "v3-3-target-000014",
            "2026-05-21T10:06:01+07:00 api-gateway: GET /api/orders?sort=name%20UNION%20SELECT%20card_number%20FROM%20payments src=203.0.113.32 status=500",
            ["sort=name%20UNION%20SELECT%20card_number%20FROM%20payments", "status=500"],
            "The encoded parameter attempts a UNION SELECT against payment data.",
        ),
        (
            "v3-3-target-000015",
            "2026-05-21T10:08:01+07:00 app=web route=/report method=GET src_ip=198.51.100.32 query=id=7 AND SLEEP(6) status=504 upstream_ms=6200",
            ["id=7 AND SLEEP(6)", "upstream_ms=6200"],
            "The query contains a timing-based SLEEP function.",
        ),
        (
            "v3-3-target-000016",
            '203.0.113.33 - - [21/May/2026:10:10:01 +0700] "GET /lookup?table=information_schema.columns HTTP/1.1" 403 490 "-" "Mozilla/5.0"',
            ["table=information_schema.columns", "403"],
            "The request probes database metadata through information_schema.",
        ),
        (
            "v3-3-target-000017",
            "2026-05-21T10:12:01+07:00 app=web route=/reset method=POST src_ip=192.0.2.32 email=' OR 'x'='x status=403",
            ["email=' OR 'x'='x", "status=403"],
            "The email field is replaced with a quoted tautology.",
        ),
        (
            "v3-3-target-000018",
            "2026-05-21T10:14:01+07:00 waf: blocked request src=198.51.100.33 uri=\"/account?id=1'/**/OR/**/'1'='1\" rule=sqli status=403",
            ["/account?id=1'/**/OR/**/'1'='1", "rule=sqli"],
            "The URI uses quotes and inline comments around an OR tautology.",
        ),
        (
            "v3-3-target-000019",
            '192.0.2.33 - - [21/May/2026:10:16:01 +0700] "GET /search?q=\\" UNION SELECT password FROM users-- HTTP/1.1" 500 533 "-" "Mozilla/5.0"',
            ['q=\\" UNION SELECT password FROM users--', "500"],
            "The request includes a quoted UNION SELECT payload.",
        ),
        (
            "v3-3-target-000020",
            "2026-05-21T10:18:01+07:00 api=customer route=/api/customer?id=42' AND 'a'='a src_ip=203.0.113.34 status=400",
            ["id=42' AND 'a'='a", "status=400"],
            "The id parameter contains a quoted AND tautology.",
        ),
    ]
    return [
        record(
            row_id,
            log_line,
            triage_output(
                label="sql_injection_attempt",
                severity="high",
                is_suspicious=True,
                evidence=evidence,
                reason=reason,
                recommended_action="Review web application logs and check whether the request reached the database layer.",
            ),
        )
        for row_id, log_line, evidence, reason in rows
    ]


def port_scan_targeted_records() -> list[JsonObject]:
    rows = [
        (
            "v3-3-target-000021",
            "2026-05-21T11:00:01+07:00 netflow: sequential connection attempts src=192.0.2.41 dst=203.0.113.41 dst_ports=21,22,23,25,80,443,8080 unique_ports=7 window=35s",
            "medium",
            ["sequential connection attempts", "unique_ports=7"],
            "The source attempted connections across many destination ports in a short window.",
        ),
        (
            "v3-3-target-000022",
            "2026-05-21T11:02:01+07:00 ids: nmap fingerprint from 198.51.100.41 to 192.0.2.42 probed_ports=22,80,443,3306 packets=118",
            "high",
            ["nmap fingerprint", "probed_ports=22,80,443,3306"],
            "The IDS identified Nmap-style probing across several services.",
        ),
        (
            "v3-3-target-000023",
            "2026-05-21T11:04:01+07:00 firewall: SYN scan detected src=203.0.113.41 dst=192.0.2.43 ports=135,139,445,3389 action=blocked",
            "high",
            ["SYN scan detected", "ports=135,139,445,3389"],
            "The firewall explicitly detected a SYN scan across Windows service ports.",
        ),
        (
            "v3-3-target-000024",
            "2026-05-21T11:06:01+07:00 ids: horizontal scan src=198.51.100.42 dst_subnet=192.0.2.0/24 dst_port=445 unique_hosts=27 window=90s",
            "high",
            ["horizontal scan", "unique_hosts=27"],
            "The source probed many hosts on the same service port.",
        ),
        (
            "v3-3-target-000025",
            "2026-05-21T11:08:01+07:00 ids: service enumeration src=203.0.113.42 dst=192.0.2.44 unique_ports=8 banners_requested=true protocols=ssh,http,smb,rdp",
            "medium",
            ["service enumeration", "unique_ports=8", "banners_requested=true"],
            "The event indicates service enumeration with banner collection.",
        ),
        (
            "v3-3-target-000026",
            "2026-05-21T11:10:01+07:00 netflow: probe burst src=192.0.2.42 dst=198.51.100.43 dst_ports=80,81,443,8000,8080,8443 unique_ports=6 window=20s",
            "medium",
            ["probe burst", "unique_ports=6"],
            "The flow shows a rapid probe across common web service ports.",
        ),
        (
            "v3-3-target-000027",
            "2026-05-21T11:12:01+07:00 ids: nmap fingerprint os_probe=true src=198.51.100.43 dst=203.0.113.43 probed_ports=22,111,2049,5900 packets=160",
            "high",
            ["nmap fingerprint", "os_probe=true", "probed_ports=22,111,2049,5900"],
            "The event reports Nmap fingerprinting with OS probing.",
        ),
        (
            "v3-3-target-000028",
            "2026-05-21T11:14:01+07:00 firewall: SYN scan detected src=203.0.113.43 dst=198.51.100.44 ports=25,110,143,465,587,993 action=blocked",
            "high",
            ["SYN scan detected", "ports=25,110,143,465,587,993"],
            "The source sent SYN probes across multiple mail service ports.",
        ),
        (
            "v3-3-target-000029",
            "2026-05-21T11:16:01+07:00 ids: horizontal scan src=192.0.2.43 dst_subnet=198.51.100.0/24 dst_port=3389 unique_hosts=31 window=120s",
            "high",
            ["horizontal scan", "unique_hosts=31"],
            "The source probed many hosts for remote desktop exposure.",
        ),
        (
            "v3-3-target-000030",
            "2026-05-21T11:18:01+07:00 ids: service enumeration src=198.51.100.44 dst=203.0.113.44 unique_ports=9 banners_requested=true user_agent=masscan-compatible",
            "high",
            ["service enumeration", "unique_ports=9", "masscan-compatible"],
            "The source enumerated services across many ports with scanner-like behavior.",
        ),
    ]
    return [
        record(
            row_id,
            log_line,
            triage_output(
                label="port_scan_or_recon",
                severity=severity,
                is_suspicious=True,
                evidence=evidence,
                reason=reason,
                recommended_action="Review network logs for additional reconnaissance from the source IP.",
            ),
        )
        for row_id, log_line, severity, evidence, reason in rows
    ]


def build_targeted_records() -> list[JsonObject]:
    return [
        *normal_targeted_records(),
        *sql_injection_targeted_records(),
        *port_scan_targeted_records(),
    ]


def label_counts(records: list[JsonObject]) -> dict[str, int]:
    counts = Counter(str(item["output"]["label"]) for item in records)
    return {label: counts[label] for label in LABELS}


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

    for item in records:
        validate_record(item)

    counts = label_counts(records)
    if counts != expected_counts:
        raise ValueError(f"{name}: expected labels {expected_counts}, got {counts}")

    format_split(records)


def build_weighted_targeted_records(targeted_records: list[JsonObject]) -> list[JsonObject]:
    weighted: list[JsonObject] = []
    for index, targeted_record in enumerate(targeted_records, start=1):
        label = str(targeted_record["output"]["label"])
        weight = TARGETED_LABEL_WEIGHTS[label]
        for repeat in range(weight):
            copy_record = copy.deepcopy(targeted_record)
            copy_record["id"] = f"{TARGETED_WEIGHTED_PREFIX}{index:03d}-{repeat + 1:02d}"
            weighted.append(copy_record)
    return weighted


def build_v3_3_split_records() -> tuple[list[JsonObject], list[JsonObject], list[JsonObject]]:
    base_train_records, validation_records = build_v3_1_split_records()
    targeted_records = build_targeted_records()
    weighted_targeted_records = build_weighted_targeted_records(targeted_records)
    train_plus_records = [*base_train_records, *weighted_targeted_records]

    validate_records(
        targeted_records,
        expected_count=30,
        expected_counts=EXPECTED_TARGETED_COUNTS,
        name="v3.3 targeted supplement",
    )
    validate_records(
        weighted_targeted_records,
        expected_count=50,
        expected_counts=EXPECTED_WEIGHTED_TARGETED_COUNTS,
        name="v3.3 weighted targeted supplement",
    )
    validate_records(
        train_plus_records,
        expected_count=550,
        expected_counts=EXPECTED_V3_3_TRAIN_COUNTS,
        name="v3.3 train",
    )
    validate_records(
        validation_records,
        expected_count=75,
        expected_counts=EXPECTED_VALIDATION_COUNTS,
        name="v3.3 validation",
    )

    base_ids = {str(item["id"]) for item in base_train_records}
    validation_ids = {str(item["id"]) for item in validation_records}
    targeted_ids = {str(item["id"]) for item in targeted_records}
    weighted_ids = {str(item["id"]) for item in weighted_targeted_records}

    if targeted_ids & base_ids:
        raise ValueError("v3.3 targeted ids overlap v3.1 base train ids")
    if weighted_ids & base_ids:
        raise ValueError("v3.3 weighted ids overlap v3.1 base train ids")
    if targeted_ids & validation_ids:
        raise ValueError("v3.3 targeted ids overlap validation ids")
    if weighted_ids & validation_ids:
        raise ValueError("v3.3 weighted ids overlap validation ids")

    train_ids = {str(item["id"]) for item in train_plus_records}
    if train_ids & validation_ids:
        raise ValueError("v3.3 train and validation records overlap")

    return train_plus_records, validation_records, targeted_records


def main() -> int:
    train_plus_records, validation_records, targeted_records = build_v3_3_split_records()

    write_jsonl(TARGETED_PATH, targeted_records)
    write_jsonl(TRAIN_PLUS_PATH, train_plus_records)
    write_jsonl(V3_3_TRAIN_PATH, train_plus_records)
    write_jsonl(V3_3_VALIDATION_PATH, validation_records)

    print(f"Wrote {len(targeted_records)} records to {TARGETED_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_plus_records)} records to {TRAIN_PLUS_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_plus_records)} records to {V3_3_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(validation_records)} records to {V3_3_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Base train source: {V3_1_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Validation source: {V3_1_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Train labels: {dict(sorted(label_counts(train_plus_records).items()))}")
    print(f"Validation labels: {dict(sorted(label_counts(validation_records).items()))}")
    print("Fixed test split was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
