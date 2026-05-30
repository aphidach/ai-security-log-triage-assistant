import type { ReactNode } from "react"

import type { MetricSnapshot } from "@/lib/demo-data"
import { METRIC_SNAPSHOTS } from "@/lib/demo-data"
import type { TriageLabel } from "@/lib/labels"
import type { TriageOutput } from "@/lib/triage-schema"

import type { PublicTriageConfig } from "./types"

export function buildMetricSnapshots(
  triageConfig: PublicTriageConfig | null,
): MetricSnapshot[] {
  const baseModel = triageConfig?.endpoints.baseModel
  const fineTuned = triageConfig?.endpoints.fineTuned
  const endpointsConfigured = Boolean(
    baseModel?.configured && fineTuned?.configured,
  )
  const configSnapshot: MetricSnapshot = {
    name: "Configured model env",
    source: "OPENAI_COMPATIBLE_MODEL / OPENAI_FINETUNE_MODEL",
    split: "server-side env model names; keys stay hidden",
    status: triageConfig
      ? endpointsConfigured
        ? "ready"
        : "unconfigured"
      : "exploratory",
    metrics: [
      {
        label: "Base model",
        value: triageConfig ? (baseModel?.model ?? "Not set") : "Loading",
        tone: baseModel?.model ? "neutral" : "warn",
      },
      {
        label: "Fine-tuned",
        value: triageConfig ? (fineTuned?.model ?? "Not set") : "Loading",
        tone: fineTuned?.model ? "neutral" : "warn",
      },
      {
        label: "Base env",
        value: baseModel?.modelEnv ?? "OPENAI_COMPATIBLE_MODEL",
        tone: "neutral",
      },
      {
        label: "Fine env",
        value: fineTuned?.modelEnv ?? "OPENAI_FINETUNE_MODEL",
        tone: "neutral",
      },
    ],
  }

  return [...METRIC_SNAPSHOTS.slice(0, -1), configSnapshot]
}

export function getLabelTone(label: TriageLabel): "normal" | "suspicious" {
  return label === "normal" ? "normal" : "suspicious"
}

export function getSeverityTone(
  severity: TriageOutput["severity"],
): "low" | "medium" | "high" | "critical" {
  return severity
}

export function highlightEvidence(logLine: string, evidence: string[]) {
  const ranges = evidence
    .map((item) => {
      const start = logLine.indexOf(item)
      return start >= 0 ? { start, end: start + item.length } : null
    })
    .filter((range): range is { start: number; end: number } => range !== null)
    .sort((left, right) => left.start - right.start)

  if (ranges.length === 0) {
    return logLine
  }

  const parts: ReactNode[] = []
  let cursor = 0

  ranges.forEach((range, index) => {
    if (range.start < cursor) {
      return
    }
    if (range.start > cursor) {
      parts.push(logLine.slice(cursor, range.start))
    }
    parts.push(
      <mark
        key={`${range.start}-${range.end}-${index}`}
        className="rounded-[4px] bg-[#F0ABFC]/25 px-1 text-[#F5D0FE] ring-1 ring-[#C084FC]/40"
      >
        {logLine.slice(range.start, range.end)}
      </mark>,
    )
    cursor = range.end
  })

  if (cursor < logLine.length) {
    parts.push(logLine.slice(cursor))
  }

  return parts
}

export function scrollToSection(id: string) {
  document.getElementById(id)?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  })
}
