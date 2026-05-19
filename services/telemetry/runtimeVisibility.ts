import type { ScheduledAction, SchedulerPlan } from "../dispatcher/autonomousScheduler";
import type { DeadLetterPacket, DeadLetterQueueState } from "../dispatcher/deadLetterQueue";
import type { WorkerHeartbeat, WorkerLeaseResult } from "../dispatcher/workerLeaseEngine";
import type { BackpressureDecision } from "../runtime/runtimeBackpressure";
import type { SupervisorAlert, SupervisorReport } from "../supervisor/runtimeSupervisor";
import type { TelemetryEvent } from "./telemetryEvent";
import { replayTelemetryEvents, type ReplayedRuntimeState } from "./telemetryReplay";

export type VisibilityFreshness = "fresh" | "stale" | "unknown";
export type VisibilitySource = "observed" | "reconstructed" | "inferred" | "fixture";

export interface VisibilityProvenance {
  runtime: VisibilitySource;
  queue: VisibilitySource;
  packets: VisibilitySource;
  failedPackets: VisibilitySource;
  workers: VisibilitySource;
  backpressure: VisibilitySource;
  telemetry: VisibilitySource;
  executionLedger: VisibilitySource;
  fixture: boolean;
}

export interface RuntimeQueueCounters {
  scheduled: number;
  dispatchable: number;
  waitingForApproval: number;
  retryable: number;
  manualReview: number;
  reclaimable: number;
  poison: number;
}

export interface RuntimeBackpressureVisibility extends BackpressureDecision {
  pressureInputs: {
    scheduledActions: number;
    expiredWorkers: number;
    poisonPackets: number;
    maxSchedulerActions: number;
    maxExpiredWorkers: number;
    maxPoisonPackets: number;
  };
}

export interface RuntimePacketVisibility {
  packetId: string;
  status: string;
  action?: ScheduledAction["action"];
  risk?: string;
  reason?: string;
  lastEventType?: string;
  lastUpdatedAt?: string;
}

export interface WorkerLeaseVisibility extends WorkerHeartbeat {
  leaseState: "active" | "stale" | "expired";
  reclaimablePacket: boolean;
  heartbeatAgeMs?: number;
  leaseExpiresInMs?: number;
}

export interface RuntimeVisibilitySnapshot {
  schema: "aios.runtime_visibility.v1";
  generatedAt: string;
  runtime: {
    runtimeId?: string;
    status: "idle" | "running" | "paused" | "degraded" | "blocked" | "unknown";
    lastTickAt?: string;
    freshness: VisibilityFreshness;
    queueSource: "runtime_context" | "scheduler_replay" | "fixture" | "unknown";
  };
  health: SupervisorReport["health"];
  queue: RuntimeQueueCounters;
  activePackets: RuntimePacketVisibility[];
  failedPackets: {
    retryable: DeadLetterPacket[];
    poison: DeadLetterPacket[];
    all: DeadLetterPacket[];
  };
  workers: WorkerLeaseVisibility[];
  backpressure: RuntimeBackpressureVisibility;
  alerts: SupervisorAlert[];
  telemetry: {
    eventCount: number;
    invalidLineCount: number;
    lastEventAt?: string;
    recentEvents: TelemetryEvent[];
    ledger: {
      path?: string;
      exists: boolean;
      sizeBytes: number;
      modifiedAt?: string;
      lineCount: number;
      validLineCount: number;
      invalidLineCount: number;
      empty: boolean;
    };
  };
  executionLedger: {
    packetCount: number;
    approvalCount: number;
    blockedPacketCount: number;
    appliedPacketCount: number;
    lastUpdatedAt?: string;
  };
  provenance: VisibilityProvenance;
  warnings: string[];
}

export interface RuntimeVisibilityInput {
  runtimeId?: string;
  runtimeStatus?: RuntimeVisibilitySnapshot["runtime"]["status"];
  lastTickAt?: string;
  queueSource?: RuntimeVisibilitySnapshot["runtime"]["queueSource"];
  supervisorReport: SupervisorReport;
  schedulerPlan: SchedulerPlan;
  workerHeartbeats: WorkerHeartbeat[];
  workerLeases: WorkerLeaseResult;
  deadLetterQueue: DeadLetterQueueState;
  backpressure: BackpressureDecision;
  backpressureThresholds?: {
    maxSchedulerActions: number;
    maxExpiredWorkers: number;
    maxPoisonPackets: number;
  };
  telemetryEvents: TelemetryEvent[];
  telemetryInvalidLineCount?: number;
  telemetryLedger?: RuntimeVisibilitySnapshot["telemetry"]["ledger"];
  provenance?: Partial<VisibilityProvenance>;
  recentEventLimit?: number;
  staleAfterMs?: number;
  now?: Date;
}

