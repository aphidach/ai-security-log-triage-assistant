# Phase 8 v4.7 Qwen3.5 Auth/SQLi/Severity Calibration Slice

This report reads the v4.6 non-fixed probe outputs and identifies the remaining failures to repair before any fixed split run.

## Headline

- Source reports: `reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.json`, `reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json`
- Fixed test split used: `false`
- Failure cases: `18`

## Bucket Summary

| Bucket | Count | IDs |
| --- | ---: | --- |
| Normal -> brute force | `7` | `v3-hard-000001`, `v3-hard-000002`, `v3-hard-000003`, `v4-6-qwen35-cal-000121`, `v4-6-qwen35-cal-000122`, `v4-6-qwen35-cal-000123`, `v4-6-qwen35-cal-000124` |
| SQLi -> brute force | `2` | `v3-hard-000021`, `v3-hard-000025` |
| Brute force medium -> high | `7` | `v3-hard-000015`, `v3-hard-000016`, `v3-hard-000018`, `v4-6-qwen35-cal-000136`, `v4-6-qwen35-cal-000137`, `v4-6-qwen35-cal-000138`, `v4-6-qwen35-cal-000139` |
| Port/recon medium -> high | `1` | `v3-hard-000050` |
| Traversal evidence miss | `1` | `v3-hard-000035` |

## Dataset Implications

| Bucket | Target | Details |
| --- | --- | --- |
| auth normal hard negatives | train-heavy supplement and 15-record probe holdout | Repair benign auth failures that resemble brute force but lack volume or scope. |
| SQLi auth-context positives | SQLi guard supplement and 5-record probe holdout | Preserve SQLi recall on login/auth routes where auth vocabulary is present. |
| medium severity boundaries | brute-force and limited port/recon calibration examples | Teach that limited repeated auth failures and small blocked recon do not automatically become high. |
| exact traversal evidence | short copied evidence substrings | Repair traversal evidence partial-match behavior without changing label taxonomy. |
