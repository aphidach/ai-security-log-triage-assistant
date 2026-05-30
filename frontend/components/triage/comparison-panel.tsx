import type { MetricSnapshot } from "@/lib/demo-data"
import { cn } from "@/lib/utils"

import { StatusDot } from "./shared"

export function ComparisonPanel({ snapshots }: { snapshots: MetricSnapshot[] }) {
  return (
    <div className="mt-8 grid gap-4 lg:grid-cols-3">
      {snapshots.map((snapshot) => (
        <article
          key={snapshot.name}
          className="min-w-0 rounded-[8px] border border-[#3A285C] bg-[#151027] p-5 shadow-[0_18px_52px_rgba(167,139,250,0.10)]"
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <h3 className="text-base font-bold text-[#F8F5FF]">
                {snapshot.name}
              </h3>
              <p className="mt-2 text-sm leading-6 text-[#C6BADF]">
                {snapshot.split}
              </p>
            </div>
            <StatusDot status={snapshot.status} />
          </div>
          <dl className="mt-5 grid grid-cols-2 gap-2">
            {snapshot.metrics.map((metric) => (
              <div
                key={`${snapshot.name}-${metric.label}`}
                className="min-w-0 rounded-[8px] border border-[#2A1D45] bg-[#110C22] p-3"
              >
                <dt className="text-xs font-semibold text-[#C6BADF]">
                  {metric.label}
                </dt>
                <dd
                  className={cn(
                    "mt-1 break-words text-sm font-bold",
                    metric.tone === "good" && "text-[#34D399]",
                    metric.tone === "warn" && "text-[#FBBF24]",
                    metric.tone === "neutral" && "text-[#F8F5FF]",
                  )}
                >
                  {metric.value}
                </dd>
              </div>
            ))}
          </dl>
          <p className="mt-4 break-words font-mono text-xs leading-5 text-[#9F93B8]">
            {snapshot.source}
          </p>
        </article>
      ))}
    </div>
  )
}
