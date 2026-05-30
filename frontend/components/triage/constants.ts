import type { AnalyzerOption } from "./types"

export const ANALYZERS: AnalyzerOption[] = [
  {
    id: "heuristic",
    label: "Heuristic",
    detail: "Local baseline",
  },
  {
    id: "base-model",
    label: "Base model",
    detail: "OpenAI-compatible",
  },
  {
    id: "fine-tuned",
    label: "Fine-tuned",
    detail: "Adapter endpoint",
  },
]

export const HERO_STATS = [
  { label: "Fixed split baseline", value: "1.00", detail: "label accuracy" },
  { label: "Schema parse", value: "100%", detail: "structured output" },
  { label: "POC taxonomy", value: "5", detail: "labels in scope" },
]

export const HERO_LOG_LINES = [
  "auth-01 sshd Failed password for admin repeated 18 times",
  "waf request=/login?username=admin%27%20OR%201%3D1-- status=500",
  "ids alert='nmap fingerprint' probed_ports=21,22,23,25,80,443",
  "web GET /download?file=..%2f..%2fetc%2fpasswd status=404",
]

export const SCHEMA_FIELDS = [
  "label",
  "severity",
  "is_suspicious",
  "evidence",
  "reason",
  "recommended_action",
]
