const fs = require("fs");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..", "..");
const runtimeDir = path.join(repoRoot, "telemetry", "runtime");
const runtimeStatePath = path.join(runtimeDir, "runtime_state.json");
const runtimeHeartbeatPath = path.join(runtimeDir, "runtime_heartbeat.json");
const runtimeProcessPath = path.join(runtimeDir, "runtime_process.json");
const telemetryLedgerPath = path.join(repoRoot, "telemetry", "work_ledger.jsonl");
const nightSupervisorLedgerPath = path.join(
  repoRoot,
  "telemetry",
  "night_supervisor",
  "night_ledger.jsonl"
);
const dispatcherQueuePath = path.join(
  repoRoot,
  "automation",
  "orchestration",
  "queue",
  "DISPATCHER_QUEUE.json"
);
const FRONTEND_BLOCKED_ACTIONS = Object.freeze([
  "protected_git",
  "apply",
  "approval_mutation",
  "lock_mutation",
  "worker_launch",
  "runtime_mutation",
  "queue_mutation",
  "broker_execution",
  "live_trading",
  "secret_access"
]);

function nowIso() {
  return new Date().toISOString();
}

function relativePath(fullPath) {
  return path.relative(repoRoot, fullPath).replace(/\\/g, "/");
}

function buildFrontendContract({
  displayState,
  sourcePath,
  sourceType,
  generatedAt,
  isStale,
  nextSafeAction
}) {
  return {
    display_state: displayState || "UNKNOWN",
    authority_state: "EVIDENCE_ONLY",
    source_path: sourcePath || "UNKNOWN",
    source_type: sourceType || "generated_projection",
    freshness: {
      generated_at: generatedAt,
      ttl_seconds: 0,
      is_stale: Boolean(isStale)
    },
    blocked_actions: [...FRONTEND_BLOCKED_ACTIONS],
    next_safe_action:
      nextSafeAction || "Review read-only runtime visibility before any protected action.",
    approval_required: true,
    execution_allowed: false,
    mutation_allowed: false,
    stale_or_legacy: Boolean(isStale),
    safe_for_frontend_display: true
  };
}

function uniquePaths(paths) {
  return [...new Set(paths.filter(Boolean))];
}

function readJsonFile(fullPath) {
  if (!fs.existsSync(fullPath)) {
    return {
      ok: false,
      exists: false,
      path: relativePath(fullPath),
      data: null,
      error: "MISSING"
    };
  }

  try {
    const content = fs.readFileSync(fullPath, "utf8").replace(/^\uFEFF/, "");

    return {
      ok: true,
      exists: true,
      path: relativePath(fullPath),
      data: JSON.parse(content),
      error: null
    };
  } catch (error) {
    return {
      ok: false,
      exists: true,
      path: relativePath(fullPath),
      data: null,
      error: `JSON_PARSE_FAILED: ${error.message}`
    };
  }
}

function readJsonLines(fullPath) {
  const result = {
    exists: fs.existsSync(fullPath),
    path: relativePath(fullPath),
    events: [],
    invalidLineCount: 0
  };

  if (!result.exists) {
    return result;
  }

  const content = fs.readFileSync(fullPath, "utf8");

  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();

    if (!trimmed) {
      continue;
    }

    try {
      result.events.push(JSON.parse(trimmed));
    } catch {
      result.invalidLineCount += 1;
    }
  }

  return result;
}

function countBy(items, key) {
  return items.reduce((counts, item) => {
    const value = item && item[key] ? String(item[key]) : "UNKNOWN";
    counts[value] = (counts[value] || 0) + 1;
    return counts;
  }, {});
}

function parseTime(value) {
  const timestamp = Date.parse(value);
  return Number.isNaN(timestamp) ? null : timestamp;
}

function latestLedgerTimestamp(events) {
  const timestamps = events
    .map((event) => event?.ts || event?.timestamp_utc || event?.timestamp || event?.generatedAt)
    .filter((value) => parseTime(value) !== null)
    .sort();

  return timestamps.at(-1) || null;
}

