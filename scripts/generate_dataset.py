#!/usr/bin/env python3
"""Generate the first synthetic security log triage dataset.

The generator is intentionally deterministic. It creates controlled examples for
the five-label POC taxonomy, validates the record contract, writes JSONL files,
and prints a compact summary for Day 2 verification.
"""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
GENERATED_PATH = ROOT / "data" / "generated" / "synthetic-security-triage.jsonl"
TRAIN_PATH = ROOT / "data" / "splits" / "train.jsonl"
VALIDATION_PATH = ROOT / "data" / "splits" / "validation.jsonl"
TEST_PATH = ROOT / "data" / "splits" / "test.jsonl"

SEED = 20260517
PER_LABEL = 100
TRAIN_PER_LABEL = 70
VALIDATION_PER_LABEL = 15
TEST_PER_LABEL = 15
INSTRUCTION = "Analyze this security log and classify whether it is suspicious."

LABELS = [
    "normal",
    "failed_login_bruteforce",
    "sql_injection_attempt",
    "directory_traversal_attempt",
    "port_scan_or_recon",
]

SEVERITIES = {"low", "medium", "high", "critical"}
OUTPUT_FIELDS = {
    "label",
    "severity",
    "is_suspicious",
    "evidence",
    "reason",
    "recommended_action",
}

USERS = [
    "admin",
    "root",
    "alice",
    "bob",
    "svc_backup",
    "deploy",
    "analyst",
    "webapp",
]
WEB_PATHS = [
    "/",
    "/health",
    "/login",
    "/api/users",
    "/api/orders",
    "/docs",
    "/status",
    "/search",
]
SQLI_PAYLOADS = [
    "' OR '1'='1",
    "UNION SELECT username,password FROM users--",
    "1; DROP TABLE users--",
    "SLEEP(5)",
    "information_schema.tables",
    "admin'--",
    "%27%20OR%20%271%27%3D%271",
]
TRAVERSAL_PAYLOADS = [
    "../../etc/passwd",
    "../../../etc/shadow",
    "..%2f..%2fetc%2fpasswd",
    "%2e%2e%2f%2e%2e%2fwindows%2fwin.ini",
    "..\\..\\windows\\win.ini",
    "../../../../var/log/auth.log",
]
PORT_SETS = [
    "21,22,23,25,80,443",
    "22,80,443,3389",
    "80,443,8080,8443",
    "135,139,445,3389",
    "25,110,143,587,993",
]


Record = dict[str, Any]
Template = Callable[[random.Random, int], Record]


def doc_ip(rng: random.Random) -> str:
    """Return an address from documentation-only IP ranges."""
    prefix = rng.choice(["192.0.2", "198.51.100", "203.0.113"])
    return f"{prefix}.{rng.randint(10, 240)}"


def hostname(rng: random.Random) -> str:
    return rng.choice(["web-01", "api-02", "auth-01", "fw-edge", "vpn-01"])


def user(rng: random.Random) -> str:
    return rng.choice(USERS)


def apache_ts(rng: random.Random, i: int) -> str:
    hour = 8 + (i % 12)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return f"17/May/2026:{hour:02d}:{minute:02d}:{second:02d} +0700"


def syslog_ts(rng: random.Random, i: int) -> str:
    hour = 8 + (i % 12)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return f"May 17 {hour:02d}:{minute:02d}:{second:02d}"


def iso_ts(rng: random.Random, i: int) -> str:
    hour = 8 + (i % 12)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return f"2026-05-17T{hour:02d}:{minute:02d}:{second:02d}+07:00"


def output(
    label: str,
    severity: str,
    is_suspicious: bool,
    evidence: list[str],
    reason: str,
    recommended_action: str,
) -> dict[str, Any]:
    return {
        "label": label,
        "severity": severity,
        "is_suspicious": is_suspicious,
        "evidence": evidence,
        "reason": reason,
        "recommended_action": recommended_action,
    }


def record(log_line: str, triage_output: dict[str, Any]) -> Record:
    return {
        "instruction": INSTRUCTION,
        "input": log_line,
        "output": triage_output,
    }


