import {
  Activity,
  ArrowRight,
  CheckCircle2,
  FileJson,
  Gauge,
  Loader2,
  Play,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react"
import type { ReactNode } from "react"

import { Button } from "@/components/ui/button"
import { HERO_LOG_LINES, HERO_STATS } from "@/components/triage/constants"
import { scrollToSection } from "@/components/triage/helpers"
import { StatusPill } from "@/components/triage/shared"
import type { AnalysisState } from "@/components/triage/types"
import { cn } from "@/lib/utils"

export function TopNav({ analysis }: { analysis: AnalysisState }) {
  const isRunning = analysis.kind === "loading"

  return (
    <header className="sticky top-0 z-40 border-b border-[#3A285C]/80 bg-[#0D091A]/88 backdrop-blur-xl">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <button
          type="button"
          onClick={() => scrollToSection("top")}
          className="flex min-w-0 items-center gap-3 rounded-[6px] outline-none transition focus-visible:ring-3 focus-visible:ring-[#A78BFA]/25"
        >
          <span className="flex size-10 shrink-0 items-center justify-center rounded-[8px] bg-[#7C3AED] text-white shadow-[0_12px_30px_rgba(124,58,237,0.35)]">
            <ShieldAlert className="size-5" aria-hidden="true" />
          </span>
          <span className="min-w-0 text-left">
            <span className="block truncate text-sm font-bold text-[#F8F5FF] sm:text-base">
              AI Security Log Triage
            </span>
            <span className="hidden text-xs font-medium text-[#C6BADF] sm:block">
              Structured output POC
            </span>
          </span>
        </button>

        <nav
          className="hidden items-center gap-1 rounded-[8px] border border-[#2A1D45] bg-[#100A1F] p-1 md:flex"
          aria-label="Primary"
        >
          <NavButton targetId="product">Product</NavButton>
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
              icon={
                <Loader2 className="size-3.5 animate-spin" aria-hidden="true" />
              }
            />
          ) : null}
          <Button
            type="button"
            size="sm"
            onClick={() => scrollToSection("demo")}
            className="hidden border-[#A78BFA]/40 bg-[#8B5CF6] text-white shadow-[0_14px_32px_rgba(139,92,246,0.28)] hover:bg-[#7C3AED] sm:inline-flex"
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
      className="h-9 rounded-[6px] px-3 text-sm font-semibold text-[#C6BADF] transition hover:bg-[#201638] hover:text-[#F8F5FF] focus-visible:ring-3 focus-visible:ring-[#A78BFA]/25"
    >
      {children}
    </button>
  )
}

export function Hero() {
  return (
    <section id="top" className="relative overflow-hidden bg-[#0D091A]">
      <div
        className="pointer-events-none absolute inset-0 overflow-hidden"
        aria-hidden="true"
      >
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(167,139,250,0.11)_1px,transparent_1px),linear-gradient(to_bottom,rgba(167,139,250,0.08)_1px,transparent_1px)] bg-[size:44px_44px]" />
        <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(76,29,149,0.35),transparent_42%),linear-gradient(225deg,rgba(34,211,238,0.13),transparent_52%)]" />
        <div className="absolute left-1/2 top-20 hidden w-[760px] -translate-x-4 rotate-1 space-y-3 opacity-75 lg:block">
          {HERO_LOG_LINES.map((line, index) => (
            <div
              key={line}
              className={cn(
                "rounded-[8px] border px-4 py-3 font-mono text-xs shadow-[0_18px_55px_rgba(9,7,21,0.10)]",
                index % 2 === 0
                  ? "border-[#3A285C] bg-[#151027]/82 text-[#D8CCFF]"
                  : "border-[#7C3AED] bg-[#21112D]/85 text-[#F0ABFC]",
              )}
            >
              {line}
            </div>
          ))}
        </div>
      </div>

      <div className="relative mx-auto w-full max-w-7xl px-4 pb-10 pt-16 sm:px-6 sm:pb-12 sm:pt-20 lg:px-8 lg:pb-14 lg:pt-24">
        <div className="min-w-0 max-w-3xl">
          <div className="inline-flex min-h-8 items-center gap-2 rounded-[6px] border border-[#3A285C] bg-[#151027]/82 px-3 text-sm font-semibold text-[#D8CCFF] shadow-[0_12px_36px_rgba(167,139,250,0.12)]">
            <Activity className="size-4 text-[#A78BFA]" aria-hidden="true" />
            Security log triage POC
          </div>
          <h1 className="mt-6 max-w-full break-words text-4xl font-bold leading-[1.05] text-[#F8F5FF] sm:max-w-2xl sm:text-5xl lg:text-6xl">
            AI Security Log Triage Assistant
          </h1>
          <p className="mt-5 max-w-full break-words text-base leading-7 text-[#C6BADF] sm:max-w-2xl sm:text-lg">
            A dark-mode SaaS proof of concept for turning noisy security logs
            into schema-valid triage decisions, visible evidence, and the next
            investigation action.
          </p>
          <div className="mt-7 flex flex-col gap-3 sm:flex-row">
            <Button
              type="button"
              size="lg"
              onClick={() => scrollToSection("demo")}
              className="w-full border-[#A78BFA]/40 bg-[#8B5CF6] text-white shadow-[0_18px_35px_rgba(139,92,246,0.32)] hover:bg-[#7C3AED] sm:w-auto"
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
              className="min-w-0 rounded-[8px] border border-[#3A285C] bg-[#151027]/82 p-4 shadow-[0_14px_42px_rgba(167,139,250,0.10)]"
            >
              <div className="text-2xl font-bold text-[#F8F5FF]">
                {stat.value}
              </div>
              <div className="mt-1 text-sm font-semibold text-[#D8CCFF]">
                {stat.label}
              </div>
              <div className="mt-1 text-xs leading-5 text-[#C6BADF]">
                {stat.detail}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export function ProductProofStrip() {
  return (
    <section
      id="product"
      className="border-y border-[#3A285C] bg-[#090715] py-8 sm:py-10"
    >
      <div className="mx-auto grid w-full max-w-7xl gap-3 px-4 sm:px-6 md:grid-cols-3 lg:px-8">
        <ProductProofItem
          icon={<ShieldCheck className="size-5" aria-hidden="true" />}
          label="Local-first baseline"
          text="Demo path works without GPU access or model credentials."
        />
        <ProductProofItem
          icon={<FileJson className="size-5" aria-hidden="true" />}
          label="Stable JSON contract"
          text="Labels, severity, evidence, reason, and action stay aligned."
        />
        <ProductProofItem
          icon={<Gauge className="size-5" aria-hidden="true" />}
          label="Measurable POC"
          text="Fixed split metrics and endpoint configuration remain visible."
        />
      </div>
    </section>
  )
}

