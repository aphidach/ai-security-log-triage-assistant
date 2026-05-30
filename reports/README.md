# Reports

This directory stores evaluation outputs for the AI Security Log Triage Assistant.
The root is intentionally small for public browsing; report artifacts are grouped
by workflow instead of living in one flat folder.

## Directory Map

| Folder | Purpose |
| --- | --- |
| `baseline/` | Local heuristic baseline outputs that can run without model keys. |
| `checksums/` | Split checksums and other small integrity records. |
| `structured-output/` | Runtime contract work before model-quality evaluation. |
| `structured-output/smoke/` | Smoke reports for structured-output modes. |
| `structured-output/probes/` | Direct backend capability probes and adversarial format probes. |
| `structured-output/mini-semantic-eval/` | Early 25-sample semantic checks after contract gates. |
| `structured-output/runtime/` | Backend inventory, capability matrix, and artifact registry notes. |
| `phase-6/` | LFM2/v3 repair reports, hard-contrast probes, failure slices, and infographics. |
| `phase-7/` | Fixed split comparison artifacts and final Phase 7 hold decision. |
| `phase-8/` | SQLi repair, Qwen3.5 diagnostics, calibration probes, training summaries, and HTML reports. |

## Naming Convention

Keep new artifacts under the workflow folder that owns the decision:

```text
reports/structured-output/smoke/{adapter}-{runtime}-{mode}-smoke.json
reports/structured-output/probes/structured-output-probe-{runtime}-{mode}-{probe}.json
reports/phase-6/{adapter}-{runtime}-{mode}-{model-version}-{probe}.json
reports/phase-7/phase-7-{candidate-or-baseline}-{eval-kind}.json
reports/phase-8/phase-8-{experiment}-{artifact-kind}.json
```

Use lowercase kebab-case for new files. Preserve historical model/version tokens
when moving old artifacts so past docs remain traceable.

## Canonical Artifacts

| Artifact | Path |
| --- | --- |
| Heuristic baseline JSON | `reports/baseline/baseline-eval.json` |
| Split checksums | `reports/checksums/frozen-splits.sha256` |
| Structured-output artifact register | `reports/structured-output/runtime/structured-output-run-artifacts.md` |
| Runtime capability matrix | `reports/structured-output/runtime/structured-output-capability-matrix.md` |
| vLLM structured-output smoke | `reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json` |
| Phase 5 mini semantic eval | `reports/structured-output/mini-semantic-eval/openai-compatible-vllm-structured-outputs-mini-semantic-eval.json` |
| Phase 7 comparison | `reports/phase-7/comparison.md` |
| Phase 7 fixed split summary | `reports/phase-7/phase-7-fixed-split-summary.html` |
| Latest v4.8 diagnostic audit | `reports/phase-8/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json` |

## Examples

```bash
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/smoke-output-contract.jsonl \
  --out reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json \
  --comparison-out reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.md
```

```bash
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/test.jsonl \
  --out reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.json \
  --comparison-out reports/phase-7/phase-7-v3-5-temp-03-2048-fixed-split-eval.md
```

Do not write new public artifacts to generic paths such as `reports/eval.json` or
`reports/openai-compatible-eval.json`; those names are too easy to overwrite.
