# Phase 7 Fixed Split Comparison

**Summary**

Phase 7 เป็น fixed split evaluation gate สำหรับวัด v3.5 แบบ as-is เทียบกับ heuristic baseline หลัง Phase 6 ปิดแล้ว เป้าหมายคือเปิด `data/splits/test.jsonl` เพียงเพื่อวัดผลและเขียน comparison report ไม่ใช่เอาผล fixed split กลับไปจูน model รอบเดิม

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ Phase 7 prerequisites (source: docs/structured-output-fix-plan.md)
- `data/splits/test.jsonl` สำหรับ fixed holdout split (source: data/splits/test.jsonl)
- `reports/checksums/frozen-splits.sha256` สำหรับ checksum ของ fixed split (source: reports/checksums/frozen-splits.sha256)
- `reports/README.md` สำหรับ fixed split report path (source: reports/README.md)
- `docs/Day6.md` สำหรับ Phase 6 closure และ v3.5 limitation ที่ยังไม่ใช่ model promotion (source: docs/Day6.md)
- `reports/phase-6/phase-6-v3-5-boundary-training-result.md` สำหรับ candidate status, runtime probe metrics และ fixed split hold status (source: reports/phase-6/phase-6-v3-5-boundary-training-result.md)
- `reports/phase-7/phase-7-v3-5-temp-03-2048-smoke-guard.json` สำหรับ smoke guard ก่อนเปิด fixed split (source: reports/phase-7/phase-7-v3-5-temp-03-2048-smoke-guard.json)
- `reports/phase-7/phase-7-heuristic-fixed-split-eval.json` สำหรับ heuristic fixed split baseline (source: reports/phase-7/phase-7-heuristic-fixed-split-eval.json)
- `reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.json` สำหรับ v3.5 as-is fixed split evaluation (source: reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.json)
- `reports/phase-7/comparison.md` และ `reports/phase-7/phase-7-fixed-split-summary.html` สำหรับ final comparison และ stakeholder summary (source: reports/phase-7/comparison.md, source: reports/phase-7/phase-7-fixed-split-summary.html)

**Last updated**

2026-05-22

## Status

Executed. Phase 7 เปิด fixed `data/splits/test.jsonl` แล้วหนึ่งรอบสำหรับ heuristic baseline และหนึ่งรอบสำหรับ v3.5 as-is candidate ด้วย config เดียวที่ระบุไว้ในหน้านี้ ผลคือ v3.5 รักษา output contract ได้ครบ แต่ยังไม่ชนะ heuristic baseline จึงตัดสินใจ `hold`

## Prerequisites

- [x] Phase 6 closed with limitations and v3.5 recorded as completed/probed
- [x] `data/splits/test.jsonl` remains held during Phase 6 tuning
- [x] report path pattern is separated by phase and candidate
- [x] user explicitly approves opening fixed split for Phase 7
- [x] serving endpoint for selected candidate is running before fine-tuned evaluation
- [x] final candidate config is frozen before any `data/splits/test.jsonl` run

## Execution Result

Phase 7 ran on 2026-05-22 with fixed split checksum `b838f07b902890a8dc9159cd1d2a413e9d7c7ae4eeff5754d9c947a35e4cdb3b`, matching `reports/checksums/frozen-splits.sha256`.

Decision: `hold`. v3.5 is useful as an as-is triage behavior measurement and demo artifact, but it is not promoted over the heuristic baseline. The fixed split result must not be used to tune v3.5; future repair work needs a separately named experiment.

### Command Outcomes

| Step | Artifact | Outcome |
| --- | --- | --- |
| Preflight | `data/splits/test.jsonl`, `reports/checksums/frozen-splits.sha256` | Schema parsed; fixed split count `75`; checksum matched frozen record |
| Smoke guard | `reports/phase-7/phase-7-v3-5-temp-03-2048-smoke-guard.json` | JSON/schema `1.0 / 1.0`, invalid `0`, label accuracy `0.8` |
| Heuristic fixed split | `reports/phase-7/phase-7-heuristic-fixed-split-eval.json` | label accuracy `1.0`, JSON/schema `1.0 / 1.0`, invalid `0` |
| v3.5 fixed split | `reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.json` | label accuracy `0.84`, JSON/schema `1.0 / 1.0`, invalid `0` |
| Final comparison | `reports/phase-7/comparison.md`, `reports/phase-7/phase-7-fixed-split-summary.html` | Final decision `hold`; report includes 5 concrete v3.5 error examples |

### Fixed Split Metrics

