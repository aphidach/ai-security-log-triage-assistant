# Phase 6 V3.5 Boundary Failure Slice

**Summary**

v3.5 slices the v3.4 temperature=0 hard-contrast failures so the next repair can target SQLi, traversal, invalid JSON, and brute-force gravity without using the fixed test split.

**Sources**

- `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-4-temp-0-hard-contrast-memorization-probe.json` for v3.4 temp 0 runtime probe predictions and metrics.
- `data/generated/v3-hard-contrast-security-triage.jsonl` for source log lines and expected outputs.
- `docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md` for the v3.4 result and v3.5 decision context.

**Last updated**

2026-05-22

## Run Snapshot

| Metric | Value |
| --- | ---: |
| Samples | `50` |
| Label failures | `16` |
| Label accuracy | `0.68` |
| JSON parse success | `0.98` |
| Schema success | `0.98` |
| Invalid outputs | `1` |
| Severity accuracy | `0.72` |
| Evidence partial match | `0.94` |

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
  "<invalid>": 1,
  "directory_traversal_attempt": 6,
  "failed_login_bruteforce": 19,
  "normal": 11,
  "port_scan_or_recon": 10,
  "sql_injection_attempt": 3
}
```

## Bucket Summary

| Bucket | Count | IDs | Diagnosis | Repair pattern |
| --- | ---: | --- | --- | --- |
| Normal -> brute force | `2` | `v3-hard-000001`, `v3-hard-000003` | Single failed-login events are still being treated as repeated guessing. | Add anti-gravity normal examples with failed_attempts=1, count=1, isolated 4625, single 401/403 responses, and no burst/correlation evidence. |
| Port/recon -> brute force | `2` | `v3-hard-000042`, `v3-hard-000049` | Reconnaissance signals are still pulled into brute force when wording is generic. | Add port/recon positives with nmap fingerprint, service enumeration, horizontal scan, unique_hosts/unique_ports thresholds, and blocked/attempt wording. |
| SQLi -> brute force | `4` | `v3-hard-000021`, `v3-hard-000023`, `v3-hard-000026`, `v3-hard-000029` | Login/API/status context still overrules clear SQL injection payloads. | Add SQLi positives in login, API, search, and reset-password contexts with 401/403/400/500 status codes, keeping quote tautologies, UNION, SLEEP/WAITFOR, stacked queries, and comment markers prominent. |
| SQLi -> invalid | `1` | `v3-hard-000030` | Quote-heavy SQLi evidence can still break JSON generation despite structured outputs. | Add quote-heavy SQLi examples and keep evidence as short exact substrings that require JSON escaping, then probe structured-output enforcement on the same shape. |
| SQLi -> normal | `1` | `v3-hard-000025` | Schema-discovery or SQL vocabulary is still underweighted in request-parameter context. | Add information_schema and encoded SQLi positives paired with benign documentation/search hard negatives that contain SQL words without payload boundaries. |
| SQLi -> traversal | `1` | `v3-hard-000028` | SQL quote/comment syntax is still confused with file/path injection syntax. | Add contrast pairs where SQL comment markers such as admin'-- are adjacent to traversal paths such as ../../etc/passwd and encoded ../ sequences. |
| Traversal -> brute force | `1` | `v3-hard-000040` | Status/blocking cues can still trigger the over-strong brute-force label. | Add traversal positives with 401/403/blocked wording and no authentication burst evidence. |
| Traversal -> normal | `2` | `v3-hard-000031`, `v3-hard-000038` | Sensitive path traversal tokens are underweighted when the log looks routine. | Add traversal positives with ../, encoded traversal, /etc/passwd, /etc/shadow, win.ini, secrets.yml, %00, and php://filter while preserving benign relative-path hard negatives. |
| Traversal -> port/recon | `2` | `v3-hard-000032`, `v3-hard-000034` | Status, user-agent, curl, and generic probing cues distract from traversal paths. | Add traversal positives with distracting curl/scanner-like user agents and blocked/404 status codes, keeping the sensitive path token prominent. |

## Failure Cases

| ID | Expected | Predicted | Bucket | Expected evidence | Predicted evidence | Repair cue |
| --- | --- | --- | --- | --- | --- | --- |
| `v3-hard-000001` | `normal` | `failed_login_bruteforce` | Normal -> brute force | Failed password; failed_attempts=1 | Failed password; failed_attempts=1 | Add anti-gravity normal examples with failed_attempts=1, count=1, isolated 4625, single 401/403 responses, and no burst/correlation evidence. |
| `v3-hard-000003` | `normal` | `failed_login_bruteforce` | Normal -> brute force | event_id=4625; count=1; status=failed_logon | event_id=4625; count=1 | Add anti-gravity normal examples with failed_attempts=1, count=1, isolated 4625, single 401/403 responses, and no burst/correlation evidence. |
| `v3-hard-000021` | `sql_injection_attempt` | `failed_login_bruteforce` | SQLi -> brute force | username=' OR '1'='1; status=403 | username=' OR '1'='1; status=403 | Add SQLi positives in login, API, search, and reset-password contexts with 401/403/400/500 status codes, keeping quote tautologies, UNION, SLEEP/WAITFOR, stacked queries, and comment markers prominent. |
| `v3-hard-000023` | `sql_injection_attempt` | `failed_login_bruteforce` | SQLi -> brute force | id=1 OR 1=1; status=400 | id=1 OR 1=1; status=400 | Add SQLi positives in login, API, search, and reset-password contexts with 401/403/400/500 status codes, keeping quote tautologies, UNION, SLEEP/WAITFOR, stacked queries, and comment markers prominent. |
| `v3-hard-000025` | `sql_injection_attempt` | `normal` | SQLi -> normal | information_schema.tables; 403 | information_schema.tables; 403 | Add information_schema and encoded SQLi positives paired with benign documentation/search hard negatives that contain SQL words without payload boundaries. |
| `v3-hard-000026` | `sql_injection_attempt` | `failed_login_bruteforce` | SQLi -> brute force | username=admin'--; status=401 | username=admin'--; status=401 | Add SQLi positives in login, API, search, and reset-password contexts with 401/403/400/500 status codes, keeping quote tautologies, UNION, SLEEP/WAITFOR, stacked queries, and comment markers prominent. |
| `v3-hard-000028` | `sql_injection_attempt` | `directory_traversal_attempt` | SQLi -> traversal | email=test@example.com' OR 'a'='a; status=403 | OR 'a'='a; status=403 | Add contrast pairs where SQL comment markers such as admin'-- are adjacent to traversal paths such as ../../etc/passwd and encoded ../ sequences. |
| `v3-hard-000029` | `sql_injection_attempt` | `failed_login_bruteforce` | SQLi -> brute force | filter=1;DROP TABLE audit_log--; status=500 | DROP TABLE audit_log--; status=500 | Add SQLi positives in login, API, search, and reset-password contexts with 401/403/400/500 status codes, keeping quote tautologies, UNION, SLEEP/WAITFOR, stacked queries, and comment markers prominent. |
| `v3-hard-000030` | `sql_injection_attempt` | `<invalid>` | SQLi -> invalid | q=\" OR \"1\"=\"1; 400 |  | Add quote-heavy SQLi examples and keep evidence as short exact substrings that require JSON escaping, then probe structured-output enforcement on the same shape. |
| `v3-hard-000031` | `directory_traversal_attempt` | `normal` | Traversal -> normal | ../config.yml; 403 | /download?file=../config.yml; 403 | Add traversal positives with ../, encoded traversal, /etc/passwd, /etc/shadow, win.ini, secrets.yml, %00, and php://filter while preserving benign relative-path hard negatives. |
| `v3-hard-000032` | `directory_traversal_attempt` | `port_scan_or_recon` | Traversal -> port/recon | ../../../etc/shadow; 404 | file=../../../etc/shadow; 404 | Add traversal positives with distracting curl/scanner-like user agents and blocked/404 status codes, keeping the sensitive path token prominent. |
| `v3-hard-000034` | `directory_traversal_attempt` | `port_scan_or_recon` | Traversal -> port/recon | /files/%2e%2e%2f%2e%2e%2fwindows%2fwin.ini; 403 | %2e%2e%2fwindows%2fwin.ini; 403 | Add traversal positives with distracting curl/scanner-like user agents and blocked/404 status codes, keeping the sensitive path token prominent. |
| `v3-hard-000038` | `directory_traversal_attempt` | `normal` | Traversal -> normal | ../../../../var/log/auth.log; 403 | ../../../../var/log/auth.log; 403 | Add traversal positives with ../, encoded traversal, /etc/passwd, /etc/shadow, win.ini, secrets.yml, %00, and php://filter while preserving benign relative-path hard negatives. |
| `v3-hard-000040` | `directory_traversal_attempt` | `failed_login_bruteforce` | Traversal -> brute force | /backup/../../secrets.yml; status=403 | status=403; secrets.yml | Add traversal positives with 401/403/blocked wording and no authentication burst evidence. |
| `v3-hard-000042` | `port_scan_or_recon` | `failed_login_bruteforce` | Port/recon -> brute force | nmap fingerprint; probed_ports=80,443,8080,8443 | ids=nmap fingerprint; probed_ports=80,443,8080,8443; packets=92 | Add port/recon positives with nmap fingerprint, service enumeration, horizontal scan, unique_hosts/unique_ports thresholds, and blocked/attempt wording. |
| `v3-hard-000049` | `port_scan_or_recon` | `failed_login_bruteforce` | Port/recon -> brute force | service enumeration; unique_ports=7; banners_requested=true | service enumeration; unique_ports=7; banners_requested=true | Add port/recon positives with nmap fingerprint, service enumeration, horizontal scan, unique_hosts/unique_ports thresholds, and blocked/attempt wording. |

## Dataset Implications

| Bucket | Target | Details |
| --- | ---: | --- |
| SQLi positives | 75 examples | Use login/API/search/reset contexts with 401/403/400/500, quote tautologies, UNION SELECT, SLEEP/WAITFOR, stacked queries, comment markers, encoded payloads, and quote-heavy evidence. |
| Traversal positives | 55 examples | Use ../, encoded %2e%2e, /etc/passwd, /etc/shadow, win.ini, secrets.yml, %00, php://filter, and distracting status/user-agent cues. |
| Normal hard negatives | 45 examples | Use single auth failures, isolated 4625, benign SQL docs/search terms, benign relative paths, allowlisted inventory, and low-scope monitoring. |
| Port/recon positives | 25 examples | Use nmap fingerprint, service enumeration, horizontal scan, unique_hosts/unique_ports, and blocked/attempt wording that should not become brute force. |
| No new brute-force positives | 0 examples | v3.5 should reduce brute-force gravity rather than further strengthening the label. |

## Hold Fixed Test

`data/splits/test.jsonl` remains held out and must not be used for selecting v3.5 repair cases or tuning prompts/runtime settings.

## Next Step

Create the v3.5 boundary repair supplement from these buckets, then train and probe v3.5 on hard-contrast before any mini semantic or fixed test comparison.
