"use client"

import { FileJson, Radar, ShieldCheck, Terminal } from "lucide-react"
import { useEffect, useMemo, useState } from "react"

import {
  FinalCta,
  Hero,
  ProductProofStrip,
  SectionIntro,
  TopNav,
  WorkflowCard,
} from "@/components/landing/landing-sections"
import { ComparisonPanel } from "@/components/triage/comparison-panel"
import { ANALYZERS, SCHEMA_FIELDS } from "@/components/triage/constants"
import { buildMetricSnapshots, getLabelTone } from "@/components/triage/helpers"
import { TriageInputPanel } from "@/components/triage/input-panel"
import { RawJsonPanel } from "@/components/triage/raw-json-panel"
import { TriageResultPanel } from "@/components/triage/result-panel"
import type {
  AnalysisState,
  AnalyzerId,
  PublicTriageConfig,
  TriageApiResponse,
} from "@/components/triage/types"
import { SAMPLE_LOGS, type SampleLog } from "@/lib/demo-data"
import { parseTriageOutput } from "@/lib/triage-schema"

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
    <main className="min-h-screen overflow-hidden bg-[#090715] text-[#F8F5FF]">
      <TopNav analysis={analysis} />
      <Hero />
      <ProductProofStrip />

      <section
        id="demo"
        className="border-y border-[#3A285C] bg-[#151027] py-10 sm:py-12 lg:py-14"
      >
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-7 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <SectionIntro
              eyebrow="Live SaaS demo"
              title="Paste a log, get a structured investigation brief."
              description="The landing page centers the working product surface: local heuristic baseline, optional model endpoints, evidence highlighting, and schema validation."
            />
            <div className="flex min-h-12 items-center gap-2 rounded-[8px] border border-[#3A285C] bg-[#100A1F] px-3 text-sm font-semibold text-[#D8CCFF]">
              <ShieldCheck className="size-4 text-[#34D399]" aria-hidden="true" />
              Runs without model keys via local baseline
            </div>
          </div>

          <div className="grid w-full gap-4 lg:grid-cols-[minmax(0,1.04fr)_minmax(360px,0.96fr)]">
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
        </div>
      </section>

      <section id="workflow" className="bg-[#090715] py-16 sm:py-20">
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

          <div className="mt-8 rounded-lg border border-[#3A285C] bg-[#151027] p-4 shadow-[0_16px_60px_rgba(167,139,250,0.10)]">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="text-sm font-semibold text-[#A78BFA]">
                  Output schema
                </div>
                <div className="mt-1 text-base font-semibold text-[#F8F5FF]">
                  The UI, API, evaluator, and dataset all share these fields.
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {SCHEMA_FIELDS.map((field) => (
                  <span
                    key={field}
                    className="rounded-[6px] border border-[#2A1D45] bg-[#100A1F] px-2.5 py-1.5 font-mono text-xs font-semibold text-[#D8CCFF]"
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
        className="border-t border-[#3A285C] bg-[#151027] py-16 sm:py-20"
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

      <FinalCta />
    </main>
  )
}
