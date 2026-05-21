const UNKNOWN = "UNKNOWN";

export const RUNTIME_VISIBILITY_SOURCE_LABELS = Object.freeze({
  MOCK_DATA: "MOCK_DATA",
  LOCAL_API_READ_ONLY: "LOCAL_API_READ_ONLY",
  UNKNOWN
});

function asObject(value) {
  return value && typeof value === "object" && !Array.isArray(value) ? value : {};
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function copyObject(value) {
  return { ...asObject(value) };
}

function countByStatus(countsByStatus, ...keys) {
  const counts = asObject(countsByStatus);

  for (const key of keys) {
    if (counts[key] !== undefined && counts[key] !== null) {
      return counts[key];
    }
  }

  return UNKNOWN;
}

function latestEventTimestamp(events) {
  const timestamps = events
    .map((event) => event.ts)
    .filter(Boolean)
    .sort();

  return timestamps.at(-1) ?? null;
}

function normalizeApiTimelineEvent(event) {
  const item = asObject(event);

  return {
    ...item,
    summary: item.summary ?? item.why ?? item.whatChanged ?? UNKNOWN
  };
}

function normalizeApiAlert(problem, healthStatus) {
  return {
    severity: healthStatus === "ACTION_NEEDED" ? "critical" : "warning",
    category: "runtime_health",
    message: problem,
    generatedAt: null
  };
}

function mapRuntimeVisibilityApiDisplayModel(input, sourceLabel) {
  const runtime = asObject(input.runtime);
  const health = asObject(input.health);
  const queue = asObject(input.queue);
  const countsByStatus = asObject(queue.countsByStatus);
  const audit = asObject(input.audit);
  const recentEvents = asArray(audit.recentTimeline).map(normalizeApiTimelineEvent);
  const problems = asArray(health.problems);
  const healthStatus = health.health ?? UNKNOWN;

  return {
    schema: input.schema ?? UNKNOWN,
    generatedAt: input.generatedAt ?? null,
    sourceLabel,
    runtime: {
      runtimeId: UNKNOWN,
      status: runtime.status ?? UNKNOWN,
      freshness: UNKNOWN,
      queueSource: RUNTIME_VISIBILITY_SOURCE_LABELS.LOCAL_API_READ_ONLY,
      lastTickAt: asObject(runtime.heartbeat).heartbeatAt ?? null
    },
    health: {
      healthy: health.healthy ?? false,
      schedulerActions: UNKNOWN,
      expiredWorkers: UNKNOWN,
      poisonPackets: UNKNOWN,
      retryablePackets: UNKNOWN,
      reclaimablePackets: UNKNOWN
    },
    queue: {
      scheduled: queue.itemCount ?? UNKNOWN,
      dispatchable: countByStatus(countsByStatus, "dispatchable", "dispatch", "queued"),
      waitingForApproval: countByStatus(
        countsByStatus,
        "waitingForApproval",
        "wait_for_approval",
        "approval_required"
      ),
      retryable: countByStatus(countsByStatus, "retryable", "retry"),
      manualReview: countByStatus(countsByStatus, "manualReview", "manual_review")
    },
    activePackets: [],
    failedPackets: {
      retryable: [],
      poison: [],
      all: []
    },
    workers: [],
    backpressure: {
      level: UNKNOWN,
      reason: UNKNOWN,
      allowedConcurrentPackets: UNKNOWN,
      pressureInputs: {}
    },
    alerts: problems.map((problem) => normalizeApiAlert(problem, healthStatus)),
    telemetry: {
      eventCount: audit.sourceEventCount ?? UNKNOWN,
      invalidLineCount: audit.invalidLineCount ?? UNKNOWN,
      lastEventAt: latestEventTimestamp(recentEvents),
      recentEvents
    },
    executionLedger: {
      packetCount: UNKNOWN,
      approvalCount: UNKNOWN,
      blockedPacketCount: UNKNOWN,
      appliedPacketCount: UNKNOWN
    },
    nextSafeAction: input.nextSafeAction ?? UNKNOWN
  };
}

export function mapRuntimeVisibilityDisplayModel(data, options = {}) {
  const sourceLabel = options.sourceLabel ?? RUNTIME_VISIBILITY_SOURCE_LABELS.UNKNOWN;
  const input = asObject(data);

  if (input.schema === "aios.runtime_visibility_api.v1") {
    return mapRuntimeVisibilityApiDisplayModel(
      input,
      options.sourceLabel ?? RUNTIME_VISIBILITY_SOURCE_LABELS.LOCAL_API_READ_ONLY
    );
  }

  const runtime = asObject(input.runtime);
  const health = asObject(input.health);
  const queue = asObject(input.queue);
  const failedPackets = asObject(input.failedPackets);
  const backpressure = asObject(input.backpressure);
  const telemetry = asObject(input.telemetry);
  const audit = asObject(input.audit);
  const executionLedger = asObject(input.executionLedger);

  return {
    schema: input.schema ?? UNKNOWN,
    generatedAt: input.generatedAt ?? null,
    sourceLabel,
    runtime: {
      runtimeId: runtime.runtimeId ?? runtime.id ?? UNKNOWN,
      status: runtime.status ?? UNKNOWN,
      freshness: runtime.freshness ?? UNKNOWN,
      queueSource: runtime.queueSource ?? UNKNOWN,
      lastTickAt: runtime.lastTickAt ?? null
    },
    health: {
      healthy: health.healthy ?? false,
      schedulerActions: health.schedulerActions ?? UNKNOWN,
      expiredWorkers: health.expiredWorkers ?? UNKNOWN,
      poisonPackets: health.poisonPackets ?? UNKNOWN,
      retryablePackets: health.retryablePackets ?? UNKNOWN,
      reclaimablePackets: health.reclaimablePackets ?? UNKNOWN
    },
    queue: { ...queue },
    activePackets: asArray(input.activePackets).map(copyObject),
    failedPackets: {
      retryable: asArray(failedPackets.retryable).map(copyObject),
      poison: asArray(failedPackets.poison).map(copyObject),
      all: asArray(failedPackets.all).map(copyObject)
    },
    workers: asArray(input.workers).map(copyObject),
    backpressure: {
      level: backpressure.level ?? UNKNOWN,
      reason: backpressure.reason ?? UNKNOWN,
      allowedConcurrentPackets: backpressure.allowedConcurrentPackets ?? UNKNOWN,
      pressureInputs: { ...asObject(backpressure.pressureInputs) }
    },
    alerts: asArray(input.alerts).map(copyObject),
    telemetry: {
      eventCount: telemetry.eventCount ?? audit.sourceEventCount ?? UNKNOWN,
      invalidLineCount: telemetry.invalidLineCount ?? audit.invalidLineCount ?? UNKNOWN,
      lastEventAt: telemetry.lastEventAt ?? null,
      recentEvents: asArray(telemetry.recentEvents ?? audit.recentTimeline).map(copyObject)
    },
    executionLedger: {
      packetCount: executionLedger.packetCount ?? UNKNOWN,
      approvalCount: executionLedger.approvalCount ?? UNKNOWN,
      blockedPacketCount: executionLedger.blockedPacketCount ?? UNKNOWN,
      appliedPacketCount: executionLedger.appliedPacketCount ?? UNKNOWN
    },
    nextSafeAction: input.nextSafeAction ?? UNKNOWN
  };
}
