import type { TriageOutput } from "./triage-schema"

const LOW_ACTION = "No immediate action required. Continue normal monitoring."

function triageOutput(
  label: TriageOutput["label"],
  severity: TriageOutput["severity"],
  isSuspicious: boolean,
  evidence: string[],
  reason: string,
  recommendedAction: string,
): TriageOutput {
  return {
    label,
    severity,
    is_suspicious: isSuspicious,
    evidence,
    reason,
    recommended_action: recommendedAction,
  }
}

function firstMatch(logLine: string, patterns: RegExp[]): string | null {
  for (const pattern of patterns) {
    const match = pattern.exec(logLine)
    if (match) {
      return match[1] ?? match[0]
    }
  }
  return null
}

function uniqueEvidence(items: Array<string | null | undefined>): string[] {
  const evidence: string[] = []
  for (const item of items) {
    if (item && !evidence.includes(item)) {
      evidence.push(item)
    }
  }
  return evidence
}

function numberAfter(logLine: string, key: string): number | null {
  const match = new RegExp(`${escapeRegExp(key)}[=\\s](\\d+)`, "i").exec(
    logLine,
  )
  if (!match) {
    return null
  }
  return Number.parseInt(match[1], 10)
}

function apacheStatus(logLine: string): string | null {
  return (
    firstMatch(logLine, [/HTTP\/1\.1"\s+(\d{3})\b/i]) ??
    firstMatch(logLine, [/\bstatus=(\d{3})\b/i])
  )
}

function analyzeSqlInjection(logLine: string): TriageOutput | null {
  const payload = firstMatch(logLine, [
    /(username=[^\s]*'(?:--|\s+OR\s+'?1'?\s*=\s*'?1'?)\S*)/i,
    /(username=%27%20OR%20[^ ]+)/i,
    /((?:id|q)=[^ ]*\bUNION\s+SELECT\b[^ ]*(?:\s+[^ ]+)*?--)/i,
    /((?:id|q)=\d+\s+OR\s+1\s*=\s*1\b)/i,
    /((?:id|q)=[^ ]*\bOR\s+1\s*=\s*1\b)/i,
    /((?:id|q)=[^ ]*\bAND\s+SLEEP\(\d+\))/i,
    /((?:id|q)=[^ ]*SLEEP\(\d+\))/i,
    /((?:id|q)=[^ ]*information_schema[^\s"]*)/i,
    /((?:id|q)=[^ ]*DROP\s+TABLE[^"\s]*)/i,
    /(%27%20OR%20%271%27%3D%271)/i,
    /(%27%20OR%201%3D1--)/i,
    /(' OR '1'='1)/i,
    /(UNION\s+SELECT\s+[^"\s]+(?:\s+[^"\s]+)*?--)/i,
    /(DROP\s+TABLE\s+\w+--)/i,
    /(SLEEP\(\d+\))/i,
    /(information_schema\.\w+)/i,
    /(admin'--)/i,
  ])

  if (!payload) {
    return null
  }

  const status = apacheStatus(logLine)
  const severity = /\bDROP\s+TABLE\b/i.test(payload) ? "critical" : "high"
  return triageOutput(
    "sql_injection_attempt",
    severity,
    true,
    uniqueEvidence([
      payload,
      logLine.includes("status=") && status ? `status=${status}` : status,
    ]),
    "The log contains SQL syntax or encoded SQL operators in a user-controlled request field.",
    "Review related web and database logs for the source and verify whether the request reached sensitive query paths.",
  )
}

function analyzeDirectoryTraversal(logLine: string): TriageOutput | null {
  const payload = firstMatch(logLine, [
    /(rule=path_traversal)/i,
    /(GET\s+\/download\?file=[^ ]+)/i,
    /(\/static\/(?:\.\.\/|\.\.%2f|%2e%2e%2f)[^ ]+)/i,
    /(\/files\/(?:\.\.\\|\.\.%5c|%2e%2e%5c)[^"]+)/i,
    /((?:\.\.\/){1,}[^ "\t]+)/i,
    /((?:\.\.\\){1,}[^ "\t]+)/i,
    /((?:\.\.%2f|%2e%2e%2f){1,}[^ "\t]+)/i,
    /((?:\.\.%5c|%2e%2e%5c){1,}[^ "\t]+)/i,
  ])

  if (!payload) {
    return null
  }

  let secondary =
    payload !== "rule=path_traversal"
      ? firstMatch(logLine, [/(rule=path_traversal)/i])
      : null
  if (!secondary) {
    const status = apacheStatus(logLine)
    secondary = logLine.includes("status=") && status ? `status=${status}` : status
  }

  return triageOutput(
    "directory_traversal_attempt",
    "high",
    true,
    uniqueEvidence([payload, secondary]),
    "The request contains parent-directory traversal sequences targeting files outside the intended path.",
    "Review web server and WAF logs to confirm the request was blocked and search for related attempts from the source.",
  )
}

function analyzeFailedLoginBruteforce(logLine: string): TriageOutput | null {
  const repeated = numberAfter(logLine, "repeated")
  const failures = numberAfter(logLine, "failures")
  const count = numberAfter(logLine, "count")

  if (/Failed password/i.test(logLine) && repeated !== null) {
    return triageOutput(
      "failed_login_bruteforce",
      repeated >= 12 ? "high" : "medium",
      true,
      uniqueEvidence(["Failed password", `repeated ${repeated} times`]),
      "The log shows repeated failed SSH authentication attempts in a short time window.",
      "Review authentication logs for the source IP and consider blocking or rate-limiting it.",
    )
  }

  if (logLine.includes("event=login_failed") && failures !== null) {
    return triageOutput(
      "failed_login_bruteforce",
      failures >= 15 ? "high" : "medium",
      true,
      uniqueEvidence([
        "event=login_failed",
        `failures=${failures}`,
        firstMatch(logLine, [/(outcome=blocked)/i]),
      ]),
      "The source generated many failed application login attempts.",
      "Review the account and source IP for password spraying or brute force activity.",
    )
  }

  if (
    logLine.includes("event_id=4625") &&
    logLine.includes("status=failed_logon") &&
    count !== null
  ) {
    return triageOutput(
      "failed_login_bruteforce",
      count >= 12 ? "high" : "medium",
      true,
      uniqueEvidence(["event_id=4625", `count=${count}`, "status=failed_logon"]),
      "Multiple failed Windows logon events indicate a brute force pattern.",
      "Check whether the target account was locked and review related endpoint events.",
    )
  }

  const webRepeated = firstMatch(logLine, [/(status=401 repeated=(\d+))/i])
  if (logLine.includes("POST /login") && webRepeated) {
    const repeatedCount = numberAfter(logLine, "repeated") ?? 0
    return triageOutput(
      "failed_login_bruteforce",
      repeatedCount >= 20 ? "high" : "medium",
      true,
      uniqueEvidence([
        "POST /login",
        `status=401 repeated=${repeatedCount}`,
        firstMatch(logLine, [/(python-requests)/i]),
      ]),
      "The log shows repeated failed login responses from one automated client.",
      "Review WAF and application logs for the source and consider temporary blocking.",
    )
  }

  return null
}

function analyzePortScan(logLine: string): TriageOutput | null {
  if (logLine.includes("nmap fingerprint")) {
    return triageOutput(
      "port_scan_or_recon",
      "high",
      true,
      uniqueEvidence([
        "nmap fingerprint",
        firstMatch(logLine, [/(probed_ports=[0-9,]+)/i]),
      ]),
      "The IDS identified an Nmap-like fingerprint and multiple probed ports.",
      "Investigate the source IP and check whether it touched other hosts.",
    )
  }

  if (logLine.includes("SYN scan detected")) {
    return triageOutput(
      "port_scan_or_recon",
      "medium",
      true,
      uniqueEvidence([
        "SYN scan detected",
        firstMatch(logLine, [/(ports=[0-9,]+)/i]),
      ]),
      "The firewall detected connection attempts across multiple destination ports.",
      "Review network logs for additional reconnaissance from the source IP.",
    )
  }

  if (logLine.includes("sequential connection attempts")) {
    return triageOutput(
      "port_scan_or_recon",
      "medium",
      true,
      uniqueEvidence([
        "sequential connection attempts",
        firstMatch(logLine, [/(unique_ports=\d+)/i]),
      ]),
      "The flow shows sequential attempts against several destination ports.",
      "Correlate with firewall and IDS logs to determine the scan scope.",
    )
  }

  return null
}

function analyzeNormal(logLine: string): TriageOutput {
  if (logLine.includes("kube-probe")) {
    return triageOutput(
      "normal",
      "low",
      false,
      uniqueEvidence([
        firstMatch(logLine, [/(GET\s+\/(?:health|status|ready))/i]),
        apacheStatus(logLine),
        logLine.includes("kube-probe/1.29") ? "kube-probe/1.29" : null,
      ]),
      "The request is a routine service health check with a successful response.",
      LOW_ACTION,
    )
  }

  if (logLine.includes("Successful login")) {
    return triageOutput(
      "normal",
      "low",
      false,
      uniqueEvidence([
        "Successful login",
        firstMatch(logLine, [/(user\s+\S+)/i]),
      ]),
      "The log shows a successful authentication event without suspicious repetition.",
      LOW_ACTION,
    )
  }

  if (logLine.includes("failed_attempts=1")) {
    return triageOutput(
      "normal",
      "low",
      false,
      ["Failed password", "failed_attempts=1"],
      "A single failed authentication event is not enough to classify as brute force.",
      "Monitor for repeated failures from the same source before escalating.",
    )
  }

  if (logLine.includes("/search?q=") && apacheStatus(logLine) === "200") {
    return triageOutput(
      "normal",
      "low",
      false,
      uniqueEvidence([firstMatch(logLine, [/(\/search\?q=[^ ]+)/i]), "200"]),
      "The request completed successfully and does not contain a suspicious attack pattern.",
      LOW_ACTION,
    )
  }

  if (
    logLine.includes("allowed tcp connection") &&
    logLine.includes("session_count=1")
  ) {
    return triageOutput(
      "normal",
      "low",
      false,
      ["allowed tcp connection", "session_count=1"],
      "The log shows one allowed connection, not a scan across multiple ports.",
      LOW_ACTION,
    )
  }

  return triageOutput(
    "normal",
    "low",
    false,
    [logLine.slice(0, 160) || "empty log input"],
    "No known suspicious pattern was matched by the heuristic baseline.",
    "Continue monitoring and correlate with surrounding logs if this event appears unusual.",
  )
}

export function analyzeLogWithHeuristic(logLine: string): TriageOutput {
  for (const analyzer of [
    analyzeSqlInjection,
    analyzeDirectoryTraversal,
    analyzeFailedLoginBruteforce,
    analyzePortScan,
  ]) {
    const result = analyzer(logLine)
    if (result) {
      return result
    }
  }
  return analyzeNormal(logLine)
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}
