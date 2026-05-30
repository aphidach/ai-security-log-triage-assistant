import {
  Braces,
  CircleDot,
  ClipboardPaste,
  Gauge,
  Layers2,
  Loader2,
  Play,
  ShieldAlert,
  ShieldCheck,
  Terminal,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { SAMPLE_LOGS, type SampleLog } from "@/lib/demo-data"
import { TRIAGE_LABEL_METADATA } from "@/lib/labels"
import { cn } from "@/lib/utils"

import { ANALYZERS } from "./constants"
import { PanelHeader, ToolPanel } from "./shared"
import type { AnalysisState, AnalyzerId, AnalyzerOption } from "./types"

export function TriageInputPanel({
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
        className="mt-4 min-h-48 w-full resize-y rounded-[8px] border border-[#3A285C] bg-[#110C22] p-4 font-mono text-[13px] leading-6 text-[#F8F5FF] outline-none transition placeholder:text-[#9F93B8] focus:border-[#A78BFA] focus:ring-3 focus:ring-[#A78BFA]/20"
        spellCheck={false}
      />

      <div className="mt-5 grid gap-4 xl:grid-cols-[minmax(0,1fr)_auto] xl:items-end">
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-[#D8CCFF]">
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
                  "min-h-16 min-w-0 rounded-[8px] border p-3 text-left outline-none transition focus-visible:ring-3 focus-visible:ring-[#A78BFA]/25",
                  selectedAnalyzerId === analyzer.id
                    ? "border-[#A78BFA] bg-[#24183D] shadow-[0_12px_32px_rgba(167,139,250,0.12)]"
                    : "border-[#2A1D45] bg-[#151027] hover:border-[#8B5CF6] hover:bg-[#100A1F]",
                )}
              >
                <span className="flex items-center gap-2 text-sm font-bold text-[#F8F5FF]">
                  <CircleDot
                    className={cn(
                      "size-3.5 shrink-0",
                      selectedAnalyzerId === analyzer.id
                        ? "text-[#A78BFA]"
                        : "text-[#73668F]",
                    )}
                    aria-hidden="true"
                  />
                  {analyzer.label}
                </span>
                <span className="mt-1 block text-xs leading-5 text-[#C6BADF]">
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
          className="min-h-12 border-[#A78BFA]/40 bg-[#8B5CF6] px-5 text-white shadow-[0_18px_32px_rgba(139,92,246,0.28)] hover:bg-[#7C3AED]"
        >
          {analysis.kind === "loading" ? (
            <Loader2 className="size-4 animate-spin" aria-hidden="true" />
          ) : (
            <Play className="size-4" aria-hidden="true" />
          )}
          Analyze
        </Button>
      </div>

      <div className="mt-6 border-t border-[#2A1D45] pt-5">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-[#D8CCFF]">
            <Braces className="size-4" aria-hidden="true" />
            Sample logs
          </div>
          <span className="rounded-[6px] border border-[#2A1D45] bg-[#100A1F] px-2 py-1 text-xs font-semibold text-[#D8CCFF]">
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
                "min-h-24 rounded-[8px] border p-3 text-left outline-none transition focus-visible:ring-3 focus-visible:ring-[#A78BFA]/25",
                selectedSampleId === sample.id
                  ? "border-[#A78BFA] bg-[#24183D]"
                  : "border-[#2A1D45] bg-[#151027] hover:border-[#8B5CF6] hover:bg-[#100A1F]",
              )}
            >
              <span className="flex items-start gap-2 text-sm font-bold text-[#F8F5FF]">
                {sample.label === "normal" ? (
                  <ShieldCheck
                    className="mt-0.5 size-4 shrink-0 text-[#34D399]"
                    aria-hidden="true"
                  />
                ) : (
                  <ShieldAlert
                    className="mt-0.5 size-4 shrink-0 text-[#F0ABFC]"
                    aria-hidden="true"
                  />
                )}
                {sample.name}
              </span>
              <span className="mt-2 block text-xs leading-5 text-[#C6BADF]">
                {TRIAGE_LABEL_METADATA[sample.label].displayName}
              </span>
            </button>
          ))}
        </div>
        <div className="mt-4 rounded-[8px] border border-[#2A1D45] bg-[#110C22] p-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#D8CCFF]">
            <Gauge className="size-4" aria-hidden="true" />
            Selected analyzer
          </div>
          <div className="mt-1 text-sm font-bold text-[#F8F5FF]">
            {selectedAnalyzer.label}
          </div>
        </div>
      </div>
    </ToolPanel>
  )
}