def normal_health_check(rng: random.Random, i: int) -> Record:
    path = rng.choice(["/health", "/status", "/ready"])
    log_line = (
        f'{doc_ip(rng)} - - [{apache_ts(rng, i)}] "GET {path} HTTP/1.1" '
        f'200 {rng.randint(64, 512)} "-" "kube-probe/1.29"'
    )
    return record(
        log_line,
        output(
            "normal",
            "low",
            False,
            [f"GET {path}", "200", "kube-probe/1.29"],
            "The request is a routine service health check with a successful response.",
            "No immediate action required. Continue normal monitoring.",
        ),
    )


def normal_successful_login(rng: random.Random, i: int) -> Record:
    selected_user = user(rng)
    src_ip = doc_ip(rng)
    log_line = (
        f"{syslog_ts(rng, i)} {hostname(rng)} app-auth: Successful login "
        f"for user {selected_user} from {src_ip} method=password"
    )
    return record(
        log_line,
        output(
            "normal",
            "low",
            False,
            ["Successful login", f"user {selected_user}"],
            "The log shows a successful authentication event without suspicious repetition.",
            "No immediate action required. Continue normal monitoring.",
        ),
    )


def normal_single_failed_login(rng: random.Random, i: int) -> Record:
    selected_user = user(rng)
    src_ip = doc_ip(rng)
    port = rng.randint(30000, 62000)
    log_line = (
        f"{syslog_ts(rng, i)} {hostname(rng)} sshd[{rng.randint(1000, 9999)}]: "
        f"Failed password for {selected_user} from {src_ip} port {port} ssh2; "
        "failed_attempts=1"
    )
    return record(
        log_line,
        output(
            "normal",
            "low",
            False,
            ["Failed password", "failed_attempts=1"],
            "A single failed authentication event is not enough to classify as brute force.",
            "Monitor for repeated failures from the same source before escalating.",
        ),
    )


def normal_search_query(rng: random.Random, i: int) -> Record:
    query = rng.choice(["select+book", "union+station", "sleep+tracking", "admin+guide"])
    log_line = (
        f'{doc_ip(rng)} - - [{apache_ts(rng, i)}] '
        f'"GET /search?q={query} HTTP/1.1" 200 {rng.randint(900, 2400)} '
        '"-" "Mozilla/5.0"'
    )
    return record(
        log_line,
        output(
            "normal",
            "low",
            False,
            [f"/search?q={query}", "200"],
            "The request contains ordinary search text and completed successfully.",
            "No immediate action required. Continue normal monitoring.",
        ),
    )


def normal_single_connection(rng: random.Random, i: int) -> Record:
    src_ip = doc_ip(rng)
    dst_ip = doc_ip(rng)
    port = rng.choice([22, 80, 443, 8080, 8443])
    log_line = (
        f"{iso_ts(rng, i)} firewall: allowed tcp connection from {src_ip} "
        f"to {dst_ip}:{port}; session_count=1"
    )
    return record(
        log_line,
        output(
            "normal",
            "low",
            False,
            ["allowed tcp connection", "session_count=1"],
            "The log shows one allowed connection, not a scan across multiple ports.",
            "No immediate action required. Continue normal monitoring.",
        ),
    )


def brute_force_ssh(rng: random.Random, i: int) -> Record:
    selected_user = rng.choice(["admin", "root", "deploy", "svc_backup"])
    count = rng.randint(7, 24)
    minutes = rng.randint(1, 5)
    src_ip = doc_ip(rng)
    log_line = (
        f"{syslog_ts(rng, i)} {hostname(rng)} sshd[{rng.randint(1000, 9999)}]: "
        f"Failed password for {selected_user} from {src_ip} "
        f"port {rng.randint(30000, 62000)} ssh2; repeated {count} times "
        f"in {minutes} minutes"
    )
    severity = "high" if count >= 12 else "medium"
    return record(
        log_line,
        output(
            "failed_login_bruteforce",
            severity,
            True,
            ["Failed password", f"repeated {count} times"],
            "The log shows repeated failed SSH authentication attempts in a short window.",
            "Review authentication logs for the source IP and consider blocking or rate-limiting it.",
        ),
    )


