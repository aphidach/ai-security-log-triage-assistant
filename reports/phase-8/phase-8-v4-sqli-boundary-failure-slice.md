# Phase 8 V4 SQLi Boundary Failure Slice

**Summary**

v4 slices the v3.5 temperature=0 2048-token hard-contrast failures so the next repair can target SQLi/quote boundaries while preserving normal/brute-force guards without using the fixed test split.

**Sources**

- `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-5-temp-0-2048-hard-contrast-memorization-probe.json` for v3.5 temp 0 2048 runtime probe predictions and metrics.
- `data/generated/v3-hard-contrast-security-triage.jsonl` for source log lines and expected outputs.
- `docs/output-structure-fix/phase-6-v3-5-boundary-repair-plan.md` for v3.5 closure context.
- `reports/phase-7/comparison.md` for Phase 7 historical context, not tuning examples.

**Last updated**

2026-05-22

## Run Snapshot

| Metric | Value |
| --- | ---: |
| Samples | `50` |
| Label failures | `8` |
| Label accuracy | `0.84` |
| JSON parse success | `0.98` |
| Schema success | `0.98` |
| Invalid outputs | `1` |
| Severity accuracy | `0.82` |
| Evidence partial match | `0.98` |

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
  "directory_traversal_attempt": 14,
  "failed_login_bruteforce": 12,
  "normal": 9,
  "port_scan_or_recon": 10,
  "sql_injection_attempt": 4
}
```

## Bucket Summary

| Bucket | Count | IDs | Diagnosis | Repair pattern |
| --- | ---: | --- | --- | --- |
| Normal -> brute force | `2` | `v3-hard-000001`, `v3-hard-000003` | Single failed-login or low-signal auth events can still be escalated. | Add normal guard examples with failed_attempts=1, repeated=1, count=1, lockout=false, correlation=none, and no burst window. |
| SQLi -> invalid | `1` | `v3-hard-000030` | Quote-heavy SQLi evidence can still break deterministic structured output. | Add quote-heavy SQLi positives with evidence substrings that require JSON escaping, but keep each evidence item short and exact. |
| SQLi -> normal | `1` | `v3-hard-000025` | SQL vocabulary or schema discovery can be underweighted in routine-looking logs. | Add SQLi positives with information_schema, encoded tautologies, and SQL comments, paired with benign SQL documentation/search hard negatives. |
| SQLi -> traversal | `4` | `v3-hard-000023`, `v3-hard-000024`, `v3-hard-000026`, `v3-hard-000029` | SQL quote/comment syntax is still confused with path traversal/file-read syntax. | Add SQLi-vs-traversal contrast examples where SQL comment markers, UNION, SLEEP, WAITFOR, and encoded quotes are separate from ../, /etc/passwd, and php://filter. |

## Failure Cases

| ID | Expected | Predicted | Bucket | Expected evidence | Predicted evidence | Repair cue |
| --- | --- | --- | --- | --- | --- | --- |
| `v3-hard-000001` | `normal` | `failed_login_bruteforce` | Normal -> brute force | Failed password; failed_attempts=1 | Failed password; failed_attempts=1 | Add normal guard examples with failed_attempts=1, repeated=1, count=1, lockout=false, correlation=none, and no burst window. |
| `v3-hard-000003` | `normal` | `failed_login_bruteforce` | Normal -> brute force | event_id=4625; count=1; status=failed_logon | event_id=4625; count=1 | Add normal guard examples with failed_attempts=1, repeated=1, count=1, lockout=false, correlation=none, and no burst window. |
| `v3-hard-000023` | `sql_injection_attempt` | `directory_traversal_attempt` | SQLi -> traversal | id=1 OR 1=1; status=400 | id=1 OR 1=1; status=400 | Add SQLi-vs-traversal contrast examples where SQL comment markers, UNION, SLEEP, WAITFOR, and encoded quotes are separate from ../, /etc/passwd, and php://filter. |
| `v3-hard-000024` | `sql_injection_attempt` | `directory_traversal_attempt` | SQLi -> traversal | id=9 AND SLEEP(5); upstream_ms=6100 | id=9 AND SLEEP(5); status=500 | Add SQLi-vs-traversal contrast examples where SQL comment markers, UNION, SLEEP, WAITFOR, and encoded quotes are separate from ../, /etc/passwd, and php://filter. |
| `v3-hard-000025` | `sql_injection_attempt` | `normal` | SQLi -> normal | information_schema.tables; 403 | information_schema.tables; 403 | Add SQLi positives with information_schema, encoded tautologies, and SQL comments, paired with benign SQL documentation/search hard negatives. |
| `v3-hard-000026` | `sql_injection_attempt` | `directory_traversal_attempt` | SQLi -> traversal | username=admin'--; status=401 | username=admin'--; status=401 | Add SQLi-vs-traversal contrast examples where SQL comment markers, UNION, SLEEP, WAITFOR, and encoded quotes are separate from ../, /etc/passwd, and php://filter. |
| `v3-hard-000029` | `sql_injection_attempt` | `directory_traversal_attempt` | SQLi -> traversal | filter=1;DROP TABLE audit_log--; status=500 | filter=1; DROP TABLE audit_log-- | Add SQLi-vs-traversal contrast examples where SQL comment markers, UNION, SLEEP, WAITFOR, and encoded quotes are separate from ../, /etc/passwd, and php://filter. |
| `v3-hard-000030` | `sql_injection_attempt` | `<invalid>` | SQLi -> invalid | q=\" OR \"1\"=\"1; 400 |  | Add quote-heavy SQLi positives with evidence substrings that require JSON escaping, but keep each evidence item short and exact. |

## Dataset Implications

| Bucket | Target | Details |
| --- | ---: | --- |
| SQLi positives | 80 examples | Emphasize quote-heavy payloads, SQL comments, UNION SELECT, SLEEP/WAITFOR, information_schema, encoded tautologies, and status/severity cues. |
| Normal hard negatives | 40 examples | Cover benign SQL documentation/search terms, single auth failures, normalized relative paths, and approved low-scope monitoring. |
| Brute-force positives | 10 examples | Keep a small guard set for repeated failures so anti-gravity examples do not erase recall. |
| Traversal positives | 20 examples | Keep traversal token ownership clear with ../, encoded traversal, sensitive files, and wrappers. |
| Port/recon positives | 10 examples | Keep recon recall guarded with unique port/host thresholds and scanner signatures. |

## Hold Fixed Test

`data/splits/test.jsonl` must not be used for selecting v4 repair cases or tuning prompts/runtime settings.

## Next Step

Create the v4 SQLi-first supplement from these buckets, then train and probe v4 on hard-contrast before any mini semantic or future fixed comparison.