function ProductProofItem({
  icon,
  label,
  text,
}: {
  icon: ReactNode
  label: string
  text: string
}) {
  return (
    <article className="min-w-0 rounded-[8px] border border-[#3A285C] bg-[#151027] p-4">
      <div className="flex items-start gap-3">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-[8px] border border-[#4C3573] bg-[#24183D] text-[#C084FC]">
          {icon}
        </span>
        <div className="min-w-0">
          <h2 className="text-base font-bold text-[#F8F5FF]">{label}</h2>
          <p className="mt-1 text-sm leading-6 text-[#C6BADF]">{text}</p>
        </div>
      </div>
    </article>
  )
}

export function FinalCta() {
  return (
    <section className="border-t border-[#3A285C] bg-[#090715] py-14 sm:py-16">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <div className="max-w-2xl">
          <div className="text-sm font-bold text-[#A78BFA]">
            Ready for review
          </div>
          <h2 className="mt-2 text-3xl font-bold leading-tight text-[#F8F5FF] sm:text-4xl">
            Keep the POC measurable while the interface feels production-grade.
          </h2>
          <p className="mt-3 text-base leading-7 text-[#C6BADF]">
            Start with the local baseline, compare model endpoints when they are
            configured, and keep every claim tied to visible evidence.
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row lg:shrink-0">
          <Button
            type="button"
            size="lg"
            onClick={() => scrollToSection("demo")}
            className="w-full border-[#A78BFA]/40 bg-[#8B5CF6] text-white shadow-[0_18px_35px_rgba(139,92,246,0.30)] hover:bg-[#7C3AED] sm:w-auto"
          >
            <Play className="size-4" aria-hidden="true" />
            Try the analyzer
          </Button>
          <Button
            type="button"
            size="lg"
            variant="outline"
            onClick={() => scrollToSection("metrics")}
            className="w-full sm:w-auto"
          >
            Compare metrics
            <ArrowRight className="size-4" aria-hidden="true" />
          </Button>
        </div>
      </div>
    </section>
  )
}

export function SectionIntro({
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
      <div className="text-sm font-bold text-[#A78BFA]">{eyebrow}</div>
      <h2 className="mt-2 text-3xl font-bold leading-tight text-[#F8F5FF] sm:text-4xl">
        {title}
      </h2>
      <p className="mt-3 text-base leading-7 text-[#C6BADF]">{description}</p>
    </div>
  )
}

export function WorkflowCard({
  icon,
  title,
  text,
}: {
  icon: ReactNode
  title: string
  text: string
}) {
  return (
    <article className="rounded-[8px] border border-[#3A285C] bg-[#151027] p-5 shadow-[0_18px_52px_rgba(167,139,250,0.10)]">
      <div className="flex size-10 items-center justify-center rounded-[8px] bg-[#24183D] text-[#B794F6]">
        {icon}
      </div>
      <h3 className="mt-4 text-lg font-bold text-[#F8F5FF]">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-[#C6BADF]">{text}</p>
    </article>
  )
}
