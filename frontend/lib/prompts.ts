import { TRIAGE_LABEL_METADATA, TRIAGE_LABELS } from "./labels"
import { TRIAGE_OUTPUT_KEYS, TRIAGE_SEVERITIES } from "./triage-schema"

export const TRIAGE_PROMPT_VERSION = "triage-json-v1"

export type TriagePromptMessage = {
  role: "system" | "user"
  content: string
}

const OUTPUT_SCHEMA_EXAMPLE = `{
  "label": "sql_injection_attempt",
  "severity": "high",
  "is_suspicious": true,
  "evidence": ["' OR '1'='1"],
  "reason": "The request contains a common SQL injection pattern.",
  "recommended_action": "Review web application logs and block or rate-limit the source IP."
}`

const LABEL_DEFINITIONS = TRIAGE_LABELS.map((label) => {
  const metadata = TRIAGE_LABEL_METADATA[label]
  return `- ${label}: ${metadata.description}`
}).join("\n")

const OUTPUT_FIELDS = TRIAGE_OUTPUT_KEYS.map((key) => `- ${key}`).join("\n")

const SEVERITY_VALUES = TRIAGE_SEVERITIES.map((severity) => `- ${severity}`).join(
  "\n",
)

export const TRIAGE_SYSTEM_PROMPT = [
  "You are a security log triage assistant.",
  "Analyze exactly one security log input and classify it for investigation.",
  "Use triage language only. Do not claim that a system is compromised.",
  "",
  "Return only one valid JSON object.",
  "Do not include markdown, code fences, comments, or explanatory text outside JSON.",
  "Do not add fields beyond the required schema.",
  "",
  "Required output fields:",
  OUTPUT_FIELDS,
  "",
  "Allowed labels:",
  LABEL_DEFINITIONS,
  "Choose exactly one label. If no listed suspicious pattern is present, use normal.",
  "",
  "Allowed severity values:",
  SEVERITY_VALUES,
  "Set is_suspicious to false only for normal. Set it to true for every other label.",
  "",
  "Evidence rules:",
  "- evidence must be an array of short substrings or concrete facts from the input log.",
  "- Do not invent evidence that is not present in the input.",
  "- For normal activity, cite the log detail that makes it routine or expected.",
  "",
  "Default severity guidance:",
  "- normal: low",
  "- failed_login_bruteforce: medium, or high when the repeated failure volume is clearly large.",
  "- sql_injection_attempt: high",
  "- directory_traversal_attempt: high",
  "- port_scan_or_recon: medium, or high when the scan is explicit or broad.",
  "",
  "Output schema example:",
  OUTPUT_SCHEMA_EXAMPLE,
].join("\n")

export function buildTriageUserPrompt(logLine: string): string {
  return [
    "Analyze this security log and classify whether it is suspicious.",
    "",
    "Log:",
    logLine,
  ].join("\n")
}

export function buildTriagePromptMessages(
  logLine: string,
): TriagePromptMessage[] {
  return [
    {
      role: "system",
      content: TRIAGE_SYSTEM_PROMPT,
    },
    {
      role: "user",
      content: buildTriageUserPrompt(logLine),
    },
  ]
}