| Metric | Heuristic baseline | v3.5 as-is candidate |
| --- | ---: | ---: |
| Label accuracy | `1.0` | `0.84` |
| JSON parse success | `1.0` | `1.0` |
| Schema success | `1.0` | `1.0` |
| Severity accuracy | `1.0` | `0.76` |
| Suspicious accuracy | `1.0` | `0.933333` |
| Evidence partial match | `1.0` | `0.973333` |
| Average latency | `0.045752 ms` | `445.131397 ms` |
| Invalid outputs | `0` | `0` |

### Label Results

| Label | Expected | Heuristic correct | v3.5 correct | v3.5 predicted |
| --- | ---: | ---: | ---: | ---: |
| `normal` | `15` | `15/15` | `11/15` | `12` |
| `failed_login_bruteforce` | `15` | `15/15` | `14/15` | `18` |
| `sql_injection_attempt` | `15` | `15/15` | `9/15` | `10` |
| `directory_traversal_attempt` | `15` | `15/15` | `14/15` | `19` |
| `port_scan_or_recon` | `15` | `15/15` | `15/15` | `16` |

### V3.5 Failure Summary

| Failure reason | Count |
| --- | ---: |
| `severity_mismatch` | `18` |
| `label_mismatch` | `12` |
| `is_suspicious_mismatch` | `5` |
| `evidence_partial_mismatch` | `2` |

Concrete examples are recorded in `reports/phase-7/comparison.md` and `reports/phase-7/phase-7-fixed-split-summary.html`, including SQLi classified as traversal/recon, single failed-login normal logs escalated to brute force, and one brute-force web login sample classified as normal.

## Phase 7 Decision

Default candidate for this runbook:

```text
candidate: lfm2-security-triage-v3-5
runtime: vLLM OpenAI-compatible structured_outputs
context: 2048-token train/runtime setting
temperature: 0.3
top_p: 0.9
extra_body: {"min_p":0.15,"repetition_penalty":1.05}
status: as-is evaluation candidate, not promotion
```

Rationale: v3.5 2048 temp 0.3 is the best recorded hard-contrast runtime probe: `label_accuracy=0.88`, JSON/schema `1.0 / 1.0`, invalid output `0`, but SQLi remains below the old strict gate. This is enough to evaluate as-is if the user accepts that fixed split results will be final evidence, not tuning feedback (source: reports/phase-6/phase-6-v3-5-boundary-training-result.md)

## Copy CLI Runbook

Copy blocks in order. Stop if any command fails or if the fixed split checksum does not match the frozen record.

### 0. Preflight Without Opening Fixed Split

These commands do not evaluate the fixed split. They only check files and show the frozen split checksum.

```bash
rtk .venv/bin/python -m json.tool data/schemas/triage-output.schema.json >/dev/null
rtk wc -l data/splits/test.jsonl
rtk shasum -a 256 data/splits/test.jsonl
rtk cat reports/checksums/frozen-splits.sha256
```

### 1. Candidate Smoke Guard

Run this before opening `data/splits/test.jsonl`. It uses the smoke split, not the fixed split.

```bash
rtk env \
  OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v3-5 \
  OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
  OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
  OPENAI_COMPATIBLE_TEMPERATURE=0.3 \
  OPENAI_COMPATIBLE_TOP_P=0.9 \
  OPENAI_COMPATIBLE_MAX_TOKENS=512 \
  OPENAI_COMPATIBLE_EXTRA_BODY='{"min_p":0.15,"repetition_penalty":1.05}' \
  .venv/bin/python scripts/evaluate.py \
    --adapter openai-compatible \
    --split data/splits/smoke-output-contract.jsonl \
    --out reports/phase-7/phase-7-v3-5-temp-03-2048-smoke-guard.json \
    --comparison-out reports/phase-7/phase-7-v3-5-temp-03-2048-smoke-guard.md
```

Expected gate before continuing:

- `json_parse_success_rate = 1.0`
- `schema_success_rate = 1.0`
- `invalid_output_count = 0`

### 2. Open Fixed Split: Heuristic Baseline

This is the first Phase 7 fixed split run.

```bash
rtk .venv/bin/python scripts/evaluate.py \
  --adapter heuristic \
  --split data/splits/test.jsonl \
  --out reports/phase-7/phase-7-heuristic-fixed-split-eval.json \
  --comparison-out reports/phase-7/phase-7-heuristic-fixed-split-eval.md
```

### 3. Open Fixed Split: V3.5 As-Is Candidate

