"use client"

import {
  AlertTriangle,
  Braces,
  CheckCircle2,
  CircleDot,
  ClipboardPaste,
  FileJson,
  Loader2,
  Play,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react"
import { useEffect, useMemo, useState, type ReactNode } from "react"

import { Button } from "@/components/ui/button"
import {
  SAMPLE_LOGS,
  METRIC_SNAPSHOTS,
  type MetricSnapshot,
  type SampleLog,
} from "@/lib/demo-data"
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
}

type AnalysisState =
  | {
      kind: "idle"
    }
  | {
      kind: "loading"
      analyzer: AnalyzerOption
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
      message: string
    }
  | {
      kind: "error"
      analyzer: AnalyzerOption
      message: string
      rawJson?: string
      validationIssues?: TriageParseIssue[]
    }

type TriageApiSuccess = {
  output: TriageOutput
  rawJson: string
  validationIssues: TriageParseIssue[]
  elapsedMs: number
}

type TriageApiError = {
  error: string
  code?: string
  rawJson?: string
  validationIssues?: TriageParseIssue[]
}

type TriageApiResponse = TriageApiSuccess | TriageApiError

type PublicEndpointConfig = {
  analyzer: Exclude<AnalyzerId, "heuristic">
  label: string
  modelEnv: string
  model: string | null
  configured: boolean
}

type PublicTriageConfig = {
  endpoints: {
    baseModel: PublicEndpointConfig
    fineTuned: PublicEndpointConfig
  }
}

const ANALYZERS: AnalyzerOption[] = [
  { id: "heuristic", label: "Heuristic" },
  { id: "base-model", label: "Base model" },
  { id: "fine-tuned", label: "Fine-tuned" },
]

const DEFAULT_SAMPLE = SAMPLE_LOGS[0]

