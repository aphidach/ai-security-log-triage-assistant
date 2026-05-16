export const TRIAGE_LABELS = [
  "normal",
  "failed_login_bruteforce",
  "sql_injection_attempt",
  "directory_traversal_attempt",
  "port_scan_or_recon",
] as const

export type TriageLabel = (typeof TRIAGE_LABELS)[number]

export type TriageLabelMetadata = {
  displayName: string
  description: string
  isSuspicious: boolean
}

export const TRIAGE_LABEL_METADATA = {
  normal: {
    displayName: "Normal",
    description: "Routine or expected activity with no clear suspicious pattern.",
    isSuspicious: false,
  },
  failed_login_bruteforce: {
    displayName: "Failed Login Brute Force",
    description:
      "Repeated failed authentication attempts suggesting password guessing or brute force activity.",
    isSuspicious: true,
  },
  sql_injection_attempt: {
    displayName: "SQL Injection Attempt",
    description:
      "Input contains SQL injection indicators such as tautologies, UNION queries, comments, or timing payloads.",
    isSuspicious: true,
  },
  directory_traversal_attempt: {
    displayName: "Directory Traversal Attempt",
    description:
      "A path or request attempts to access files outside the intended directory.",
    isSuspicious: true,
  },
  port_scan_or_recon: {
    displayName: "Port Scan Or Recon",
    description:
      "Activity suggests scanning, probing, enumeration, or reconnaissance.",
    isSuspicious: true,
  },
} satisfies Record<TriageLabel, TriageLabelMetadata>

export const TRIAGE_LABEL_SET: ReadonlySet<TriageLabel> = new Set(TRIAGE_LABELS)

export function isTriageLabel(value: unknown): value is TriageLabel {
  return typeof value === "string" && TRIAGE_LABEL_SET.has(value as TriageLabel)
}
