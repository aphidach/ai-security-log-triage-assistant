# Phase 8 V4.1 SQLi Boundary Failure Slice

**Summary**

v4.1 slices the v4 hard-contrast failures at temp 0 and temp 0.3 so the next repair can focus narrowly on SQLi boundaries, especially SQLi mistaken for traversal, without using the fixed test split.

**Sources**

- `reports/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json` for v4 temp 0 failures.
- `reports/openai-compatible-vllm-structured-outputs-v4-temp-03-2048-hard-contrast-memorization-probe.json` for v4 temp 0.3 failures.
- `data/generated/v3-hard-contrast-security-triage.jsonl` for source log lines and expected outputs.
- `docs/output-structure-fix/phase-8-v4-sqli-boundary-repair-plan.md` for v4 hold context.

**Last updated**

2026-05-22

## Probe Snapshots

| Probe | Samples | Label failures | Label accuracy | JSON/schema | Invalid | SQLi predicted traversal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `temp_0` | `50` | `8` | `0.84` | `1.0 / 1.0` | `0` | `4` |
| `temp_0_3` | `50` | `8` | `0.84` | `1.0 / 1.0` | `0` | `5` |

## Bucket Summary

### `temp_0`

| Bucket | Count | IDs | Diagnosis | Repair pattern |
| --- | ---: | --- | --- | --- |
| Normal -> brute force | `2` | `v3-hard-000001`, `v3-hard-000003` | Single or isolated failed-auth events still look too much like threshold-based attacks. | Add normal auth negatives with failed_attempts=1, count=1, correlation=none, lockout=false, and no short burst window. |
| SQLi -> normal | `1` | `v3-hard-000025` | Schema-discovery SQLi can be mistaken for ordinary documentation or search traffic. | Add SQLi positives for information_schema, sqlite_master, pg_catalog, blocked status, and database-backed routes, paired with benign SQL documentation searches. |
| SQLi -> port/recon | `1` | `v3-hard-000024` | Time-delay/API error SQLi can drift into generic reconnaissance. | Add SLEEP, pg_sleep, WAITFOR, and upstream latency SQLi positives without port/host enumeration cues. |
| SQLi -> traversal | `4` | `v3-hard-000021`, `v3-hard-000023`, `v3-hard-000026`, `v3-hard-000029` | SQL quote/comment boundaries are still confused with file-read or traversal signals. | Add close SQLi-vs-traversal contrasts: SQL comments, quotes, tautologies, stacked queries, and schema names versus ../, /etc/passwd, win.ini, .env, and wrappers. |

### `temp_0_3`

| Bucket | Count | IDs | Diagnosis | Repair pattern |
| --- | ---: | --- | --- | --- |
| Normal -> brute force | `2` | `v3-hard-000001`, `v3-hard-000003` | Single or isolated failed-auth events still look too much like threshold-based attacks. | Add normal auth negatives with failed_attempts=1, count=1, correlation=none, lockout=false, and no short burst window. |
| SQLi -> normal | `1` | `v3-hard-000025` | Schema-discovery SQLi can be mistaken for ordinary documentation or search traffic. | Add SQLi positives for information_schema, sqlite_master, pg_catalog, blocked status, and database-backed routes, paired with benign SQL documentation searches. |
| SQLi -> traversal | `5` | `v3-hard-000021`, `v3-hard-000023`, `v3-hard-000024`, `v3-hard-000026`, `v3-hard-000029` | SQL quote/comment boundaries are still confused with file-read or traversal signals. | Add close SQLi-vs-traversal contrasts: SQL comments, quotes, tautologies, stacked queries, and schema names versus ../, /etc/passwd, win.ini, .env, and wrappers. |

## Union Failures

Union failure ids: `v3-hard-000001`, `v3-hard-000003`, `v3-hard-000021`, `v3-hard-000023`, `v3-hard-000024`, `v3-hard-000025`, `v3-hard-000026`, `v3-hard-000029`

| ID | Expected | Evidence | Probe predictions |
| --- | --- | --- | --- |
| `v3-hard-000001` | `normal` | Failed password; failed_attempts=1 | temp_0: failed_login_bruteforce (normal_to_bruteforce); temp_0_3: failed_login_bruteforce (normal_to_bruteforce) |
| `v3-hard-000003` | `normal` | event_id=4625; count=1; status=failed_logon | temp_0: failed_login_bruteforce (normal_to_bruteforce); temp_0_3: failed_login_bruteforce (normal_to_bruteforce) |
| `v3-hard-000021` | `sql_injection_attempt` | username=' OR '1'='1; status=403 | temp_0: directory_traversal_attempt (sqli_to_traversal); temp_0_3: directory_traversal_attempt (sqli_to_traversal) |
| `v3-hard-000023` | `sql_injection_attempt` | id=1 OR 1=1; status=400 | temp_0: directory_traversal_attempt (sqli_to_traversal); temp_0_3: directory_traversal_attempt (sqli_to_traversal) |
| `v3-hard-000024` | `sql_injection_attempt` | id=9 AND SLEEP(5); upstream_ms=6100 | temp_0: port_scan_or_recon (sqli_to_port); temp_0_3: directory_traversal_attempt (sqli_to_traversal) |
| `v3-hard-000025` | `sql_injection_attempt` | information_schema.tables; 403 | temp_0: normal (sqli_to_normal); temp_0_3: normal (sqli_to_normal) |
| `v3-hard-000026` | `sql_injection_attempt` | username=admin'--; status=401 | temp_0: directory_traversal_attempt (sqli_to_traversal); temp_0_3: directory_traversal_attempt (sqli_to_traversal) |
| `v3-hard-000029` | `sql_injection_attempt` | filter=1;DROP TABLE audit_log--; status=500 | temp_0: directory_traversal_attempt (sqli_to_traversal); temp_0_3: directory_traversal_attempt (sqli_to_traversal) |

## Dataset Implications

| Bucket | Target | Details |
| --- | ---: | --- |
| SQLi positives | 100 examples | Overweight bare and quoted tautologies, SQL comments, SLEEP/pg_sleep/WAITFOR, information_schema/sqlite_master/pg_catalog, and stacked queries. |
| Normal hard negatives | 24 examples | Keep normal guard examples focused on benign SQL searches and single auth failures. |
| Brute-force positives | 6 examples | Preserve threshold ownership with repeated failures, short windows, and spray cues. |
| Traversal positives | 16 examples | Keep true traversal/file-read tokens clearly separate from SQL comment syntax. |
| Port/recon positives | 4 examples | Use only clear service/host enumeration cues as a small recall guard. |

## Hold Fixed Test

`data/splits/test.jsonl` must not be used for selecting v4.1 repair cases or tuning prompts/runtime settings.

## Next Step

Create the v4.1 SQLi-boundary supplement on top of the v4 train split, then train from the base LFM2-350M model and run hard-contrast probes before any mini semantic eval.
