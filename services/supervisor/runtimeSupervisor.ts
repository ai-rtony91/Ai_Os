import type { SchedulerPlan } from "../dispatcher/autonomousScheduler";
import type { WorkerLeaseResult } from "../dispatcher/workerLeaseEngine";
import type { WorkerHeartbeat } from "../dispatcher/workerLeaseEngine";
import type { DeadLetterQueueState } from "../dispatcher/deadLetterQueue";
import type { RuntimeContext } from "../runtime/runtimeContext";
import type { TelemetryEvent } from "../telemetry/telemetryEvent";
import {
  buildRuntimeVisibilitySnapshot,
  type RuntimeVisibilitySnapshot
} from "../telemetry/runtimeVisibility";

export interface RuntimeHealthSnapshot {
  schedulerActions: number;
  staleWorkers: number;
  staleAssignedPackets?: number;
  expiredWorkers: number;
  reclaimablePackets: number;
  retryablePackets: number;
  poisonPackets: number;
  replayInvalidLines?: number;
  invalidPacketStatuses?: number;
  healthy: boolean;
  generatedAt: string;
}

export interface SupervisorAlert {
  severity: "info" | "warning" | "critical";
  category:
    | "scheduler"
    | "worker"
    | "recovery"
    | "policy"
    | "dead_letter_queue"
    | "backpressure";
  message: string;
  generatedAt: string;
}

export interface SupervisorReport {
  health: RuntimeHealthSnapshot;
  alerts: SupervisorAlert[];
}

export interface RuntimeSupervisorDiagnostics {
  replayInvalidLines?: number;
  invalidPacketStatuses?: number;
}

export function generateRuntimeHealth(
  scheduler: SchedulerPlan,
  workerLeases: WorkerLeaseResult,
  deadLetters: DeadLetterQueueState,
  diagnostics: RuntimeSupervisorDiagnostics = {}
): RuntimeHealthSnapshot {
  const retryablePackets = deadLetters.packets.filter(
    (packet) => packet.retryable
  ).length;

  const poisonPackets = deadLetters.packets.filter(
    (packet) => !packet.retryable
  ).length;

  const replayInvalidLines = diagnostics.replayInvalidLines ?? 0;
  const invalidPacketStatuses = diagnostics.invalidPacketStatuses ?? 0;

  const healthy =
    workerLeases.expiredWorkers.length === 0 &&
    poisonPackets === 0 &&
    replayInvalidLines === 0 &&
    invalidPacketStatuses === 0;

  return {
    schedulerActions: scheduler.actions.length,
    staleWorkers: workerLeases.staleWorkers.length,
    staleAssignedPackets: (workerLeases.staleAssignedPackets ?? []).length,
    expiredWorkers: workerLeases.expiredWorkers.length,
    reclaimablePackets: workerLeases.reclaimablePackets.length,
    retryablePackets,
    poisonPackets,
    replayInvalidLines,
    invalidPacketStatuses,
    healthy,
    generatedAt: new Date().toISOString()
  };
}

export function generateSupervisorReport(
  scheduler: SchedulerPlan,
  workerLeases: WorkerLeaseResult,
  deadLetters: DeadLetterQueueState,
  diagnostics: RuntimeSupervisorDiagnostics = {}
): SupervisorReport {
  const health = generateRuntimeHealth(
    scheduler,
    workerLeases,
    deadLetters,
    diagnostics
  );

  const alerts: SupervisorAlert[] = [];

  if (health.expiredWorkers > 0) {
    alerts.push({
      severity: "warning",
      category: "worker",
      message: `${health.expiredWorkers} workers have expired leases`,
      generatedAt: new Date().toISOString()
    });
  }

  if ((health.staleAssignedPackets ?? 0) > 0) {
    alerts.push({
      severity: "warning",
      category: "worker",
      message: `${health.staleAssignedPackets ?? 0} packets are assigned to stale workers`,
      generatedAt: new Date().toISOString()
    });
  }

  if ((health.replayInvalidLines ?? 0) > 0) {
    alerts.push({
      severity: "warning",
      category: "recovery",
      message: `${health.replayInvalidLines ?? 0} telemetry ledger lines could not be replayed`,
      generatedAt: new Date().toISOString()
    });
  }

  if ((health.invalidPacketStatuses ?? 0) > 0) {
    alerts.push({
      severity: "warning",
      category: "recovery",
      message: `${health.invalidPacketStatuses ?? 0} replayed packets have invalid lifecycle status`,
      generatedAt: new Date().toISOString()
    });
  }

  if (health.poisonPackets > 0) {
    alerts.push({
      severity: "critical",
      category: "dead_letter_queue",
      message: `${health.poisonPackets} poison packets require manual review`,
      generatedAt: new Date().toISOString()
    });
  }

  if (health.schedulerActions === 0) {
    alerts.push({
      severity: "info",
      category: "scheduler",
      message: "Scheduler generated no active actions",
      generatedAt: new Date().toISOString()
    });
  }

  return {
    health,
    alerts
  };
}

export function buildSupervisorVisibilityReport(
  context: RuntimeContext,
  workerHeartbeats: WorkerHeartbeat[],
  telemetryEvents: TelemetryEvent[],
  telemetryInvalidLineCount = 0,
  telemetryLedger?: RuntimeVisibilitySnapshot["telemetry"]["ledger"]
): RuntimeVisibilitySnapshot | null {
  if (
    !context.supervisorReport ||
    !context.schedulerPlan ||
    !context.workerLeases ||
    !context.deadLetterQueue ||
    !context.backpressure
  ) {
    return null;
  }

  return buildRuntimeVisibilitySnapshot({
    runtimeId: context.runtimeId,
    runtimeStatus: context.status,
    lastTickAt: context.lastTickAt,
    queueSource: "runtime_context",
    supervisorReport: context.supervisorReport,
    schedulerPlan: context.schedulerPlan,
    workerHeartbeats,
    workerLeases: context.workerLeases,
    deadLetterQueue: context.deadLetterQueue,
    backpressure: context.backpressure,
    telemetryEvents,
    telemetryInvalidLineCount,
    telemetryLedger
  });
}