function ledgerStatus(ledger) {
  if (!ledger.exists) {
    return "MISSING";
  }

  if (ledger.invalidLineCount > 0) {
    return "MIXED_OR_INVALID";
  }

  if (ledger.events.length === 0) {
    return "EMPTY_OR_STALE";
  }

  return "HAS_EVENTS";
}

function getLedgerAuthority() {
  const workLedger = readJsonLines(telemetryLedgerPath);
  const nightLedger = readJsonLines(nightSupervisorLedgerPath);
  const workLatest = latestLedgerTimestamp(workLedger.events);
  const nightLatest = latestLedgerTimestamp(nightLedger.events);

  return {
    schema: "aios.ledger_authority_api.v1",
    mode: "READ_ONLY",
    workLedger: {
      path: workLedger.path,
      role: "GENERAL_WORK_TELEMETRY",
      status: ledgerStatus(workLedger),
      eventCount: workLedger.events.length,
      invalidLineCount: workLedger.invalidLineCount,
      latestEventAt: workLatest,
      evidenceClass: workLatest ? "HISTORICAL_OR_CURRENT_BY_TIMESTAMP" : "STALE_OR_EMPTY"
    },
    nightSupervisorLedger: {
      path: nightLedger.path,
      role: "ACTIVE_NIGHT_RUNTIME_LEDGER",
      status: ledgerStatus(nightLedger),
      eventCount: nightLedger.events.length,
      invalidLineCount: nightLedger.invalidLineCount,
      latestEventAt: nightLatest,
      evidenceClass: nightLatest ? "CURRENT_NIGHT_RUNTIME_EVIDENCE_BY_TIMESTAMP" : "MISSING_OR_STALE"
    },
    activeNightRuntimeLedgerPath: relativePath(nightSupervisorLedgerPath),
    proofBoundary:
      "Night ledger evidence proves Night Supervisor/Night Cycle activity only; productive autonomy requires a real GREEN task output plus truthful marker, validator, ledger, and report evidence.",
    warning:
      "Do not treat stale telemetry/work_ledger.jsonl as proof that no night runtime activity occurred."
  };
}

function getProcessRunning(processInfo) {
  if (!processInfo || !processInfo.processId) {
    return false;
  }

  try {
    process.kill(Number(processInfo.processId), 0);
    return true;
  } catch {
    return false;
  }
}

function getRuntimeStatus() {
  const state = readJsonFile(runtimeStatePath);
  const heartbeat = readJsonFile(runtimeHeartbeatPath);
  const processInfo = readJsonFile(runtimeProcessPath);

  return {
    schema: "aios.runtime_status_api.v1",
    generatedAt: nowIso(),
    repoRoot,
    runtime: {
      statePath: state.path,
      heartbeatPath: heartbeat.path,
      processPath: processInfo.path,
      state: state.data,
      heartbeat: heartbeat.data,
      process: processInfo.data,
      processRunning: getProcessRunning(processInfo.data),
      status: state.data?.status || heartbeat.data?.status || "UNKNOWN"
    },
    sources: {
      state: { exists: state.exists, ok: state.ok, error: state.error },
      heartbeat: { exists: heartbeat.exists, ok: heartbeat.ok, error: heartbeat.error },
      process: { exists: processInfo.exists, ok: processInfo.ok, error: processInfo.error }
    },
    nextSafeAction: "Review runtime status only. This API does not start or stop runtime processes."
  };
}

function getQueueStatus() {
  const queue = readJsonFile(dispatcherQueuePath);
  const items = Array.isArray(queue.data?.items) ? queue.data.items : [];

  return {
    schema: "aios.queue_status_api.v1",
    generatedAt: nowIso(),
    queue: {
      path: queue.path,
      exists: queue.exists,
      ok: queue.ok,
      error: queue.error,
      status: queue.data?.status || "UNKNOWN",
      itemCount: items.length,
      countsByStatus: countBy(items, "status"),
      countsByLane: countBy(items, "lane"),
      items
    },
    nextSafeAction: "Review queue state only. This API does not assign, advance, or edit queue items."
  };
}

