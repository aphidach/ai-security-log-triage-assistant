# Phase 8 V4.2 SQLi Priority Diagnostic Slice

**Summary**

v4.2 slices the v4.1 hard-contrast label failures so the next repair can test SQLi label-priority prompt rules without adding training data or using the fixed test split.

**Sources**

- `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.json` for v4.1 temp 0 failures.
- `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-1-temp-03-2048-hard-contrast-memorization-probe.json` for v4.1 temp 0.3 failures.
- `data/generated/v3-hard-contrast-security-triage.jsonl` for source log lines and expected outputs.
- `docs/output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan.md` for v4.1 hold context.

**Last updated**

2026-05-22

## Probe Snapshots

| Probe | Samples | Label failures | Label accuracy | JSON/schema | Invalid | SQLi predicted traversal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `temp_0` | `50` | `6` | `0.88` | `1.0 / 1.0` | `0` | `2` |
| `temp_0_3` | `50` | `5` | `0.9` | `1.0 / 1.0` | `0` | `1` |

## Bucket Summary

### `temp_0`

| Bucket | Count | IDs | Diagnosis | Prompt repair pattern |
| --- | ---: | --- | --- | --- |
| Normal -> brute force | `2` | `v3-hard-000001`, `v3-hard-000003` | Single failed-auth events are still over-escalated without repeated attempts or short-window volume. | State that brute force needs repeated failures, a short window, many users, or many passwords; single failed logons remain normal monitoring cases. |
| SQLi -> normal | `1` | `v3-hard-000025` | Database schema-discovery tokens can still be treated as ordinary search traffic. | Give SQLi priority to information_schema, sqlite_master, and pg_catalog when they appear in request, query, body, search, or API fields. |
| SQLi -> port/recon | `1` | `v3-hard-000024` | Time-delay SQLi can drift into generic reconnaissance when the log includes API errors or latency. | State that SLEEP, pg_sleep, and WAITFOR DELAY are SQLi timing payloads unless explicit host, port, scan, or service-enumeration evidence is present. |
| SQLi -> traversal | `2` | `v3-hard-000026`, `v3-hard-000029` | SQL comments, stacked queries, and destructive SQL verbs can still be confused with file/path access. | State that SQL comments and ;DROP TABLE / ;SELECT should stay SQLi unless traversal tokens such as ../, /etc/passwd, win.ini, .env, WEB-INF, or php://filter are present. |

### `temp_0_3`

| Bucket | Count | IDs | Diagnosis | Prompt repair pattern |
| --- | ---: | --- | --- | --- |
| Normal -> brute force | `2` | `v3-hard-000001`, `v3-hard-000003` | Single failed-auth events are still over-escalated without repeated attempts or short-window volume. | State that brute force needs repeated failures, a short window, many users, or many passwords; single failed logons remain normal monitoring cases. |
| SQLi -> normal | `1` | `v3-hard-000025` | Database schema-discovery tokens can still be treated as ordinary search traffic. | Give SQLi priority to information_schema, sqlite_master, and pg_catalog when they appear in request, query, body, search, or API fields. |
| SQLi -> port/recon | `1` | `v3-hard-000024` | Time-delay SQLi can drift into generic reconnaissance when the log includes API errors or latency. | State that SLEEP, pg_sleep, and WAITFOR DELAY are SQLi timing payloads unless explicit host, port, scan, or service-enumeration evidence is present. |
| SQLi -> traversal | `1` | `v3-hard-000026` | SQL comments, stacked queries, and destructive SQL verbs can still be confused with file/path access. | State that SQL comments and ;DROP TABLE / ;SELECT should stay SQLi unless traversal tokens such as ../, /etc/passwd, win.ini, .env, WEB-INF, or php://filter are present. |

## Union Failures

Union failure ids: `v3-hard-000001`, `v3-hard-000003`, `v3-hard-000024`, `v3-hard-000025`, `v3-hard-000026`, `v3-hard-000029`

| ID | Expected | Evidence | Probe predictions |
| --- | --- | --- | --- |
| `v3-hard-000001` | `normal` | Failed password; failed_attempts=1 | temp_0: failed_login_bruteforce (normal_to_bruteforce); temp_0_3: failed_login_bruteforce (normal_to_bruteforce) |
| `v3-hard-000003` | `normal` | event_id=4625; count=1; status=failed_logon | temp_0: failed_login_bruteforce (normal_to_bruteforce); temp_0_3: failed_login_bruteforce (normal_to_bruteforce) |
| `v3-hard-000024` | `sql_injection_attempt` | id=9 AND SLEEP(5); upstream_ms=6100 | temp_0: port_scan_or_recon (sqli_to_port); temp_0_3: port_scan_or_recon (sqli_to_port) |
| `v3-hard-000025` | `sql_injection_attempt` | information_schema.tables; 403 | temp_0: normal (sqli_to_normal); temp_0_3: normal (sqli_to_normal) |
| `v3-hard-000026` | `sql_injection_attempt` | username=admin'--; status=401 | temp_0: directory_traversal_attempt (sqli_to_traversal); temp_0_3: directory_traversal_attempt (sqli_to_traversal) |
| `v3-hard-000029` | `sql_injection_attempt` | filter=1;DROP TABLE audit_log--; status=500 | temp_0: directory_traversal_attempt (sqli_to_traversal) |

## Prompt Diagnostic Rules

| Rule | Details |
| --- | --- |
| SQLi priority | Prioritize SQLi when SQL tokens appear in request/query/body/login fields: OR 1=1, quoted tautologies, SQL comments, SLEEP/pg_sleep/WAITFOR DELAY, information_schema/sqlite_master/pg_catalog, ;DROP TABLE, and ;SELECT. |
| Traversal guard | Traversal still needs file/path access cues such as ../, encoded traversal, /etc/passwd, win.ini, .env, WEB-INF, or php://filter. |
| Bruteforce guard | Brute force still needs repeated failures, a short window, or many users/passwords. |
| Recon guard | Recon still needs explicit scan, probing, enumeration, host, service, nmap, SYN scan, or multi-port evidence. |

## Hold Fixed Test

`data/splits/test.jsonl` must not be used for selecting v4.2 prompt rules or tuning runtime settings.

## No Training Artifacts

v4.2 does not create supplement data, train/validation splits, a LoRA config, or train allowlist entries.

## Next Step

Run hard-contrast probes against alias lfm2-security-triage-v4-1 with OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.2-sqli-priority before any mini semantic eval.
