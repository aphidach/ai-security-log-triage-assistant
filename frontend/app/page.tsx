"use client"

import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Braces,
  CheckCircle2,
  CircleDot,
  ClipboardPaste,
  Code2,
  FileJson,
  Gauge,
  Layers2,
  Loader2,
  Play,
  Radar,
  ShieldAlert,
  ShieldCheck,
  Terminal,
} from "lucide-react"
import { useEffect, useMemo, useState, type ReactNode } from "react"

import { Button } from "@/components/ui/button"
import {
  METRIC_SNAPSHOTS,
  SAMPLE_LOGS,
  type MetricSnapshot,
  type SampleLog,
} from "@/lib/demo-data"
import { TRIAGE_LABEL_METADATA, type TriageLabel } from "@/lib/labels"
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
  detail: string
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

const DEFAULT_SAMPLE = SAMPLE_LOGS[0]

const HERO_STATS = [
  { label: "Fixed split baseline", value: "1.00", detail: "label accuracy" },
  { label: "Schema parse", value: "100%", detail: "structured output" },
  { label: "POC taxonomy", value: "5", detail: "labels in scope" },
]

const HERO_LOG_LINES = [
  "auth-01 sshd Failed password for admin repeated 18 times",
  "waf request=/login?username=admin%27%20OR%201%3D1-- status=500",
  "ids alert='nmap fingerprint' probed_ports=21,22,23,25,80,443",
  "web GET /download?file=..%2f..%2fetc%2fpasswd status=404",
]

