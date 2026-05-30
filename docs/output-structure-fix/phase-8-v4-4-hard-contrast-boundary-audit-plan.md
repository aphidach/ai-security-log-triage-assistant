# Phase 8 V4.4 Hard-Contrast Boundary Audit Plan

**Summary**

v4.4 เป็น boundary audit ต่อจาก v4.3 Qwen3.5 hold decision โดย v4.3 ใช้ `unsloth/Qwen3.5-0.8B` เป็น base model ตรงจาก Hub ไม่ใช่ model ที่ train/LoRA แล้ว รอบนี้ไม่ได้ train เพิ่มและไม่ได้เปิด fixed split แต่อ่านเฉพาะ hard-contrast report ของ base model ทั้ง temp `0` และ temp `0.3` แล้วสรุปว่า failure หลักคือ suspicious security semantics ถูกลดเป็น `normal`: union label failures มี `26` IDs, persistent failures มี `25` IDs, และ SQLi/traversal/recon -> normal มี `20/50` ที่ temp `0` กับ `22/50` ที่ temp `0.3`

**Sources**

- v4.3 Qwen3.5 capacity diagnostic decision (source: docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md)
- v4.3 Qwen3.5 base-model hard-contrast temp 0 report (source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.json)
- v4.3 Qwen3.5 base-model hard-contrast temp 0.3 report (source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.json)
- v4.4 generated boundary audit artifacts (source: scripts/create_v4_4_hard_contrast_boundary_audit.py, source: reports/phase-8/phase-8-v4-4-hard-contrast-boundary-audit.json, source: reports/phase-8/phase-8-v4-4-hard-contrast-boundary-audit.md)
- hard-contrast source split used only for expected labels/evidence (source: data/generated/v3-hard-contrast-security-triage.jsonl)

**Last updated**

2026-05-23

## Status

Audit complete; next decision pending. v4.4 created only audit reports:

```text
reports/phase-8/phase-8-v4-4-hard-contrast-boundary-audit.json
reports/phase-8/phase-8-v4-4-hard-contrast-boundary-audit.md
```

No `data/splits/test.jsonl` run was opened. No v4.4 training split, generated supplement, LoRA config, or train allowlist entry should exist.

## Why This Exists

v4.3 answered one useful question already: base `unsloth/Qwen3.5-0.8B`, served as-is with no project LoRA, can follow the structured-output contract through vLLM structured outputs. JSON parse and schema success stayed `1.0`, invalid output stayed `0`, and evidence extraction was not the main blocker.

But the same reports showed semantic quality is far below gate. The model often quotes useful evidence, then explains it away as routine traffic. That is different from a pure parser problem and different from the earlier v4.2 SQLi-to-traversal drift. The v4.4 job is to name that failure clearly before we choose the next experiment.

## Audit Result Summary

| Probe | Samples | Label failures | Persistent failures | Label accuracy | JSON/schema | Invalid | SQLi/traversal/recon -> normal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Temp `0` | `50` | `25` | `25` | `0.50` | `1.0 / 1.0` | `0` | `20` |
| Temp `0.3` | `50` | `26` | `25` | `0.48` | `1.0 / 1.0` | `0` | `22` |

The audit report found `26` union failure IDs. Of those, `25` fail in both hard-contrast probes. Temp `0.3` adds only one extra label failure, `v3-hard-000024`, so sampling does not change the shape of the problem.

## Boundary Buckets

| Bucket | Temp 0 | Temp 0.3 | Read |
| --- | ---: | ---: | --- |
| Normal auth negative -> brute force | `2` | `2` | small guardrail issue |
| Brute force -> normal | `1` | `1` | secondary because failed-login recall is still `9/10` |
| SQLi tautology -> normal | `4` | `5` | classic OR/quote cues are seen but not treated as security evidence |
| SQLi schema discovery -> normal | `1` | `1` | `information_schema` in a request field is treated as benign database/search activity |
| SQLi timing -> normal | `0` | `1` | `SLEEP(5)` and latency cues can be explained away as backend processing |
| SQLi login payload -> brute force | `2` | `1` | route/status context can overpower SQL payload syntax |
| Traversal -> normal | `8` | `8` | traversal strings are reframed as common or legitimate file access |
| Recon -> normal | `7` | `7` | Nmap/probe/enumeration vocabulary is treated as routine admin traffic |

