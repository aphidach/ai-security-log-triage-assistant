import { FileJson } from "lucide-react"

import { PanelHeader, ToolPanel } from "./shared"
import type { AnalysisState } from "./types"

export function RawJsonPanel({ analysis }: { analysis: AnalysisState }) {
  return (
    <ToolPanel id="raw-json">
      <PanelHeader
        eyebrow="Raw JSON"
        title="Output payload"
        icon={<FileJson className="size-4" aria-hidden="true" />}
      />
      <pre className="mt-4 min-h-72 overflow-auto rounded-[8px] border border-[#3A285C] bg-[#080512] p-4 font-mono text-xs leading-5 text-[#EDE9FE]">
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
