import { NextResponse } from "next/server"

import { analyzeLogWithHeuristic } from "@/lib/heuristic-baseline"
import { TRIAGE_PROVIDER_SCHEMA } from "@/lib/provider-schema"
import { buildTriagePromptMessages } from "@/lib/prompts"
import {
  parseTriageOutput,
  type TriageOutput,
  type TriageParseIssue,
} from "@/lib/triage-schema"

export const dynamic = "force-dynamic"
export const runtime = "nodejs"

type AnalyzerId = "heuristic" | "base-model" | "fine-tuned"
type ResponseFormat =
  | "off"
  | "json_object"
  | "json_schema"
  | "structured_outputs"
  | "guided_json"
  | "responses_parse"

type EndpointEnv = {
  baseUrl: string
  apiKey: string
  model: string
  timeoutSeconds: string
  maxRetries: string
  maxTokens: string
  responseFormat: string
  temperature: string
  topP: string
  extraBody: string
}

type EndpointConfig = {
  baseUrl: string
  apiKey: string
  model: string
  timeoutMs: number
  maxRetries: number
  maxTokens: number
  responseFormat: ResponseFormat
  temperature?: number
  topP?: number
  extraBody?: Record<string, unknown>
}

type SuccessPayload = {
  analyzer: AnalyzerId
  output: TriageOutput
  rawJson: string
  validationIssues: TriageParseIssue[]
  elapsedMs: number
  metadata: Record<string, unknown>
}

type PublicEndpointConfig = {
  analyzer: Exclude<AnalyzerId, "heuristic">
  label: string
  modelEnv: string
  model: string | null
  configured: boolean
}

type PublicConfigPayload = {
  endpoints: {
    baseModel: PublicEndpointConfig
    fineTuned: PublicEndpointConfig
  }
}

const ENDPOINT_ENVS: Record<Exclude<AnalyzerId, "heuristic">, EndpointEnv> = {
  "base-model": {
    baseUrl: "OPENAI_COMPATIBLE_BASE_URL",
    apiKey: "OPENAI_COMPATIBLE_API_KEY",
    model: "OPENAI_COMPATIBLE_MODEL",
    timeoutSeconds: "OPENAI_COMPATIBLE_TIMEOUT_SECONDS",
    maxRetries: "OPENAI_COMPATIBLE_MAX_RETRIES",
    maxTokens: "OPENAI_COMPATIBLE_MAX_TOKENS",
    responseFormat: "OPENAI_COMPATIBLE_RESPONSE_FORMAT",
    temperature: "OPENAI_COMPATIBLE_TEMPERATURE",
    topP: "OPENAI_COMPATIBLE_TOP_P",
    extraBody: "OPENAI_COMPATIBLE_EXTRA_BODY",
  },
  "fine-tuned": {
    baseUrl: "OPENAI_FINETUNE_BASE_URL",
    apiKey: "OPENAI_FINETUNE_API_KEY",
    model: "OPENAI_FINETUNE_MODEL",
    timeoutSeconds: "OPENAI_FINETUNE_TIMEOUT_SECONDS",
    maxRetries: "OPENAI_FINETUNE_MAX_RETRIES",
    maxTokens: "OPENAI_FINETUNE_MAX_TOKENS",
    responseFormat: "OPENAI_FINETUNE_RESPONSE_FORMAT",
    temperature: "OPENAI_FINETUNE_TEMPERATURE",
    topP: "OPENAI_FINETUNE_TOP_P",
    extraBody: "OPENAI_FINETUNE_EXTRA_BODY",
  },
}

const RESPONSE_FORMATS: ReadonlySet<ResponseFormat> = new Set([
  "off",
  "json_object",
  "json_schema",
  "structured_outputs",
  "guided_json",
  "responses_parse",
])

export async function GET() {
  return NextResponse.json({
    endpoints: {
      baseModel: readPublicEndpointConfig("base-model"),
      fineTuned: readPublicEndpointConfig("fine-tuned"),
    },
  } satisfies PublicConfigPayload)
}