function countActions(
  actions: ScheduledAction[],
  action: ScheduledAction["action"]
): number {
  return actions.filter((item) => item.action === action).length;
}

function buildQueueCounters(
  schedulerPlan: SchedulerPlan,
  deadLetterQueue: DeadLetterQueueState
): RuntimeQueueCounters {
  return {
    scheduled: schedulerPlan.actions.length,
    dispatchable: countActions(schedulerPlan.actions, "dispatch"),
    waitingForApproval: countActions(schedulerPlan.actions, "wait_for_approval"),
    retryable: countActions(schedulerPlan.actions, "retry"),
    manualReview: countActions(schedulerPlan.actions, "manual_review"),
    reclaimable: schedulerPlan.reclaimablePackets.length,
    poison: deadLetterQueue.packets.filter((packet) => !packet.retryable).length
  };
}

function buildPacketVisibility(
  schedulerPlan: SchedulerPlan,
  replayedState: ReplayedRuntimeState
): RuntimePacketVisibility[] {
  const packets = new Map<string, RuntimePacketVisibility>();

  for (const packet of Object.values(replayedState.packets)) {
    packets.set(packet.packetId, {
      packetId: packet.packetId,
      status: packet.status,
      risk: packet.risk,
      lastEventType: packet.lastEventType,
      lastUpdatedAt: packet.lastUpdatedAt
    });
  }

  for (const action of schedulerPlan.actions) {
    const existing = packets.get(action.packetId);

    packets.set(action.packetId, {
      packetId: action.packetId,
      status: existing?.status ?? action.action,
      action: action.action,
      risk: existing?.risk,
      reason: action.reason,
      lastEventType: existing?.lastEventType,
      lastUpdatedAt: existing?.lastUpdatedAt
    });
  }

  return [...packets.values()].sort((a, b) =>
    (b.lastUpdatedAt ?? "").localeCompare(a.lastUpdatedAt ?? "")
  );
}

function buildWorkerVisibility(
  workers: WorkerHeartbeat[],
  workerLeases: WorkerLeaseResult,
  now: Date
): WorkerLeaseVisibility[] {
  return workers.map((worker) => {
    const leaseState = workerLeases.expiredWorkers.includes(worker.workerId)
      ? "expired"
      : workerLeases.staleWorkers.includes(worker.workerId)
        ? "stale"
        : "active";

    return {
      ...worker,
      leaseState,
      heartbeatAgeMs: Number.isNaN(new Date(worker.lastHeartbeatAt).getTime())
        ? undefined
        : now.getTime() - new Date(worker.lastHeartbeatAt).getTime(),
      leaseExpiresInMs: worker.leaseExpiresAt &&
        !Number.isNaN(new Date(worker.leaseExpiresAt).getTime())
        ? new Date(worker.leaseExpiresAt).getTime() - now.getTime()
        : undefined,
      reclaimablePacket: worker.packetId
        ? workerLeases.reclaimablePackets.includes(worker.packetId)
        : false
    };
  });
}

function findLedgerLastUpdatedAt(events: TelemetryEvent[]): string | undefined {
  const timestamps = events
    .map((event) => event.ts)
    .filter(Boolean)
    .sort();

  return timestamps[timestamps.length - 1];
}

function buildVisibilityAlerts(input: RuntimeVisibilityInput): SupervisorAlert[] {
  const alerts = [...input.supervisorReport.alerts];

  if (input.backpressure.throttled) {
    alerts.push({
      severity: input.backpressure.level === "blocked" ? "critical" : "warning",
      category: "backpressure",
      message: `Runtime is throttled to ${input.backpressure.allowedConcurrentPackets} concurrent packets`,
      generatedAt: input.backpressure.checkedAt
    });
  }

  return alerts;
}

function buildFailedPacketGroups(deadLetterQueue: DeadLetterQueueState): RuntimeVisibilitySnapshot["failedPackets"] {
  const retryable = deadLetterQueue.packets.filter((packet) => packet.retryable);
  const poison = deadLetterQueue.packets.filter((packet) => !packet.retryable);

  return {
    retryable,
    poison,
    all: deadLetterQueue.packets
  };
}

function buildBackpressureVisibility(
  input: RuntimeVisibilityInput
): RuntimeBackpressureVisibility {
  const thresholds = input.backpressureThresholds ?? {
    maxSchedulerActions: input.schedulerPlan.actions.length,
    maxExpiredWorkers: 2,
    maxPoisonPackets: 1
  };

  return {
    ...input.backpressure,
    pressureInputs: {
      scheduledActions: input.schedulerPlan.actions.length,
      expiredWorkers: input.workerLeases.expiredWorkers.length,
      poisonPackets: input.deadLetterQueue.packets.filter((packet) => !packet.retryable).length,
      ...thresholds
    }
  };
}

