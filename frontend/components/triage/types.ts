import type { TriageOutput, TriageParseIssue } from "@/lib/triage-schema"

export type AnalyzerId = "heuristic" | "base-model" | "fine-tuned"

export type AnalyzerOption = {
  id: AnalyzerId
  label: string
  detail: string
}

export type AnalysisState =
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

export type TriageApiSuccess = {
  output: TriageOutput
  rawJson: string
  validationIssues: TriageParseIssue[]
  elapsedMs: number
}

export type TriageApiError = {
  error: string
  code?: string
  rawJson?: string
  validationIssues?: TriageParseIssue[]
}

export type TriageApiResponse = TriageApiSuccess | TriageApiError

export type PublicEndpointConfig = {
  analyzer: Exclude<AnalyzerId, "heuristic">
  label: string
  modelEnv: string
  model: string | null
  configured: boolean
}

export type PublicTriageConfig = {
  endpoints: {
    baseModel: PublicEndpointConfig
    fineTuned: PublicEndpointConfig
  }
}