def brute_force_app(rng: random.Random, i: int) -> Record:
    selected_user = rng.choice(["admin", "alice", "svc_backup", "webapp"])
    count = rng.randint(8, 35)
    minutes = rng.randint(1, 10)
    src_ip = doc_ip(rng)
    log_line = (
        f"{iso_ts(rng, i)} app=auth event=login_failed user={selected_user} "
        f"src_ip={src_ip} failures={count} window={minutes}m outcome=blocked"
    )
    severity = "high" if count >= 15 else "medium"
    return record(
        log_line,
        output(
            "failed_login_bruteforce",
            severity,
            True,
            ["event=login_failed", f"failures={count}", "outcome=blocked"],
            "The source generated many failed login attempts and was blocked.",
            "Review the account and source IP for password spraying or brute force activity.",
        ),
    )


def brute_force_windows(rng: random.Random, i: int) -> Record:
    selected_user = rng.choice(["administrator", "backup_svc", "helpdesk", "jdoe"])
    count = rng.randint(6, 20)
    src_ip = doc_ip(rng)
    log_line = (
        f"{iso_ts(rng, i)} winlog event_id=4625 host={hostname(rng)} "
        f"target_user={selected_user} src_ip={src_ip} count={count} "
        "status=failed_logon"
    )
    severity = "high" if count >= 12 else "medium"
    return record(
        log_line,
        output(
            "failed_login_bruteforce",
            severity,
            True,
            ["event_id=4625", f"count={count}", "status=failed_logon"],
            "Multiple failed Windows logon events indicate a brute force pattern.",
            "Check whether the target account was locked and review related endpoint events.",
        ),
    )


def brute_force_web_401(rng: random.Random, i: int) -> Record:
    count = rng.randint(10, 40)
    src_ip = doc_ip(rng)
    log_line = (
        f"{iso_ts(rng, i)} waf: POST /login src={src_ip} "
        f"status=401 repeated={count} window=120s user_agent=python-requests"
    )
    severity = "high" if count >= 20 else "medium"
    return record(
        log_line,
        output(
            "failed_login_bruteforce",
            severity,
            True,
            ["POST /login", f"status=401 repeated={count}", "python-requests"],
            "The log shows repeated failed login responses from one automated client.",
            "Review WAF and application logs for the source and consider temporary blocking.",
        ),
    )


def sql_injection_search(rng: random.Random, i: int) -> Record:
    payload = rng.choice(SQLI_PAYLOADS)
    status = rng.choice([400, 403, 500])
    log_line = (
        f'{doc_ip(rng)} - - [{apache_ts(rng, i)}] '
        f'"GET /search?q={payload} HTTP/1.1" {status} {rng.randint(128, 2048)} '
        '"-" "Mozilla/5.0"'
    )
    severity = "critical" if "DROP TABLE" in payload else "high"
    return record(
        log_line,
        output(
            "sql_injection_attempt",
            severity,
            True,
            [payload, str(status)],
            "The request contains SQL syntax in a user-controlled search parameter.",
            "Review web application logs for the source IP and check whether the request reached the database layer.",
        ),
    )


def sql_injection_login(rng: random.Random, i: int) -> Record:
    payload = rng.choice(["admin'--", "' OR '1'='1", "%27%20OR%201%3D1--"])
    status = rng.choice([401, 403, 500])
    log_line = (
        f"{iso_ts(rng, i)} app=web route=/login method=POST "
        f"src_ip={doc_ip(rng)} username={payload} status={status}"
    )
    return record(
        log_line,
        output(
            "sql_injection_attempt",
            "high",
            True,
            [f"username={payload}", f"status={status}"],
            "The login parameter contains a common SQL injection authentication bypass pattern.",
            "Review application logs for similar payloads and verify whether authentication logic was affected.",
        ),
    )


