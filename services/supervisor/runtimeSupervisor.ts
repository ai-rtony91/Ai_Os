import type { SchedulerPlan } from "../dispatcher/autonomousScheduler";
import type { WorkerLeaseResult } from "../dispatcher/workerLeaseEngine";
import type { DeadLetterQueueState } from "../dispatcher/deadLetterQueue";

export interface RuntimeHealthSnapshot {
  schedulerActions: number;
  staleWorkers: number;
  expiredWorkers: number;
  reclaimablePackets: number;
  retryablePackets: number;
  poisonPackets: number;
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

export function generateRuntimeHealth(
  scheduler: SchedulerPlan,
  workerLeases: WorkerLeaseResult,
  deadLetters: DeadLetterQueueState
): RuntimeHealthSnapshot {
  const retryablePackets = deadLetters.packets.filter(
    (packet) => packet.retryable
  ).length;

  const poisonPackets = deadLetters.packets.filter(
    (packet) => !packet.retryable
  ).length;

  const healthy =
    workerLeases.expiredWorkers.length === 0 && poisonPackets === 0;

  return {
    schedulerActions: scheduler.actions.length,
    staleWorkers: workerLeases.staleWorkers.length,
    expiredWorkers: workerLeases.expiredWorkers.length,
    reclaimablePackets: workerLeases.reclaimablePackets.length,
    retryablePackets,
    poisonPackets,
    healthy,
    generatedAt: new Date().toISOString()
  };
}

export function generateSupervisorReport(
  scheduler: SchedulerPlan,
  workerLeases: WorkerLeaseResult,
  deadLetters: DeadLetterQueueState
): SupervisorReport {
  const health = generateRuntimeHealth(
    scheduler,
    workerLeases,
    deadLetters
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
