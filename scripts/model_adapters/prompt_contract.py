#!/usr/bin/env python3
"""Prompt contract used by Python model adapters."""

from __future__ import annotations

import argparse

TRIAGE_PROMPT_VERSION = "triage-json-v2.1"
SQLI_PRIORITY_PROMPT_VERSION = "triage-json-v2.2-sqli-priority"
PROMPT_VERSIONS = (TRIAGE_PROMPT_VERSION, SQLI_PRIORITY_PROMPT_VERSION)

TRIAGE_LABELS = (
    "normal",
    "failed_login_bruteforce",
    "sql_injection_attempt",
    "directory_traversal_attempt",
    "port_scan_or_recon",
)

TRIAGE_SEVERITIES = ("low", "medium", "high", "critical")

TRIAGE_OUTPUT_KEYS = (
    "label",
    "severity",
    "is_suspicious",
    "evidence",
    "reason",
    "recommended_action",
)

LABEL_DEFINITIONS = {
    "normal": "Routine or expected activity with no clear suspicious pattern.",
    "failed_login_bruteforce": (
        "Repeated failed authentication attempts suggesting password guessing or brute force activity."
    ),
    "sql_injection_attempt": (
        "Input contains SQL injection indicators such as tautologies, UNION queries, comments, "
        "or timing payloads."
    ),
    "directory_traversal_attempt": (
        "A path or request attempts to access files outside the intended directory."
    ),
    "port_scan_or_recon": "Activity suggests scanning, probing, enumeration, or reconnaissance.",
}

def _bullets(items: tuple[str, ...]) -> str:
    return "\n".join(f"- {item}" for item in items)


TRIAGE_SYSTEM_PROMPT = "\n".join(
    [
        "You are a security log triage assistant.",
        "Analyze exactly one security log input and classify it for investigation.",
        "Use triage language only. Do not claim that a system is compromised.",
        "",
        "Return only one valid JSON object.",
        "The response must start with { and end with }.",
        "Do not include markdown, code fences, comments, or explanatory text outside JSON.",
        "Do not repeat the prompt or mention the schema outside the JSON object.",
        "Do not add fields beyond the required schema.",
        "Always include every required field, including recommended_action.",
        "",
        "Required output fields:",
        _bullets(TRIAGE_OUTPUT_KEYS),
        "",
        "Allowed labels:",
        "\n".join(f"- {label}: {LABEL_DEFINITIONS[label]}" for label in TRIAGE_LABELS),
        "Choose exactly one label. If no listed suspicious pattern is present, use normal.",
        "",
        "Allowed severity values:",
        _bullets(TRIAGE_SEVERITIES),
        "Set is_suspicious to false only for normal. Set it to true for every other label.",
        "",
        "Evidence rules:",
        "- evidence must contain one to three short exact substrings copied from the input log.",
        "- Each evidence item must be 1 to 160 characters.",
        "- Do not use label names or invent evidence that is not present in the input.",
        "- For normal activity, cite the log detail that makes it routine or expected.",
        "",
        "Default severity guidance:",
        "- normal: low",
        "- failed_login_bruteforce: medium, or high when the repeated failure volume is clearly large.",
        "- sql_injection_attempt: high",
        "- directory_traversal_attempt: high",
        "- port_scan_or_recon: medium, or high when the scan is explicit or broad.",
    ]
)

SQLI_PRIORITY_RULES = "\n".join(
    [
        "",
        "SQLi priority rules:",
        "- If a request, query parameter, body field, username, search term, filter, or API argument contains SQL injection cues, choose sql_injection_attempt even when the surrounding route is login, search, API, error, or blocked traffic.",
        "- SQL injection cues include OR 1=1, quoted tautologies such as ' OR '1'='1, SQL comments such as '--, --, or /* */, timing payloads such as SLEEP, pg_sleep, or WAITFOR DELAY, schema discovery such as information_schema, sqlite_master, or pg_catalog, and stacked statements such as ;DROP TABLE or ;SELECT.",
        "- A SQL comment marker or destructive SQL verb is not directory traversal unless file/path access evidence is also present.",
        "- A timing SQL payload such as SLEEP or pg_sleep is not port scan or recon unless explicit host, port, service, scan, or enumeration evidence is present.",
        "- A login or failed-auth context is not brute force unless repeated failures, a short window, many users, or many password attempts are present.",
        "- Traversal requires file or path access evidence such as ../, encoded traversal, /etc/passwd, win.ini, .env, WEB-INF, or php://filter.",
        "- Recon requires explicit scanning, probing, enumeration, many ports, many hosts, nmap, SYN scan, or service discovery evidence.",
    ]
)

TRIAGE_SYSTEM_PROMPT_V2_2_SQLI_PRIORITY = TRIAGE_SYSTEM_PROMPT + SQLI_PRIORITY_RULES


def get_triage_system_prompt(prompt_version: str = TRIAGE_PROMPT_VERSION) -> str:
    if prompt_version == TRIAGE_PROMPT_VERSION:
        return TRIAGE_SYSTEM_PROMPT
    if prompt_version == SQLI_PRIORITY_PROMPT_VERSION:
        return TRIAGE_SYSTEM_PROMPT_V2_2_SQLI_PRIORITY
    raise ValueError(f"Unsupported triage prompt version: {prompt_version}")


def validate_triage_prompt_version(prompt_version: str) -> str:
    if prompt_version not in PROMPT_VERSIONS:
        raise ValueError(f"prompt_version must be one of: {', '.join(PROMPT_VERSIONS)}")
    return prompt_version


def build_triage_user_prompt(log_line: str) -> str:
    return "\n".join(
        [
            "Analyze this security log and classify whether it is suspicious.",
            "Respond with the JSON object only.",
            "",
            "Log:",
            log_line,
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print the triage prompt contract used by model adapters.",
    )
    parser.add_argument(
        "--kind",
        choices=("system", "version", "user"),
        default="system",
        help="Prompt contract value to print. Default: system.",
    )
    parser.add_argument(
        "--log-line",
        default="",
        help="Security log line to use when --kind=user.",
    )
    parser.add_argument(
        "--prompt-version",
        choices=PROMPT_VERSIONS,
        default=TRIAGE_PROMPT_VERSION,
        help=f"System prompt profile to print when --kind=system. Default: {TRIAGE_PROMPT_VERSION}.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.kind == "version":
        print(TRIAGE_PROMPT_VERSION)
        return 0

    if args.kind == "user":
        if not args.log_line:
            raise SystemExit("--log-line is required when --kind=user")
        print(build_triage_user_prompt(args.log_line))
        return 0

    print(get_triage_system_prompt(args.prompt_version))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
