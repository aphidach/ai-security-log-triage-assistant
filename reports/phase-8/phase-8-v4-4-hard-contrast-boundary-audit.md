# Phase 8 V4.4 Hard-Contrast Boundary Audit

**Summary**

v4.4 audits the v4.3 Qwen3.5 base-model hard-contrast failures. The model keeps JSON/schema reliability but collapses many suspicious SQLi, traversal, and recon records into normal.

**Sources**

- `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.json` for Qwen3.5 base-model temp 0 hard-contrast failures.
- `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.json` for Qwen3.5 base-model temp 0.3 hard-contrast failures.
- `data/generated/v3-hard-contrast-security-triage.jsonl` for source log lines and expected outputs.
- `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md` for the v4.3 hold decision.

**Last updated**

2026-05-23

## Probe Snapshots

| Probe | Samples | Label failures | Persistent? | Label accuracy | JSON/schema | Invalid | SQLi/traversal/recon -> normal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `temp_0` | `50` | `25` | `25` | `0.5` | `1.0 / 1.0` | `0` | `20` |
| `temp_0_3` | `50` | `26` | `25` | `0.48` | `1.0 / 1.0` | `0` | `22` |

## Boundary Read

- Union label failures: `26` IDs.
- Persistent failures across both probes: `25` IDs.
- Main failure family: suspicious SQLi/traversal/recon examples are classified as `normal` while JSON/schema stay perfect.
- Temp `0.3` adds one extra failure (`v3-hard-000024`) and does not change the core failure shape.

## Bucket Summary

### `temp_0`

| Bucket | Count | IDs | Boundary read | Next action |
| --- | ---: | --- | --- | --- |
| Brute force -> normal | `1` | `v3-hard-000013` | This is secondary because failed_login_bruteforce recall remains 9/10. | Review the one missed brute-force case after suspicious-to-normal collapse is handled. |
| Normal auth negative -> brute force | `2` | `v3-hard-000001`, `v3-hard-000002` | This is a small guardrail issue, not the main v4.4 blocker. | Keep the single-attempt threshold wording in future prompt/data audits. |
| Recon -> normal | `7` | `v3-hard-000041`, `v3-hard-000042`, `v3-hard-000045`, `v3-hard-000046`, `v3-hard-000048`, `v3-hard-000049`, `v3-hard-000050` | The model treats SOC/security-tool vocabulary as benign admin activity by default. | Require recon labels for explicit scan/probe/enumeration tokens unless the log states approved/internal testing. |
| SQLi login payload -> brute force | `2` | `v3-hard-000026`, `v3-hard-000028` | This is older Phase 8 gravity in a smaller form; route context is overpowering payload semantics. | Teach that SQL payload syntax inside username/email fields owns the label over generic login failure wording. |
| SQLi schema discovery -> normal | `1` | `v3-hard-000025` | The label boundary needs to say schema names in request/query fields are suspicious. | Pair benign SQL documentation searches against malicious request-field schema discovery. |
| SQLi tautology -> normal | `4` | `v3-hard-000021`, `v3-hard-000023`, `v3-hard-000027`, `v3-hard-000030` | The model notices text fragments but does not attach the security meaning strongly enough. | If using prompt/data repair later, make SQL tautology cues explicit positives even inside normal-looking routes. |
| Traversal -> normal | `8` | `v3-hard-000031`, `v3-hard-000032`, `v3-hard-000033`, `v3-hard-000034`, `v3-hard-000037`, `v3-hard-000038`, `v3-hard-000039`, `v3-hard-000040` | This is a security-semantics miss, not an evidence extraction miss. | Keep traversal cues as suspicious even when the HTTP status is 403/404 or the route is a normal file endpoint. |

### `temp_0_3`

| Bucket | Count | IDs | Boundary read | Next action |
| --- | ---: | --- | --- | --- |
| Brute force -> normal | `1` | `v3-hard-000013` | This is secondary because failed_login_bruteforce recall remains 9/10. | Review the one missed brute-force case after suspicious-to-normal collapse is handled. |
| Normal auth negative -> brute force | `2` | `v3-hard-000001`, `v3-hard-000002` | This is a small guardrail issue, not the main v4.4 blocker. | Keep the single-attempt threshold wording in future prompt/data audits. |
| Recon -> normal | `7` | `v3-hard-000041`, `v3-hard-000042`, `v3-hard-000045`, `v3-hard-000046`, `v3-hard-000048`, `v3-hard-000049`, `v3-hard-000050` | The model treats SOC/security-tool vocabulary as benign admin activity by default. | Require recon labels for explicit scan/probe/enumeration tokens unless the log states approved/internal testing. |
| SQLi login payload -> brute force | `1` | `v3-hard-000026` | This is older Phase 8 gravity in a smaller form; route context is overpowering payload semantics. | Teach that SQL payload syntax inside username/email fields owns the label over generic login failure wording. |
| SQLi schema discovery -> normal | `1` | `v3-hard-000025` | The label boundary needs to say schema names in request/query fields are suspicious. | Pair benign SQL documentation searches against malicious request-field schema discovery. |
| SQLi tautology -> normal | `5` | `v3-hard-000021`, `v3-hard-000023`, `v3-hard-000027`, `v3-hard-000028`, `v3-hard-000030` | The model notices text fragments but does not attach the security meaning strongly enough. | If using prompt/data repair later, make SQL tautology cues explicit positives even inside normal-looking routes. |
| SQLi timing -> normal | `1` | `v3-hard-000024` | The model needs an explicit security mapping from timing functions to SQLi. | Use SLEEP/pg_sleep/WAITFOR cases only as SQLi positives unless host/port scan evidence is present. |
| Traversal -> normal | `8` | `v3-hard-000031`, `v3-hard-000032`, `v3-hard-000033`, `v3-hard-000034`, `v3-hard-000037`, `v3-hard-000038`, `v3-hard-000039`, `v3-hard-000040` | This is a security-semantics miss, not an evidence extraction miss. | Keep traversal cues as suspicious even when the HTTP status is 403/404 or the route is a normal file endpoint. |

