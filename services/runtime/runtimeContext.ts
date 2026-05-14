import type { SchedulerPlan } from "../dispatcher/autonomousScheduler";
import type { DeadLetterQueueState } from "../dispatcher/deadLetterQueue";
import type { ResumePlan } from "../dispatcher/packetResumeEngine";
import type { RebuiltDispatcherState } from "../dispatcher/runtimeStateRebuilder";
import type { WorkerLeaseResult } from "../dispatcher/workerLeaseEngine";
import type { SupervisorReport } from "../supervisor/runtimeSupervisor";
import type { BackpressureDecision } from "./runtimeBackpressure";

export interface RuntimeContext {
  runtimeId: string;
  status: "idle" | "running" | "paused" | "degraded" | "blocked";
  dispatcherState?: RebuiltDispatcherState;
  resumePlan?: ResumePlan;
  schedulerPlan?: SchedulerPlan;
  workerLeases?: WorkerLeaseResult;
  deadLetterQueue?: DeadLetterQueueState;
  supervisorReport?: SupervisorReport;
  backpressure?: BackpressureDecision;
  lastTickAt?: string;
  createdAt: string;
  updatedAt: string;
}

export function createRuntimeContext(runtimeId: string): RuntimeContext {
  const now = new Date().toISOString();

  return {
    runtimeId,
    status: "idle",
    createdAt: now,
    updatedAt: now
  };
}

export function updateRuntimeContext(
  context: RuntimeContext,
  patch: Partial<RuntimeContext>
): RuntimeContext {
  return {
    ...context,
    ...patch,
    updatedAt: new Date().toISOString()
  };
}