The largest problem is not one SQLi variant. It is a broader security-semantics weakness: clear attack/recon tokens are recognized as text, but the model does not consistently assign the security label.

## Interpretation

The base Qwen3.5-0.8B candidate is not blocked by structured output. It is blocked by boundary meaning. The model often says the request contains SQLi, traversal, Nmap, or service enumeration cues, then still returns `normal` with low severity.

This makes a future direct Qwen LoRA run risky as the next default step. If we train immediately from this base-model result, we may only teach a small model to memorize these hard-contrast forms without proving it understands the broader boundary. A Qwen LoRA smoke can still exist as an explicitly exploratory pilot, but it should not become the v4.4 gate by itself.

## Decision

Hold the base Qwen3.5-0.8B candidate after v4.4 boundary audit. Do not run the fixed split. Do not create v4.4 training artifacts from this audit by default.

Default next path: test another capacity candidate that is stronger at text/security-log semantics under the same prompt, schema, hard-contrast split, and port `8080` serving convention. If compute or model availability blocks that path, run a deliberately scoped prompt/data boundary repair using only the buckets above, not a broad synthetic-data expansion.

## Command Runbook

Regenerate the audit artifacts:

```bash
rtk .venv/bin/python scripts/create_v4_4_hard_contrast_boundary_audit.py
```

Inspect the headline numbers:

```bash
rtk .venv/bin/python - <<'PY'
import json
from pathlib import Path

report = json.loads(Path("reports/phase-8/phase-8-v4-4-hard-contrast-boundary-audit.json").read_text())
print("union_label_failure_count:", report["union_label_failure_count"])
print("persistent_label_failure_count:", report["persistent_label_failure_count"])
for probe, summary in report["probe_summaries"].items():
    print(probe)
    print("  label_failure_count:", summary["label_failure_count"])
    print("  label_accuracy:", summary["metrics"]["label_accuracy"])
    print("  json/schema:", summary["metrics"]["json_parse_success_rate"], summary["metrics"]["schema_success_rate"])
    print("  invalid:", summary["metrics"]["invalid_output_count"])
    print("  SQLi/traversal/recon -> normal:", summary["key_case_counts"]["sqli_traversal_recon_to_normal_count"])
PY
```

Check that v4.4 did not accidentally create train artifacts:

```bash
rtk find data/splits data/generated ml/unsloth -maxdepth 1 -name '*v4-4*' -print
```

Expected output is empty. The only v4.4 artifacts should be the audit script and the two report files.

## Next Work Options

| Option | When to choose | What it proves | Risk |
| --- | --- | --- | --- |
| Another capacity candidate | Default next step if the machine can serve another small/medium model | Whether the failure is Qwen3.5-0.8B-specific | More runtime setup |
| Scoped prompt/data boundary repair | If model swapping is blocked or user wants to keep Qwen | Whether explicit security-boundary wording/examples can rescue the current candidate | May overfit the hard-contrast split |
| Future Qwen LoRA exploratory pilot | Only if explicitly named as exploration after the base-model hold | Whether the training stack works for Qwen3.5 | Not a gate; should not unlock fixed split |

## Non-Goals

- No fixed split run
- No new v4.4 synthetic supplement
- No v4.4 train/validation split
- No `ml/unsloth/config.v4-4.yaml`
- No prompt default change
- No taxonomy expansion beyond the five existing labels

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-23 | Codex | Created v4.4 hard-contrast boundary audit from the two v4.3 Qwen3.5 base-model hard-contrast reports | `scripts/create_v4_4_hard_contrast_boundary_audit.py`, `reports/phase-8/phase-8-v4-4-hard-contrast-boundary-audit.json`, `reports/phase-8/phase-8-v4-4-hard-contrast-boundary-audit.md` | Audit complete |
| 2026-05-23 | User/Codex | Clarified that the audited v4.3 Qwen3.5 reports are base-model reports, not trained Qwen reports | `docs/output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan.md` | Clarified |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-23 | Hold base Qwen3.5-0.8B after v4.4 boundary audit | `25` failure IDs persist across both base-model probes, and the main failure is SQLi/traversal/recon -> `normal` despite perfect JSON/schema | Do not open fixed split or create v4.4 train artifacts; choose another capacity candidate or a scoped boundary-repair experiment |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan]]
- [[fine-tuning-notes]]
- [[label-taxonomy]]
- [[openai-adapter-runtime-config]]