def sql_injection_api(rng: random.Random, i: int) -> Record:
    payload = rng.choice(["id=1 OR 1=1", "id=5 UNION SELECT token FROM sessions--", "id=9 AND SLEEP(5)"])
    status = rng.choice([400, 500])
    log_line = (
        f"{iso_ts(rng, i)} api-gateway: GET /api/users?{payload} "
        f"src={doc_ip(rng)} status={status} upstream_ms={rng.randint(900, 6200)}"
    )
    return record(
        log_line,
        output(
            "sql_injection_attempt",
            "high",
            True,
            [payload, f"status={status}"],
            "The API request includes SQL operators or functions inside a query parameter.",
            "Inspect API logs and database query logs for related requests from the same source.",
        ),
    )


def directory_traversal_download(rng: random.Random, i: int) -> Record:
    payload = rng.choice(TRAVERSAL_PAYLOADS)
    status = rng.choice([400, 403, 404])
    log_line = (
        f'{doc_ip(rng)} - - [{apache_ts(rng, i)}] '
        f'"GET /download?file={payload} HTTP/1.1" {status} {rng.randint(128, 2048)} '
        '"-" "curl/8.1"'
    )
    return record(
        log_line,
        output(
            "directory_traversal_attempt",
            "high",
            True,
            [payload, f"GET /download?file={payload}"],
            "The requested file path contains parent-directory traversal sequences.",
            "Review web server logs and verify that sensitive files were not returned.",
        ),
    )


def directory_traversal_static(rng: random.Random, i: int) -> Record:
    payload = rng.choice(["../config.yml", "../../.env", "..%2f..%2fapp%2fsettings.py"])
    status = rng.choice([403, 404])
    log_line = (
        f"{iso_ts(rng, i)} app=web route=/static/{payload} "
        f"src_ip={doc_ip(rng)} status={status} bytes={rng.randint(0, 900)}"
    )
    return record(
        log_line,
        output(
            "directory_traversal_attempt",
            "high",
            True,
            [f"/static/{payload}", f"status={status}"],
            "The static file route includes traversal sequences targeting configuration files.",
            "Confirm the route rejected the request and search for other traversal attempts from the source.",
        ),
    )


def directory_traversal_windows(rng: random.Random, i: int) -> Record:
    payload = rng.choice(["..\\..\\windows\\win.ini", "..%5c..%5cwindows%5cwin.ini"])
    status = rng.choice([400, 403, 404])
    log_line = (
        f"{iso_ts(rng, i)} waf: blocked request src={doc_ip(rng)} "
        f'uri="/files/{payload}" rule=path_traversal status={status}'
    )
    return record(
        log_line,
        output(
            "directory_traversal_attempt",
            "high",
            True,
            [payload, "rule=path_traversal"],
            "The URI contains Windows-style directory traversal patterns.",
            "Review WAF and application logs to confirm the request was blocked.",
        ),
    )


def port_scan_firewall(rng: random.Random, i: int) -> Record:
    src_ip = doc_ip(rng)
    dst_ip = doc_ip(rng)
    ports = rng.choice(PORT_SETS)
    log_line = (
        f"{iso_ts(rng, i)} firewall: SYN scan detected src={src_ip} "
        f"dst={dst_ip} ports={ports} action=blocked"
    )
    return record(
        log_line,
        output(
            "port_scan_or_recon",
            "medium",
            True,
            ["SYN scan detected", f"ports={ports}"],
            "The firewall detected connection attempts across multiple destination ports.",
            "Review network logs for additional reconnaissance from the source IP.",
        ),
    )


def port_scan_ids(rng: random.Random, i: int) -> Record:
    src_ip = doc_ip(rng)
    dst_ip = doc_ip(rng)
    ports = rng.choice(PORT_SETS)
    log_line = (
        f"{iso_ts(rng, i)} ids: nmap fingerprint from {src_ip} to {dst_ip}; "
        f"probed_ports={ports}; packets={rng.randint(40, 180)}"
    )
    return record(
        log_line,
        output(
            "port_scan_or_recon",
            "high",
            True,
            ["nmap fingerprint", f"probed_ports={ports}"],
            "The IDS identified an Nmap-like fingerprint and multiple probed ports.",
            "Investigate the source IP and check whether it touched other hosts.",
        ),
    )


