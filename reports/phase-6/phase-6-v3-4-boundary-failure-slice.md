# Phase 6 V3.4 Boundary Failure Slice

**Summary**

This report slices the v3.3 temp 0.3 hard-contrast probe by label-boundary failure so v3.4 data repair can be targeted instead of guessed.

**Sources**

- `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json` for v3.3 runtime probe predictions and metrics.
- `data/generated/v3-hard-contrast-security-triage.jsonl` for source log lines and expected outputs.
- `docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md` for the v3.4 repair plan.

**Last updated**

2026-05-22

## Run Snapshot

| Metric | Value |
| --- | ---: |
| Samples | `50` |
| Label failures | `18` |
| Label accuracy | `0.64` |
| JSON parse success | `1.0` |
| Schema success | `1.0` |
| Invalid outputs | `0` |
| Severity accuracy | `0.7` |
| Evidence partial match | `0.94` |

Runtime context:

- model: `lfm2-security-triage-v3-3`
- response format: `structured_outputs` / `structured_outputs_json`
- prompt version: `triage-json-v2.1`
- request options: `{"temperature": 0.3, "top_p": 0.9}`
- extra body: `{"min_p": 0.15, "repetition_penalty": 1.05}`

Expected label distribution:

```json
{
  "directory_traversal_attempt": 10,
  "failed_login_bruteforce": 10,
  "normal": 10,
  "port_scan_or_recon": 10,
  "sql_injection_attempt": 10
}
```

Predicted label distribution:

```json
{
  "directory_traversal_attempt": 8,
  "failed_login_bruteforce": 20,
  "normal": 11,
  "port_scan_or_recon": 8,
  "sql_injection_attempt": 3
}
```

## Bucket Summary

| Bucket | Count | IDs | Diagnosis | Repair pattern |
| --- | ---: | --- | --- | --- |
| Normal -> brute force | `2` | `v3-hard-000001`, `v3-hard-000003` | The model treats failed-login vocabulary as sufficient evidence for brute force even when the log explicitly shows a single event. | Add brute-force anti-gravity normal examples with failed_attempts=1, count=1, isolated 4625, and paired burst examples where the count crosses the threshold. |
| SQLi -> brute force | `4` | `v3-hard-000021`, `v3-hard-000023`, `v3-hard-000024`, `v3-hard-000029` | The model notices login/API/status cues before the SQL payload, especially when the request is blocked with 401, 403, 400, or 500-like status signals. | Add SQLi positives inside login/API/search contexts with quote tautologies, UNION SELECT, SLEEP, stacked queries, and comment markers, including blocked status codes. |
| SQLi -> traversal | `2` | `v3-hard-000026`, `v3-hard-000028` | The model treats SQL comment markers and quoted values as a generic injection shape, then selects directory traversal instead of the SQL-specific label. | Add paired examples contrasting SQL comments such as admin'-- with traversal paths such as ../../etc/passwd and encoded ../ sequences. |
| SQLi -> normal/port | `2` | `v3-hard-000025`, `v3-hard-000030` | The model sometimes treats information_schema or OR payloads as benign search content or generic probing unless the attack boundary is very explicit. | Add clearer SQLi positives with encoded tautologies, schema discovery in request parameters, and hard negatives where select/union/sleep/information_schema are benign text. |
| Traversal boundary drift | `4` | `v3-hard-000031`, `v3-hard-000032`, `v3-hard-000034`, `v3-hard-000040` | Traversal is no longer the primary blocker, but several traversal cases are still being overruled by status, user-agent, encoding, or generic suspicious cues. | Add traversal positives that keep the sensitive path token prominent, plus hard negatives where ../ appears in benign normalized documentation paths. |
| Port/recon -> brute force | `3` | `v3-hard-000042`, `v3-hard-000046`, `v3-hard-000049` | The model still uses generic suspicious wording as a shortcut for brute force, even when the evidence is clearly network reconnaissance. | Add port/recon positives with nmap fingerprint, service enumeration, unique_ports>=10, horizontal scans, and many hosts/ports, paired with auth-failure negatives. |
| Port/recon -> normal | `1` | `v3-hard-000044` | The model underweights horizontal scan and unique host thresholds when the log lacks strong malicious wording. | Add contrast pairs for inventory/health checks versus horizontal scan, using explicit unique_hosts and unique_ports thresholds. |