function eventCategory(eventType) {
  switch (eventType) {
    case "policy_decision":
      return "policy_decision";
    case "approval_requested":
    case "approval_decided":
      return "approval";
    case "packet_blocked":
      return "failure";
    case "packet_applied":
      return "execution";
    case "clean_state_checked":
      return "recovery";
    case "packet_dispatched":
      return "packet_lifecycle";
    default:
      return "telemetry";
  }
}

function toAuditEntry(event) {
  const eventType = event.eventType || "unknown";
  const packetId = event.packetId || "";
  const approvalId = event.approvalId || "";
  const status = event.status || "";
  const whatChanged = packetId && status
    ? `Packet ${packetId} status became ${status}`
    : approvalId && status
      ? `Approval ${approvalId} status became ${status}`
      : packetId
        ? `Packet ${packetId} recorded ${eventType}`
        : `Recorded ${eventType}`;

  return {
    eventId: event.eventId,
    ts: event.ts,
    category: eventCategory(eventType),
    eventType,
    source: event.source,
    packetId: event.packetId,
    approvalId: event.approvalId,
    status: event.status,
    risk: event.risk,
    why: event.summary,
    whatChanged,
    recoveryAction: eventType === "packet_blocked"
      ? "Keep packet blocked until human review clears approval, policy, and rollback evidence."
      : null
  };
}

function getAuditTimeline(options = {}) {
  const recent = Math.max(0, Number(options.recent || 0));
  const ledger = readJsonLines(telemetryLedgerPath);
  const ledgerAuthority = getLedgerAuthority();
  let timeline = ledger.events
    .map(toAuditEntry)
    .sort((left, right) => String(left.ts || "").localeCompare(String(right.ts || "")));

  if (recent > 0) {
    timeline = timeline.slice(-recent);
  }

  return {
    schema: "aios.audit_timeline_api.v1",
    generatedAt: nowIso(),
    ledgerPath: ledger.path,
    sourceEventCount: ledger.events.length,
    invalidLineCount: ledger.invalidLineCount,
    ledgerAuthority,
    timeline,
    nextSafeAction: "Review blocked, failed, or pending approval events before APPLY, commit, or push."
  };
}

function getRuntimeHealth(options = {}) {
  const staleHeartbeatMinutes = Math.max(1, Number(options.staleHeartbeatMinutes || 2));
  const status = getRuntimeStatus();
  const queue = getQueueStatus();
  const audit = getAuditTimeline();
  const problems = [];
  const heartbeatAt = status.runtime.heartbeat?.heartbeatAt;
  const heartbeatTime = parseTime(heartbeatAt);

  if (!status.sources.state.exists) {
    problems.push("Runtime state file is missing.");
  } else if (!status.sources.state.ok) {
    problems.push(status.sources.state.error);
  } else if (["blocked", "degraded", "failed"].includes(String(status.runtime.status).toLowerCase())) {
    problems.push(`Runtime state is ${status.runtime.status}.`);
  }

  if (!status.sources.heartbeat.exists) {
    problems.push("Runtime heartbeat file is missing.");
  } else if (!status.sources.heartbeat.ok) {
    problems.push(status.sources.heartbeat.error);
  } else if (!heartbeatTime) {
    problems.push("Runtime heartbeat timestamp is invalid.");
  } else {
    const ageMinutes = (Date.now() - heartbeatTime) / 60000;
    if (ageMinutes > staleHeartbeatMinutes) {
      problems.push(`Runtime heartbeat is stale: ${ageMinutes.toFixed(1)} minutes old.`);
    }
  }

  if (!queue.queue.exists) {
    problems.push("Dispatcher queue file is missing.");
  } else if (!queue.queue.ok) {
    problems.push(queue.queue.error);
  }

  if (audit.invalidLineCount > 0) {
    problems.push(`Telemetry ledger has ${audit.invalidLineCount} invalid line(s).`);
  }

  const health = problems.length === 0 ? "OK" : problems.length <= 2 ? "WARN" : "ACTION_NEEDED";

  return {
    schema: "aios.runtime_health_api.v1",
    generatedAt: nowIso(),
    health,
    healthy: problems.length === 0,
    problems,
    runtime: {
      status: status.runtime.status,
      heartbeatAt,
      processRunning: status.runtime.processRunning
    },
    queue: {
      status: queue.queue.status,
      itemCount: queue.queue.itemCount,
      countsByStatus: queue.queue.countsByStatus
    },
    telemetry: {
      ledgerPath: audit.ledgerPath,
      eventCount: audit.sourceEventCount,
      invalidLineCount: audit.invalidLineCount,
      ledgerAuthority: audit.ledgerAuthority
    },
    nextSafeAction: problems.length > 0
      ? "Review health problems before runtime control, APPLY, commit, or push."
      : "Runtime visibility is readable. Continue with read-only monitoring unless APPLY is explicitly approved."
  };
}

