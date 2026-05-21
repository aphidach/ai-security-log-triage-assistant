import { isTriageLabel, type TriageLabel } from "./labels"

export const TRIAGE_SEVERITIES = ["low", "medium", "high", "critical"] as const
export const TRIAGE_EVIDENCE_MIN_ITEMS = 1
export const TRIAGE_EVIDENCE_MAX_ITEMS = 3
export const TRIAGE_EVIDENCE_MAX_LENGTH = 160

export type TriageSeverity = (typeof TRIAGE_SEVERITIES)[number]

export type TriageOutput = {
  label: TriageLabel
  severity: TriageSeverity
  is_suspicious: boolean
  evidence: string[]
  reason: string
  recommended_action: string
}

export const TRIAGE_OUTPUT_KEYS = [
  "label",
  "severity",
  "is_suspicious",
  "evidence",
  "reason",
  "recommended_action",
] as const

export type TriageOutputKey = (typeof TRIAGE_OUTPUT_KEYS)[number]

export type TriageParseIssue = {
  path: string
  message: string
}

export type TriageParseResult =
  | {
      ok: true
      data: TriageOutput
    }
  | {
      ok: false
      errors: TriageParseIssue[]
    }

const TRIAGE_SEVERITY_SET: ReadonlySet<TriageSeverity> = new Set(
  TRIAGE_SEVERITIES,
)

const TRIAGE_OUTPUT_KEY_SET: ReadonlySet<string> = new Set(TRIAGE_OUTPUT_KEYS)

export function isTriageSeverity(value: unknown): value is TriageSeverity {
  return (
    typeof value === "string" &&
    TRIAGE_SEVERITY_SET.has(value as TriageSeverity)
  )
}

export function parseTriageOutput(value: unknown): TriageParseResult {
  const errors: TriageParseIssue[] = []

  if (!isPlainRecord(value)) {
    return {
      ok: false,
      errors: [
        {
          path: "$",
          message: "Expected triage output to be an object.",
        },
      ],
    }
  }

  const candidate = value

  for (const key of Object.keys(candidate)) {
    if (!TRIAGE_OUTPUT_KEY_SET.has(key)) {
      errors.push({
        path: `$.${key}`,
        message: "Unexpected field is not allowed.",
      })
    }
  }

  if (!isTriageLabel(candidate.label)) {
    errors.push({
      path: "$.label",
      message: "Expected one of the supported triage labels.",
    })
  }

  if (!isTriageSeverity(candidate.severity)) {
    errors.push({
      path: "$.severity",
      message: "Expected severity to be low, medium, high, or critical.",
    })
  }

  if (typeof candidate.is_suspicious !== "boolean") {
    errors.push({
      path: "$.is_suspicious",
      message: "Expected is_suspicious to be a boolean.",
    })
  }

  if (!Array.isArray(candidate.evidence)) {
    errors.push({
      path: "$.evidence",
      message: "Expected evidence to be an array of non-empty strings.",
    })
  } else {
    if (
      candidate.evidence.length < TRIAGE_EVIDENCE_MIN_ITEMS ||
      candidate.evidence.length > TRIAGE_EVIDENCE_MAX_ITEMS
    ) {
      errors.push({
        path: "$.evidence",
        message: "Expected evidence to contain one to three items.",
      })
    }
    candidate.evidence.forEach((item, index) => {
      if (typeof item !== "string" || item.length === 0) {
        errors.push({
          path: `$.evidence[${index}]`,
          message: "Expected evidence item to be a non-empty string.",
        })
      } else if (item.length > TRIAGE_EVIDENCE_MAX_LENGTH) {
        errors.push({
          path: `$.evidence[${index}]`,
          message: "Expected evidence item to be 160 characters or fewer.",
        })
      }
    })
  }

  if (typeof candidate.reason !== "string" || candidate.reason.length === 0) {
    errors.push({
      path: "$.reason",
      message: "Expected reason to be a non-empty string.",
    })
  }

  if (
    typeof candidate.recommended_action !== "string" ||
    candidate.recommended_action.length === 0
  ) {
    errors.push({
      path: "$.recommended_action",
      message: "Expected recommended_action to be a non-empty string.",
    })
  }

  if (errors.length > 0) {
    return {
      ok: false,
      errors,
    }
  }

  return {
    ok: true,
    data: candidate as TriageOutput,
  }
}

export function isTriageOutput(value: unknown): value is TriageOutput {
  return parseTriageOutput(value).ok
}

function isPlainRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value)
}
