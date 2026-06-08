const fs = require("fs");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..", "..");

const PATHS = {
  approvalInbox: path.join(repoRoot, "automation", "orchestration", "approval_inbox", "APPROVAL_INBOX_001.json"),
  applyGate: path.join(repoRoot, "automation", "orchestration", "approval_inbox", "APPLY_APPROVAL_GATE_001.json"),
  commandQueue: path.join(repoRoot, "automation", "orchestration", "command_queue", "AIOS_COMMAND_QUEUE.json"),
  workerInbox: path.join(repoRoot, "automation", "orchestration", "workers", "inbox", "AIOS_WORKER_INBOX.json"),
  workerRegistry: path.join(repoRoot, "automation", "orchestration", "workers", "AIOS_WORKER_REGISTRY.json"),
  workerProfiles: path.join(repoRoot, "automation", "orchestration", "workers", "AIOS_WORKER_PROFILES.json"),
  lockRegistry: path.join(repoRoot, "automation", "orchestration", "locks", "FILE_LOCK_REGISTRY_001.json"),
  reportRoot: path.join(repoRoot, "Reports", "phase_0_to_4_bridge")
};

const BLOCKED_PACKET_PATTERNS = [
  { id: "secret_request", pattern: /(print|show|display)\s+(secret|token|key)|api[_ -]?key|\.env/i },
  { id: "provider_call", pattern: /openai api call|provider api call|live model|external model/i },
  { id: "cloud_or_tunnel", pattern: /azure app service|cloud deploy|deployment|tunnel|ngrok|cloudflared/i },
  { id: "approval_mutation", pattern: /mutate approval|approve automatically|auto[-_ ]?approve/i },
  { id: "worker_mutation", pattern: /mutate worker|launch codex|run queued command|execute queue/i },
  { id: "live_trading", pattern: /live trading|real order|place order|oanda|broker runtime/i }
];

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

function countBy(items, key) {
  return items.reduce((counts, item) => {
    const value = item && item[key] ? String(item[key]) : "UNKNOWN";
    counts[value] = (counts[value] || 0) + 1;
    return counts;
  }, {});
}

