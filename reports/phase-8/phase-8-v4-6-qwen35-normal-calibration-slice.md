# Phase 8 v4.6 Qwen3.5 Normal Calibration Slice

This report reads the v4.5 trained-Qwen hard-contrast report and identifies the calibration failures to repair before any fixed split run.

## Headline

- Source report: `reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B—v1temp-0-hard-contrast-memorization-probe.json`
- Source split: `data/generated/v3-hard-contrast-security-triage.jsonl`
- Fixed test split used: `false`
- Label failures: `6`
- Severity failures: `14`
- Severity-only failures: `8`
- Evidence failures: `1`

## Bucket Summary

| Bucket | Count | IDs |
| --- | ---: | --- |
| Brute force severity too high | `3` | `v3-hard-000015`, `v3-hard-000016`, `v3-hard-000018` |
| Evidence miss | `1` | `v3-hard-000035` |
| Normal -> brute force | `3` | `v3-hard-000001`, `v3-hard-000002`, `v3-hard-000003` |
| Normal -> SQLi | `2` | `v3-hard-000005`, `v3-hard-000009` |
| Normal -> traversal | `1` | `v3-hard-000007` |
| Port/recon severity too low | `5` | `v3-hard-000042`, `v3-hard-000043`, `v3-hard-000044`, `v3-hard-000046`, `v3-hard-000047` |

## Dataset Implications

| Bucket | Target | Details |
| --- | --- | --- |
| normal hard negatives | train-heavy supplement | Repair normal -> brute force, SQLi, and traversal false positives without touching fixed test. |
| severity calibration | medium brute-force and high recon positives | Teach severity boundaries while keeping labels unchanged. |
| suspicious recall guard | small SQLi/traversal positives | Prevent the normal repair from causing a return to suspicious -> normal collapse. |