function getVisibilitySnapshot() {
  const status = getRuntimeStatus();
  const queue = getQueueStatus();
  const audit = getAuditTimeline({ recent: 20 });
  const health = getRuntimeHealth();
  const generatedAt = nowIso();
  const sourcePaths = uniquePaths([
    status.runtime.statePath,
    status.runtime.heartbeatPath,
    status.runtime.processPath,
    queue.queue.path,
    audit.ledgerPath,
    audit.ledgerAuthority?.nightSupervisorLedger?.path
  ]);
  const nextSafeAction = "Use this visibility snapshot for internal read-only consumers. No control action is exposed.";

  return {
    schema: "aios.runtime_visibility_api.v1",
    generatedAt,
    mode: "READ_ONLY",
    source_paths: sourcePaths,
    frontend_contract: buildFrontendContract({
      displayState: health.healthy ? "READY" : "REVIEW",
      sourcePath: "/api/runtime/visibility",
      sourceType: "api_read_model",
      generatedAt,
      isStale: !health.healthy,
      nextSafeAction
    }),
    projection_items: [
      buildFrontendContract({
        displayState: status.runtime.status,
        sourcePath: status.runtime.statePath,
        sourceType: "runtime_state",
        generatedAt,
        isStale: !health.healthy,
        nextSafeAction: "Review runtime status only. This projection cannot start or stop runtime."
      }),
      buildFrontendContract({
        displayState: queue.queue.status,
        sourcePath: queue.queue.path,
        sourceType: "queue_state",
        generatedAt,
        isStale: !queue.queue.ok,
        nextSafeAction: "Review queue state only. This projection cannot mutate queue items."
      }),
      buildFrontendContract({
        displayState: audit.invalidLineCount > 0 ? "REVIEW" : "DISPLAY_ONLY",
        sourcePath: audit.ledgerPath,
        sourceType: "telemetry",
        generatedAt,
        isStale: audit.sourceEventCount === 0,
        nextSafeAction: "Review telemetry as evidence only before any protected action."
      }),
      buildFrontendContract({
        displayState: "BLOCKED",
        sourcePath: "/api/runtime/control",
        sourceType: "api_read_model",
        generatedAt,
        isStale: false,
        nextSafeAction: "Use PowerShell control scripts only with explicit operator approval."
      })
    ],
    runtime: status.runtime,
    health,
    queue: queue.queue,
    audit: {
      ledgerPath: audit.ledgerPath,
      sourceEventCount: audit.sourceEventCount,
      invalidLineCount: audit.invalidLineCount,
      ledgerAuthority: audit.ledgerAuthority,
      recentTimeline: audit.timeline
    },
    ledgerAuthority: audit.ledgerAuthority,
    controls: getControlSummary().controls,
    nextSafeAction
  };
}

function getControlSummary() {
  return {
    schema: "aios.runtime_control_api.v1",
    generatedAt: nowIso(),
    mode: "READ_ONLY",
    controls: {
      startRuntime: "BLOCKED_BY_API_DEFAULT",
      stopRuntime: "BLOCKED_BY_API_DEFAULT",
      assignQueueItem: "BLOCKED_BY_API_DEFAULT",
      advancePacket: "BLOCKED_BY_API_DEFAULT"
    },
    allowedMethods: ["GET"],
    nextSafeAction: "Use PowerShell control scripts only with explicit operator approval. This API exposes visibility only."
  };
}

module.exports = {
  getRuntimeStatus,
  getQueueStatus,
  getAuditTimeline,
  getRuntimeHealth,
  getVisibilitySnapshot,
  getLedgerAuthority,
  getControlSummary
};
