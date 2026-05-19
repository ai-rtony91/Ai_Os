import type { ScheduledAction, SchedulerPlan } from "../dispatcher/autonomousScheduler";
import type { DeadLetterPacket, DeadLetterQueueState } from "../dispatcher/deadLetterQueue";
import type { PacketQueueSnapshot } from "../dispatcher/packetQueue";
import type { WorkerHeartbeat, WorkerLeaseResult } from "../dispatcher/workerLeaseEngine";
import type { BackpressureDecision } from "../runtime/runtimeBackpressure";
import type { SupervisorAlert, SupervisorReport } from "../supervisor/runtimeSupervisor";
import type { TelemetryEvent } from "./telemetryEvent";
import { replayTelemetryEvents, type ReplayedRuntimeState } from "./telemetryReplay";

export type VisibilityFreshness = "fresh" | "stale" | "unknown";

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
    queueSource: "packet_queue" | "runtime_context" | "scheduler_replay" | "fixture" | "unknown";
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
  };
  executionLedger: {
    packetCount: number;
    approvalCount: number;
    blockedPacketCount: number;
    appliedPacketCount: number;
    lastUpdatedAt?: string;
  };
}

export interface RuntimeVisibilityInput {
  runtimeId?: string;
  runtimeStatus?: RuntimeVisibilitySnapshot["runtime"]["status"];
  lastTickAt?: string;
  queueSource?: RuntimeVisibilitySnapshot["runtime"]["queueSource"];
  supervisorReport: SupervisorReport;
  schedulerPlan: SchedulerPlan;
  packetQueueSnapshot?: PacketQueueSnapshot;
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
  deadLetterQueue: DeadLetterQueueState,
  packetQueueSnapshot?: PacketQueueSnapshot
): RuntimeQueueCounters {
  if (packetQueueSnapshot) {
    return {
      scheduled: packetQueueSnapshot.counters.scheduled,
      dispatchable: packetQueueSnapshot.counters.claimable,
      waitingForApproval: packetQueueSnapshot.counters.waitingForApproval,
      retryable: packetQueueSnapshot.counters.retrying + packetQueueSnapshot.counters.failed,
      manualReview: packetQueueSnapshot.counters.manualReview + packetQueueSnapshot.counters.deadLetter,
      reclaimable: schedulerPlan.reclaimablePackets.length,
      poison: deadLetterQueue.packets.filter((packet) => !packet.retryable).length
    };
  }

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
  replayedState: ReplayedRuntimeState,
  packetQueueSnapshot?: PacketQueueSnapshot
): RuntimePacketVisibility[] {
  const packets = new Map<string, RuntimePacketVisibility>();

  if (packetQueueSnapshot) {
    for (const record of packetQueueSnapshot.records) {
      const packet = record.packet as { risk?: string; priority?: string };

      packets.set(record.packetId, {
        packetId: record.packetId,
        status: record.status,
        risk: String(packet.risk ?? packet.priority ?? "UNKNOWN"),
        reason: record.lastReason,
        lastUpdatedAt: record.updatedAt
      });
    }
  }

  for (const packet of Object.values(replayedState.packets)) {
    if (packets.has(packet.packetId)) {
      continue;
    }

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

export function buildRuntimeVisibilitySnapshot(
  input: RuntimeVisibilityInput
): RuntimeVisibilitySnapshot {
  const now = input.now ?? new Date();
  const staleAfterMs = input.staleAfterMs ?? 300000;
  const recentEventLimit = input.recentEventLimit ?? 20;
  const replayedState = replayTelemetryEvents(input.telemetryEvents);
  const lastEventAt = findLedgerLastUpdatedAt(input.telemetryEvents);

  return {
    schema: "aios.runtime_visibility.v1",
    generatedAt: now.toISOString(),
    runtime: {
      runtimeId: input.runtimeId,
      status: input.runtimeStatus ?? "unknown",
      lastTickAt: input.lastTickAt,
      freshness: buildFreshness(now, lastEventAt, staleAfterMs),
      queueSource: input.packetQueueSnapshot
        ? "packet_queue"
        : input.queueSource ?? "scheduler_replay"
    },
    health: input.supervisorReport.health,
    queue: buildQueueCounters(
      input.schedulerPlan,
      input.deadLetterQueue,
      input.packetQueueSnapshot
    ),
    activePackets: buildPacketVisibility(
      input.schedulerPlan,
      replayedState,
      input.packetQueueSnapshot
    ),
    failedPackets: buildFailedPacketGroups(input.deadLetterQueue),
    workers: buildWorkerVisibility(input.workerHeartbeats, input.workerLeases, now),
    backpressure: buildBackpressureVisibility(input),
    alerts: buildVisibilityAlerts(input),
    telemetry: {
      eventCount: input.telemetryEvents.length,
      invalidLineCount: input.telemetryInvalidLineCount ?? replayedState.invalidLineCount,
      lastEventAt,
      recentEvents: input.telemetryEvents.slice(-recentEventLimit).reverse()
    },
    executionLedger: {
      packetCount: Object.keys(replayedState.packets).length,
      approvalCount: Object.keys(replayedState.approvals).length,
      blockedPacketCount: replayedState.blockedPackets.length,
      appliedPacketCount: replayedState.appliedPackets.length,
      lastUpdatedAt: lastEventAt
    }
  };
}
