# Phase 7 Fixed Split Comparison

**Summary**

Phase 7 opened the fixed `data/splits/test.jsonl` split exactly once for the selected as-is v3.5 candidate and the heuristic baseline. The v3.5 candidate preserved the output contract on the fixed split, but it did not outperform the deterministic heuristic baseline on this synthetic fixed split. Decision: `hold`.

**Sources**

- `reports/phase-7/phase-7-heuristic-fixed-split-eval.json`
- `reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.json`
- `reports/phase-7/phase-7-v3-5-temp-03-2048-smoke-guard.json`
- `docs/output-structure-fix/phase-7-fixed-split-comparison.md`
- `reports/checksums/frozen-splits.sha256`

**Last updated**

2026-05-22

## Decision

`hold`: v3.5 is useful as an as-is triage behavior measurement and demo artifact, but it is not promoted over the heuristic baseline. The fixed split result must not be used to tune v3.5; any repair work must start as a separately named experiment.

## Candidate Config

| Field | Value |
| --- | --- |
| Model alias | `lfm2-security-triage-v3-5` |
| Runtime | `vLLM OpenAI-compatible structured_outputs` |
| Temperature | `0.3` |
| Top p | `0.9` |
| Extra body | `{"min_p":0.15,"repetition_penalty":1.05}` |
| Fixed split | `data/splits/test.jsonl`, 75 samples |
| Evaluation mode | as-is fixed split evaluation, not promotion |

## Smoke Guard

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.8` |
| `json_parse_success_rate` | `1` |
| `schema_success_rate` | `1` |
| `invalid_output_count` | `0` |
| `average_latency_ms` | `745.482` |

The smoke guard passed the output-contract gate before fixed split evaluation: JSON parse `1.0`, schema `1.0`, invalid outputs `0`.

## Fixed Split Metrics

| Metric | Heuristic baseline | v3.5 as-is candidate |
| --- | ---: | ---: |
| Label accuracy | `1` | `0.84` |
| JSON parse success | `1` | `1` |
| Schema success | `1` | `1` |
| Severity accuracy | `1` | `0.76` |
| Suspicious accuracy | `1` | `0.933333` |
| Evidence partial match | `1` | `0.973333` |
| Average latency ms | `0.045752` | `445.131` |
| Invalid outputs | `0` | `0` |

## Label Results

| Label | Expected | Heuristic correct | v3.5 correct | v3.5 predicted |
| --- | ---: | ---: | ---: | ---: |
| `normal` | `15` | `15/15` | `11/15` | `12` |
| `failed_login_bruteforce` | `15` | `15/15` | `14/15` | `18` |
| `sql_injection_attempt` | `15` | `15/15` | `9/15` | `10` |
| `directory_traversal_attempt` | `15` | `15/15` | `14/15` | `19` |
| `port_scan_or_recon` | `15` | `15/15` | `15/15` | `16` |

## V3.5 Failure Reasons

| Failure reason | Count |
| --- | ---: |
| `severity_mismatch` | `18` |
| `label_mismatch` | `12` |
| `is_suspicious_mismatch` | `5` |
| `evidence_partial_mismatch` | `2` |

## V3.5 Confusion Matrix

| Expected \ Predicted | `normal` | `failed_login_bruteforce` | `sql_injection_attempt` | `directory_traversal_attempt` | `port_scan_or_recon` | `invalid` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `normal` | `11` | `4` | `0` | `0` | `0` | `0` |
| `failed_login_bruteforce` | `1` | `14` | `0` | `0` | `0` | `0` |
| `sql_injection_attempt` | `0` | `0` | `9` | `5` | `1` | `0` |
| `directory_traversal_attempt` | `0` | `0` | `1` | `14` | `0` | `0` |
| `port_scan_or_recon` | `0` | `0` | `0` | `0` | `15` | `0` |

## Concrete V3.5 Error Examples

### `sample-000248`

- Failure reasons: `label_mismatch`
- Expected: `sql_injection_attempt` / `high` / suspicious `True`
- Predicted: `directory_traversal_attempt` / `high` / suspicious `True`
- Expected evidence: `['id=9 AND SLEEP(5)', 'status=500']`
- Predicted evidence: `['id=9 AND SLEEP(5)']`

```text
2026-05-17T19:00:50+07:00 api-gateway: GET /api/users?id=9 AND SLEEP(5) src=198.51.100.169 status=500 upstream_ms=3904
```

### `sample-000013`

- Failure reasons: `label_mismatch, severity_mismatch, is_suspicious_mismatch`
- Expected: `normal` / `low` / suspicious `False`
- Predicted: `failed_login_bruteforce` / `high` / suspicious `True`
- Expected evidence: `['Failed password', 'failed_attempts=1']`
- Predicted evidence: `['Failed password', 'failed_attempts=1']`

```text
May 17 08:29:28 vpn-01 sshd[8158]: Failed password for admin from 198.51.100.225 port 44971 ssh2; failed_attempts=1
```

### `sample-000136`

- Failure reasons: `label_mismatch, severity_mismatch, is_suspicious_mismatch`
- Expected: `failed_login_bruteforce` / `medium` / suspicious `True`
- Predicted: `normal` / `low` / suspicious `False`
- Expected evidence: `['POST /login', 'status=401 repeated=17', 'python-requests']`
- Predicted evidence: `['POST /login', 'status=401 repeated=17', 'python-requests']`

```text
2026-05-17T19:42:27+07:00 waf: POST /login src=192.0.2.231 status=401 repeated=17 window=120s user_agent=python-requests
```

### `sample-000078`

- Failure reasons: `label_mismatch, severity_mismatch, is_suspicious_mismatch`
- Expected: `normal` / `low` / suspicious `False`
- Predicted: `failed_login_bruteforce` / `medium` / suspicious `True`
- Expected evidence: `['Failed password', 'failed_attempts=1']`
- Predicted evidence: `['Failed password', 'failed_attempts=1']`

```text
May 17 13:06:07 vpn-01 sshd[6242]: Failed password for admin from 192.0.2.173 port 33737 ssh2; failed_attempts=1
```

### `sample-000218`

- Failure reasons: `label_mismatch, severity_mismatch`
- Expected: `sql_injection_attempt` / `high` / suspicious `True`
- Predicted: `port_scan_or_recon` / `medium` / suspicious `True`
- Expected evidence: `['id=1 OR 1=1', 'status=400']`
- Predicted evidence: `['id=1 OR 1=1', 'status=400']`

```text
2026-05-17T13:12:16+07:00 api-gateway: GET /api/users?id=1 OR 1=1 src=203.0.113.137 status=400 upstream_ms=2740
```

## Limitations

- This is a triage-pattern evaluation on a synthetic fixed split, not proof that the model detects compromise.
- The heuristic baseline is deterministic and template-aligned, so its perfect score is a useful control rather than evidence of production readiness.
- v3.5 fixed split results are historical evidence and must not be used to tune v3.5. Future repair must use a new experiment name.

## Related pages

- [[output-structure-fix/phase-7-fixed-split-comparison]]
- [[Day7]]
- [[output-structure-fix/phase-6-v3-5-boundary-repair-plan]]
