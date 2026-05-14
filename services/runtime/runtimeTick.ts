import { replayTelemetryLedgerFile } from "../telemetry/telemetryReplay";
import { rebuildDispatcherState } from "../dispatcher/runtimeStateRebuilder";
import { generateResumePlan } from "../dispatcher/packetResumeEngine";
import { generateSchedulerPlan } from "../dispatcher/autonomousScheduler";
import { generateSupervisorReport } from "../supervisor/runtimeSupervisor";
import { evaluateRuntimeBackpressure } from "./runtimeBackpressure";
import { updateRuntimeContext, type RuntimeContext } from "./runtimeContext";
import type { DeadLetterQueueState } from "../dispatcher/deadLetterQueue";
import type { WorkerLeaseResult } from "../dispatcher/workerLeaseEngine";

export interface RuntimeTickInput {
  context: RuntimeContext;
  deadLetterQueue: DeadLetterQueueState;
  workerLeases: WorkerLeaseResult;
  maxConcurrentPackets?: number;
}

export function runRuntimeTick(
  input: RuntimeTickInput
): RuntimeContext {
  const replayed = replayTelemetryLedgerFile();
  const dispatcherState = rebuildDispatcherState(replayed);
  const resumePlan = generateResumePlan(dispatcherState);

  const schedulerPlan = generateSchedulerPlan({
    resumePlan,
    deadLetterQueue: input.deadLetterQueue,
    workerLeases: input.workerLeases,
    maxConcurrentPackets: input.maxConcurrentPackets ?? 5
  });

  const supervisorReport = generateSupervisorReport(
    schedulerPlan,
    input.workerLeases,
    input.deadLetterQueue
  );

  const backpressure = evaluateRuntimeBackpressure({
    schedulerPlan,
    workerLeases: input.workerLeases,
    deadLetterQueue: input.deadLetterQueue,
    maxSchedulerActions: input.maxConcurrentPackets ?? 5,
    maxExpiredWorkers: 2,
    maxPoisonPackets: 1
  });

  const runtimeStatus =
    backpressure.level === "blocked"
      ? "blocked"
      : supervisorReport.health.healthy
        ? "running"
        : "degraded";

  return updateRuntimeContext(input.context, {
    status: runtimeStatus,
    dispatcherState,
    resumePlan,
    schedulerPlan,
    workerLeases: input.workerLeases,
    deadLetterQueue: input.deadLetterQueue,
    supervisorReport,
    backpressure,
    lastTickAt: new Date().toISOString()
  });
}