Use the exact same candidate config as the smoke guard. Do not change temperature, schema mode, model alias, or output paths after seeing baseline results.

```bash
rtk env \
  OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v3-5 \
  OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
  OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
  OPENAI_COMPATIBLE_TEMPERATURE=0.3 \
  OPENAI_COMPATIBLE_TOP_P=0.9 \
  OPENAI_COMPATIBLE_MAX_TOKENS=512 \
  OPENAI_COMPATIBLE_EXTRA_BODY='{"min_p":0.15,"repetition_penalty":1.05}' \
  .venv/bin/python scripts/evaluate.py \
    --adapter openai-compatible \
    --split data/splits/test.jsonl \
    --out reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.json \
    --comparison-out reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.md
```

### 4. Extract Metrics For Comparison

This command prints the main metrics from both fixed split reports.

```bash
rtk .venv/bin/python - <<'PY'
import json
from pathlib import Path

paths = [
    Path("reports/phase-7/phase-7-heuristic-fixed-split-eval.json"),
    Path("reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.json"),
]
for path in paths:
    data = json.loads(path.read_text())
    print(f"\n{path}")
    print(f"adapter: {data.get('adapter')}")
    print(f"sample_count: {data.get('sample_count')}")
    for key, value in data.get("metrics", {}).items():
        print(f"{key}: {value}")
    print(f"predicted_label_distribution: {data.get('predicted_label_distribution')}")
PY
```

### 5. Verify Artifacts Exist

```bash
rtk ls -lh \
  reports/phase-7/phase-7-heuristic-fixed-split-eval.json \
  reports/phase-7/phase-7-heuristic-fixed-split-eval.md \
  reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.json \
  reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.md
```

### 6. Write Final Comparison Report

Use the two fixed split JSON reports above as sources. The final report path should be:

```text
reports/phase-7/comparison.md
```

The report should include:

- heuristic vs v3.5 metric table
- label distribution comparison
- JSON/schema success and invalid output counts
- severity and evidence quality comparison
- 3-5 concrete error examples from the v3.5 fixed split report
- final decision: `demo_only`, `hold`, or `needs_new_experiment`

Do not call the result a compromise detector. Use triage wording only.

## Pass Condition

- report บอกตรง ๆ ว่า fine-tuned model ชนะหรือแพ้ heuristic baseline ตรงไหน
- มีตัวอย่าง error 3-5 เคส
- ไม่มี overclaim ว่า model ยืนยัน compromise ได้
- fixed split result is not used to tune v3.5 afterward

## Guardrails

- Do not run multiple candidate configs on `data/splits/test.jsonl` and pick the best.
- Do not change prompt/schema/runtime after seeing fixed split results.
- Do not overwrite Phase 6 hard-contrast reports with Phase 7 outputs.
- If Phase 7 fails, open a new experiment name for repair work and keep this fixed split result as historical evidence.

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 7 detail stub | `docs/output-structure-fix/phase-7-fixed-split-comparison.md` | Drafted |
| 2026-05-22 | Codex | Added copyable Phase 7 fixed split CLI runbook | `docs/output-structure-fix/phase-7-fixed-split-comparison.md` | Runbook prepared |
| 2026-05-22 | Codex | Ran Phase 7 fixed split evaluation and recorded final comparison artifacts | `reports/phase-7/phase-7-heuristic-fixed-split-eval.json`, `reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.json`, `reports/phase-7/comparison.md`, `reports/phase-7/phase-7-fixed-split-summary.html` | Executed; decision `hold` |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-22 | Treat Phase 7 as an as-is fixed split evaluation gate | Phase 6 closed with limitations and v3.5 has enough evidence to evaluate, but not enough to call it a promotion run | Candidate config must be frozen before fixed split and results cannot be used to tune v3.5 |
| 2026-05-22 | Use copyable CLI blocks for all Phase 7 execution steps | Phase 7 should be repeatable by a human without reconstructing env vars or report paths from scattered docs | The page now includes preflight, smoke guard, heuristic eval, v3.5 eval, metric extraction, and artifact verification commands |
| 2026-05-22 | Hold v3.5 after fixed split evaluation | v3.5 preserved JSON/schema on the fixed split but scored `0.84` label accuracy versus heuristic `1.0`, with SQLi and normal/brute-force boundary misses still visible | v3.5 remains a demo/exploratory artifact; fixed split result becomes historical evidence and must not tune v3.5 |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-6-v3-or-runtime-decision]]
- [[output-structure-fix/phase-6-v3-5-boundary-repair-plan]]
- [[structured-output-fix-plan]]
