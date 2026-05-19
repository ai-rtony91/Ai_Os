const fs = require("fs");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..", "..");
const runtimeDir = path.join(repoRoot, "telemetry", "runtime");
const runtimeStatePath = path.join(runtimeDir, "runtime_state.json");
const runtimeHeartbeatPath = path.join(runtimeDir, "runtime_heartbeat.json");
const runtimeProcessPath = path.join(runtimeDir, "runtime_process.json");
const telemetryLedgerPath = path.join(repoRoot, "telemetry", "work_ledger.jsonl");
const dispatcherQueuePath = path.join(
  repoRoot,
  "automation",
  "orchestration",
  "queue",
  "DISPATCHER_QUEUE.json"
);

function nowIso() {
  return new Date().toISOString();
}

function relativePath(fullPath) {
  return path.relative(repoRoot, fullPath).replace(/\\/g, "/");
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
      invalidLineCount: audit.invalidLineCount
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

  return {
    schema: "aios.runtime_visibility_api.v1",
    generatedAt: nowIso(),
    mode: "READ_ONLY",
    runtime: status.runtime,
    health,
    queue: queue.queue,
    audit: {
      ledgerPath: audit.ledgerPath,
      sourceEventCount: audit.sourceEventCount,
      invalidLineCount: audit.invalidLineCount,
      recentTimeline: audit.timeline
    },
    controls: getControlSummary().controls,
    nextSafeAction: "Use this visibility snapshot for internal read-only consumers. No control action is exposed."
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
  getControlSummary
};
