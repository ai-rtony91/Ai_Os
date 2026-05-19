import type { ScheduledAction, SchedulerPlan } from "../dispatcher/autonomousScheduler";
import type { DeadLetterPacket, DeadLetterQueueState } from "../dispatcher/deadLetterQueue";
import type { WorkerHeartbeat, WorkerLeaseResult } from "../dispatcher/workerLeaseEngine";
import type { BackpressureDecision } from "../runtime/runtimeBackpressure";
import type { SupervisorAlert, SupervisorReport } from "../supervisor/runtimeSupervisor";
import type { TelemetryEvent } from "./telemetryEvent";
import { replayTelemetryEvents, type ReplayedRuntimeState } from "./telemetryReplay";

export interface RuntimeQueueCounters {
  scheduled: number;
  dispatchable: number;
  waitingForApproval: number;
  retryable: number;
  manualReview: number;
  reclaimable: number;
  poison: number;
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
}

export interface RuntimeVisibilitySnapshot {
  schema: "aios.runtime_visibility.v1";
  generatedAt: string;
  health: SupervisorReport["health"];
  queue: RuntimeQueueCounters;
  activePackets: RuntimePacketVisibility[];
  failedPackets: DeadLetterPacket[];
  workers: WorkerLeaseVisibility[];
  backpressure: BackpressureDecision;
  alerts: SupervisorAlert[];
  telemetry: {
    eventCount: number;
    invalidLineCount: number;
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
  supervisorReport: SupervisorReport;
  schedulerPlan: SchedulerPlan;
  workerHeartbeats: WorkerHeartbeat[];
  workerLeases: WorkerLeaseResult;
  deadLetterQueue: DeadLetterQueueState;
  backpressure: BackpressureDecision;
  telemetryEvents: TelemetryEvent[];
  telemetryInvalidLineCount?: number;
  recentEventLimit?: number;
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
  workerLeases: WorkerLeaseResult
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

export function buildRuntimeVisibilitySnapshot(
  input: RuntimeVisibilityInput
): RuntimeVisibilitySnapshot {
  const recentEventLimit = input.recentEventLimit ?? 20;
  const replayedState = replayTelemetryEvents(input.telemetryEvents);

  return {
    schema: "aios.runtime_visibility.v1",
    generatedAt: new Date().toISOString(),
    health: input.supervisorReport.health,
    queue: buildQueueCounters(input.schedulerPlan, input.deadLetterQueue),
    activePackets: buildPacketVisibility(input.schedulerPlan, replayedState),
    failedPackets: input.deadLetterQueue.packets,
    workers: buildWorkerVisibility(input.workerHeartbeats, input.workerLeases),
    backpressure: input.backpressure,
    alerts: buildVisibilityAlerts(input),
    telemetry: {
      eventCount: input.telemetryEvents.length,
      invalidLineCount: input.telemetryInvalidLineCount ?? replayedState.invalidLineCount,
      recentEvents: input.telemetryEvents.slice(-recentEventLimit).reverse()
    },
    executionLedger: {
      packetCount: Object.keys(replayedState.packets).length,
      approvalCount: Object.keys(replayedState.approvals).length,
      blockedPacketCount: replayedState.blockedPackets.length,
      appliedPacketCount: replayedState.appliedPackets.length,
      lastUpdatedAt: findLedgerLastUpdatedAt(input.telemetryEvents)
    }
  };
}