## Failure Cases

| ID | Expected | Predicted | Bucket | Expected evidence | Predicted evidence | Repair cue |
| --- | --- | --- | --- | --- | --- | --- |
| `v3-hard-000001` | `normal` | `failed_login_bruteforce` | Normal -> brute force | Failed password; failed_attempts=1 | Failed password; failed_attempts=1 | Add brute-force anti-gravity normal examples with failed_attempts=1, count=1, isolated 4625, and paired burst examples where the count crosses the threshold. |
| `v3-hard-000003` | `normal` | `failed_login_bruteforce` | Normal -> brute force | event_id=4625; count=1; status=failed_logon | event_id=4625; count=1 | Add brute-force anti-gravity normal examples with failed_attempts=1, count=1, isolated 4625, and paired burst examples where the count crosses the threshold. |
| `v3-hard-000021` | `sql_injection_attempt` | `failed_login_bruteforce` | SQLi -> brute force | username=' OR '1'='1; status=403 | username=' OR '1'='1; status=403 | Add SQLi positives inside login/API/search contexts with quote tautologies, UNION SELECT, SLEEP, stacked queries, and comment markers, including blocked status codes. |
| `v3-hard-000023` | `sql_injection_attempt` | `failed_login_bruteforce` | SQLi -> brute force | id=1 OR 1=1; status=400 | id=1; status=400; status=1200 | Add SQLi positives inside login/API/search contexts with quote tautologies, UNION SELECT, SLEEP, stacked queries, and comment markers, including blocked status codes. |
| `v3-hard-000024` | `sql_injection_attempt` | `failed_login_bruteforce` | SQLi -> brute force | id=9 AND SLEEP(5); upstream_ms=6100 | id=9; and SLEEP(5) | Add SQLi positives inside login/API/search contexts with quote tautologies, UNION SELECT, SLEEP, stacked queries, and comment markers, including blocked status codes. |
| `v3-hard-000025` | `sql_injection_attempt` | `normal` | SQLi -> normal/port | information_schema.tables; 403 | query=information_schema.tables; 403 | Add clearer SQLi positives with encoded tautologies, schema discovery in request parameters, and hard negatives where select/union/sleep/information_schema are benign text. |
| `v3-hard-000026` | `sql_injection_attempt` | `directory_traversal_attempt` | SQLi -> traversal | username=admin'--; status=401 | username=admin'--; status=401 | Add paired examples contrasting SQL comments such as admin'-- with traversal paths such as ../../etc/passwd and encoded ../ sequences. |
| `v3-hard-000028` | `sql_injection_attempt` | `directory_traversal_attempt` | SQLi -> traversal | email=test@example.com' OR 'a'='a; status=403 | RESET_PASSWORD; OR 'A'='A; status=403 | Add paired examples contrasting SQL comments such as admin'-- with traversal paths such as ../../etc/passwd and encoded ../ sequences. |
| `v3-hard-000029` | `sql_injection_attempt` | `failed_login_bruteforce` | SQLi -> brute force | filter=1;DROP TABLE audit_log--; status=500 | DROP TABLE audit_log--; 1 | Add SQLi positives inside login/API/search contexts with quote tautologies, UNION SELECT, SLEEP, stacked queries, and comment markers, including blocked status codes. |
| `v3-hard-000030` | `sql_injection_attempt` | `port_scan_or_recon` | SQLi -> normal/port | q=\" OR \"1\"=\"1; 400 | OR; 1 | Add clearer SQLi positives with encoded tautologies, schema discovery in request parameters, and hard negatives where select/union/sleep/information_schema are benign text. |
| `v3-hard-000031` | `directory_traversal_attempt` | `normal` | Traversal boundary drift | ../config.yml; 403 | file=../config.yml; 403 | Add traversal positives that keep the sensitive path token prominent, plus hard negatives where ../ appears in benign normalized documentation paths. |
| `v3-hard-000032` | `directory_traversal_attempt` | `port_scan_or_recon` | Traversal boundary drift | ../../../etc/shadow; 404 | 404; curl/8.1 | Add traversal positives that keep the sensitive path token prominent, plus hard negatives where ../ appears in benign normalized documentation paths. |
| `v3-hard-000034` | `directory_traversal_attempt` | `sql_injection_attempt` | Traversal boundary drift | /files/%2e%2e%2f%2e%2e%2fwindows%2fwin.ini; 403 | %2e%2e%2f%2e%2e%2fwindows%2fwin.ini; 403; cannot be matched to any file type | Add traversal positives that keep the sensitive path token prominent, plus hard negatives where ../ appears in benign normalized documentation paths. |
| `v3-hard-000040` | `directory_traversal_attempt` | `failed_login_bruteforce` | Traversal boundary drift | /backup/../../secrets.yml; status=403 | status=403; bytes=0 | Add traversal positives that keep the sensitive path token prominent, plus hard negatives where ../ appears in benign normalized documentation paths. |
| `v3-hard-000042` | `port_scan_or_recon` | `failed_login_bruteforce` | Port/recon -> brute force | nmap fingerprint; probed_ports=80,443,8080,8443 | nmap fingerprint; probed_ports=80,443,8080,8443 | Add port/recon positives with nmap fingerprint, service enumeration, unique_ports>=10, horizontal scans, and many hosts/ports, paired with auth-failure negatives. |
| `v3-hard-000044` | `port_scan_or_recon` | `normal` | Port/recon -> normal | horizontal scan; unique_hosts=18 | horizontal scan; unique_hosts=18 | Add contrast pairs for inventory/health checks versus horizontal scan, using explicit unique_hosts and unique_ports thresholds. |
| `v3-hard-000046` | `port_scan_or_recon` | `failed_login_bruteforce` | Port/recon -> brute force | nmap fingerprint; probed_ports=135,139,445,3389 | ids=nmap fingerprint; probed_ports=135,139,445,3389 | Add port/recon positives with nmap fingerprint, service enumeration, unique_ports>=10, horizontal scans, and many hosts/ports, paired with auth-failure negatives. |
| `v3-hard-000049` | `port_scan_or_recon` | `failed_login_bruteforce` | Port/recon -> brute force | service enumeration; unique_ports=7; banners_requested=true | enumeration; banners_requested | Add port/recon positives with nmap fingerprint, service enumeration, unique_ports>=10, horizontal scans, and many hosts/ports, paired with auth-failure negatives. |

