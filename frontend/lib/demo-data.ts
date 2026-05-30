import type { TriageLabel } from "./labels"

export type SampleLog = {
  id: string
  label: TriageLabel
  name: string
  log: string
}

export type MetricSnapshot = {
  name: string
  source: string
  split: string
  status: "ready" | "exploratory" | "held" | "unconfigured"
  metrics: Array<{
    label: string
    value: string
    tone?: "good" | "warn" | "neutral"
  }>
}

export const SAMPLE_LOGS: SampleLog[] = [
  {
    id: "normal-health",
    label: "normal",
    name: "Health check",
    log: '10.10.4.20 - - [22/May/2026:10:14:22 +0700] "GET /health HTTP/1.1" 200 42 "-" "kube-probe/1.29"',
  },
  {
    id: "bruteforce-ssh",
    label: "failed_login_bruteforce",
    name: "Repeated SSH failures",
    log: "May 22 10:18:41 auth-01 sshd[2204]: Failed password for admin from 203.0.113.77 port 51244 ssh2 repeated 18 times",
  },
  {
    id: "sqli-web",
    label: "sql_injection_attempt",
    name: "SQLi payload",
    log: '198.51.100.24 - - [22/May/2026:10:20:11 +0700] "GET /login?username=admin%27%20OR%201%3D1-- HTTP/1.1" 500 921 "-" "curl/8.4"',
  },
  {
    id: "traversal-web",
    label: "directory_traversal_attempt",
    name: "Traversal path",
    log: '192.0.2.40 - - [22/May/2026:10:23:08 +0700] "GET /download?file=..%2f..%2fetc%2fpasswd HTTP/1.1" 404 212 "-" "Mozilla/5.0"',
  },
  {
    id: "recon-ids",
    label: "port_scan_or_recon",
    name: "Nmap fingerprint",
    log: "2026-05-22T10:25:00+07:00 ids sensor=dmz-01 alert='nmap fingerprint' src=203.0.113.91 dst=10.0.4.15 probed_ports=21,22,23,25,80,443",
  },
]

export const METRIC_SNAPSHOTS: MetricSnapshot[] = [
  {
    name: "Heuristic fixed split",
    source: "reports/phase-7/phase-7-heuristic-fixed-split-eval.json",
    split: "fixed test split, 75 samples",
    status: "ready",
    metrics: [
      { label: "Label accuracy", value: "1.00", tone: "good" },
      { label: "Schema success", value: "1.00", tone: "good" },
      { label: "Evidence match", value: "1.00", tone: "good" },
      { label: "Latency", value: "0.05 ms", tone: "good" },
    ],
  },
  {
    name: "Latest fine-tuned v4.7",
    source:
      "reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.json",
    split: "Qwen3.5 v4.7 hard-contrast probe, 50 samples; not fixed split",
    status: "held",
    metrics: [
      { label: "Label accuracy", value: "0.92", tone: "good" },
      { label: "Severity", value: "0.92", tone: "good" },
      { label: "Schema success", value: "1.00", tone: "good" },
      { label: "Calib label", value: "0.37", tone: "warn" },
    ],
  },
  {
    name: "Configured model env",
    source: "OPENAI_COMPATIBLE_MODEL / OPENAI_FINETUNE_MODEL",
    split: "server-side env model names; keys stay hidden",
    status: "exploratory",
    metrics: [
      { label: "Base model", value: "Loading", tone: "neutral" },
      { label: "Fine-tuned", value: "Loading", tone: "neutral" },
      { label: "Base env", value: "OPENAI_COMPATIBLE_MODEL", tone: "neutral" },
      { label: "Fine env", value: "OPENAI_FINETUNE_MODEL", tone: "neutral" },
    ],
  },
]
