# Structured Output Probe Report

- Base URL: `http://192.168.8.141:8888/v1`
- Endpoint: `http://192.168.8.141:8888/v1/chat/completions`
- Requested model: `current`
- Mode: `json_schema`
- Provider schema mode: `response_format.json_schema.strict`
- Adversarial format: `none`
- Split: `data/splits/smoke-output-contract.jsonl`
- Schema: `/Volumes/Hiksemi/Code/ai-security-log-triage-assistant/data/schemas/triage-output.schema.json`

## Summary

| Metric | Value |
| --- | ---: |
| `samples` | `5` |
| `json_parse_success_rate` | `0.2` |
| `schema_success_rate` | `0.2` |
| `error_count` | `0` |
| `markdown_fence_count` | `4` |
| `plain_json_object_count` | `1` |
| `average_latency_ms` | `4590.22345` |

## Samples

| ID | Response model | JSON | Schema | Fence | Plain object | Latency ms | Error |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `sample-000035` | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` | `false` | `false` | `true` | `false` | `4896.467875` |  |
| `sample-000137` | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` | `true` | `true` | `false` | `true` | `3655.197959` |  |
| `sample-000248` | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` | `false` | `false` | `true` | `false` | `4651.764875` |  |
| `sample-000331` | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` | `false` | `false` | `true` | `false` | `4513.483833` |  |
| `sample-000474` | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` | `false` | `false` | `true` | `false` | `5234.202708` |  |

## Raw Outputs

### `sample-000035`

- Response model: `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226`
- JSON parse success: `false`
- Schema success: `false`
- Has markdown fence: `true`

```text
```json
{
  "label": "port_scan_or_recon",
  "severity": "high",
  "is_suspicious": true,
  "evidence": ["tcp connection", "session_count=1"],
  "reason": "This log indicates a port scan attempt from a known malicious IP address, suggesting potential reconnaissance or reconnaissance activity.",
  "recommended_action": "Isolate the affected port and investigate further to determine if the port is being used for reconnaissance or if the source IP is malicious."
}
```
```

### `sample-000137`

- Response model: `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226`
- JSON parse success: `true`
- Schema success: `true`
- Has markdown fence: `false`

```text
{ "label": "failed_login_bruteforce", "severity": "high", "is_suspicious": true, "evidence": ["auth-01 sshd[3146]", "sshd.log", "ssh2.log"], "reason": "Multiple failed login attempts from a specific IP address", "recommended_action": "Block IP address and increase authentication timeout"}
```

### `sample-000248`

- Response model: `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226`
- JSON parse success: `false`
- Schema success: `false`
- Has markdown fence: `true`

```text
```json
{
  "label": "ssh_attempt_failed",
  "severity": "high",
  "is_suspicious": true,
  "evidence": [
    "SLEEP(5)",
    "src=198.51.100.169",
    "status=500",
    "src=80",
    "response_time=3904ms"
  ],
  "reason": "Multiple failed SSH login attempts from IP address 198.51.100.169 with a response time of 3904ms, indicating a brute force attack attempt."
}
```
```

### `sample-000331`

- Response model: `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226`
- JSON parse success: `false`
- Schema success: `false`
- Has markdown fence: `true`

```text
```json
{
  "label": "failed_login_bruteforce",
  "severity": "high",
  "is_suspicious": true,
  "evidence": ["GET /download?file=..\\..\\windows\\win.ini HTTP/1.1", "403", "curl/8.1"],
  "reason": "Multiple failed login attempts from 203.0.113.50 targeting the specified domain.",
  "recommended_action": "Block IP address and attempt to block IP address on next login attempt."
}
```
```

### `sample-000474`

- Response model: `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226`
- JSON parse success: `false`
- Schema success: `false`
- Has markdown fence: `true`

```text
```json
{
  "label": "ssh_bruteforce_attempt",
  "severity": "high",
  "is_suspicious": true,
  "evidence": [
    "ids: nmap fingerprint from 198.51.100.117 to 203.0.113.205",
    "probed_ports=21,22,23,25,80,443",
    "packets=106"
  ],
  "reason": "Multiple failed login attempts detected from IP address 198.51.100.117 targeting ports 21, 22, 23, 80, 443, indicating a brute force attack attempt."
}
```
```