## Dataset Implications

| Bucket | Target | Details |
| --- | ---: | --- |
| SQLi positives | 35-45 examples | Use login/API/search contexts with explicit payloads: quote tautology, UNION SELECT, SLEEP, information_schema, SQL comment markers, encoded SQLi, and stacked query syntax. |
| SQLi hard negatives | 20-30 examples | Use select, union, sleep, schema, and information_schema in documentation, search, or admin contexts without attack payload boundaries. |
| Port/recon positives | 35-45 examples | Use nmap fingerprint, SYN scan detected, service enumeration, horizontal scan, unique_ports>=10, unique_hosts>=10, and short scan windows. |
| Port/recon hard negatives | 20-30 examples | Use authorized inventory, one-port monitoring, health checks, known scanner allowlists, and low unique port counts. |
| Brute-force anti-gravity negatives | 20-30 examples | Use failed, blocked, 401, 403, 4625, or attempt wording without repeated login burst; pair failed_attempts=1 with failed_attempts>=10. |

## Hold Fixed Test

data/splits/test.jsonl remains held out and must not be used for selecting repair cases or tuning prompts/runtime settings.

## Next Step

Create the v3.4 boundary repair supplement from these buckets, then train and probe v3.4 on hard-contrast and mini semantic splits before any fixed test comparison.
