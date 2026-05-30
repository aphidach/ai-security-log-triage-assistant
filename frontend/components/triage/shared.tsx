import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

export function ToolPanel({
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
        "min-w-0 scroll-mt-24 rounded-[8px] border border-[#3A285C] bg-[#151027] p-4 shadow-[0_18px_60px_rgba(167,139,250,0.12)] sm:p-5",
        className,
      )}
    >
      {children}
    </section>
  )
}

export function PanelHeader({
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
          <span className="flex size-9 shrink-0 items-center justify-center rounded-[8px] border border-[#3A285C] bg-[#24183D] text-[#B794F6]">
            {icon}
          </span>
        ) : null}
        <div className="min-w-0">
          <div className="text-sm font-bold text-[#A78BFA]">{eyebrow}</div>
          <h2 className="truncate text-xl font-bold leading-tight text-[#F8F5FF]">
            {title}
          </h2>
        </div>
      </div>
      {meta || action ? (
        <div className="flex w-full shrink-0 items-center justify-between gap-2 sm:w-auto sm:justify-end">
          {meta ? (
            <span className="rounded-[6px] border border-[#2A1D45] bg-[#100A1F] px-2 py-1 text-xs font-bold text-[#D8CCFF]">
              {meta}
            </span>
          ) : null}
          {action}
        </div>
      ) : null}
    </div>
  )
}

export function FieldBlock({
  title,
  icon,
  children,
}: {
  title: string
  icon: ReactNode
  children: ReactNode
}) {
  return (
    <div className="border-t border-[#2A1D45] pt-4">
      <div className="mb-2 flex items-center gap-2 text-sm font-bold text-[#D8CCFF]">
        {icon}
        {title}
      </div>
      <div className="text-sm leading-6 text-[#F8F5FF]">{children}</div>
    </div>
  )
}

export function StatusPill({
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
        tone === "info" && "border-[#3A285C] bg-[#24183D] text-[#D8CCFF]",
        tone === "warn" && "border-[#F59E0B] bg-[#2A1703] text-[#FDE68A]",
      )}
    >
      {icon}
      {label}
    </span>
  )
}

export function ResultBadge({
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
        tone === "normal" && "border-[#1F8A5F] bg-[#052E24] text-[#A7F3D0]",
        tone === "suspicious" && "border-[#7C3AED] bg-[#21112D] text-[#F0ABFC]",
        tone === "low" && "border-[#3A285C] bg-[#100A1F] text-[#C6BADF]",
        tone === "medium" && "border-[#3A285C] bg-[#24183D] text-[#D8CCFF]",
        tone === "high" && "border-[#F59E0B] bg-[#2A1703] text-[#FDE68A]",
        tone === "critical" && "border-[#F87171] bg-[#2A0C14] text-[#FCA5A5]",
      )}
    >
      {children}
    </span>
  )
}

export function StatusDot({
  status,
}: {
  status: "ready" | "exploratory" | "held" | "unconfigured"
}) {
  return (
    <span
      className={cn(
        "inline-flex min-h-7 items-center rounded-[6px] border px-2 text-xs font-bold capitalize",
        status === "ready" && "border-[#1F8A5F] bg-[#052E24] text-[#A7F3D0]",
        status === "exploratory" &&
          "border-[#F59E0B] bg-[#2A1703] text-[#FDE68A]",
        status === "held" && "border-[#F59E0B] bg-[#2A1703] text-[#FDE68A]",
        status === "unconfigured" &&
          "border-[#3A285C] bg-[#100A1F] text-[#C6BADF]",
      )}
    >
      {status}
    </span>
  )
}
