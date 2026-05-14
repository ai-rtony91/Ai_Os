import { replayTelemetryLedgerFile } from "../telemetry/telemetryReplay";
import { rebuildDispatcherState } from "../dispatcher/runtimeStateRebuilder";
import { generateResumePlan } from "../dispatcher/packetResumeEngine";
import { generateSchedulerPlan } from "../dispatcher/autonomousScheduler";
import { generateSupervisorReport } from "../supervisor/runtimeSupervisor";
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

  return updateRuntimeContext(input.context, {
    status: supervisorReport.health.healthy ? "running" : "degraded",
    dispatcherState,
    resumePlan,
    schedulerPlan,
    workerLeases: input.workerLeases,
    deadLetterQueue: input.deadLetterQueue,
    supervisorReport,
    lastTickAt: new Date().toISOString()
  });
}
