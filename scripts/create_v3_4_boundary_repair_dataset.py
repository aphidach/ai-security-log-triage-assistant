#!/usr/bin/env python3
"""Create Phase 6 v3.4 boundary repair data without fixed-test use.

The v3.4 supplement is built from the v3.3 failure slice. It targets three
semantic boundaries before any fixed split comparison:

- SQLi payloads in login/API/search contexts.
- Port/recon positives versus benign inventory and monitoring.
- Brute-force gravity, especially isolated failed-login events.
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

from scripts.create_v3_3_training_split import (  # noqa: E402
    V3_3_TRAIN_PATH,
    V3_3_VALIDATION_PATH,
    build_v3_3_split_records,
)
from scripts.generate_dataset import INSTRUCTION, LABELS, validate_record, write_jsonl  # noqa: E402
from ml.unsloth.training_format import format_split  # noqa: E402


SUPPLEMENT_PATH = ROOT / "data" / "generated" / "v3-4-boundary-repair-security-triage.jsonl"
TRAIN_PLUS_PATH = ROOT / "data" / "generated" / "train-plus-v3-4-boundary-repair.jsonl"
V3_4_TRAIN_PATH = ROOT / "data" / "splits" / "train-v3-4-boundary-repair.jsonl"
V3_4_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v3-4-boundary-repair.jsonl"

EXPECTED_SUPPLEMENT_COUNTS = {
    "normal": 60,
    "failed_login_bruteforce": 20,
    "sql_injection_attempt": 40,
    "directory_traversal_attempt": 0,
    "port_scan_or_recon": 40,
}
EXPECTED_V3_4_TRAIN_COUNTS = {
    "normal": 170,
    "failed_login_bruteforce": 120,
    "sql_injection_attempt": 160,
    "directory_traversal_attempt": 100,
    "port_scan_or_recon": 160,
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
            "phase": "phase-6-v3-4-boundary-repair",
            "repair_bucket": repair_bucket,
        },
    }


def make_id(index: int) -> str:
    return f"v3-4-boundary-{index:06d}"


def sqli_positive_records(start_index: int) -> list[JsonObject]:
    payloads = [
        ("username=admin' OR '1'='1", "The parameter contains a quoted OR tautology."),
        ("id=1 OR 1=1", "The parameter contains an OR tautology."),
        ("id=9 AND SLEEP(5)", "The parameter contains a time-based SLEEP payload."),
        ("filter=1;DROP TABLE audit_log--", "The parameter contains a stacked query and SQL comment marker."),
        ("q=information_schema.tables", "The request probes database metadata through information_schema."),
        ("email=test@example.com' OR 'a'='a", "The parameter contains a quoted tautology in an email field."),
        ("sort=name UNION SELECT password FROM users--", "The parameter contains a UNION SELECT clause."),
        ("account=42' AND 'x'='x", "The parameter contains a quoted AND tautology."),
        ("search=%27%20OR%20%271%27%3D%271--", "The request contains an encoded tautology and comment marker."),
        ("uri=/account?id=1'/**/OR/**/'1'='1", "The URI contains obfuscated OR tautology syntax."),
    ]
    context_templates = [
        "2026-05-22T10:{minute:02d}:01+07:00 app=web route=/login method=POST src_ip=198.51.100.{host} {payload} status=403",
        "2026-05-22T10:{minute:02d}:17+07:00 api-gateway: GET /api/items?{payload} src=203.0.113.{host} status=400",
        '192.0.2.{host} - - [22/May/2026:10:{minute:02d}:31 +0700] "GET /search?{payload} HTTP/1.1" 500 822 "-" "Mozilla/5.0"',
        '2026-05-22T10:{minute:02d}:45+07:00 waf: blocked request src=198.51.100.{host} {payload} rule=sqli status=403',
    ]

    rows: list[JsonObject] = []
    index = start_index
    for payload_index, (payload, reason) in enumerate(payloads):
        for context_index, template in enumerate(context_templates):
            status_evidence = "rule=sqli" if "rule=sqli" in template else "status=403" if "status=403" in template else "status=400" if "status=400" in template else "500"
            log_line = template.format(
                minute=payload_index * len(context_templates) + context_index,
                host=40 + index,
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
                        reason=reason,
                        recommended_action="Review web application logs and check whether the request reached the database layer.",
                    ),
                    repair_bucket="sqli_positive_boundary",
                )
            )
            index += 1
    return rows


def sqli_hard_negative_records(start_index: int) -> list[JsonObject]:
    benign_queries = [
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
    ]
    templates = [
        "2026-05-22T11:{minute:02d}:01+07:00 app=docs route=/search method=GET src_ip=203.0.113.{host} {query} status=200",
        "2026-05-22T11:{minute:02d}:31+07:00 app=training route=/lesson method=GET src_ip=198.51.100.{host} {query} status=200",
    ]

    rows: list[JsonObject] = []
    index = start_index
    for query_index, query in enumerate(benign_queries):
        for template_index, template in enumerate(templates):
            log_line = template.format(
                minute=query_index * len(templates) + template_index,
                host=40 + index,
                query=query,
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
                        reason="SQL-related words appear in ordinary documentation or training content without an injection payload.",
                        recommended_action="No immediate action required. Continue normal monitoring.",
                    ),
                    repair_bucket="sqli_hard_negative",
                )
            )
            index += 1
    return rows


def port_positive_records(start_index: int) -> list[JsonObject]:
    signals = [
        ("nmap fingerprint", "probed_ports=22,80,443,3306", "The IDS identified Nmap-style probing across several services."),
        ("SYN scan detected", "ports=135,139,445,3389", "The firewall detected a SYN scan across Windows service ports."),
        ("horizontal scan", "unique_hosts=24", "The source probed many hosts in a short window."),
        ("service enumeration", "unique_ports=12", "The event shows service enumeration across many ports."),
        ("probe burst", "unique_ports=18", "The source generated a rapid burst of probes across destination ports."),
        ("masscan-compatible", "unique_ports=22", "The user agent and high port count indicate scanner-like behavior."),
        ("tcp half-open scan", "unique_ports=16", "The flow shows half-open TCP probes across many ports."),
        ("udp service sweep", "unique_ports=14", "The source swept many UDP services."),
        ("banner grab", "banners_requested=true", "The event shows banner collection during service enumeration."),
        ("sequential port walk", "unique_ports=20", "The source walked sequential destination ports."),
    ]
    templates = [
        "2026-05-22T12:{minute:02d}:01+07:00 ids: {signal} src=198.51.100.{host} dst=203.0.113.{dst} {detail} window=45s action=blocked",
        "2026-05-22T12:{minute:02d}:17+07:00 firewall: {signal} src=203.0.113.{host} dst=192.0.2.{dst} {detail} packets=148",
        "2026-05-22T12:{minute:02d}:31+07:00 netflow: {signal} src=192.0.2.{host} dst=198.51.100.{dst} {detail} window=60s",
        "2026-05-22T12:{minute:02d}:45+07:00 siem: recon_alert type={signal} src=198.51.100.{host} target=192.0.2.{dst} {detail}",
    ]

    rows: list[JsonObject] = []
    index = start_index
    for signal_index, (signal, detail, reason) in enumerate(signals):
        for template_index, template in enumerate(templates):
            log_line = template.format(
                minute=signal_index * len(templates) + template_index,
                host=50 + index,
                dst=80 + index,
                signal=signal,
                detail=detail,
            )
            rows.append(
                record(
                    make_id(index),
                    log_line,
                    triage_output(
                        label="port_scan_or_recon",
                        severity="high" if signal in {"nmap fingerprint", "SYN scan detected", "masscan-compatible"} else "medium",
                        is_suspicious=True,
                        evidence=[signal, detail],
                        reason=reason,
                        recommended_action="Review network logs for additional reconnaissance from the source IP.",
                    ),
                    repair_bucket="port_recon_positive_boundary",
                )
            )
            index += 1
    return rows


def port_hard_negative_records(start_index: int) -> list[JsonObject]:
    benign_events = [
        ("approved inventory", "unique_ports=2", "approved=true"),
        ("health check", "unique_ports=1", "monitoring=true"),
        ("allowlisted scanner", "unique_ports=3", "allowlist=asset-inventory"),
        ("known TLS fingerprint", "dst_port=443", "signature=ja3_known_client"),
        ("one-port monitoring", "unique_ports=1", "dst_port=9100"),
        ("approved service check", "unique_ports=2", "change_ticket=CHG-2241"),
        ("load balancer probe", "unique_ports=1", "pool=web"),
        ("backup agent connection", "unique_ports=1", "agent=backupd"),
        ("database readiness probe", "unique_ports=1", "dst_port=5432"),
        ("authorized vulnerability scan", "unique_ports=4", "scanner=approved"),
    ]
    templates = [
        "2026-05-22T13:{minute:02d}:01+07:00 asset-inventory: {event} src=monitor-01 dst=192.0.2.{host} {detail} {extra} status=completed",
        "2026-05-22T13:{minute:02d}:31+07:00 netflow: {event} src=198.51.100.{host} dst=203.0.113.{dst} {detail} {extra} action=allowed",
    ]

    rows: list[JsonObject] = []
    index = start_index
    for event_index, (event, detail, extra) in enumerate(benign_events):
        for template_index, template in enumerate(templates):
            log_line = template.format(
                minute=event_index * len(templates) + template_index,
                host=50 + index,
                dst=80 + index,
                event=event,
                detail=detail,
                extra=extra,
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
                    repair_bucket="port_recon_hard_negative",
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
    templates = [
        "2026-05-22T14:{minute:02d}:01+07:00 auth: user=webapp src_ip=198.51.100.{host} {event} {detail} window=10m outcome=allowed_retry",
        "2026-05-22T14:{minute:02d}:31+07:00 idp: target_user=analyst src_ip=203.0.113.{host} {event} {detail} correlation=none",
    ]

    rows: list[JsonObject] = []
    index = start_index
    for event_index, (event, detail, reason) in enumerate(low_signal_events):
        for template_index, template in enumerate(templates):
            log_line = template.format(
                minute=event_index * len(templates) + template_index,
                host=50 + index,
                event=event,
                detail=detail,
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


def brute_threshold_positive_records(start_index: int) -> list[JsonObject]:
    burst_events = [
        ("Failed password", "failed_attempts=12", "Repeated SSH password failures indicate brute force."),
        ("event_id=4625", "count=16", "Multiple Windows failed logons indicate repeated guessing."),
        ("login_failed", "failures=18", "Many application login failures in one window indicate brute force."),
        ("status=401", "repeated=24", "Repeated 401 login responses suggest automated guessing."),
        ("auth_burst", "failed_attempts=21", "The correlation event reports an authentication burst."),
        ("password_guessing", "failures=11", "The event explicitly reports repeated password guessing."),
        ("vpn auth failed", "repeated=13", "Repeated VPN failures from one source are suspicious."),
        ("lockout=true", "failed_attempts=10", "A lockout after many failures suggests brute force."),
        ("rate_limited", "failures=31", "Rate limiting after many login failures indicates brute force."),
        ("password_spray", "unique_users=18", "Many users targeted by one source suggests password spraying."),
    ]
    templates = [
        "2026-05-22T15:{minute:02d}:01+07:00 auth: user=webapp src_ip=198.51.100.{host} {event} {detail} window=5m outcome=blocked",
        "2026-05-22T15:{minute:02d}:31+07:00 idp: target_user=admin src_ip=203.0.113.{host} {event} {detail} correlation=auth_burst",
    ]

    rows: list[JsonObject] = []
    index = start_index
    for event_index, (event, detail, reason) in enumerate(burst_events):
        for template_index, template in enumerate(templates):
            log_line = template.format(
                minute=event_index * len(templates) + template_index,
                host=50 + index,
                event=event,
                detail=detail,
            )
            rows.append(
                record(
                    make_id(index),
                    log_line,
                    triage_output(
                        label="failed_login_bruteforce",
                        severity="high",
                        is_suspicious=True,
                        evidence=[event, detail],
                        reason=reason,
                        recommended_action="Review authentication logs for the source IP and consider blocking or rate-limiting it.",
                    ),
                    repair_bucket="bruteforce_threshold_positive",
                )
            )
            index += 1
    return rows


def build_supplement_records() -> list[JsonObject]:
    records: list[JsonObject] = []
    for builder in (
        sqli_positive_records,
        sqli_hard_negative_records,
        port_positive_records,
        port_hard_negative_records,
        brute_antigravity_normal_records,
        brute_threshold_positive_records,
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


def build_v3_4_split_records() -> tuple[list[JsonObject], list[JsonObject], list[JsonObject]]:
    base_train_records, validation_records, _targeted_records = build_v3_3_split_records()
    supplement_records = build_supplement_records()
    train_plus_records = [*base_train_records, *strip_metadata(supplement_records)]

    validate_records(
        supplement_records,
        expected_count=160,
        expected_counts=EXPECTED_SUPPLEMENT_COUNTS,
        name="v3.4 boundary repair supplement",
    )
    validate_records(
        train_plus_records,
        expected_count=710,
        expected_counts=EXPECTED_V3_4_TRAIN_COUNTS,
        name="v3.4 train",
    )
    validate_records(
        validation_records,
        expected_count=75,
        expected_counts=EXPECTED_VALIDATION_COUNTS,
        name="v3.4 validation",
    )

    base_ids = {str(item["id"]) for item in base_train_records}
    validation_ids = {str(item["id"]) for item in validation_records}
    supplement_ids = {str(item["id"]) for item in supplement_records}

    if supplement_ids & base_ids:
        raise ValueError("v3.4 supplement ids overlap v3.3 base train ids")
    if supplement_ids & validation_ids:
        raise ValueError("v3.4 supplement ids overlap validation ids")

    train_ids = {str(item["id"]) for item in train_plus_records}
    if train_ids & validation_ids:
        raise ValueError("v3.4 train and validation records overlap")

    return train_plus_records, validation_records, supplement_records


def main() -> int:
    train_plus_records, validation_records, supplement_records = build_v3_4_split_records()
    clean_supplement_records = strip_metadata(supplement_records)

    write_jsonl(SUPPLEMENT_PATH, clean_supplement_records)
    write_jsonl(TRAIN_PLUS_PATH, train_plus_records)
    write_jsonl(V3_4_TRAIN_PATH, train_plus_records)
    write_jsonl(V3_4_VALIDATION_PATH, validation_records)

    print(f"Wrote {len(clean_supplement_records)} records to {SUPPLEMENT_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_plus_records)} records to {TRAIN_PLUS_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_plus_records)} records to {V3_4_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(validation_records)} records to {V3_4_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Base train source: {V3_3_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Validation source: {V3_3_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Supplement labels: {dict(sorted(label_counts(clean_supplement_records).items()))}")
    print(f"Supplement buckets: {metadata_counts(supplement_records)}")
    print(f"Train labels: {dict(sorted(label_counts(train_plus_records).items()))}")
    print(f"Validation labels: {dict(sorted(label_counts(validation_records).items()))}")
    print("Fixed test split was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