export async function POST(request: Request) {
  const started = performance.now()
  let body: unknown

  try {
    body = await request.json()
  } catch {
    return errorResponse("Request body must be valid JSON.", 400)
  }

  if (!isPlainRecord(body)) {
    return errorResponse("Request body must be a JSON object.", 400)
  }

  const analyzer = body.analyzer
  const logLine = body.logLine

  if (!isAnalyzerId(analyzer)) {
    return errorResponse("Unknown analyzer.", 400)
  }

  if (typeof logLine !== "string" || logLine.trim().length === 0) {
    return errorResponse("logLine must be a non-empty string.", 400)
  }

  if (analyzer === "heuristic") {
    const output = analyzeLogWithHeuristic(logLine.trim())
    const validation = parseTriageOutput(output)
    return NextResponse.json({
      analyzer,
      output,
      rawJson: JSON.stringify(output, null, 2),
      validationIssues: validation.ok ? [] : validation.errors,
      elapsedMs: performance.now() - started,
      metadata: {
        provider: "local-heuristic",
      },
    } satisfies SuccessPayload)
  }

  const config = readEndpointConfig(analyzer)
  if ("error" in config) {
    return errorResponse(config.error, 400, {
      code: "unconfigured",
      analyzer,
      elapsedMs: performance.now() - started,
    })
  }

  const invokeResult = await invokeOpenAICompatible(logLine.trim(), config)
  if ("error" in invokeResult) {
    return errorResponse(invokeResult.error, invokeResult.status, {
      analyzer,
      rawJson: invokeResult.rawJson,
      elapsedMs: performance.now() - started,
    })
  }

  const parsed = parseTriageOutput(invokeResult.output)
  if (!parsed.ok) {
    return errorResponse("Endpoint returned JSON that does not match the triage schema.", 502, {
      analyzer,
      rawJson: JSON.stringify(invokeResult.output, null, 2),
      validationIssues: parsed.errors,
      elapsedMs: performance.now() - started,
      metadata: invokeResult.metadata,
    })
  }

  return NextResponse.json({
    analyzer,
    output: parsed.data,
    rawJson: JSON.stringify(parsed.data, null, 2),
    validationIssues: [],
    elapsedMs: performance.now() - started,
    metadata: invokeResult.metadata,
  } satisfies SuccessPayload)
}

function readPublicEndpointConfig(
  analyzer: Exclude<AnalyzerId, "heuristic">,
): PublicEndpointConfig {
  const env = ENDPOINT_ENVS[analyzer]
  const model = process.env[env.model]?.trim() || null

  return {
    analyzer,
    label: analyzer === "base-model" ? "Base model" : "Fine-tuned model",
    modelEnv: env.model,
    model,
    configured: Boolean(
      process.env[env.baseUrl]?.trim() &&
        process.env[env.apiKey]?.trim() &&
        model,
    ),
  }
}

function readEndpointConfig(
  analyzer: Exclude<AnalyzerId, "heuristic">,
): EndpointConfig | { error: string } {
  const env = ENDPOINT_ENVS[analyzer]
  const baseUrl = process.env[env.baseUrl]
  const apiKey = process.env[env.apiKey]
  const model = process.env[env.model]

  const missing = [
    [env.baseUrl, baseUrl],
    [env.apiKey, apiKey],
    [env.model, model],
  ]
    .filter(([, value]) => !value)
    .map(([name]) => name)

  if (missing.length > 0) {
    return {
      error: `Missing endpoint environment variables: ${missing.join(", ")}.`,
    }
  }

  const responseFormat = parseResponseFormat(process.env[env.responseFormat])
  const extraBody = parseExtraBody(process.env[env.extraBody])
  if ("error" in extraBody) {
    return { error: extraBody.error }
  }

  return {
    baseUrl: baseUrl!,
    apiKey: apiKey!,
    model: model!,
    timeoutMs: secondsToMs(process.env[env.timeoutSeconds], 30),
    maxRetries: parseInteger(process.env[env.maxRetries], 1),
    maxTokens: parseInteger(process.env[env.maxTokens], 512),
    responseFormat,
    temperature: parseOptionalNumber(process.env[env.temperature]),
    topP: parseOptionalNumber(process.env[env.topP]),
    extraBody: extraBody.value,
  }
}

async function invokeOpenAICompatible(
  logLine: string,
  config: EndpointConfig,
): Promise<
  | {
      output: unknown
      metadata: Record<string, unknown>
    }
  | {
      error: string
      status: number
      rawJson?: string
    }
> {
  const requestBody = buildChatCompletionBody(logLine, config)
  const endpoint = chatCompletionsEndpoint(config.baseUrl)
  let lastError = "Endpoint request failed."

  for (let attempt = 0; attempt <= config.maxRetries; attempt += 1) {
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), config.timeoutMs)

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${config.apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      })
      const responseText = await response.text()

      if (!response.ok) {
        lastError = `Endpoint returned ${response.status}: ${responseText.slice(0, 500)}`
        continue
      }

      const responseJson = safeJsonParse(responseText)
      if (!responseJson.ok) {
        return {
          error: "Endpoint response was not valid JSON.",
          status: 502,
          rawJson: responseText,
        }
      }

      const content = extractChatContent(responseJson.value)
      if (typeof content !== "string" || content.trim().length === 0) {
        return {
          error: "Endpoint response did not include message content.",
          status: 502,
          rawJson: JSON.stringify(responseJson.value, null, 2),
        }
      }

      const parsedContent = parseModelJson(content)
      if (!parsedContent.ok) {
        return {
          error: parsedContent.error,
          status: 502,
          rawJson: content,
        }
      }

      return {
        output: parsedContent.value,
        metadata: {
          provider: "openai-compatible-chat",
          model: config.model,
          response_format_requested: config.responseFormat,
          endpoint,
          attempts: attempt + 1,
        },
      }
    } catch (error) {
      lastError =
        error instanceof Error ? `${error.name}: ${error.message}` : String(error)
    } finally {
      clearTimeout(timeout)
    }
  }

  return {
    error: lastError,
    status: 502,
  }
}

