import { TRIAGE_LABELS } from "./labels"
import {
  TRIAGE_EVIDENCE_MAX_ITEMS,
  TRIAGE_EVIDENCE_MAX_LENGTH,
  TRIAGE_EVIDENCE_MIN_ITEMS,
  TRIAGE_OUTPUT_KEYS,
  TRIAGE_SEVERITIES,
} from "./triage-schema"

export const TRIAGE_PROVIDER_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: TRIAGE_OUTPUT_KEYS,
  properties: {
    label: {
      type: "string",
      enum: TRIAGE_LABELS,
    },
    severity: {
      type: "string",
      enum: TRIAGE_SEVERITIES,
    },
    is_suspicious: {
      type: "boolean",
    },
    evidence: {
      type: "array",
      minItems: TRIAGE_EVIDENCE_MIN_ITEMS,
      maxItems: TRIAGE_EVIDENCE_MAX_ITEMS,
      items: {
        type: "string",
        minLength: 1,
        maxLength: TRIAGE_EVIDENCE_MAX_LENGTH,
      },
    },
    reason: {
      type: "string",
      minLength: 1,
    },
    recommended_action: {
      type: "string",
      minLength: 1,
    },
  },
} as const
