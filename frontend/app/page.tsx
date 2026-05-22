"use client"

import {
  AlertTriangle,
  Braces,
  CheckCircle2,
  CircleDot,
  ClipboardPaste,
  FileJson,
  Play,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react"
import { useMemo, useState, type ReactNode } from "react"

import { Button } from "@/components/ui/button"
import { SAMPLE_LOGS, METRIC_SNAPSHOTS, type SampleLog } from "@/lib/demo-data"
import { analyzeLogWithHeuristic } from "@/lib/heuristic-baseline"
import {
  TRIAGE_LABEL_METADATA,
  type TriageLabel,
} from "@/lib/labels"
import {
  parseTriageOutput,
  type TriageOutput,
  type TriageParseIssue,
} from "@/lib/triage-schema"
import { cn } from "@/lib/utils"

type AnalyzerId = "heuristic" | "base-model" | "fine-tuned"

type AnalyzerOption = {
  id: AnalyzerId
  label: string
  status: "ready" | "unconfigured"
}

type AnalysisState =
  | {
      kind: "idle"
    }
  | {
      kind: "result"
      output: TriageOutput
      rawJson: string
      validationIssues: TriageParseIssue[]
      elapsedMs: number
    }
  | {
      kind: "unconfigured"
      analyzer: AnalyzerOption
    }

const ANALYZERS: AnalyzerOption[] = [
  { id: "heuristic", label: "Heuristic", status: "ready" },
  { id: "base-model", label: "Base model", status: "unconfigured" },
  { id: "fine-tuned", label: "Fine-tuned", status: "unconfigured" },
]

const DEFAULT_SAMPLE = SAMPLE_LOGS[0]

export default function Home() {
  const [logInput, setLogInput] = useState(DEFAULT_SAMPLE.log)
  const [selectedSampleId, setSelectedSampleId] = useState(DEFAULT_SAMPLE.id)
  const [selectedAnalyzerId, setSelectedAnalyzerId] =
    useState<AnalyzerId>("heuristic")
  const [analysis, setAnalysis] = useState<AnalysisState>({ kind: "idle" })

  const selectedAnalyzer = useMemo(
    () =>
      ANALYZERS.find((analyzer) => analyzer.id === selectedAnalyzerId) ??
      ANALYZERS[0],
    [selectedAnalyzerId],
  )

  const result = analysis.kind === "result" ? analysis.output : null
  const labelTone = result ? getLabelTone(result.label) : null

  function selectSample(sample: SampleLog) {
    setSelectedSampleId(sample.id)
    setLogInput(sample.log)
    setAnalysis({ kind: "idle" })
  }

  function analyzeLog() {
    if (selectedAnalyzer.status !== "ready") {
      setAnalysis({ kind: "unconfigured", analyzer: selectedAnalyzer })
      return
    }

    const started = performance.now()
    const output = analyzeLogWithHeuristic(logInput.trim())
    const validation = parseTriageOutput(output)
    const elapsedMs = performance.now() - started

    setAnalysis({
      kind: "result",
      output,
      rawJson: JSON.stringify(output, null, 2),
      validationIssues: validation.ok ? [] : validation.errors,
      elapsedMs,
    })
  }

  return (
    <main className="min-h-screen bg-[#f7f8fa] text-slate-950">
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex min-w-0 items-center gap-3">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-emerald-600 text-white">
                <ShieldAlert className="size-5" aria-hidden="true" />
              </div>
              <div className="min-w-0">
                <h1 className="text-xl font-semibold text-slate-950 sm:text-2xl">
                  AI Security Log Triage Assistant
                </h1>
                <p className="mt-1 text-sm text-slate-600">
                  Phase 7 demo workspace
                </p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:justify-end">
              <StatusPill
                label="Heuristic ready"
                tone="good"
                icon={<CheckCircle2 className="size-3.5" aria-hidden="true" />}
              />
              <StatusPill
                label="Fixed split held"
                tone="warn"
                icon={<AlertTriangle className="size-3.5" aria-hidden="true" />}
              />
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto grid w-full max-w-7xl gap-5 px-4 py-5 sm:px-6 lg:grid-cols-[minmax(0,1.08fr)_minmax(380px,0.92fr)] lg:px-8">
        <div className="min-w-0 space-y-5">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center justify-between gap-3">
              <h2 className="text-sm font-semibold uppercase text-slate-500">
                Input
              </h2>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  void navigator.clipboard?.writeText(logInput)
                }}
              >
                <ClipboardPaste className="size-4" aria-hidden="true" />
                Copy
              </Button>
            </div>
            <textarea
              value={logInput}
              onChange={(event) => {
                setLogInput(event.target.value)
                setSelectedSampleId("")
                setAnalysis({ kind: "idle" })
              }}
              className="min-h-44 w-full resize-y rounded-lg border border-slate-300 bg-slate-50 p-3 font-mono text-sm leading-6 text-slate-950 outline-none ring-0 transition focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
              spellCheck={false}
            />
            <div className="mt-4 grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
              <div>
                <div className="mb-2 text-sm font-semibold text-slate-700">
                  Analyzer
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {ANALYZERS.map((analyzer) => (
                    <button
                      key={analyzer.id}
                      type="button"
                      onClick={() => {
                        setSelectedAnalyzerId(analyzer.id)
                        setAnalysis({ kind: "idle" })
                      }}
                      className={cn(
                        "flex h-12 min-w-0 items-center justify-center gap-2 rounded-lg border px-2 text-sm font-medium transition",
                        selectedAnalyzerId === analyzer.id
                          ? "border-emerald-600 bg-emerald-50 text-emerald-800"
                          : "border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50",
                      )}
                    >
                      <CircleDot className="size-3.5 shrink-0" aria-hidden="true" />
                      <span className="truncate">{analyzer.label}</span>
                    </button>
                  ))}
                </div>
              </div>
              <Button
                type="button"
                size="lg"
                onClick={analyzeLog}
                disabled={logInput.trim().length === 0}
                className="h-11 bg-emerald-700 px-4 text-white hover:bg-emerald-800"
              >
                <Play className="size-4" aria-hidden="true" />
                Analyze
              </Button>
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center justify-between gap-3">
              <h2 className="text-sm font-semibold uppercase text-slate-500">
                Samples
              </h2>
              <span className="text-sm text-slate-500">5 labels</span>
            </div>
            <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-5">
              {SAMPLE_LOGS.map((sample) => (
                <button
                  key={sample.id}
                  type="button"
                  onClick={() => selectSample(sample)}
                  className={cn(
                    "min-h-24 rounded-lg border p-3 text-left transition",
                    selectedSampleId === sample.id
                      ? "border-emerald-600 bg-emerald-50"
                      : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50",
                  )}
                >
                  <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                    {sample.label === "normal" ? (
                      <ShieldCheck className="size-4 text-emerald-700" aria-hidden="true" />
                    ) : (
                      <ShieldAlert className="size-4 text-amber-700" aria-hidden="true" />
                    )}
                    <span>{sample.name}</span>
                  </div>
                  <div className="mt-2 text-xs text-slate-500">
                    {TRIAGE_LABEL_METADATA[sample.label].displayName}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <ComparisonPanel />
        </div>

        <div className="min-w-0 space-y-5">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center justify-between gap-3">
              <h2 className="text-sm font-semibold uppercase text-slate-500">
                Result
              </h2>
              {analysis.kind === "result" ? (
                <span className="text-sm text-slate-500">
                  {analysis.elapsedMs.toFixed(2)} ms
                </span>
              ) : null}
            </div>

            {analysis.kind === "idle" ? (
              <EmptyState />
            ) : null}

            {analysis.kind === "unconfigured" ? (
              <UnconfiguredState analyzer={analysis.analyzer} />
            ) : null}

            {analysis.kind === "result" && result ? (
              <div className="space-y-4">
                <div
                  className={cn(
                    "border-l-4 px-4 py-3",
                    labelTone === "normal"
                      ? "border-emerald-500 bg-emerald-50"
                      : "border-amber-500 bg-amber-50",
                  )}
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <div className="text-sm text-slate-600">Label</div>
                      <div className="mt-1 text-2xl font-semibold text-slate-950">
                        {TRIAGE_LABEL_METADATA[result.label].displayName}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <ResultBadge tone={labelTone ?? "normal"}>
                        {result.is_suspicious ? "Suspicious" : "Normal"}
                      </ResultBadge>
                      <ResultBadge tone={getSeverityTone(result.severity)}>
                        {result.severity}
                      </ResultBadge>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="mb-2 text-sm font-semibold text-slate-700">
                    Evidence highlight
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-950 p-3 font-mono text-sm leading-6 text-slate-100">
                    {highlightEvidence(logInput, result.evidence)}
                  </div>
                </div>

                <FieldBlock title="Evidence">
                  <div className="flex flex-wrap gap-2">
                    {result.evidence.map((item) => (
                      <span
                        key={item}
                        className="rounded-md border border-sky-200 bg-sky-50 px-2 py-1 font-mono text-xs text-sky-900"
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </FieldBlock>

                <FieldBlock title="Reason">{result.reason}</FieldBlock>
                <FieldBlock title="Recommended action">
                  {result.recommended_action}
                </FieldBlock>

                {analysis.validationIssues.length > 0 ? (
                  <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
                    {analysis.validationIssues.map((issue) => (
                      <div key={`${issue.path}-${issue.message}`}>
                        {issue.path}: {issue.message}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm font-medium text-emerald-800">
                    <CheckCircle2 className="size-4" aria-hidden="true" />
                    Schema-valid output
                  </div>
                )}
              </div>
            ) : null}
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              <FileJson className="size-4 text-slate-500" aria-hidden="true" />
              <h2 className="text-sm font-semibold uppercase text-slate-500">
                Raw JSON
              </h2>
            </div>
            <pre className="min-h-72 overflow-auto rounded-lg border border-slate-200 bg-slate-950 p-3 text-xs leading-5 text-slate-100">
              {analysis.kind === "result"
                ? analysis.rawJson
                : analysis.kind === "unconfigured"
                  ? JSON.stringify(
                      {
                        status: "unconfigured",
                        analyzer: analysis.analyzer.id,
                      },
                      null,
                      2,
                    )
                : "{\n  \"status\": \"pending\"\n}"}
            </pre>
          </div>
        </div>
      </section>
    </main>
  )
}

function ComparisonPanel() {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase text-slate-500">
          Comparison
        </h2>
        <span className="text-sm text-slate-500">Current artifacts</span>
      </div>
      <div className="grid gap-3 xl:grid-cols-3">
        {METRIC_SNAPSHOTS.map((snapshot) => (
          <article
            key={snapshot.name}
            className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="text-base font-semibold text-slate-950">
                  {snapshot.name}
                </h3>
                <p className="mt-1 text-xs text-slate-500">{snapshot.split}</p>
              </div>
              <StatusDot status={snapshot.status} />
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-2">
              {snapshot.metrics.map((metric) => (
                <div
                  key={`${snapshot.name}-${metric.label}`}
                  className="rounded-md border border-slate-200 bg-slate-50 p-2"
                >
                  <dt className="text-xs text-slate-500">{metric.label}</dt>
                  <dd
                    className={cn(
                      "mt-1 text-sm font-semibold",
                      metric.tone === "good" && "text-emerald-700",
                      metric.tone === "warn" && "text-amber-700",
                      metric.tone === "neutral" && "text-slate-800",
                    )}
                  >
                    {metric.value}
                  </dd>
                </div>
              ))}
            </dl>
            <p className="mt-3 break-words font-mono text-xs text-slate-500">
              {snapshot.source}
            </p>
          </article>
        ))}
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
      <Braces className="size-8 text-slate-400" aria-hidden="true" />
      <div className="mt-3 text-sm font-medium text-slate-600">
        No analysis yet
      </div>
    </div>
  )
}

function UnconfiguredState({ analyzer }: { analyzer: AnalyzerOption }) {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center rounded-lg border border-amber-200 bg-amber-50 p-6 text-center">
      <AlertTriangle className="size-8 text-amber-700" aria-hidden="true" />
      <div className="mt-3 text-base font-semibold text-amber-950">
        {analyzer.label} is not configured
      </div>
      <div className="mt-2 max-w-sm text-sm text-amber-800">
        No endpoint configured.
      </div>
    </div>
  )
}

function FieldBlock({
  title,
  children,
}: {
  title: string
  children: ReactNode
}) {
  return (
    <div className="border-t border-slate-200 pt-3">
      <div className="mb-2 text-sm font-semibold text-slate-700">{title}</div>
      <div className="text-sm leading-6 text-slate-700">{children}</div>
    </div>
  )
}

function StatusPill({
  label,
  tone,
  icon,
}: {
  label: string
  tone: "good" | "warn"
  icon: ReactNode
}) {
  return (
    <span
      className={cn(
        "inline-flex h-8 items-center justify-center gap-1.5 rounded-lg border px-2 text-sm font-medium",
        tone === "good" && "border-emerald-200 bg-emerald-50 text-emerald-800",
        tone === "warn" && "border-amber-200 bg-amber-50 text-amber-800",
      )}
    >
      {icon}
      {label}
    </span>
  )
}

function ResultBadge({
  tone,
  children,
}: {
  tone: "normal" | "suspicious" | "low" | "medium" | "high" | "critical"
  children: ReactNode
}) {
  return (
    <span
      className={cn(
        "inline-flex h-8 items-center rounded-lg border px-2 text-sm font-semibold capitalize",
        tone === "normal" && "border-emerald-300 bg-white text-emerald-800",
        tone === "suspicious" && "border-amber-300 bg-white text-amber-800",
        tone === "low" && "border-slate-300 bg-white text-slate-700",
        tone === "medium" && "border-sky-300 bg-white text-sky-800",
        tone === "high" && "border-amber-300 bg-white text-amber-800",
        tone === "critical" && "border-red-300 bg-white text-red-800",
      )}
    >
      {children}
    </span>
  )
}

function StatusDot({ status }: { status: "ready" | "exploratory" | "unconfigured" }) {
  return (
    <span
      className={cn(
        "inline-flex h-7 items-center rounded-lg border px-2 text-xs font-semibold capitalize",
        status === "ready" && "border-emerald-200 bg-emerald-50 text-emerald-800",
        status === "exploratory" && "border-amber-200 bg-amber-50 text-amber-800",
        status === "unconfigured" && "border-slate-200 bg-slate-50 text-slate-600",
      )}
    >
      {status}
    </span>
  )
}

function highlightEvidence(logLine: string, evidence: string[]) {
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
        className="rounded bg-yellow-300 px-0.5 text-slate-950"
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

function getLabelTone(label: TriageLabel): "normal" | "suspicious" {
  return label === "normal" ? "normal" : "suspicious"
}

function getSeverityTone(
  severity: TriageOutput["severity"],
): "low" | "medium" | "high" | "critical" {
  return severity
}
