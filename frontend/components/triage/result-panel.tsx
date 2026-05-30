import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Braces,
  CheckCircle2,
  Code2,
  Loader2,
  Radar,
  ShieldCheck,
} from "lucide-react"

import { TRIAGE_LABEL_METADATA } from "@/lib/labels"
import type { TriageOutput, TriageParseIssue } from "@/lib/triage-schema"
import { cn } from "@/lib/utils"

import {
  getSeverityTone,
  highlightEvidence,
} from "./helpers"
import {
  FieldBlock,
  PanelHeader,
  ResultBadge,
  ToolPanel,
} from "./shared"
import type { AnalysisState, AnalyzerOption } from "./types"

export function TriageResultPanel({
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
                  ? "border-[#1F8A5F] bg-[#052E24]"
                  : "border-[#7C3AED] bg-[#21112D]",
              )}
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-[#D8CCFF]">
                    Label
                  </div>
                  <div className="mt-1 break-words text-2xl font-bold leading-tight text-[#F8F5FF]">
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
              <div className="overflow-x-auto whitespace-pre-wrap break-words rounded-[8px] border border-[#3A285C] bg-[#110C22] p-3 font-mono text-[13px] leading-6 text-[#F8F5FF]">
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
                    className="rounded-[6px] border border-[#3A285C] bg-[#24183D] px-2.5 py-1.5 font-mono text-xs font-semibold leading-5 text-[#D8CCFF]"
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
              <div className="rounded-[8px] border border-[#F87171] bg-[#2A0C14] p-3 text-sm leading-6 text-[#FCA5A5]">
                {analysis.validationIssues.map((issue) => (
                  <div key={`${issue.path}-${issue.message}`}>
                    {issue.path}: {issue.message}
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center gap-2 rounded-[8px] border border-[#1F8A5F] bg-[#052E24] p-3 text-sm font-bold text-[#A7F3D0]">
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

function EmptyState() {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center rounded-[8px] border border-dashed border-[#3A285C] bg-[#110C22] p-6 text-center">
      <Braces className="size-8 text-[#7DD3FC]" aria-hidden="true" />
      <div className="mt-3 text-sm font-bold text-[#D8CCFF]">
        Awaiting analysis
      </div>
    </div>
  )
}

function LoadingState({ analyzer }: { analyzer: AnalyzerOption }) {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center rounded-[8px] border border-dashed border-[#3A285C] bg-[#110C22] p-6 text-center">
      <Loader2 className="size-8 animate-spin text-[#A78BFA]" aria-hidden="true" />
      <div className="mt-3 text-sm font-bold text-[#D8CCFF]">
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
    <div className="flex min-h-72 flex-col items-center justify-center rounded-[8px] border border-[#F59E0B] bg-[#2A1703] p-6 text-center">
      <AlertTriangle className="size-8 text-[#FBBF24]" aria-hidden="true" />
      <div className="mt-3 text-base font-bold text-[#FDE68A]">
        {analyzer.label} is not configured
      </div>
      <div className="mt-2 max-w-sm text-sm leading-6 text-[#FDE68A]">
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
    <div className="min-h-72 rounded-[8px] border border-[#F87171] bg-[#2A0C14] p-6">
      <div className="flex items-center gap-2 text-base font-bold text-[#FCA5A5]">
        <AlertTriangle className="size-5 text-[#F87171]" aria-hidden="true" />
        Analyzer error
      </div>
      <p className="mt-3 text-sm leading-6 text-[#FCA5A5]">{message}</p>
      {validationIssues && validationIssues.length > 0 ? (
        <div className="mt-4 space-y-1 text-sm leading-6 text-[#FCA5A5]">
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