export default function Home() {
  const [logInput, setLogInput] = useState(DEFAULT_SAMPLE.log)
  const [selectedSampleId, setSelectedSampleId] = useState(DEFAULT_SAMPLE.id)
  const [selectedAnalyzerId, setSelectedAnalyzerId] =
    useState<AnalyzerId>("heuristic")
  const [analysis, setAnalysis] = useState<AnalysisState>({ kind: "idle" })
  const [triageConfig, setTriageConfig] = useState<PublicTriageConfig | null>(
    null,
  )

  const selectedAnalyzer = useMemo(
    () =>
      ANALYZERS.find((analyzer) => analyzer.id === selectedAnalyzerId) ??
      ANALYZERS[0],
    [selectedAnalyzerId],
  )

  const result = analysis.kind === "result" ? analysis.output : null
  const labelTone = result ? getLabelTone(result.label) : null
  const metricSnapshots = useMemo(
    () => buildMetricSnapshots(triageConfig),
    [triageConfig],
  )

  useEffect(() => {
    let isMounted = true

    async function loadTriageConfig() {
      try {
        const response = await fetch("/api/triage")
        if (!response.ok) {
          return
        }
        const payload = (await response.json()) as PublicTriageConfig
        if (isMounted) {
          setTriageConfig(payload)
        }
      } catch {
        // Keep the static loading snapshot if config metadata cannot be read.
      }
    }

    void loadTriageConfig()

    return () => {
      isMounted = false
    }
  }, [])

  function selectSample(sample: SampleLog) {
    setSelectedSampleId(sample.id)
    setLogInput(sample.log)
    setAnalysis({ kind: "idle" })
  }

  async function analyzeLog() {
    const analyzer = selectedAnalyzer
    setAnalysis({ kind: "loading", analyzer })

    try {
      const response = await fetch("/api/triage", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          analyzer: analyzer.id,
          logLine: logInput.trim(),
        }),
      })
      const payload = (await response.json()) as TriageApiResponse

      if (!response.ok || "error" in payload) {
        const message =
          "error" in payload ? payload.error : "Analyzer request failed."
        if ("code" in payload && payload.code === "unconfigured") {
          setAnalysis({
            kind: "unconfigured",
            analyzer,
            message,
          })
          return
        }
        setAnalysis({
          kind: "error",
          analyzer,
          message,
          rawJson: "rawJson" in payload ? payload.rawJson : undefined,
          validationIssues:
            "validationIssues" in payload ? payload.validationIssues : undefined,
        })
        return
      }

      const validation = parseTriageOutput(payload.output)
      setAnalysis({
        kind: "result",
        output: payload.output,
        rawJson: payload.rawJson,
        validationIssues: validation.ok ? payload.validationIssues : validation.errors,
        elapsedMs: payload.elapsedMs,
      })
    } catch (error) {
      setAnalysis({
        kind: "error",
        analyzer,
        message:
          error instanceof Error
            ? `${error.name}: ${error.message}`
            : "Analyzer request failed.",
      })
    }
  }

  return (
    <main className="min-h-screen bg-[#0B0C0F] text-[#EAEAF0]">
      <TopNav analysis={analysis} />
      <div className="flex min-h-[calc(100vh-48px)]">
        <AppSidebar selectedAnalyzer={selectedAnalyzer.label} />

        <section className="min-w-0 flex-1">
          <div className="grid w-full gap-4 p-3 sm:p-4 xl:grid-cols-[minmax(0,1.08fr)_minmax(380px,0.92fr)]">
            <div className="min-w-0 space-y-4">
              <Panel id="triage-input">
                <SectionHeader
                  eyebrow="Input"
                  title="Log event"
                  meta="single event"
                  icon={<Braces className="size-4" aria-hidden="true" />}
                  action={
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        void navigator.clipboard?.writeText(logInput)
                      }}
                      className="min-h-11 md:min-h-8"
                    >
                      <ClipboardPaste className="size-4" aria-hidden="true" />
                      Copy
                    </Button>
                  }
                />

                <textarea
                  value={logInput}
                  onChange={(event) => {
                    setLogInput(event.target.value)
                    setSelectedSampleId("")
                    setAnalysis({ kind: "idle" })
                  }}
                  className="mt-3 min-h-44 w-full resize-y rounded-[6px] border border-[#35363D] bg-[#27282F] p-3 font-mono text-[13px] leading-6 text-[#EAEAF0] outline-none transition placeholder:text-[#5A5C66] focus:border-[#AE4DFF] focus:ring-3 focus:ring-[#AE4DFF]/30"
                  spellCheck={false}
                />

                <div className="mt-4 grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
                  <div>
                    <div className="mb-2 text-xs font-semibold text-[#8B8D97]">
                      Analyzer
                    </div>
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
                      {ANALYZERS.map((analyzer) => (
                        <button
                          key={analyzer.id}
                          type="button"
                          onClick={() => {
                            setSelectedAnalyzerId(analyzer.id)
                            setAnalysis({ kind: "idle" })
                          }}
                          className={cn(
                            "flex min-h-11 min-w-0 cursor-pointer items-center justify-center gap-2 rounded-[6px] border px-3 text-sm font-semibold transition outline-none focus-visible:border-[#AE4DFF] focus-visible:ring-3 focus-visible:ring-[#AE4DFF]/30",
                            selectedAnalyzerId === analyzer.id
                              ? "border-[#AE4DFF] bg-[#AE4DFF]/15 text-white"
                              : "border-[#35363D] bg-transparent text-[#EAEAF0] hover:border-[#4A4B54] hover:bg-[#27282F]",
                          )}
                        >
                          <CircleDot
                            className={cn(
                              "size-3.5 shrink-0",
                              selectedAnalyzerId === analyzer.id
                                ? "text-[#AE4DFF]"
                                : "text-[#8B8D97]",
                            )}
                            aria-hidden="true"
                          />
                          <span>{analyzer.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  <Button
                    type="button"
                    size="lg"
                    onClick={() => {
                      void analyzeLog()
                    }}
                    disabled={
                      logInput.trim().length === 0 || analysis.kind === "loading"
                    }
                    className="min-h-11 px-5"
                  >
                    {analysis.kind === "loading" ? (
                      <Loader2 className="size-4 animate-spin" aria-hidden="true" />
                    ) : (
                      <Play className="size-4" aria-hidden="true" />
                    )}
                    Analyze
                  </Button>
                </div>
              </Panel>

              <Panel id="samples">
                <SectionHeader
                  eyebrow="Samples"
                  title="Coverage set"
                  meta="5 labels"
                  icon={<ShieldAlert className="size-4" aria-hidden="true" />}
                />
                <div className="mt-3 grid gap-2 sm:grid-cols-2 2xl:grid-cols-5">
                  {SAMPLE_LOGS.map((sample) => (
                    <button
                      key={sample.id}
                      type="button"
                      onClick={() => selectSample(sample)}
                      className={cn(
                        "min-h-24 cursor-pointer rounded-lg border p-3 text-left transition outline-none focus-visible:border-[#AE4DFF] focus-visible:ring-3 focus-visible:ring-[#AE4DFF]/30",
                        selectedSampleId === sample.id
                          ? "border-[#AE4DFF] bg-[#AE4DFF]/10"
                          : "border-[#35363D] bg-[#111216] hover:border-[#4A4B54] hover:bg-[#27282F]",
                      )}
                    >
                      <div className="flex items-center gap-2 text-sm font-semibold text-[#EAEAF0]">
                        {sample.label === "normal" ? (
                          <ShieldCheck
                            className="size-4 text-[#8B8D97]"
                            aria-hidden="true"
                          />
                        ) : (
                          <ShieldAlert
                            className="size-4 text-[#F59E0B]"
                            aria-hidden="true"
                          />
                        )}
                        <span>{sample.name}</span>
                      </div>
                      <div className="mt-2 text-xs leading-5 text-[#8B8D97]">
                        {TRIAGE_LABEL_METADATA[sample.label].displayName}
                      </div>
                    </button>
                  ))}
                </div>
              </Panel>

              <ComparisonPanel snapshots={metricSnapshots} />
            </div>

            <div className="min-w-0 space-y-4">
              <Panel id="result-panel">
                <SectionHeader
                  eyebrow="Result"
                  title="Structured triage"
                  meta={
                    analysis.kind === "result"
                      ? `${analysis.elapsedMs.toFixed(2)} ms`
                      : "pending"
                  }
                  icon={<ShieldCheck className="size-4" aria-hidden="true" />}
                />

                <div className="mt-3">
                  {analysis.kind === "idle" ? <EmptyState /> : null}

                  {analysis.kind === "loading" ? (
                    <LoadingState analyzer={analysis.analyzer} />
                  ) : null}

                  {analysis.kind === "unconfigured" ? (
                    <UnconfiguredState
                      analyzer={analysis.analyzer}
                      message={analysis.message}
                    />
                  ) : null}

                  {analysis.kind === "error" ? (
                    <ErrorState
                      message={analysis.message}
                      validationIssues={analysis.validationIssues}
                    />
                  ) : null}

                  {analysis.kind === "result" && result ? (
                    <div className="space-y-4">
                      <div
                        className={cn(
                          "rounded-lg border p-4",
                          labelTone === "normal"
                            ? "border-[#35363D] bg-[#111216]"
                            : "border-[#F59E0B]/50 bg-[#F59E0B]/10",
                        )}
                      >
                        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                          <div>
                            <div className="text-xs font-medium text-[#8B8D97]">
                              Label
                            </div>
                            <div className="mt-1 text-xl font-semibold leading-tight text-[#EAEAF0]">
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

                      <FieldBlock title="Evidence highlight">
                        <div className="overflow-x-auto whitespace-pre-wrap break-words rounded-[6px] border border-[#35363D] bg-[#0B0C0F] p-3 font-mono text-[13px] leading-6 text-[#EAEAF0]">
                          {highlightEvidence(logInput, result.evidence)}
                        </div>
                      </FieldBlock>

                      <FieldBlock title="Evidence">
                        <div className="flex flex-wrap gap-2">
                          {result.evidence.map((item) => (
                            <span
                              key={item}
                              className="rounded-[4px] border border-[#4F8EF7]/40 bg-[#4F8EF7]/10 px-2 py-1 font-mono text-xs leading-5 text-[#AECBFF]"
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
                        <div className="rounded-lg border border-[#EF4444]/40 bg-[#EF4444]/10 p-3 text-sm leading-6 text-[#FCA5A5]">
                          {analysis.validationIssues.map((issue) => (
                            <div key={`${issue.path}-${issue.message}`}>
                              {issue.path}: {issue.message}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 rounded-lg border border-[#4F8EF7]/40 bg-[#4F8EF7]/10 p-3 text-sm font-semibold text-[#AECBFF]">
                          <CheckCircle2 className="size-4" aria-hidden="true" />
                          Schema-valid output
                        </div>
                      )}
                    </div>
                  ) : null}
                </div>
              </Panel>

              <Panel id="raw-json">
                <SectionHeader
                  eyebrow="Raw JSON"
                  title="Output payload"
                  icon={<FileJson className="size-4" aria-hidden="true" />}
                />
                <pre className="mt-3 min-h-72 overflow-auto rounded-[6px] border border-[#35363D] bg-[#0B0C0F] p-3 font-mono text-xs leading-5 text-[#EAEAF0]">
                  {analysis.kind === "result"
                    ? analysis.rawJson
                    : analysis.kind === "unconfigured"
                      ? JSON.stringify(
                          {
                            status: "unconfigured",
                            analyzer: analysis.analyzer.id,
                            message: analysis.message,
                          },
                          null,
                          2,
                        )
                      : analysis.kind === "error"
                        ? analysis.rawJson ??
                          JSON.stringify(
                            {
                              status: "error",
                              analyzer: analysis.analyzer.id,
                              message: analysis.message,
                            },
                            null,
                            2,
                          )
                        : analysis.kind === "loading"
                          ? JSON.stringify(
                              {
                                status: "running",
                                analyzer: analysis.analyzer.id,
                              },
                              null,
                              2,
                            )
                          : "{\n  \"status\": \"pending\"\n}"}
                </pre>
              </Panel>
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}

function TopNav({ analysis }: { analysis: AnalysisState }) {
  return (
    <header className="sticky top-0 z-20 flex h-12 items-center justify-between border-b border-[#1C1D22] bg-[#0B0C0F] px-3 sm:px-4">
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex size-8 shrink-0 items-center justify-center rounded-[6px] bg-[#AE4DFF] text-white">
          <ShieldAlert className="size-4" aria-hidden="true" />
        </div>
        <div className="min-w-0">
          <h1 className="truncate text-sm font-bold leading-tight text-[#EAEAF0] sm:text-base">
            AI Security Log Triage Assistant
          </h1>
          <p className="hidden text-xs leading-tight text-[#8B8D97] sm:block">
            Phase 7 demo workspace
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <StatusPill
          label="Heuristic ready"
          tone="info"
          icon={<CheckCircle2 className="size-3.5" aria-hidden="true" />}
        />
        <StatusPill
          label="Fixed split held"
          tone="warn"
          icon={<AlertTriangle className="size-3.5" aria-hidden="true" />}
        />
        {analysis.kind === "loading" ? (
          <span className="hidden h-8 items-center gap-1.5 rounded-[6px] border border-[#35363D] bg-[#27282F] px-2 text-xs font-semibold text-[#8B8D97] sm:inline-flex">
            <Loader2 className="size-3.5 animate-spin" aria-hidden="true" />
            Running
          </span>
        ) : null}
      </div>
    </header>
  )
}

function AppSidebar({ selectedAnalyzer }: { selectedAnalyzer: string }) {
  const items = [
    {
      label: "Triage",
      icon: ShieldAlert,
      active: true,
      targetId: "triage-input",
    },
    { label: "Samples", icon: Braces, active: false, targetId: "samples" },
    {
      label: "Results",
      icon: ShieldCheck,
      active: false,
      targetId: "result-panel",
    },
    { label: "JSON", icon: FileJson, active: false, targetId: "raw-json" },
  ]

  return (
    <aside className="sticky top-12 hidden h-[calc(100vh-48px)] w-16 shrink-0 flex-col border-r border-[#1C1D22] bg-[#0B0C0F] p-2 md:flex lg:w-60">
      <div className="space-y-1">
        {items.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.label}
              type="button"
              title={item.label}
              onClick={() => {
                document.getElementById(item.targetId)?.scrollIntoView({
                  behavior: "smooth",
                  block: "start",
                })
              }}
              className={cn(
                "flex min-h-11 w-full cursor-pointer items-center justify-center gap-3 rounded-[6px] px-3 text-sm font-semibold transition outline-none focus-visible:border-[#AE4DFF] focus-visible:ring-3 focus-visible:ring-[#AE4DFF]/30 lg:justify-start",
                item.active
                  ? "bg-[#AE4DFF]/15 text-white"
                  : "text-[#8B8D97] hover:bg-[#1C1D22] hover:text-[#EAEAF0]",
              )}
            >
              <Icon
                className={cn(
                  "size-4 shrink-0",
                  item.active ? "text-[#AE4DFF]" : "text-[#8B8D97]",
                )}
                aria-hidden="true"
              />
              <span className="hidden lg:inline">{item.label}</span>
            </button>
          )
        })}
      </div>

      <div className="mt-auto hidden rounded-lg border border-[#35363D] bg-[#1C1D22] p-3 lg:block">
        <div className="text-xs font-medium text-[#8B8D97]">Analyzer</div>
        <div className="mt-1 text-sm font-semibold text-[#EAEAF0]">
          {selectedAnalyzer}
        </div>
      </div>
    </aside>
  )
}

function buildMetricSnapshots(
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

function ComparisonPanel({ snapshots }: { snapshots: MetricSnapshot[] }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="text-xs font-semibold text-[#8B8D97]">Comparison</div>
          <h2 className="text-base font-semibold text-[#EAEAF0]">
            Current artifacts
          </h2>
        </div>
        <span className="rounded-full border border-[#35363D] px-2 py-1 text-xs text-[#8B8D97]">
          docs + env
        </span>
      </div>
      <div className="grid gap-3 xl:grid-cols-3">
        {snapshots.map((snapshot) => (
          <article
            key={snapshot.name}
            className="min-w-0 rounded-lg border border-[#35363D] bg-[#1C1D22] p-4 shadow-[0_0_0_1px_rgba(255,255,255,0.05)]"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-[#EAEAF0]">
                  {snapshot.name}
                </h3>
                <p className="mt-1 text-xs leading-5 text-[#8B8D97]">
                  {snapshot.split}
                </p>
              </div>
              <StatusDot status={snapshot.status} />
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-2">
              {snapshot.metrics.map((metric) => (
                <div
                  key={`${snapshot.name}-${metric.label}`}
                  className="min-w-0 rounded-[6px] border border-[#35363D] bg-[#111216] p-2"
                >
                  <dt className="text-xs text-[#8B8D97]">{metric.label}</dt>
                  <dd
                    className={cn(
                      "mt-1 break-words text-sm font-semibold",
                      metric.tone === "good" && "text-[#4F8EF7]",
                      metric.tone === "warn" && "text-[#F59E0B]",
                      metric.tone === "neutral" && "text-[#EAEAF0]",
                    )}
                  >
                    {metric.value}
                  </dd>
                </div>
              ))}
            </dl>
            <p className="mt-3 break-words font-mono text-xs leading-5 text-[#8B8D97]">
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
    <div className="flex min-h-72 flex-col items-center justify-center rounded-lg border border-dashed border-[#35363D] bg-[#111216] p-6 text-center">
      <Braces className="size-8 text-[#5A5C66]" aria-hidden="true" />
      <div className="mt-3 text-sm font-semibold text-[#8B8D97]">
        No analysis yet
      </div>
    </div>
  )
}

function LoadingState({ analyzer }: { analyzer: AnalyzerOption }) {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center rounded-lg border border-dashed border-[#35363D] bg-[#111216] p-6 text-center">
      <Loader2 className="size-8 animate-spin text-[#AE4DFF]" aria-hidden="true" />
      <div className="mt-3 text-sm font-semibold text-[#8B8D97]">
        Running {analyzer.label}
      </div>
    </div>
  )
}

function UnconfiguredState({
  analyzer,
  message,
}: {
  analyzer: AnalyzerOption
  message?: string
}) {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center rounded-lg border border-[#F59E0B]/40 bg-[#F59E0B]/10 p-6 text-center">
      <AlertTriangle className="size-8 text-[#F59E0B]" aria-hidden="true" />
      <div className="mt-3 text-base font-semibold text-[#FDE68A]">
        {analyzer.label} is not configured
      </div>
      <div className="mt-2 max-w-sm text-sm leading-6 text-[#FCD34D]">
        {message ?? "No endpoint configured."}
      </div>
    </div>
  )
}

function ErrorState({
  message,
  validationIssues,
}: {
  message: string
  validationIssues?: TriageParseIssue[]
}) {
  return (
    <div className="min-h-72 rounded-lg border border-[#EF4444]/40 bg-[#EF4444]/10 p-6">
      <div className="flex items-center gap-2 text-base font-semibold text-[#FCA5A5]">
        <AlertTriangle className="size-5 text-[#EF4444]" aria-hidden="true" />
        Analyzer error
      </div>
      <p className="mt-3 text-sm leading-6 text-[#FECACA]">{message}</p>
      {validationIssues && validationIssues.length > 0 ? (
        <div className="mt-4 space-y-1 text-sm leading-6 text-[#FECACA]">
          {validationIssues.map((issue) => (
            <div key={`${issue.path}-${issue.message}`}>
              {issue.path}: {issue.message}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  )
}

function Panel({
  children,
  className,
  id,
}: {
  children: ReactNode
  className?: string
  id?: string
}) {
  return (
    <section
      id={id}
      className={cn(
        "scroll-mt-16 rounded-lg border border-[#35363D] bg-[#1C1D22] p-4 shadow-[0_0_0_1px_rgba(255,255,255,0.05)]",
        className,
      )}
    >
      {children}
    </section>
  )
}

function SectionHeader({
  eyebrow,
  title,
  meta,
  icon,
  action,
}: {
  eyebrow: string
  title: string
  meta?: string
  icon?: ReactNode
  action?: ReactNode
}) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex min-w-0 items-center gap-2">
        {icon ? (
          <span className="flex size-8 shrink-0 items-center justify-center rounded-[6px] border border-[#35363D] bg-[#27282F] text-[#8B8D97]">
            {icon}
          </span>
        ) : null}
        <div className="min-w-0">
          <div className="text-xs font-semibold text-[#8B8D97]">{eyebrow}</div>
          <h2 className="truncate text-base font-semibold leading-tight text-[#EAEAF0]">
            {title}
          </h2>
        </div>
      </div>
      {meta || action ? (
        <div className="flex w-full shrink-0 items-center justify-between gap-2 sm:w-auto sm:justify-end">
          {meta ? (
            <span className="hidden text-xs text-[#8B8D97] sm:inline">
              {meta}
            </span>
          ) : null}
          {action}
        </div>
      ) : null}
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
    <div className="border-t border-[#35363D] pt-3">
      <div className="mb-2 text-xs font-semibold text-[#8B8D97]">{title}</div>
      <div className="text-sm leading-6 text-[#EAEAF0]">{children}</div>
    </div>
  )
}

function StatusPill({
  label,
  tone,
  icon,
}: {
  label: string
  tone: "info" | "warn"
  icon: ReactNode
}) {
  return (
    <span
      className={cn(
        "hidden h-8 items-center justify-center gap-1.5 rounded-[6px] border px-2 text-xs font-semibold sm:inline-flex",
        tone === "info" && "border-[#4F8EF7]/40 bg-[#4F8EF7]/10 text-[#AECBFF]",
        tone === "warn" && "border-[#F59E0B]/40 bg-[#F59E0B]/10 text-[#FCD34D]",
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
        "inline-flex h-8 items-center rounded-[4px] border px-2 text-sm font-semibold capitalize",
        tone === "normal" && "border-[#8B8D97]/40 bg-[#8B8D97]/10 text-[#C7C8D0]",
        tone === "suspicious" && "border-[#F59E0B]/40 bg-[#F59E0B]/10 text-[#FCD34D]",
        tone === "low" && "border-[#8B8D97]/40 bg-[#8B8D97]/10 text-[#C7C8D0]",
        tone === "medium" && "border-[#4F8EF7]/40 bg-[#4F8EF7]/10 text-[#AECBFF]",
        tone === "high" && "border-[#F59E0B]/40 bg-[#F59E0B]/10 text-[#FCD34D]",
        tone === "critical" && "border-[#EF4444]/40 bg-[#EF4444]/10 text-[#FCA5A5]",
      )}
    >
      {children}
    </span>
  )
}

function StatusDot({
  status,
}: {
  status: "ready" | "exploratory" | "held" | "unconfigured"
}) {
  return (
    <span
      className={cn(
        "inline-flex h-7 items-center rounded-[4px] border px-2 text-xs font-semibold capitalize",
        status === "ready" && "border-[#4F8EF7]/40 bg-[#4F8EF7]/10 text-[#AECBFF]",
        status === "exploratory" && "border-[#F59E0B]/40 bg-[#F59E0B]/10 text-[#FCD34D]",
        status === "held" && "border-[#F59E0B]/40 bg-[#F59E0B]/10 text-[#FCD34D]",
        status === "unconfigured" && "border-[#35363D] bg-[#27282F] text-[#8B8D97]",
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
        className="rounded-[4px] bg-[#F59E0B]/25 px-1 text-[#FDE68A] ring-1 ring-[#F59E0B]/40"
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