def port_scan_netflow(rng: random.Random, i: int) -> Record:
    src_ip = doc_ip(rng)
    dst_ip = doc_ip(rng)
    ports = rng.choice(PORT_SETS)
    unique_ports = len(ports.split(","))
    window = rng.randint(20, 90)
    log_line = (
        f"{iso_ts(rng, i)} netflow: sequential connection attempts src={src_ip} "
        f"dst={dst_ip} dst_ports={ports} unique_ports={unique_ports} window={window}s"
    )
    return record(
        log_line,
        output(
            "port_scan_or_recon",
            "medium",
            True,
            ["sequential connection attempts", f"unique_ports={unique_ports}"],
            "The flow shows sequential attempts against several destination ports.",
            "Correlate with firewall and IDS logs to determine the scan scope.",
        ),
    )


TEMPLATES: dict[str, list[Template]] = {
    "normal": [
        normal_health_check,
        normal_successful_login,
        normal_single_failed_login,
        normal_search_query,
        normal_single_connection,
    ],
    "failed_login_bruteforce": [
        brute_force_ssh,
        brute_force_app,
        brute_force_windows,
        brute_force_web_401,
    ],
    "sql_injection_attempt": [
        sql_injection_search,
        sql_injection_login,
        sql_injection_api,
    ],
    "directory_traversal_attempt": [
        directory_traversal_download,
        directory_traversal_static,
        directory_traversal_windows,
    ],
    "port_scan_or_recon": [
        port_scan_firewall,
        port_scan_ids,
        port_scan_netflow,
    ],
}


def generate_records() -> list[Record]:
    rng = random.Random(SEED)
    records: list[Record] = []
    next_id = 1

    for label in LABELS:
        templates = TEMPLATES[label]
        for i in range(PER_LABEL):
            template = templates[i % len(templates)]
            generated = template(rng, i)
            generated["id"] = f"sample-{next_id:06d}"
            records.append(generated)
            next_id += 1

    return records


def split_records(records: list[Record]) -> dict[str, list[Record]]:
    rng = random.Random(SEED + 1)
    by_label: dict[str, list[Record]] = defaultdict(list)
    for item in records:
        by_label[item["output"]["label"]].append(item)

    splits = {"train": [], "validation": [], "test": []}
    for label in LABELS:
        items = list(by_label[label])
        rng.shuffle(items)
        splits["train"].extend(items[:TRAIN_PER_LABEL])
        splits["validation"].extend(items[TRAIN_PER_LABEL : TRAIN_PER_LABEL + VALIDATION_PER_LABEL])
        splits["test"].extend(items[TRAIN_PER_LABEL + VALIDATION_PER_LABEL :])

    for items in splits.values():
        rng.shuffle(items)

    return splits


def validate_record(item: Record) -> None:
    required_record_fields = {"id", "instruction", "input", "output"}
    if set(item) != required_record_fields:
        raise ValueError(f"{item.get('id', '<missing>')}: record fields do not match contract")
    if not isinstance(item["id"], str) or not item["id"]:
        raise ValueError("record id must be a non-empty string")
    if item["instruction"] != INSTRUCTION:
        raise ValueError(f"{item['id']}: instruction changed")
    if not isinstance(item["input"], str) or not item["input"]:
        raise ValueError(f"{item['id']}: input must be a non-empty string")

    triage_output = item["output"]
    if not isinstance(triage_output, dict) or set(triage_output) != OUTPUT_FIELDS:
        raise ValueError(f"{item['id']}: output fields do not match schema")

    label = triage_output["label"]
    severity = triage_output["severity"]
    is_suspicious = triage_output["is_suspicious"]
    evidence = triage_output["evidence"]

    if label not in LABELS:
        raise ValueError(f"{item['id']}: unknown label {label}")
    if severity not in SEVERITIES:
        raise ValueError(f"{item['id']}: unknown severity {severity}")
    if not isinstance(is_suspicious, bool):
        raise ValueError(f"{item['id']}: is_suspicious must be boolean")
    if is_suspicious != (label != "normal"):
        raise ValueError(f"{item['id']}: suspicious flag does not match label")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError(f"{item['id']}: evidence must be a non-empty list")
    if len(evidence) > 3:
        raise ValueError(f"{item['id']}: evidence must contain at most three items")
    if not all(isinstance(entry, str) and entry for entry in evidence):
        raise ValueError(f"{item['id']}: every evidence entry must be a non-empty string")
    for entry in evidence:
        if len(entry) > 160:
            raise ValueError(f"{item['id']}: evidence entry must be 160 characters or fewer: {entry}")
        if entry not in item["input"]:
            raise ValueError(f"{item['id']}: evidence not found in input: {entry}")
    for field in ["reason", "recommended_action"]:
        if not isinstance(triage_output[field], str) or not triage_output[field]:
            raise ValueError(f"{item['id']}: {field} must be a non-empty string")


