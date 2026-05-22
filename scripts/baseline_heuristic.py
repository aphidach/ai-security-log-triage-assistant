#!/usr/bin/env python3
"""Rule-based baseline for the security log triage POC.

This script intentionally uses only Python's standard library. It gives Day 3 a
repeatable baseline that returns the same output schema as model adapters, so
later evaluation can compare a fine-tuned model against simple deterministic
rules.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


TriageOutput = dict[str, Any]

LOW_ACTION = "No immediate action required. Continue normal monitoring."


def triage_output(
    label: str,
    severity: str,
    is_suspicious: bool,
    evidence: list[str],
    reason: str,
    recommended_action: str,
) -> TriageOutput:
    return {
        "label": label,
        "severity": severity,
        "is_suspicious": is_suspicious,
        "evidence": evidence,
        "reason": reason,
        "recommended_action": recommended_action,
    }


def first_match(log_line: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, log_line, flags=re.IGNORECASE)
        if match:
            return match.group(1) if match.groups() else match.group(0)
    return None


def unique_evidence(items: list[str | None]) -> list[str]:
    evidence: list[str] = []
    for item in items:
        if item and item not in evidence:
            evidence.append(item)
    return evidence


def number_after(log_line: str, key: str) -> int | None:
    match = re.search(rf"{re.escape(key)}[=\s](\d+)", log_line, flags=re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def apache_status(log_line: str) -> str | None:
    match = re.search(r'HTTP/1\.1"\s+(\d{3})\b', log_line)
    if match:
        return match.group(1)
    return first_match(log_line, [r"\bstatus=(\d{3})\b"])


def analyze_sql_injection(log_line: str) -> TriageOutput | None:
    payload = first_match(
        log_line,
        [
            r"(username=[^\s]*'(?:--|\s+OR\s+'?1'?\s*=\s*'?1'?)\S*)",
            r"(username=%27%20OR%20[^ ]+)",
            r"((?:id|q)=[^ ]*\bUNION\s+SELECT\b[^ ]*(?:\s+[^ ]+)*?--)",
            r"((?:id|q)=\d+\s+OR\s+1\s*=\s*1\b)",
            r"((?:id|q)=[^ ]*\bOR\s+1\s*=\s*1\b)",
            r"((?:id|q)=[^ ]*\bAND\s+SLEEP\(\d+\))",
            r"((?:id|q)=[^ ]*SLEEP\(\d+\))",
            r"((?:id|q)=[^ ]*information_schema[^\s\"]*)",
            r"((?:id|q)=[^ ]*DROP\s+TABLE[^\"\s]*)",
            r"(%27%20OR%20%271%27%3D%271)",
            r"(%27%20OR%201%3D1--)",
            r"(' OR '1'='1)",
            r"(UNION\s+SELECT\s+[^\"\s]+(?:\s+[^\"\s]+)*?--)",
            r"(DROP\s+TABLE\s+\w+--)",
            r"(SLEEP\(\d+\))",
            r"(information_schema\.\w+)",
            r"(admin'--)",
        ],
    )
    if not payload:
        return None

    status = apache_status(log_line)
    evidence = unique_evidence([payload, f"status={status}" if "status=" in log_line and status else status])
    severity = "critical" if re.search(r"\bDROP\s+TABLE\b", payload, flags=re.IGNORECASE) else "high"
    return triage_output(
        "sql_injection_attempt",
        severity,
        True,
        evidence,
        "The log contains SQL syntax or encoded SQL operators in a user-controlled request field.",
        "Review related web and database logs for the source and verify whether the request reached sensitive query paths.",
    )


def analyze_directory_traversal(log_line: str) -> TriageOutput | None:
    payload = first_match(
        log_line,
        [
            r"(rule=path_traversal)",
            r"(GET\s+/download\?file=[^ ]+)",
            r"(/static/(?:\.\./|\.\.%2f|%2e%2e%2f)[^ ]+)",
            r"(/files/(?:\.\.\\|\.\.%5c|%2e%2e%5c)[^\"]+)",
            r"((?:\.\./){1,}[^ \"\t]+)",
            r"((?:\.\.\\){1,}[^ \"\t]+)",
            r"((?:\.\.%2f|%2e%2e%2f){1,}[^ \"\t]+)",
            r"((?:\.\.%5c|%2e%2e%5c){1,}[^ \"\t]+)",
        ],
    )
    if not payload:
        return None

    secondary = None
    if payload != "rule=path_traversal":
        secondary = first_match(log_line, [r"(rule=path_traversal)"])
    if secondary is None:
        status = apache_status(log_line)
        secondary = f"status={status}" if "status=" in log_line and status else status

    return triage_output(
        "directory_traversal_attempt",
        "high",
        True,
        unique_evidence([payload, secondary]),
        "The request contains parent-directory traversal sequences targeting files outside the intended path.",
        "Review web server and WAF logs to confirm the request was blocked and search for related attempts from the source.",
    )


def analyze_failed_login_bruteforce(log_line: str) -> TriageOutput | None:
    repeated = number_after(log_line, "repeated")
    failures = number_after(log_line, "failures")
    count = number_after(log_line, "count")

    if re.search(r"Failed password", log_line, flags=re.IGNORECASE) and repeated is not None:
        severity = "high" if repeated >= 12 else "medium"
        return triage_output(
            "failed_login_bruteforce",
            severity,
            True,
            unique_evidence(["Failed password", f"repeated {repeated} times"]),
            "The log shows repeated failed SSH authentication attempts in a short time window.",
            "Review authentication logs for the source IP and consider blocking or rate-limiting it.",
        )

    if "event=login_failed" in log_line and failures is not None:
        severity = "high" if failures >= 15 else "medium"
        return triage_output(
            "failed_login_bruteforce",
            severity,
            True,
            unique_evidence(["event=login_failed", f"failures={failures}", first_match(log_line, [r"(outcome=blocked)"])]),
            "The source generated many failed application login attempts.",
            "Review the account and source IP for password spraying or brute force activity.",
        )

    if "event_id=4625" in log_line and "status=failed_logon" in log_line and count is not None:
        severity = "high" if count >= 12 else "medium"
        return triage_output(
            "failed_login_bruteforce",
            severity,
            True,
            unique_evidence(["event_id=4625", f"count={count}", "status=failed_logon"]),
            "Multiple failed Windows logon events indicate a brute force pattern.",
            "Check whether the target account was locked and review related endpoint events.",
        )

    web_repeated = first_match(log_line, [r"(status=401 repeated=(\d+))"])
    if "POST /login" in log_line and web_repeated:
        repeated_count = number_after(log_line, "repeated") or 0
        severity = "high" if repeated_count >= 20 else "medium"
        return triage_output(
            "failed_login_bruteforce",
            severity,
            True,
            unique_evidence(["POST /login", f"status=401 repeated={repeated_count}", first_match(log_line, [r"(python-requests)"])]),
            "The log shows repeated failed login responses from one automated client.",
            "Review WAF and application logs for the source and consider temporary blocking.",
        )

    return None


def analyze_port_scan(log_line: str) -> TriageOutput | None:
    if "nmap fingerprint" in log_line:
        ports = first_match(log_line, [r"(probed_ports=[0-9,]+)"])
        return triage_output(
            "port_scan_or_recon",
            "high",
            True,
            unique_evidence(["nmap fingerprint", ports]),
            "The IDS identified an Nmap-like fingerprint and multiple probed ports.",
            "Investigate the source IP and check whether it touched other hosts.",
        )

    if "SYN scan detected" in log_line:
        ports = first_match(log_line, [r"(ports=[0-9,]+)"])
        return triage_output(
            "port_scan_or_recon",
            "medium",
            True,
            unique_evidence(["SYN scan detected", ports]),
            "The firewall detected connection attempts across multiple destination ports.",
            "Review network logs for additional reconnaissance from the source IP.",
        )

    if "sequential connection attempts" in log_line:
        unique_ports = first_match(log_line, [r"(unique_ports=\d+)"])
        return triage_output(
            "port_scan_or_recon",
            "medium",
            True,
            unique_evidence(["sequential connection attempts", unique_ports]),
            "The flow shows sequential attempts against several destination ports.",
            "Correlate with firewall and IDS logs to determine the scan scope.",
        )

    return None


def analyze_normal(log_line: str) -> TriageOutput:
    if "kube-probe" in log_line:
        request = first_match(log_line, [r"(GET\s+/(?:health|status|ready))"])
        return triage_output(
            "normal",
            "low",
            False,
            unique_evidence([request, apache_status(log_line), "kube-probe/1.29" if "kube-probe/1.29" in log_line else None]),
            "The request is a routine service health check with a successful response.",
            LOW_ACTION,
        )

    if "Successful login" in log_line:
        user = first_match(log_line, [r"(user\s+\S+)"])
        return triage_output(
            "normal",
            "low",
            False,
            unique_evidence(["Successful login", user]),
            "The log shows a successful authentication event without suspicious repetition.",
            LOW_ACTION,
        )

    if "failed_attempts=1" in log_line:
        return triage_output(
            "normal",
            "low",
            False,
            ["Failed password", "failed_attempts=1"],
            "A single failed authentication event is not enough to classify as brute force.",
            "Monitor for repeated failures from the same source before escalating.",
        )

    if "/search?q=" in log_line and apache_status(log_line) == "200":
        query = first_match(log_line, [r"(/search\?q=[^ ]+)"])
        return triage_output(
            "normal",
            "low",
            False,
            unique_evidence([query, "200"]),
            "The request completed successfully and does not contain a suspicious attack pattern.",
            LOW_ACTION,
        )

    if "allowed tcp connection" in log_line and "session_count=1" in log_line:
        return triage_output(
            "normal",
            "low",
            False,
            ["allowed tcp connection", "session_count=1"],
            "The log shows one allowed connection, not a scan across multiple ports.",
            LOW_ACTION,
        )

    return triage_output(
        "normal",
        "low",
        False,
        [log_line[:160] or "empty log input"],
        "No known suspicious pattern was matched by the heuristic baseline.",
        "Continue monitoring and correlate with surrounding logs if this event appears unusual.",
    )


def analyze_log(log_line: str) -> TriageOutput:
    """Classify one log line and return the shared triage output schema."""
    for analyzer in (
        analyze_sql_injection,
        analyze_directory_traversal,
        analyze_failed_login_bruteforce,
        analyze_port_scan,
    ):
        result = analyzer(log_line)
        if result is not None:
            return result
    return analyze_normal(log_line)


def iter_inputs(args: argparse.Namespace) -> list[str]:
    if args.input is not None:
        return [args.input]

    if args.file is not None:
        return [line.rstrip("\n") for line in args.file.read_text(encoding="utf-8").splitlines() if line.strip()]

    stdin_text = sys.stdin.read().strip()
    if not stdin_text:
        raise SystemExit("Provide --input, --file, or log text on stdin.")
    return [stdin_text]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the rule-based security log triage baseline.")
    parser.add_argument("--input", help="Single log line to classify.")
    parser.add_argument("--file", type=Path, help="Plain text file with one log line per line.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    indent = 2 if args.pretty else None
    for log_line in iter_inputs(args):
        print(json.dumps(analyze_log(log_line), ensure_ascii=False, sort_keys=True, indent=indent))


if __name__ == "__main__":
    main()