function buildFreshness(
  now: Date,
  lastEventAt: string | undefined,
  staleAfterMs: number
): VisibilityFreshness {
  if (!lastEventAt) {
    return "unknown";
  }

  const lastEventTime = new Date(lastEventAt).getTime();

  if (Number.isNaN(lastEventTime)) {
    return "unknown";
  }

  return now.getTime() - lastEventTime > staleAfterMs ? "stale" : "fresh";
}

function buildProvenance(input: RuntimeVisibilityInput): VisibilityProvenance {
  return {
    runtime: input.runtimeStatus ? "observed" : "inferred",
    queue: input.queueSource === "runtime_context" ? "observed" : "reconstructed",
    packets: "reconstructed",
    failedPackets: "observed",
    workers: "observed",
    backpressure: "inferred",
    telemetry: "observed",
    executionLedger: "reconstructed",
    fixture: false,
    ...input.provenance
  };
}

function buildWarnings(
  freshness: VisibilityFreshness,
  provenance: VisibilityProvenance,
  telemetryLedger: RuntimeVisibilitySnapshot["telemetry"]["ledger"],
  eventCount: number
): string[] {
  const warnings: string[] = [];

  if (provenance.fixture) {
    warnings.push("Fixture data is loaded; this is not live runtime truth.");
  }

  if (freshness !== "fresh") {
    warnings.push(`Runtime visibility freshness is ${freshness}.`);
  }

  if (!telemetryLedger.exists) {
    warnings.push("Telemetry ledger file is missing.");
  }

  if (telemetryLedger.empty && eventCount > 0) {
    warnings.push("Telemetry event count is present but ledger inspection reports an empty ledger.");
  }

  if (telemetryLedger.invalidLineCount > 0) {
    warnings.push(`${telemetryLedger.invalidLineCount} invalid telemetry ledger lines were detected.`);
  }

  return warnings;
}

export function buildRuntimeVisibilitySnapshot(
  input: RuntimeVisibilityInput
): RuntimeVisibilitySnapshot {
  const now = input.now ?? new Date();
  const staleAfterMs = input.staleAfterMs ?? 300000;
  const recentEventLimit = input.recentEventLimit ?? 20;
  const replayedState = replayTelemetryEvents(input.telemetryEvents);
  const lastEventAt = findLedgerLastUpdatedAt(input.telemetryEvents);
  const freshness = buildFreshness(now, lastEventAt, staleAfterMs);
  const provenance = buildProvenance(input);
  const telemetryLedger = input.telemetryLedger ?? {
    exists: input.telemetryEvents.length > 0,
    sizeBytes: 0,
    lineCount: input.telemetryEvents.length + (input.telemetryInvalidLineCount ?? 0),
    validLineCount: input.telemetryEvents.length,
    invalidLineCount: input.telemetryInvalidLineCount ?? replayedState.invalidLineCount,
    empty: input.telemetryEvents.length === 0
  };

  return {
    schema: "aios.runtime_visibility.v1",
    generatedAt: now.toISOString(),
    runtime: {
      runtimeId: input.runtimeId,
      status: input.runtimeStatus ?? "unknown",
      lastTickAt: input.lastTickAt,
      freshness,
      queueSource: input.queueSource ?? "scheduler_replay"
    },
    health: input.supervisorReport.health,
    queue: buildQueueCounters(input.schedulerPlan, input.deadLetterQueue),
    activePackets: buildPacketVisibility(input.schedulerPlan, replayedState),
    failedPackets: buildFailedPacketGroups(input.deadLetterQueue),
    workers: buildWorkerVisibility(input.workerHeartbeats, input.workerLeases, now),
    backpressure: buildBackpressureVisibility(input),
    alerts: buildVisibilityAlerts(input),
    telemetry: {
      eventCount: input.telemetryEvents.length,
      invalidLineCount: input.telemetryInvalidLineCount ?? replayedState.invalidLineCount,
      lastEventAt,
      recentEvents: input.telemetryEvents.slice(-recentEventLimit).reverse(),
      ledger: telemetryLedger
    },
    executionLedger: {
      packetCount: Object.keys(replayedState.packets).length,
      approvalCount: Object.keys(replayedState.approvals).length,
      blockedPacketCount: replayedState.blockedPackets.length,
      appliedPacketCount: replayedState.appliedPackets.length,
      lastUpdatedAt: lastEventAt
    },
    provenance,
    warnings: buildWarnings(
      freshness,
      provenance,
      telemetryLedger,
      input.telemetryEvents.length
    )
  };
}
