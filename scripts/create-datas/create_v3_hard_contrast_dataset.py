#!/usr/bin/env python3
"""Create the Phase 6 v3 hard-contrast training supplement.

The file produced by this script is intentionally separate from the frozen
train/validation/test splits. It targets the semantic collapse seen in Phase 6.1
mini eval, where the model over-predicted failed_login_bruteforce.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_dataset import INSTRUCTION, LABELS, validate_record  # noqa: E402
from ml.unsloth.training_format import format_split  # noqa: E402


DEFAULT_OUTPUT_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"

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


def normal_records() -> list[JsonObject]:
    rows = [
        (
            "v3-hard-000001",
            "May 18 09:00:01 auth-01 sshd[2011]: Failed password for webapp from 192.0.2.44 port 51422 ssh2; failed_attempts=1",
            ["Failed password", "failed_attempts=1"],
            "A single failed SSH login is not enough to classify as brute force.",
            "Monitor for repeated failures from this source before escalating.",
        ),
        (
            "v3-hard-000002",
            "2026-05-18T09:02:10+07:00 app=auth event=login_failed user=svc_backup src_ip=198.51.100.24 failures=1 window=10m outcome=allowed_retry",
            ["event=login_failed", "failures=1", "outcome=allowed_retry"],
            "One failed application login with a normal retry outcome is not a brute force pattern.",
            "Continue normal monitoring and correlate only if repeated failures appear.",
        ),
        (
            "v3-hard-000003",
            "2026-05-18T09:04:30+07:00 winlog event_id=4625 host=ws-07 target_user=jdoe src_ip=203.0.113.74 count=1 status=failed_logon",
            ["event_id=4625", "count=1", "status=failed_logon"],
            "A single Windows failed logon event does not show repeated guessing.",
            "Monitor for additional failed logons from the same source or target account.",
        ),
        (
            "v3-hard-000004",
            '198.51.100.31 - - [18/May/2026:09:06:11 +0700] "GET /search?q=select+blueprints HTTP/1.1" 200 1420 "-" "Mozilla/5.0"',
            ["/search?q=select+blueprints", "200"],
            "The word select appears as ordinary search text, not SQL syntax.",
            "No immediate action required. Continue normal monitoring.",
        ),
        (
            "v3-hard-000005",
            '203.0.113.87 - - [18/May/2026:09:08:12 +0700] "GET /search?q=union+station+map HTTP/1.1" 200 1188 "-" "Mozilla/5.0"',
            ["/search?q=union+station+map", "200"],
            "The query uses union in a benign phrase and has no SQL injection operator.",
            "No immediate action required. Continue normal monitoring.",
        ),
        (
            "v3-hard-000006",
            '192.0.2.77 - - [18/May/2026:09:10:13 +0700] "GET /search?q=sleep+tracking+tips HTTP/1.1" 200 1764 "-" "Mozilla/5.0"',
            ["/search?q=sleep+tracking+tips", "200"],
            "The word sleep is part of a normal search query, not a timing payload.",
            "No immediate action required. Continue normal monitoring.",
        ),
        (
            "v3-hard-000007",
            '203.0.113.41 - - [18/May/2026:09:12:16 +0700] "GET /docs/../guide HTTP/1.1" 200 998 "-" "Mozilla/5.0"',
            ["/docs/../guide", "200"],
            "The normalized documentation route resolves inside expected content and returned successfully.",
            "No immediate action required unless similar requests target sensitive paths.",
        ),
        (
            "v3-hard-000008",
            "2026-05-18T09:14:22+07:00 firewall: allowed tcp connection from 198.51.100.66 to 192.0.2.10:443; session_count=1",
            ["allowed tcp connection", "session_count=1"],
            "A single allowed connection to one port is not reconnaissance.",
            "No immediate action required. Continue normal monitoring.",
        ),
        (
            "v3-hard-000009",
            "2026-05-18T09:16:48+07:00 api=inventory route=/api/items method=GET query=category=unionized-tools src_ip=192.0.2.98 status=200",
            ["query=category=unionized-tools", "status=200"],
            "The query value is a normal category string and does not contain SQL operators.",
            "No immediate action required. Continue normal monitoring.",
        ),
        (
            "v3-hard-000010",
            "May 18 09:18:19 vpn-01 openvpn[4419]: TLS handshake completed for user alice from 203.0.113.91; auth_failures=0",
            ["TLS handshake completed", "auth_failures=0"],
            "The VPN authentication completed successfully with no failed attempts.",
            "No immediate action required. Continue normal monitoring.",
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
                recommended_action=action,
            ),
        )
        for row_id, log_line, evidence, reason, action in rows
    ]


def brute_force_records() -> list[JsonObject]:
    rows = [
        (
            "v3-hard-000011",
            "May 18 09:00:05 auth-01 sshd[2012]: Failed password for webapp from 192.0.2.44 port 51422 ssh2; failed_attempts=12 window=3m",
            "high",
            ["Failed password", "failed_attempts=12", "window=3m"],
            "The log shows repeated SSH password failures in a short time window.",
        ),
        (
            "v3-hard-000012",
            "2026-05-18T09:02:14+07:00 app=auth event=login_failed user=svc_backup src_ip=198.51.100.24 failures=18 window=10m outcome=blocked",
            "high",
            ["event=login_failed", "failures=18", "outcome=blocked"],
            "The source generated many failed application logins and was blocked.",
        ),
        (
            "v3-hard-000013",
            "2026-05-18T09:04:35+07:00 winlog event_id=4625 host=ws-07 target_user=jdoe src_ip=203.0.113.74 count=16 status=failed_logon",
            "high",
            ["event_id=4625", "count=16", "status=failed_logon"],
            "Multiple Windows failed logon events indicate a brute force pattern.",
        ),
        (
            "v3-hard-000014",
            "2026-05-18T09:20:00+07:00 waf: POST /login src=203.0.113.108 status=401 repeated=24 window=120s user_agent=python-requests",
            "high",
            ["POST /login", "status=401 repeated=24", "python-requests"],
            "Repeated failed login responses from an automated client suggest brute force.",
        ),
        (
            "v3-hard-000015",
            "May 18 09:22:18 api-02 sshd[8842]: Failed password for root from 198.51.100.202 port 60111 ssh2; repeated 9 times in 2 minutes",
            "medium",
            ["Failed password", "repeated 9 times", "2 minutes"],
            "The source made repeated failed SSH attempts in a short period.",
        ),
        (
            "v3-hard-000016",
            "2026-05-18T09:24:44+07:00 app=auth event=password_guessing user=admin src_ip=192.0.2.190 failures=11 window=5m lockout=true",
            "medium",
            ["event=password_guessing", "failures=11", "lockout=true"],
            "The event explicitly reports password guessing with repeated failures.",
        ),
        (
            "v3-hard-000017",
            "2026-05-18T09:26:31+07:00 idp: login_failed user=analyst src_ip=203.0.113.51 attempts=14 unique_passwords=14 window=4m",
            "high",
            ["login_failed", "attempts=14", "unique_passwords=14"],
            "Many failed attempts with unique passwords indicate password guessing.",
        ),
        (
            "v3-hard-000018",
            "May 18 09:28:09 vpn-01 openvpn[5012]: auth failed for user deploy from 198.51.100.64; repeated=13 window=6m",
            "medium",
            ["auth failed", "repeated=13", "window=6m"],
            "The VPN log shows repeated authentication failures from one source.",
        ),
        (
            "v3-hard-000019",
            "2026-05-18T09:30:55+07:00 app=auth event=login_failed user=webapp src_ip=192.0.2.88 failures=31 window=15m outcome=rate_limited",
            "high",
            ["event=login_failed", "failures=31", "outcome=rate_limited"],
            "High-volume failed logins with rate limiting indicate brute force activity.",
        ),
        (
            "v3-hard-000020",
            "2026-05-18T09:32:12+07:00 siem correlation=auth_burst target_user=admin src_ip=203.0.113.199 failed_attempts=21 distinct_hosts=1",
            "high",
            ["auth_burst", "failed_attempts=21", "distinct_hosts=1"],
            "The correlation event reports a burst of failed authentication attempts.",
        ),
    ]
    return [
        record(
            row_id,
            log_line,
            triage_output(
                label="failed_login_bruteforce",
                severity=severity,
                is_suspicious=True,
                evidence=evidence,
                reason=reason,
                recommended_action="Review authentication logs for the source IP and consider blocking or rate-limiting it.",
            ),
        )
        for row_id, log_line, severity, evidence, reason in rows
    ]


def sql_injection_records() -> list[JsonObject]:
    rows = [
        (
            "v3-hard-000021",
            "2026-05-18T10:00:01+07:00 app=web route=/login method=POST src_ip=198.51.100.121 username=' OR '1'='1 status=403",
            ["username=' OR '1'='1", "status=403"],
            "The username field contains a tautology commonly used for SQL injection.",
        ),
        (
            "v3-hard-000022",
            '203.0.113.49 - - [18/May/2026:10:02:14 +0700] "GET /search?q=UNION SELECT username,password FROM users-- HTTP/1.1" 500 812 "-" "Mozilla/5.0"',
            ["UNION SELECT username,password FROM users--", "500"],
            "The search parameter contains a UNION SELECT payload.",
        ),
        (
            "v3-hard-000023",
            "2026-05-18T10:04:17+07:00 api-gateway: GET /api/users?id=1 OR 1=1 src=192.0.2.132 status=400 upstream_ms=1200",
            ["id=1 OR 1=1", "status=400"],
            "The API query contains a tautological SQL condition.",
        ),
        (
            "v3-hard-000024",
            "2026-05-18T10:06:44+07:00 api-gateway: GET /api/orders?id=9 AND SLEEP(5) src=198.51.100.88 status=500 upstream_ms=6100",
            ["id=9 AND SLEEP(5)", "upstream_ms=6100"],
            "The request includes a timing-based SQL injection function.",
        ),
        (
            "v3-hard-000025",
            '192.0.2.111 - - [18/May/2026:10:08:22 +0700] "GET /search?q=information_schema.tables HTTP/1.1" 403 640 "-" "Mozilla/5.0"',
            ["information_schema.tables", "403"],
            "The request probes database metadata through information_schema.",
        ),
        (
            "v3-hard-000026",
            "2026-05-18T10:10:15+07:00 app=web route=/login method=POST src_ip=203.0.113.155 username=admin'-- status=401",
            ["username=admin'--", "status=401"],
            "The login username includes a quote and SQL comment marker.",
        ),
        (
            "v3-hard-000027",
            '198.51.100.141 - - [18/May/2026:10:12:20 +0700] "GET /products?sort=name%27%20OR%20%271%27%3D%271 HTTP/1.1" 400 455 "-" "Mozilla/5.0"',
            ["name%27%20OR%20%271%27%3D%271", "400"],
            "The encoded parameter contains an OR tautology pattern.",
        ),
        (
            "v3-hard-000028",
            "2026-05-18T10:14:39+07:00 app=web route=/reset-password method=POST src_ip=192.0.2.56 email=test@example.com' OR 'a'='a status=403",
            ["email=test@example.com' OR 'a'='a", "status=403"],
            "The email field contains a quoted tautology.",
        ),
        (
            "v3-hard-000029",
            "2026-05-18T10:16:07+07:00 api-gateway: GET /api/report?filter=1;DROP TABLE audit_log-- src=203.0.113.167 status=500",
            ["filter=1;DROP TABLE audit_log--", "status=500"],
            "The request contains a destructive SQL statement and comment marker.",
        ),
        (
            "v3-hard-000030",
            '203.0.113.77 - - [18/May/2026:10:18:25 +0700] "GET /search?q=\\" OR \\"1\\"=\\"1 HTTP/1.1" 400 530 "-" "Mozilla/5.0"',
            ['q=\\" OR \\"1\\"=\\"1', "400"],
            "The request includes a quoted tautology in a query parameter.",
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


def traversal_records() -> list[JsonObject]:
    rows = [
        (
            "v3-hard-000031",
            '198.51.100.72 - - [18/May/2026:11:00:05 +0700] "GET /download?file=../config.yml HTTP/1.1" 403 210 "-" "curl/8.1"',
            ["../config.yml", "403"],
            "The request includes a parent-directory traversal sequence.",
        ),
        (
            "v3-hard-000032",
            '203.0.113.18 - - [18/May/2026:11:02:19 +0700] "GET /download?file=../../../etc/shadow HTTP/1.1" 404 1874 "-" "curl/8.1"',
            ["../../../etc/shadow", "404"],
            "The path attempts to reach a sensitive system file outside the web root.",
        ),
        (
            "v3-hard-000033",
            "2026-05-18T11:04:21+07:00 app=web route=/static/..%2f..%2fapp%2fsettings.py src_ip=192.0.2.133 status=404 bytes=109",
            ["/static/..%2f..%2fapp%2fsettings.py", "status=404"],
            "The route contains encoded parent-directory traversal.",
        ),
        (
            "v3-hard-000034",
            '192.0.2.172 - - [18/May/2026:11:06:33 +0700] "GET /files/%2e%2e%2f%2e%2e%2fwindows%2fwin.ini HTTP/1.1" 403 700 "-" "curl/8.1"',
            ["/files/%2e%2e%2f%2e%2e%2fwindows%2fwin.ini", "403"],
            "The URI uses encoded traversal to target a Windows file.",
        ),
        (
            "v3-hard-000035",
            "2026-05-18T11:08:11+07:00 waf: blocked request src=203.0.113.222 uri=\"/files/..\\..\\windows\\win.ini\" rule=path_traversal status=403",
            ["..\\..\\windows\\win.ini", "rule=path_traversal"],
            "The URI contains Windows-style directory traversal.",
        ),
        (
            "v3-hard-000036",
            "2026-05-18T11:10:48+07:00 waf: blocked request src=198.51.100.45 uri=\"/files/..%5c..%5cwindows%5cwin.ini\" rule=path_traversal status=400",
            ["..%5c..%5cwindows%5cwin.ini", "rule=path_traversal"],
            "The request uses encoded Windows path traversal.",
        ),
        (
            "v3-hard-000037",
            "2026-05-18T11:12:56+07:00 app=web route=/static/../../.env src_ip=203.0.113.72 status=403 bytes=892",
            ["/static/../../.env", "status=403"],
            "The static file request attempts to traverse to an environment file.",
        ),
        (
            "v3-hard-000038",
            '203.0.113.201 - - [18/May/2026:11:14:29 +0700] "GET /download?file=../../../../var/log/auth.log HTTP/1.1" 403 122 "-" "curl/8.1"',
            ["../../../../var/log/auth.log", "403"],
            "The requested path climbs out of the allowed directory toward log files.",
        ),
        (
            "v3-hard-000039",
            "2026-05-18T11:16:02+07:00 api=files action=open path=..%2f..%2f..%2fetc%2fpasswd src_ip=192.0.2.39 result=denied",
            ["path=..%2f..%2f..%2fetc%2fpasswd", "result=denied"],
            "The path parameter contains encoded traversal toward passwd.",
        ),
        (
            "v3-hard-000040",
            "2026-05-18T11:18:40+07:00 app=web route=/backup/../../secrets.yml src_ip=198.51.100.116 status=403 bytes=0",
            ["/backup/../../secrets.yml", "status=403"],
            "The request tries to access a secrets file via parent-directory traversal.",
        ),
    ]
    return [
        record(
            row_id,
            log_line,
            triage_output(
                label="directory_traversal_attempt",
                severity="high",
                is_suspicious=True,
                evidence=evidence,
                reason=reason,
                recommended_action="Review web server logs and verify that sensitive files were not returned.",
            ),
        )
        for row_id, log_line, evidence, reason in rows
    ]


def port_scan_records() -> list[JsonObject]:
    rows = [
        (
            "v3-hard-000041",
            "2026-05-18T12:00:11+07:00 netflow: sequential connection attempts src=192.0.2.205 dst=203.0.113.10 dst_ports=22,80,443,3389 unique_ports=4 window=45s",
            "medium",
            ["sequential connection attempts", "unique_ports=4"],
            "The flow shows sequential attempts across multiple destination ports.",
        ),
        (
            "v3-hard-000042",
            "2026-05-18T12:02:18+07:00 ids: nmap fingerprint from 198.51.100.61 to 203.0.113.224; probed_ports=80,443,8080,8443; packets=92",
            "high",
            ["nmap fingerprint", "probed_ports=80,443,8080,8443"],
            "The IDS identified an Nmap-like fingerprint and multiple probed ports.",
        ),
        (
            "v3-hard-000043",
            "2026-05-18T12:04:37+07:00 firewall: SYN scan detected src=198.51.100.105 dst=192.0.2.203 ports=80,443,8080 action=blocked",
            "high",
            ["SYN scan detected", "ports=80,443,8080"],
            "The firewall explicitly detected a SYN scan across several ports.",
        ),
        (
            "v3-hard-000044",
            "2026-05-18T12:06:22+07:00 ids: horizontal scan src=203.0.113.90 dst_subnet=192.0.2.0/24 dst_port=22 unique_hosts=18 window=60s",
            "high",
            ["horizontal scan", "unique_hosts=18"],
            "The source probed many hosts for the same service.",
        ),
        (
            "v3-hard-000045",
            "2026-05-18T12:08:53+07:00 netflow: probe burst src=192.0.2.61 dst=198.51.100.17 dst_ports=21,22,23,25,80,443 unique_ports=6 window=30s",
            "medium",
            ["probe burst", "unique_ports=6"],
            "The flow shows a burst against many destination ports.",
        ),
        (
            "v3-hard-000046",
            "2026-05-18T12:10:40+07:00 ids: nmap fingerprint from 203.0.113.120 to 198.51.100.77; probed_ports=135,139,445,3389; packets=140",
            "high",
            ["nmap fingerprint", "probed_ports=135,139,445,3389"],
            "The IDS recognized Nmap-like probing across Windows service ports.",
        ),
        (
            "v3-hard-000047",
            "2026-05-18T12:12:02+07:00 firewall: SYN scan detected src=192.0.2.144 dst=198.51.100.220 ports=25,110,143,587,993 action=blocked",
            "high",
            ["SYN scan detected", "ports=25,110,143,587,993"],
            "The firewall detected a SYN scan across multiple mail service ports.",
        ),
        (
            "v3-hard-000048",
            "2026-05-18T12:14:24+07:00 netflow: sequential connection attempts src=203.0.113.188 dst=192.0.2.51 dst_ports=80,443,8080,8443 unique_ports=4 window=20s",
            "medium",
            ["sequential connection attempts", "unique_ports=4"],
            "The flow records sequential attempts against several web ports.",
        ),
        (
            "v3-hard-000049",
            "2026-05-18T12:16:55+07:00 ids: service enumeration src=198.51.100.200 dst=203.0.113.11 unique_ports=7 banners_requested=true",
            "medium",
            ["service enumeration", "unique_ports=7", "banners_requested=true"],
            "The source appears to enumerate services and request banners.",
        ),
        (
            "v3-hard-000050",
            "2026-05-18T12:18:16+07:00 firewall: blocked recon src=192.0.2.199 dst=198.51.100.42 tcp_flags=SYN dst_ports=22,80,443,3306,5432 unique_ports=5",
            "medium",
            ["blocked recon", "tcp_flags=SYN", "unique_ports=5"],
            "The log shows blocked SYN probes across several common ports.",
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


def build_records() -> list[JsonObject]:
    return [
        *normal_records(),
        *brute_force_records(),
        *sql_injection_records(),
        *traversal_records(),
        *port_scan_records(),
    ]


def validate_records(records: list[JsonObject]) -> None:
    ids = [item["id"] for item in records]
    if len(ids) != len(set(ids)):
        raise ValueError("record ids must be unique")

    for item in records:
        validate_record(item)

    counts = Counter(item["output"]["label"] for item in records)
    for label in LABELS:
        if counts[label] != 10:
            raise ValueError(f"{label}: expected 10 hard-contrast records, got {counts[label]}")

    # Ensure the SFT formatter accepts the records and preserves the raw JSON assistant target.
    format_split(records)


def write_jsonl(path: Path, records: list[JsonObject]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")


def label_summary(records: list[JsonObject]) -> str:
    counts = Counter(item["output"]["label"] for item in records)
    return ", ".join(f"{label}={counts[label]}" for label in LABELS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create the Phase 6 v3 hard-contrast JSONL supplement.")
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output JSONL path. Default: {DEFAULT_OUTPUT_PATH}",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = args.out if args.out.is_absolute() else ROOT / args.out
    records = build_records()
    validate_records(records)
    write_jsonl(output_path, records)

    print(f"Wrote {len(records)} v3 hard-contrast records to {output_path.relative_to(ROOT)}")
    print(f"Labels: {label_summary(records)}")
    print("Validation: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