const SCHEMA_FIELDS = [
  "label",
  "severity",
  "is_suspicious",
  "evidence",
  "reason",
  "recommended_action",
]

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
        validationIssues: validation.ok
          ? payload.validationIssues
          : validation.errors,
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
    <main className="min-h-screen overflow-hidden bg-[#F7FBFF] text-[#082F49]">
      <TopNav analysis={analysis} />
      <Hero />

      <section
        id="demo"
        className="border-y border-[#BAE6FD] bg-white py-8 sm:py-10 lg:py-12"
      >
        <div className="mx-auto grid w-full max-w-7xl gap-4 px-4 sm:px-6 lg:grid-cols-[minmax(0,1.04fr)_minmax(360px,0.96fr)] lg:px-8">
          <TriageInputPanel
            analysis={analysis}
            logInput={logInput}
            selectedAnalyzerId={selectedAnalyzerId}
            selectedSampleId={selectedSampleId}
            selectedAnalyzer={selectedAnalyzer}
            onAnalyze={() => {
              void analyzeLog()
            }}
            onLogInputChange={(value) => {
              setLogInput(value)
              setSelectedSampleId("")
              setAnalysis({ kind: "idle" })
            }}
            onSampleSelect={selectSample}
            onAnalyzerSelect={(analyzerId) => {
              setSelectedAnalyzerId(analyzerId)
              setAnalysis({ kind: "idle" })
            }}
          />

          <div className="min-w-0 space-y-4">
            <TriageResultPanel
              analysis={analysis}
              logInput={logInput}
              result={result}
              labelTone={labelTone}
            />
            <RawJsonPanel analysis={analysis} />
          </div>
        </div>
      </section>

      <section id="workflow" className="bg-[#F7FBFF] py-16 sm:py-20">
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
          <SectionIntro
            eyebrow="Evaluation-ready workflow"
            title="Built around a stable triage contract."
            description="The demo keeps the product story close to the measurable POC: fixed labels, schema-valid JSON, visible evidence, and baseline comparison."
          />

          <div className="mt-8 grid gap-4 lg:grid-cols-3">
            <WorkflowCard
              icon={<Terminal className="size-5" aria-hidden="true" />}
              title="Raw event in"
              text="A single security log line stays visible while the analyzer produces the structured result."
            />
            <WorkflowCard
              icon={<Radar className="size-5" aria-hidden="true" />}
              title="Evidence marked"
              text="Matched fragments are highlighted in the source log and repeated as evidence chips."
            />
            <WorkflowCard
              icon={<FileJson className="size-5" aria-hidden="true" />}
              title="JSON contract out"
              text="Every result is checked against the shared schema before it is shown as valid output."
            />
          </div>

          <div className="mt-8 rounded-lg border border-[#BAE6FD] bg-white p-4 shadow-[0_16px_60px_rgba(14,165,233,0.10)]">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="text-sm font-semibold text-[#0369A1]">
                  Output schema
                </div>
                <div className="mt-1 text-base font-semibold text-[#082F49]">
                  The UI, API, evaluator, and dataset all share these fields.
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {SCHEMA_FIELDS.map((field) => (
                  <span
                    key={field}
                    className="rounded-[6px] border border-[#E0F2FE] bg-[#F0F9FF] px-2.5 py-1.5 font-mono text-xs font-semibold text-[#075985]"
                  >
                    {field}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        id="metrics"
        className="border-t border-[#BAE6FD] bg-white py-16 sm:py-20"
      >
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
          <SectionIntro
            eyebrow="Comparison"
            title="Baseline and model artifacts stay in view."
            description="The landing page still behaves like a working triage tool, with the current fixed-split and endpoint configuration surfaced below the demo."
          />
          <ComparisonPanel snapshots={metricSnapshots} />
        </div>
      </section>
    </main>
  )
}

function TopNav({ analysis }: { analysis: AnalysisState }) {
  const isRunning = analysis.kind === "loading"

  return (
    <header className="sticky top-0 z-40 border-b border-[#BAE6FD]/80 bg-white/90 backdrop-blur-xl">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <button
          type="button"
          onClick={() => scrollToSection("top")}
          className="flex min-w-0 items-center gap-3 rounded-[6px] outline-none transition focus-visible:ring-3 focus-visible:ring-[#0EA5E9]/25"
        >
          <span className="flex size-10 shrink-0 items-center justify-center rounded-[8px] bg-[#0EA5E9] text-white shadow-[0_12px_30px_rgba(14,165,233,0.30)]">
            <ShieldAlert className="size-5" aria-hidden="true" />
          </span>
          <span className="min-w-0 text-left">
            <span className="block truncate text-sm font-bold text-[#082F49] sm:text-base">
              AI Security Log Triage
            </span>
            <span className="hidden text-xs font-medium text-[#0C4A6E] sm:block">
              Structured output POC
            </span>
          </span>
        </button>

        <nav
          className="hidden items-center gap-1 rounded-[8px] border border-[#E0F2FE] bg-[#F0F9FF] p-1 md:flex"
          aria-label="Primary"
        >
          <NavButton targetId="demo">Demo</NavButton>
          <NavButton targetId="workflow">Contract</NavButton>
          <NavButton targetId="metrics">Metrics</NavButton>
        </nav>

        <div className="flex shrink-0 items-center gap-2">
          <StatusPill
            label="Heuristic ready"
            tone="info"
            icon={<CheckCircle2 className="size-3.5" aria-hidden="true" />}
          />
          {isRunning ? (
            <StatusPill
              label="Running"
              tone="warn"
              icon={<Loader2 className="size-3.5 animate-spin" aria-hidden="true" />}
            />
          ) : null}
          <Button
            type="button"
            size="sm"
            onClick={() => scrollToSection("demo")}
            className="hidden border-[#FED7AA] bg-[#F97316] text-white hover:bg-[#EA580C] sm:inline-flex"
          >
            <Play className="size-3.5" aria-hidden="true" />
            Try demo
          </Button>
        </div>
      </div>
    </header>
  )
}

function NavButton({
  targetId,
  children,
}: {
  targetId: string
  children: ReactNode
}) {
  return (
    <button
      type="button"
      onClick={() => scrollToSection(targetId)}
      className="h-9 rounded-[6px] px-3 text-sm font-semibold text-[#0C4A6E] transition hover:bg-white hover:text-[#082F49] focus-visible:ring-3 focus-visible:ring-[#0EA5E9]/25"
    >
      {children}
    </button>
  )
}

function Hero() {
  return (
    <section id="top" className="relative overflow-hidden bg-[#F0F9FF]">
      <div
        className="pointer-events-none absolute inset-0 overflow-hidden"
        aria-hidden="true"
      >
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(14,165,233,0.10)_1px,transparent_1px),linear-gradient(to_bottom,rgba(14,165,233,0.10)_1px,transparent_1px)] bg-[size:44px_44px]" />
        <div className="absolute left-1/2 top-20 hidden w-[760px] -translate-x-4 rotate-1 space-y-3 opacity-90 lg:block">
          {HERO_LOG_LINES.map((line, index) => (
            <div
              key={line}
              className={cn(
                "rounded-[8px] border px-4 py-3 font-mono text-xs shadow-[0_18px_55px_rgba(8,47,73,0.10)]",
                index % 2 === 0
                  ? "border-[#BAE6FD] bg-white/80 text-[#075985]"
                  : "border-[#FED7AA] bg-[#FFF7ED]/85 text-[#9A3412]",
              )}
            >
              {line}
            </div>
          ))}
        </div>
      </div>

      <div className="relative mx-auto w-full max-w-7xl px-4 pb-10 pt-16 sm:px-6 sm:pb-12 sm:pt-20 lg:px-8 lg:pb-14 lg:pt-24">
        <div className="min-w-0 max-w-3xl">
          <div className="inline-flex min-h-8 items-center gap-2 rounded-[6px] border border-[#BAE6FD] bg-white/80 px-3 text-sm font-semibold text-[#075985] shadow-[0_12px_36px_rgba(14,165,233,0.12)]">
            <Activity className="size-4 text-[#0EA5E9]" aria-hidden="true" />
            Security log triage POC
          </div>
          <h1 className="mt-6 max-w-full break-words text-4xl font-bold leading-[1.05] text-[#082F49] sm:max-w-2xl sm:text-5xl lg:text-6xl">
            AI Security Log Triage Assistant
          </h1>
          <p className="mt-5 max-w-full break-words text-base leading-7 text-[#0C4A6E] sm:max-w-2xl sm:text-lg">
            A focused SaaS-style demo for classifying one security event into a
            stable label, severity, evidence list, reason, and next
            investigation action.
          </p>
          <div className="mt-7 flex flex-col gap-3 sm:flex-row">
            <Button
              type="button"
              size="lg"
              onClick={() => scrollToSection("demo")}
              className="w-full border-[#FED7AA] bg-[#F97316] text-white shadow-[0_18px_35px_rgba(249,115,22,0.24)] hover:bg-[#EA580C] sm:w-auto"
            >
              <Play className="size-4" aria-hidden="true" />
              Analyze sample
            </Button>
            <Button
              type="button"
              size="lg"
              variant="outline"
              onClick={() => scrollToSection("metrics")}
              className="w-full sm:w-auto"
            >
              View metrics
              <ArrowRight className="size-4" aria-hidden="true" />
            </Button>
          </div>
        </div>

        <div className="mt-10 grid min-w-0 gap-3 sm:grid-cols-3 lg:max-w-3xl">
          {HERO_STATS.map((stat) => (
            <div
              key={stat.label}
              className="min-w-0 rounded-[8px] border border-[#BAE6FD] bg-white/80 p-4 shadow-[0_14px_42px_rgba(14,165,233,0.10)]"
            >
              <div className="text-2xl font-bold text-[#082F49]">
                {stat.value}
              </div>
              <div className="mt-1 text-sm font-semibold text-[#075985]">
                {stat.label}
              </div>
              <div className="mt-1 text-xs leading-5 text-[#0C4A6E]">
                {stat.detail}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function TriageInputPanel({
  analysis,
  logInput,
  selectedAnalyzerId,
  selectedSampleId,
  selectedAnalyzer,
  onAnalyze,
  onAnalyzerSelect,
  onLogInputChange,
  onSampleSelect,
}: {
  analysis: AnalysisState
  logInput: string
  selectedAnalyzerId: AnalyzerId
  selectedSampleId: string
  selectedAnalyzer: AnalyzerOption
  onAnalyze: () => void
  onAnalyzerSelect: (analyzerId: AnalyzerId) => void
  onLogInputChange: (value: string) => void
  onSampleSelect: (sample: SampleLog) => void
}) {
  return (
    <ToolPanel id="triage-input" className="lg:sticky lg:top-20">
      <PanelHeader
        eyebrow="Live triage"
        title="Input log"
        icon={<Terminal className="size-4" aria-hidden="true" />}
        action={
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
        }
      />

      <label htmlFor="log-input" className="sr-only">
        Security log input
      </label>
      <textarea
        id="log-input"
        value={logInput}
        onChange={(event) => onLogInputChange(event.target.value)}
        className="mt-4 min-h-48 w-full resize-y rounded-[8px] border border-[#BAE6FD] bg-[#F8FCFF] p-4 font-mono text-[13px] leading-6 text-[#082F49] outline-none transition placeholder:text-[#64748B] focus:border-[#0EA5E9] focus:ring-3 focus:ring-[#0EA5E9]/20"
        spellCheck={false}
      />

      <div className="mt-5 grid gap-4 xl:grid-cols-[minmax(0,1fr)_auto] xl:items-end">
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-[#075985]">
            <Layers2 className="size-4" aria-hidden="true" />
            Analyzer
          </div>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            {ANALYZERS.map((analyzer) => (
              <button
                key={analyzer.id}
                type="button"
                onClick={() => onAnalyzerSelect(analyzer.id)}
                className={cn(
                  "min-h-16 min-w-0 rounded-[8px] border p-3 text-left outline-none transition focus-visible:ring-3 focus-visible:ring-[#0EA5E9]/25",
                  selectedAnalyzerId === analyzer.id
                    ? "border-[#0EA5E9] bg-[#E0F2FE] shadow-[0_12px_32px_rgba(14,165,233,0.12)]"
                    : "border-[#E0F2FE] bg-white hover:border-[#7DD3FC] hover:bg-[#F0F9FF]",
                )}
              >
                <span className="flex items-center gap-2 text-sm font-bold text-[#082F49]">
                  <CircleDot
                    className={cn(
                      "size-3.5 shrink-0",
                      selectedAnalyzerId === analyzer.id
                        ? "text-[#0EA5E9]"
                        : "text-[#94A3B8]",
                    )}
                    aria-hidden="true"
                  />
                  {analyzer.label}
                </span>
                <span className="mt-1 block text-xs leading-5 text-[#0C4A6E]">
                  {analyzer.detail}
                </span>
              </button>
            ))}
          </div>
        </div>
        <Button
          type="button"
          size="lg"
          onClick={onAnalyze}
          disabled={logInput.trim().length === 0 || analysis.kind === "loading"}
          className="min-h-12 border-[#FED7AA] bg-[#F97316] px-5 text-white shadow-[0_18px_32px_rgba(249,115,22,0.22)] hover:bg-[#EA580C]"
        >
          {analysis.kind === "loading" ? (
            <Loader2 className="size-4 animate-spin" aria-hidden="true" />
          ) : (
            <Play className="size-4" aria-hidden="true" />
          )}
          Analyze
        </Button>
      </div>

      <div className="mt-6 border-t border-[#E0F2FE] pt-5">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-[#075985]">
            <Braces className="size-4" aria-hidden="true" />
            Sample logs
          </div>
          <span className="rounded-[6px] border border-[#E0F2FE] bg-[#F0F9FF] px-2 py-1 text-xs font-semibold text-[#075985]">
            {SAMPLE_LOGS.length} labels
          </span>
        </div>
        <div className="grid gap-2 sm:grid-cols-2">
          {SAMPLE_LOGS.map((sample) => (
            <button
              key={sample.id}
              type="button"
              onClick={() => onSampleSelect(sample)}
              className={cn(
                "min-h-24 rounded-[8px] border p-3 text-left outline-none transition focus-visible:ring-3 focus-visible:ring-[#0EA5E9]/25",
                selectedSampleId === sample.id
                  ? "border-[#0EA5E9] bg-[#E0F2FE]"
                  : "border-[#E0F2FE] bg-white hover:border-[#7DD3FC] hover:bg-[#F0F9FF]",
              )}
            >
              <span className="flex items-start gap-2 text-sm font-bold text-[#082F49]">
                {sample.label === "normal" ? (
                  <ShieldCheck
                    className="mt-0.5 size-4 shrink-0 text-[#059669]"
                    aria-hidden="true"
                  />
                ) : (
                  <ShieldAlert
                    className="mt-0.5 size-4 shrink-0 text-[#F97316]"
                    aria-hidden="true"
                  />
                )}
                {sample.name}
              </span>
              <span className="mt-2 block text-xs leading-5 text-[#0C4A6E]">
                {TRIAGE_LABEL_METADATA[sample.label].displayName}
              </span>
            </button>
          ))}
        </div>
        <div className="mt-4 rounded-[8px] border border-[#E0F2FE] bg-[#F8FCFF] p-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#075985]">
            <Gauge className="size-4" aria-hidden="true" />
            Selected analyzer
          </div>
          <div className="mt-1 text-sm font-bold text-[#082F49]">
            {selectedAnalyzer.label}
          </div>
        </div>
      </div>
    </ToolPanel>
  )
}

function TriageResultPanel({
  analysis,
  logInput,
  result,
  labelTone,
}: {
  analysis: AnalysisState
  logInput: string
  result: TriageOutput | null
  labelTone: "normal" | "suspicious" | null
}) {
  return (
    <ToolPanel id="result-panel">
      <PanelHeader
        eyebrow="Structured output"
        title="Result"
        meta={
          analysis.kind === "result"
            ? `${analysis.elapsedMs.toFixed(2)} ms`
            : "pending"
        }
        icon={<ShieldCheck className="size-4" aria-hidden="true" />}
      />

      <div className="mt-4">
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
                "rounded-[8px] border p-4",
                labelTone === "normal"
                  ? "border-[#A7F3D0] bg-[#ECFDF5]"
                  : "border-[#FED7AA] bg-[#FFF7ED]",
              )}
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-[#075985]">
                    Label
                  </div>
                  <div className="mt-1 break-words text-2xl font-bold leading-tight text-[#082F49]">
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

            <FieldBlock
              title="Evidence marker"
              icon={<Code2 className="size-4" aria-hidden="true" />}
            >
              <div className="overflow-x-auto whitespace-pre-wrap break-words rounded-[8px] border border-[#BAE6FD] bg-[#F8FCFF] p-3 font-mono text-[13px] leading-6 text-[#082F49]">
                {highlightEvidence(logInput, result.evidence)}
              </div>
            </FieldBlock>

            <FieldBlock
              title="Evidence"
              icon={<Radar className="size-4" aria-hidden="true" />}
            >
              <div className="flex flex-wrap gap-2">
                {result.evidence.map((item) => (
                  <span
                    key={item}
                    className="rounded-[6px] border border-[#BAE6FD] bg-[#E0F2FE] px-2.5 py-1.5 font-mono text-xs font-semibold leading-5 text-[#075985]"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </FieldBlock>

            <FieldBlock
              title="Reason"
              icon={<Activity className="size-4" aria-hidden="true" />}
            >
              {result.reason}
            </FieldBlock>
            <FieldBlock
              title="Recommended action"
              icon={<ArrowRight className="size-4" aria-hidden="true" />}
            >
              {result.recommended_action}
            </FieldBlock>

            {analysis.validationIssues.length > 0 ? (
              <div className="rounded-[8px] border border-[#FCA5A5] bg-[#FEF2F2] p-3 text-sm leading-6 text-[#991B1B]">
                {analysis.validationIssues.map((issue) => (
                  <div key={`${issue.path}-${issue.message}`}>
                    {issue.path}: {issue.message}
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center gap-2 rounded-[8px] border border-[#A7F3D0] bg-[#ECFDF5] p-3 text-sm font-bold text-[#047857]">
                <CheckCircle2 className="size-4" aria-hidden="true" />
                Schema-valid output
              </div>
            )}
          </div>
        ) : null}
      </div>
    </ToolPanel>
  )
}

function RawJsonPanel({ analysis }: { analysis: AnalysisState }) {
  return (
    <ToolPanel id="raw-json">
      <PanelHeader
        eyebrow="Raw JSON"
        title="Output payload"
        icon={<FileJson className="size-4" aria-hidden="true" />}
      />
      <pre className="mt-4 min-h-72 overflow-auto rounded-[8px] border border-[#BAE6FD] bg-[#082F49] p-4 font-mono text-xs leading-5 text-[#E0F2FE]">
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
    </ToolPanel>
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
    <div className="mt-8 grid gap-4 lg:grid-cols-3">
      {snapshots.map((snapshot) => (
        <article
          key={snapshot.name}
          className="min-w-0 rounded-[8px] border border-[#BAE6FD] bg-white p-5 shadow-[0_18px_52px_rgba(14,165,233,0.10)]"
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <h3 className="text-base font-bold text-[#082F49]">
                {snapshot.name}
              </h3>
              <p className="mt-2 text-sm leading-6 text-[#0C4A6E]">
                {snapshot.split}
              </p>
            </div>
            <StatusDot status={snapshot.status} />
          </div>
          <dl className="mt-5 grid grid-cols-2 gap-2">
            {snapshot.metrics.map((metric) => (
              <div
                key={`${snapshot.name}-${metric.label}`}
                className="min-w-0 rounded-[8px] border border-[#E0F2FE] bg-[#F8FCFF] p-3"
              >
                <dt className="text-xs font-semibold text-[#0C4A6E]">
                  {metric.label}
                </dt>
                <dd
                  className={cn(
                    "mt-1 break-words text-sm font-bold",
                    metric.tone === "good" && "text-[#047857]",
                    metric.tone === "warn" && "text-[#C2410C]",
                    metric.tone === "neutral" && "text-[#082F49]",
                  )}
                >
                  {metric.value}
                </dd>
              </div>
            ))}
          </dl>
          <p className="mt-4 break-words font-mono text-xs leading-5 text-[#64748B]">
            {snapshot.source}
          </p>
        </article>
      ))}
    </div>
  )
}

function SectionIntro({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string
  title: string
  description: string
}) {
  return (
    <div className="max-w-3xl">
      <div className="text-sm font-bold text-[#0369A1]">{eyebrow}</div>
      <h2 className="mt-2 text-3xl font-bold leading-tight text-[#082F49] sm:text-4xl">
        {title}
      </h2>
      <p className="mt-3 text-base leading-7 text-[#0C4A6E]">{description}</p>
    </div>
  )
}

function WorkflowCard({
  icon,
  title,
  text,
}: {
  icon: ReactNode
  title: string
  text: string
}) {
  return (
    <article className="rounded-[8px] border border-[#BAE6FD] bg-white p-5 shadow-[0_18px_52px_rgba(14,165,233,0.10)]">
      <div className="flex size-10 items-center justify-center rounded-[8px] bg-[#E0F2FE] text-[#0284C7]">
        {icon}
      </div>
      <h3 className="mt-4 text-lg font-bold text-[#082F49]">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-[#0C4A6E]">{text}</p>
    </article>
  )
}

function EmptyState() {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center rounded-[8px] border border-dashed border-[#BAE6FD] bg-[#F8FCFF] p-6 text-center">
      <Braces className="size-8 text-[#7DD3FC]" aria-hidden="true" />
      <div className="mt-3 text-sm font-bold text-[#075985]">
        Awaiting analysis
      </div>
    </div>
  )
}

function LoadingState({ analyzer }: { analyzer: AnalyzerOption }) {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center rounded-[8px] border border-dashed border-[#BAE6FD] bg-[#F8FCFF] p-6 text-center">
      <Loader2 className="size-8 animate-spin text-[#0EA5E9]" aria-hidden="true" />
      <div className="mt-3 text-sm font-bold text-[#075985]">
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
    <div className="flex min-h-72 flex-col items-center justify-center rounded-[8px] border border-[#FED7AA] bg-[#FFF7ED] p-6 text-center">
      <AlertTriangle className="size-8 text-[#F97316]" aria-hidden="true" />
      <div className="mt-3 text-base font-bold text-[#9A3412]">
        {analyzer.label} is not configured
      </div>
      <div className="mt-2 max-w-sm text-sm leading-6 text-[#9A3412]">
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
    <div className="min-h-72 rounded-[8px] border border-[#FCA5A5] bg-[#FEF2F2] p-6">
      <div className="flex items-center gap-2 text-base font-bold text-[#991B1B]">
        <AlertTriangle className="size-5 text-[#DC2626]" aria-hidden="true" />
        Analyzer error
      </div>
      <p className="mt-3 text-sm leading-6 text-[#991B1B]">{message}</p>
      {validationIssues && validationIssues.length > 0 ? (
        <div className="mt-4 space-y-1 text-sm leading-6 text-[#991B1B]">
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

function ToolPanel({
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
        "min-w-0 scroll-mt-24 rounded-[8px] border border-[#BAE6FD] bg-white p-4 shadow-[0_18px_60px_rgba(14,165,233,0.12)] sm:p-5",
        className,
      )}
    >
      {children}
    </section>
  )
}

function PanelHeader({
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
      <div className="flex min-w-0 items-center gap-3">
        {icon ? (
          <span className="flex size-9 shrink-0 items-center justify-center rounded-[8px] border border-[#BAE6FD] bg-[#E0F2FE] text-[#0284C7]">
            {icon}
          </span>
        ) : null}
        <div className="min-w-0">
          <div className="text-sm font-bold text-[#0369A1]">{eyebrow}</div>
          <h2 className="truncate text-xl font-bold leading-tight text-[#082F49]">
            {title}
          </h2>
        </div>
      </div>
      {meta || action ? (
        <div className="flex w-full shrink-0 items-center justify-between gap-2 sm:w-auto sm:justify-end">
          {meta ? (
            <span className="rounded-[6px] border border-[#E0F2FE] bg-[#F0F9FF] px-2 py-1 text-xs font-bold text-[#075985]">
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
  icon,
  children,
}: {
  title: string
  icon: ReactNode
  children: ReactNode
}) {
  return (
    <div className="border-t border-[#E0F2FE] pt-4">
      <div className="mb-2 flex items-center gap-2 text-sm font-bold text-[#075985]">
        {icon}
        {title}
      </div>
      <div className="text-sm leading-6 text-[#082F49]">{children}</div>
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
        "hidden h-8 items-center justify-center gap-1.5 rounded-[6px] border px-2 text-xs font-bold sm:inline-flex",
        tone === "info" && "border-[#BAE6FD] bg-[#E0F2FE] text-[#075985]",
        tone === "warn" && "border-[#FED7AA] bg-[#FFF7ED] text-[#9A3412]",
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
        "inline-flex min-h-8 items-center rounded-[6px] border px-2.5 text-sm font-bold capitalize",
        tone === "normal" && "border-[#A7F3D0] bg-[#ECFDF5] text-[#047857]",
        tone === "suspicious" && "border-[#FED7AA] bg-[#FFF7ED] text-[#C2410C]",
        tone === "low" && "border-[#E2E8F0] bg-[#F8FAFC] text-[#475569]",
        tone === "medium" && "border-[#BAE6FD] bg-[#E0F2FE] text-[#075985]",
        tone === "high" && "border-[#FED7AA] bg-[#FFF7ED] text-[#C2410C]",
        tone === "critical" && "border-[#FCA5A5] bg-[#FEF2F2] text-[#991B1B]",
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
        "inline-flex min-h-7 items-center rounded-[6px] border px-2 text-xs font-bold capitalize",
        status === "ready" && "border-[#A7F3D0] bg-[#ECFDF5] text-[#047857]",
        status === "exploratory" && "border-[#FED7AA] bg-[#FFF7ED] text-[#C2410C]",
        status === "held" && "border-[#FED7AA] bg-[#FFF7ED] text-[#C2410C]",
        status === "unconfigured" && "border-[#E2E8F0] bg-[#F8FAFC] text-[#475569]",
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
        className="rounded-[4px] bg-[#FDBA74]/45 px-1 text-[#7C2D12] ring-1 ring-[#F97316]/35"
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

function scrollToSection(id: string) {
  document.getElementById(id)?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  })
}
