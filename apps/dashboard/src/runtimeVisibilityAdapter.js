const UNKNOWN = "UNKNOWN";

export const RUNTIME_VISIBILITY_SOURCE_LABELS = Object.freeze({
  MOCK_DATA: "MOCK_DATA",
  READ_ONLY_API: "READ_ONLY_API",
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

export function mapRuntimeVisibilityDisplayModel(data, options = {}) {
  const sourceLabel = options.sourceLabel ?? RUNTIME_VISIBILITY_SOURCE_LABELS.UNKNOWN;
  const input = asObject(data);
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
