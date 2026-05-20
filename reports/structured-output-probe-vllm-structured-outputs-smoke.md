# Structured Output Probe Report

- Base URL: `http://192.168.8.141:8080/v1`
- Endpoint: `http://192.168.8.141:8080/v1/chat/completions`
- Requested model: `lfm2-security-triage`
- Mode: `structured_outputs`
- Provider schema mode: `extra_body.structured_outputs.json`
- Adversarial format: `none`
- Split: `data/splits/smoke-output-contract.jsonl`
- Schema: `/Volumes/Hiksemi/Code/ai-security-log-triage-assistant/data/schemas/triage-output.schema.json`

## Summary

| Metric | Value |
| --- | ---: |
| `samples` | `5` |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `error_count` | `0` |
| `markdown_fence_count` | `0` |
| `plain_json_object_count` | `5` |
| `average_latency_ms` | `1302.791642` |

## Samples

| ID | Response model | JSON | Schema | Fence | Plain object | Latency ms | Error |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `sample-000035` | `lfm2-security-triage` | `true` | `true` | `false` | `true` | `1964.281834` |  |
| `sample-000137` | `lfm2-security-triage` | `true` | `true` | `false` | `true` | `1264.819958` |  |
| `sample-000248` | `lfm2-security-triage` | `true` | `true` | `false` | `true` | `717.494125` |  |
| `sample-000331` | `lfm2-security-triage` | `true` | `true` | `false` | `true` | `1211.491333` |  |
| `sample-000474` | `lfm2-security-triage` | `true` | `true` | `false` | `true` | `1355.870958` |  |

## Raw Outputs

### `sample-000035`

- Response model: `lfm2-security-triage`
- JSON parse success: `true`
- Schema success: `true`
- Has markdown fence: `false`

```text
{ "label": "failed_login_bruteforce", "severity": "high", "is_suspicious": true, "evidence": ["tcp connection from 192.0.2.35 to 192.0.2.21:443", "session_count=1"], "reason": "Multiple failed login attempts from a single IP address, indicating a brute force attack attempt.",
  "recommended_action": "Block the IP address and investigate further to determine if the attack is active."}
```

### `sample-000137`

- Response model: `lfm2-security-triage`
- JSON parse success: `true`
- Schema success: `true`
- Has markdown fence: `false`

```text
{ "label": "failed_login_bruteforce", "severity": "high", "is_suspicious": true, "evidence": ["auth-01 sshd[3146]", "sshd.log", "ssh2.log"], "reason": "Multiple failed login attempts from a specific IP address in a short time frame", "recommended_action": "Block IP address and investigate further"}
```

### `sample-000248`

- Response model: `lfm2-security-triage`
- JSON parse success: `true`
- Schema success: `true`
- Has markdown fence: `false`

```text
{ "label": "failed_login_bruteforce", "severity": "high", "is_suspicious": true, "evidence": ["GET /api/users?id=9", "status=500", "src=198.51.100.169", "upstream_ms=3904"], "reason": "Multiple failed login attempts from IP 198.51.100.169 within 5 seconds", "recommended_action": "Block IP 198.51.100.169 and investigate further for potential brute force attack."}
```

### `sample-000331`

- Response model: `lfm2-security-triage`
- JSON parse success: `true`
- Schema success: `true`
- Has markdown fence: `false`

```text
{ "label": "failed_login_bruteforce", "severity": "high", "is_suspicious": true, "evidence": ["203.0.113.50 - - [17/May/2026:14:56:44 +0700] \"GET /download?file=..\\..\\windows\\win.ini HTTP/1.1\"", "403", "403", "403", "403"], "reason": "Multiple failed login attempts from 203.0.113.50 targeting the specified IP address and URL", "recommended_action": "Block IP address and attempt to block subsequent failed login attempts"}
```

### `sample-000474`

- Response model: `lfm2-security-triage`
- JSON parse success: `true`
- Schema success: `true`
- Has markdown fence: `false`

```text
{ "label": "sql_injection_attempt", "severity": "high", "is_suspicious": true, "evidence": ["ids: nmap fingerprint from 198.51.100.117 to 203.0.113.205", "probed_ports=21,22,23,25,80,443", "packets=106"], "reason": "SQL injection attempt detected from IP address 198.51.100.117 targeting ports 21, 22, 23, 25, 80, 443", "recommended_action": "Block IP address and investigate further for potential SQL injection attack."}
```