def validate_records(records: list[Record], splits: dict[str, list[Record]]) -> None:
    expected_total = PER_LABEL * len(LABELS)
    if len(records) != expected_total:
        raise ValueError(f"expected {expected_total} records, got {len(records)}")

    ids = [item["id"] for item in records]
    if len(set(ids)) != len(ids):
        raise ValueError("record ids must be unique")

    for item in records:
        validate_record(item)

    label_counts = Counter(item["output"]["label"] for item in records)
    for label in LABELS:
        if label_counts[label] != PER_LABEL:
            raise ValueError(f"{label}: expected {PER_LABEL}, got {label_counts[label]}")

    expected_split_sizes = {
        "train": TRAIN_PER_LABEL * len(LABELS),
        "validation": VALIDATION_PER_LABEL * len(LABELS),
        "test": TEST_PER_LABEL * len(LABELS),
    }
    split_ids: dict[str, set[str]] = {}
    for split_name, expected_size in expected_split_sizes.items():
        items = splits[split_name]
        if len(items) != expected_size:
            raise ValueError(f"{split_name}: expected {expected_size}, got {len(items)}")
        split_ids[split_name] = {item["id"] for item in items}
        split_counts = Counter(item["output"]["label"] for item in items)
        expected_per_label = expected_size // len(LABELS)
        for label in LABELS:
            if split_counts[label] != expected_per_label:
                raise ValueError(
                    f"{split_name}/{label}: expected {expected_per_label}, got {split_counts[label]}"
                )

    if split_ids["train"] & split_ids["validation"]:
        raise ValueError("train and validation splits overlap")
    if split_ids["train"] & split_ids["test"]:
        raise ValueError("train and test splits overlap")
    if split_ids["validation"] & split_ids["test"]:
        raise ValueError("validation and test splits overlap")

    combined_split_ids = split_ids["train"] | split_ids["validation"] | split_ids["test"]
    if combined_split_ids != set(ids):
        raise ValueError("splits do not cover the full dataset")


def write_jsonl(path: Path, records: list[Record]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")


def write_outputs(records: list[Record], splits: dict[str, list[Record]]) -> None:
    write_jsonl(GENERATED_PATH, records)
    write_jsonl(TRAIN_PATH, splits["train"])
    write_jsonl(VALIDATION_PATH, splits["validation"])
    write_jsonl(TEST_PATH, splits["test"])


def label_summary(records: list[Record]) -> str:
    counts = Counter(item["output"]["label"] for item in records)
    return ", ".join(f"{label}={counts[label]}" for label in LABELS)


def print_summary(records: list[Record], splits: dict[str, list[Record]]) -> None:
    print(f"Generated {len(records)} records with seed {SEED}.")
    print(f"Overall labels: {label_summary(records)}")
    for split_name in ["train", "validation", "test"]:
        items = splits[split_name]
        print(f"{split_name}: {len(items)} records ({label_summary(items)})")
    print("Validation: passed")
    print("Wrote:")
    for path in [GENERATED_PATH, TRAIN_PATH, VALIDATION_PATH, TEST_PATH]:
        print(f"- {path.relative_to(ROOT)}")


def main() -> None:
    records = generate_records()
    splits = split_records(records)
    validate_records(records, splits)
    write_outputs(records, splits)
    print_summary(records, splits)


if __name__ == "__main__":
    main()