function chatCompletionsEndpoint(baseUrl: string): string {
  const endpoint = baseUrl.replace(/\/+$/, "")
  return endpoint.endsWith("/chat/completions")
    ? endpoint
    : `${endpoint}/chat/completions`
}

function buildChatCompletionBody(
  logLine: string,
  config: EndpointConfig,
): Record<string, unknown> {
  const body: Record<string, unknown> = {
    model: config.model,
    messages: buildTriagePromptMessages(logLine),
    max_tokens: config.maxTokens,
  }

  if (config.temperature !== undefined) {
    body.temperature = config.temperature
  }
  if (config.topP !== undefined) {
    body.top_p = config.topP
  }

  if (config.responseFormat === "json_object") {
    body.response_format = { type: "json_object" }
  }
  if (
    config.responseFormat === "json_schema" ||
    config.responseFormat === "responses_parse"
  ) {
    body.response_format = {
      type: "json_schema",
      json_schema: {
        name: "triage_output",
        strict: true,
        schema: TRIAGE_PROVIDER_SCHEMA,
      },
    }
  }
  if (config.responseFormat === "structured_outputs") {
    body.structured_outputs = { json: TRIAGE_PROVIDER_SCHEMA }
  }
  if (config.responseFormat === "guided_json") {
    body.guided_json = TRIAGE_PROVIDER_SCHEMA
  }

  return {
    ...body,
    ...(config.extraBody ?? {}),
  }
}

function parseModelJson(
  content: string,
): { ok: true; value: unknown } | { ok: false; error: string } {
  const direct = safeJsonParse(content)
  if (direct.ok) {
    return direct
  }

  const start = content.indexOf("{")
  const end = content.lastIndexOf("}")
  if (start >= 0 && end > start) {
    const extracted = safeJsonParse(content.slice(start, end + 1))
    if (extracted.ok) {
      return extracted
    }
  }

  return {
    ok: false,
    error: "Endpoint message content was not a valid JSON object.",
  }
}

function extractChatContent(value: unknown): unknown {
  if (!isPlainRecord(value) || !Array.isArray(value.choices)) {
    return null
  }
  const firstChoice = value.choices[0]
  if (!isPlainRecord(firstChoice) || !isPlainRecord(firstChoice.message)) {
    return null
  }
  return firstChoice.message.content
}

function errorResponse(
  error: string,
  status: number,
  details: Record<string, unknown> = {},
) {
  return NextResponse.json(
    {
      error,
      ...details,
    },
    { status },
  )
}

function parseResponseFormat(value: string | undefined): ResponseFormat {
  if (value && RESPONSE_FORMATS.has(value as ResponseFormat)) {
    return value as ResponseFormat
  }
  return "structured_outputs"
}

function parseExtraBody(
  value: string | undefined,
): { value: Record<string, unknown> | undefined } | { error: string } {
  if (!value) {
    return { value: undefined }
  }
  const parsed = safeJsonParse(value)
  if (!parsed.ok || !isPlainRecord(parsed.value)) {
    return { error: "Endpoint EXTRA_BODY must be a JSON object." }
  }
  return { value: parsed.value }
}

function secondsToMs(value: string | undefined, fallback: number): number {
  return parseInteger(value, fallback) * 1000
}

function parseInteger(value: string | undefined, fallback: number): number {
  if (!value) {
    return fallback
  }
  const parsed = Number.parseInt(value, 10)
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback
}

function parseOptionalNumber(value: string | undefined): number | undefined {
  if (!value) {
    return undefined
  }
  const parsed = Number.parseFloat(value)
  return Number.isFinite(parsed) ? parsed : undefined
}

function safeJsonParse(
  value: string,
): { ok: true; value: unknown } | { ok: false } {
  try {
    return {
      ok: true,
      value: JSON.parse(value),
    }
  } catch {
    return { ok: false }
  }
}

function isAnalyzerId(value: unknown): value is AnalyzerId {
  return (
    value === "heuristic" ||
    value === "base-model" ||
    value === "fine-tuned"
  )
}

function isPlainRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value)
}
