import type { SchedulerPlan } from "../dispatcher/autonomousScheduler";
import type { DeadLetterQueueState } from "../dispatcher/deadLetterQueue";
import type { WorkerLeaseResult } from "../dispatcher/workerLeaseEngine";

export interface BackpressureInput {
  schedulerPlan: SchedulerPlan;
  workerLeases: WorkerLeaseResult;
  deadLetterQueue: DeadLetterQueueState;
  maxSchedulerActions: number;
  maxExpiredWorkers: number;
  maxPoisonPackets: number;
}

export interface BackpressureDecision {
  throttled: boolean;
  level: "none" | "soft" | "hard" | "blocked";
  reason: string;
  allowedConcurrentPackets: number;
  checkedAt: string;
}

export function evaluateRuntimeBackpressure(
  input: BackpressureInput
): BackpressureDecision {
  const schedulerPressure = input.schedulerPlan.actions.length;
  const expiredWorkers = input.workerLeases.expiredWorkers.length;
  const poisonPackets = input.deadLetterQueue.packets.filter(
    (packet) => !packet.retryable
  ).length;

  if (poisonPackets > input.maxPoisonPackets) {
    return {
      throttled: true,
      level: "blocked",
      reason: "Poison packet pressure exceeds safe threshold",
      allowedConcurrentPackets: 0,
      checkedAt: new Date().toISOString()
    };
  }

  if (expiredWorkers > input.maxExpiredWorkers) {
    return {
      throttled: true,
      level: "hard",
      reason: "Expired worker pressure exceeds safe threshold",
      allowedConcurrentPackets: 1,
      checkedAt: new Date().toISOString()
    };
  }

  if (schedulerPressure > input.maxSchedulerActions) {
    return {
      throttled: true,
      level: "soft",
      reason: "Scheduler action pressure exceeds preferred threshold",
      allowedConcurrentPackets: Math.max(1, Math.floor(input.maxSchedulerActions / 2)),
      checkedAt: new Date().toISOString()
    };
  }

  return {
    throttled: false,
    level: "none",
    reason: "Runtime pressure is within limits",
    allowedConcurrentPackets: input.maxSchedulerActions,
    checkedAt: new Date().toISOString()
  };
}