## Union Failures

Union failure ids: `v3-hard-000001`, `v3-hard-000002`, `v3-hard-000013`, `v3-hard-000021`, `v3-hard-000023`, `v3-hard-000024`, `v3-hard-000025`, `v3-hard-000026`, `v3-hard-000027`, `v3-hard-000028`, `v3-hard-000030`, `v3-hard-000031`, `v3-hard-000032`, `v3-hard-000033`, `v3-hard-000034`, `v3-hard-000037`, `v3-hard-000038`, `v3-hard-000039`, `v3-hard-000040`, `v3-hard-000041`, `v3-hard-000042`, `v3-hard-000045`, `v3-hard-000046`, `v3-hard-000048`, `v3-hard-000049`, `v3-hard-000050`

| ID | Expected | Evidence | Temp 0 | Temp 0.3 |
| --- | --- | --- | --- | --- |
| `v3-hard-000001` | `normal` | Failed password; failed_attempts=1 | failed_login_bruteforce | failed_login_bruteforce |
| `v3-hard-000002` | `normal` | event=login_failed; failures=1; outcome=allowed_retry | failed_login_bruteforce | failed_login_bruteforce |
| `v3-hard-000013` | `failed_login_bruteforce` | event_id=4625; count=16; status=failed_logon | normal | normal |
| `v3-hard-000021` | `sql_injection_attempt` | username=' OR '1'='1; status=403 | normal | normal |
| `v3-hard-000023` | `sql_injection_attempt` | id=1 OR 1=1; status=400 | normal | normal |
| `v3-hard-000024` | `sql_injection_attempt` | id=9 AND SLEEP(5); upstream_ms=6100 | pass | normal |
| `v3-hard-000025` | `sql_injection_attempt` | information_schema.tables; 403 | normal | normal |
| `v3-hard-000026` | `sql_injection_attempt` | username=admin'--; status=401 | failed_login_bruteforce | failed_login_bruteforce |
| `v3-hard-000027` | `sql_injection_attempt` | name%27%20OR%20%271%27%3D%271; 400 | normal | normal |
| `v3-hard-000028` | `sql_injection_attempt` | email=test@example.com' OR 'a'='a; status=403 | failed_login_bruteforce | normal |
| `v3-hard-000030` | `sql_injection_attempt` | q=\" OR \"1\"=\"1; 400 | normal | normal |
| `v3-hard-000031` | `directory_traversal_attempt` | ../config.yml; 403 | normal | normal |
| `v3-hard-000032` | `directory_traversal_attempt` | ../../../etc/shadow; 404 | normal | normal |
| `v3-hard-000033` | `directory_traversal_attempt` | /static/..%2f..%2fapp%2fsettings.py; status=404 | normal | normal |
| `v3-hard-000034` | `directory_traversal_attempt` | /files/%2e%2e%2f%2e%2e%2fwindows%2fwin.ini; 403 | normal | normal |
| `v3-hard-000037` | `directory_traversal_attempt` | /static/../../.env; status=403 | normal | normal |
| `v3-hard-000038` | `directory_traversal_attempt` | ../../../../var/log/auth.log; 403 | normal | normal |
| `v3-hard-000039` | `directory_traversal_attempt` | path=..%2f..%2f..%2fetc%2fpasswd; result=denied | normal | normal |
| `v3-hard-000040` | `directory_traversal_attempt` | /backup/../../secrets.yml; status=403 | normal | normal |
| `v3-hard-000041` | `port_scan_or_recon` | sequential connection attempts; unique_ports=4 | normal | normal |
| `v3-hard-000042` | `port_scan_or_recon` | nmap fingerprint; probed_ports=80,443,8080,8443 | normal | normal |
| `v3-hard-000045` | `port_scan_or_recon` | probe burst; unique_ports=6 | normal | normal |
| `v3-hard-000046` | `port_scan_or_recon` | nmap fingerprint; probed_ports=135,139,445,3389 | normal | normal |
| `v3-hard-000048` | `port_scan_or_recon` | sequential connection attempts; unique_ports=4 | normal | normal |
| `v3-hard-000049` | `port_scan_or_recon` | service enumeration; unique_ports=7; banners_requested=true | normal | normal |
| `v3-hard-000050` | `port_scan_or_recon` | blocked recon; tcp_flags=SYN; unique_ports=5 | normal | normal |

## Decision

Do not train from this result yet. The next useful evidence is either a candidate with stronger security-log semantics or a deliberately scoped prompt/data boundary repair based on the suspicious-to-normal buckets.

## Next Step

Keep fixed test closed, keep Qwen3.5-0.8B held, and choose between another capacity candidate and a small boundary-repair prompt/data experiment.

## Hold Fixed Test

`data/splits/test.jsonl` was not read and must stay closed for this boundary audit.

## No Training Artifacts

v4.4 creates only audit reports. It does not create supplement data, train/validation splits, a LoRA config, or train allowlist entries.
