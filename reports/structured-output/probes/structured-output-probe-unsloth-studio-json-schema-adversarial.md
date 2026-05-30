# Structured Output Probe Report

- Base URL: `http://192.168.8.141:8888/v1`
- Endpoint: `http://192.168.8.141:8888/v1/chat/completions`
- Requested model: `current`
- Mode: `json_schema`
- Provider schema mode: `response_format.json_schema.strict`
- Adversarial format: `markdown_fence`
- Split: `data/splits/smoke-output-contract.jsonl`
- Schema: `/Volumes/Hiksemi/Code/ai-security-log-triage-assistant/data/schemas/triage-output.schema.json`

## Summary

| Metric | Value |
| --- | ---: |
| `samples` | `5` |
| `json_parse_success_rate` | `0.0` |
| `schema_success_rate` | `0.0` |
| `error_count` | `1` |
| `markdown_fence_count` | `4` |
| `plain_json_object_count` | `0` |
| `average_latency_ms` | `42400.176783` |

## Samples

| ID | Response model | JSON | Schema | Fence | Plain object | Latency ms | Error |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `sample-000035` | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` | `false` | `false` | `true` | `false` | `4999.40325` |  |
| `sample-000137` | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` | `false` | `false` | `true` | `false` | `4158.707083` |  |
| `sample-000248` | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` | `false` | `false` | `true` | `false` | `4596.776667` |  |
| `sample-000331` | `None` | `false` | `false` | `false` | `false` | `181484.885375` | APITimeoutError: Request timed out. |
| `sample-000474` | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` | `false` | `false` | `true` | `false` | `16761.111542` |  |

## Raw Outputs

### `sample-000035`

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
  "evidence": ["tcp connection from 192.0.2.35 to 192.0.2.21:443", "session_count=1"],
  "reason": "Multiple failed login attempts from IP 192.0.2.35 to 192.0.2.21 exceeding 5 attempts in 5 minutes",
  "recommended_action": "Block IP 192.0.2.35 from all incoming connections and investigate further"
}
```
```

### `sample-000137`

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
  "evidence": ["ssh2; repeated 11 times in 5 minutes", "sshd[3146] failed password", "ssh2 failed login attempts"],
  "reason": "ssh2 failed login attempts from 192.0.2.105 multiple times in a short period, indicating brute force attempt."
}
```
```

### `sample-000248`

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
  "evidence": ["GET /api/users?id=9", "status=500", "src=198.51.100.169", "upstream_ms=3904"],
  "reason": "Multiple failed login attempts from IP 198.51.100.169 within 5 seconds",
  "recommended_action": "Block IP 198.51.100.169 and investigate further for potential brute force attack."
}
```
```

### `sample-000331`

- Response model: `None`
- JSON parse success: `false`
- Schema success: `false`
- Has markdown fence: `false`

```text

```

### `sample-000474`

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
  "evidence": [
    "ids: nmap fingerprint from 198.51.100.117 to 203.0.113.205",
    "probed_ports=21,22,23,25,80,443",
    "packets=106"
  ],
  "reason": "Multiple probes targeting high-risk ports (22, 80, 443) with repeated failed attempts to brute-force credentials."
}
```
```