function listLatestReports(limit = 10) {
  if (!fs.existsSync(PATHS.reportRoot)) {
    return [];
  }

  return fs.readdirSync(PATHS.reportRoot, { withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => {
      const fullPath = path.join(PATHS.reportRoot, entry.name);
      const stats = fs.statSync(fullPath);
      return {
        path: relativePath(fullPath),
        name: entry.name,
        sizeBytes: stats.size,
        modifiedAt: stats.mtime.toISOString()
      };
    })
    .sort((left, right) => right.modifiedAt.localeCompare(left.modifiedAt))
    .slice(0, limit);
}

function getBridgeHealth() {
  return {
    schema: "aios.app_service_bridge.health.v0",
    generatedAt: nowIso(),
    mode: "LOCAL_DRY_RUN_PREVIEW_ONLY",
    ok: true,
    service: "aios-app-service-bridge-v0",
    localOnly: true,
    providerCallsEnabled: false,
    approvalMutationEnabled: false,
    workerMutationEnabled: false,
    queuedCommandExecutionEnabled: false,
    codexLaunchEnabled: false,
    cloudDeploymentEnabled: false,
    tunnelEnabled: false,
    hookInstallEnabled: false,
    stateStore: {
      mode: "PROPOSED_ONLY",
      proposedRoot: "telemetry/app_service_bridge/",
      writesEnabled: false,
      gitignoreHandling: "Propose before writing recurring generated outputs."
    },
    endpoints: ["GET /health", "POST /packets", "GET /queue", "POST /approvals", "GET /workers", "GET /reports/latest", "POST /sos"],
    nextSafeAction: "Use endpoints for local preview and read-only status only."
  };
}

function validatePacketDraft(body = {}) {
  const text = String(body.packet_text || body.prompt || body.text || "");
  const packetId = String(body.packet_id || body.packetId || "UNKNOWN");
  const errors = [];
  const warnings = [];

  if (!text.trim()) {
    errors.push("packet_text is required for preview validation.");
  }
  if (text && !text.split(/\r?\n/)[0].includes("CODEX-ONLY PROMPT")) {
    errors.push("Packet must begin with CODEX-ONLY PROMPT.");
  }
  for (const marker of ["AI_OS EXECUTION TOKEN", "AI_OS BOOTSTRAP REQUIRED", "MISSION", "VALIDATOR CHAIN", "STOP POINT"]) {
    if (text && !text.includes(marker)) {
      warnings.push(`Missing expected marker: ${marker}`);
    }
  }

  const blocked = BLOCKED_PACKET_PATTERNS
    .filter((rule) => rule.pattern.test(text))
    .map((rule) => rule.id);

  return {
    schema: "aios.app_service_bridge.packet_preview.v0",
    generatedAt: nowIso(),
    mode: "PREVIEW_ONLY",
    packetId,
    acceptedForExecution: false,
    providerCallPerformed: false,
    codexLaunched: false,
    queueMutated: false,
    approvalMutated: false,
    status: errors.length || blocked.length ? "BLOCKED" : warnings.length ? "REVIEW" : "PREVIEW_READY",
    errors,
    warnings,
    blockedReasons: blocked,
    routePreview: {
      suggestedLane: body.lane || body.suggested_lane || "UNRESOLVED",
      approvalRequired: true,
      nextRequiredHumanAction: "Review packet and approve a separate APPLY command before mutation."
    },
    nextSafeAction: "Validate locally and submit for Human Owner approval before APPLY."
  };
}

function getQueuePreview() {
  const commandQueue = readJsonFile(PATHS.commandQueue);
  const workerInbox = readJsonFile(PATHS.workerInbox);
  const commandItems = Array.isArray(commandQueue.data?.items) ? commandQueue.data.items : [];
  const workerItems = Array.isArray(workerInbox.data?.items) ? workerInbox.data.items : [];

  return {
    schema: "aios.app_service_bridge.queue.v0",
    generatedAt: nowIso(),
    mode: "READ_ONLY",
    commandQueue: {
      source: commandQueue.path,
      exists: commandQueue.exists,
      ok: commandQueue.ok,
      error: commandQueue.error,
      itemCount: commandItems.length,
      countsByStatus: countBy(commandItems, "status")
    },
    workerInbox: {
      source: workerInbox.path,
      exists: workerInbox.exists,
      ok: workerInbox.ok,
      error: workerInbox.error,
      itemCount: workerItems.length,
      countsByStatus: countBy(workerItems, "status"),
      countsByApprovalStatus: countBy(workerItems, "approval_status")
    },
    mutationEnabled: false,
    queuedCommandExecutionEnabled: false,
    nextSafeAction: "Review queue status only. This endpoint does not add, move, launch, or execute work."
  };
}

function previewApproval(body = {}) {
  const approvalInbox = readJsonFile(PATHS.approvalInbox);
  const applyGate = readJsonFile(PATHS.applyGate);
  const requestedAction = String(body.requested_action || body.action || "UNKNOWN");

  return {
    schema: "aios.app_service_bridge.approval_preview.v0",
    generatedAt: nowIso(),
    mode: "PREVIEW_ONLY",
    requestedAction,
    approvalRecorded: false,
    approvalInboxMutated: false,
    applyGateMutated: false,
    authority: {
      approvalInbox: {
        source: approvalInbox.path,
        exists: approvalInbox.exists,
        ok: approvalInbox.ok,
        approvalStatus: approvalInbox.data?.approval_status || "UNKNOWN"
      },
      applyGate: {
        source: applyGate.path,
        exists: applyGate.exists,
        ok: applyGate.ok,
        approvalStatus: applyGate.data?.approval_status || "UNKNOWN",
        approvedMode: applyGate.data?.approved_mode || "UNKNOWN"
      }
    },
    decisionPreview: "HUMAN_OWNER_REVIEW_REQUIRED",
    nextSafeAction: "Create or update approval records only through a separately approved workflow."
  };
}

function getWorkersPreview() {
  const registry = readJsonFile(PATHS.workerRegistry);
  const profiles = readJsonFile(PATHS.workerProfiles);
  const inbox = readJsonFile(PATHS.workerInbox);
  const locks = readJsonFile(PATHS.lockRegistry);
  const workers = Array.isArray(registry.data?.workers) ? registry.data.workers : [];
  const inboxItems = Array.isArray(inbox.data?.items) ? inbox.data.items : [];

  return {
    schema: "aios.app_service_bridge.workers.v0",
    generatedAt: nowIso(),
    mode: "READ_ONLY",
    registry: {
      source: registry.path,
      exists: registry.exists,
      ok: registry.ok,
      workerCount: workers.length,
      countsByType: countBy(workers, "type")
    },
    profiles: {
      source: profiles.path,
      exists: profiles.exists,
      ok: profiles.ok,
      error: profiles.error
    },
    inbox: {
      source: inbox.path,
      exists: inbox.exists,
      ok: inbox.ok,
      itemCount: inboxItems.length,
      countsByStatus: countBy(inboxItems, "status")
    },
    locks: {
      source: locks.path,
      exists: locks.exists,
      ok: locks.ok,
      status: locks.data?.status || "UNKNOWN",
      lockId: locks.data?.lock_id || "UNKNOWN"
    },
    mutationEnabled: false,
    codexLaunchEnabled: false,
    nextSafeAction: "Review worker and lock status only. This endpoint does not claim locks or launch workers."
  };
}

function getLatestReports() {
  const reports = listLatestReports();
  return {
    schema: "aios.app_service_bridge.reports_latest.v0",
    generatedAt: nowIso(),
    mode: "READ_ONLY",
    reportRoot: relativePath(PATHS.reportRoot),
    latest: reports[0] || null,
    reports,
    nextSafeAction: "Use report evidence for review only. This endpoint does not generate or promote reports."
  };
}

function previewSos(body = {}) {
  const message = String(body.message || body.summary || "");
  const severity = String(body.severity || "SOS_PREVIEW").toUpperCase();
  const allowed = severity.includes("SOS") || severity === "CRITICAL";

  return {
    schema: "aios.app_service_bridge.sos_preview.v0",
    generatedAt: nowIso(),
    mode: "PREVIEW_ONLY",
    acceptedForNotification: allowed,
    notificationSent: false,
    telemetryWritten: false,
    severity,
    messagePreview: message.slice(0, 500),
    blockedReason: allowed ? null : "Only SOS or CRITICAL notification previews are accepted in v0.",
    nextSafeAction: "Send no notification from v0. Route SOS preview for Human Owner review."
  };
}

module.exports = {
  getBridgeHealth,
  validatePacketDraft,
  getQueuePreview,
  previewApproval,
  getWorkersPreview,
  getLatestReports,
  previewSos
};
