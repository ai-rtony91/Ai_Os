import { replayTelemetryLedgerFile } from "../telemetry/telemetryReplay";
import { rebuildDispatcherState } from "../dispatcher/runtimeStateRebuilder";
import { generateResumePlan } from "../dispatcher/packetResumeEngine";
import { generateSchedulerPlan } from "../dispatcher/autonomousScheduler";
import { generateSupervisorReport } from "../supervisor/runtimeSupervisor";
import { evaluateRuntimeBackpressure } from "./runtimeBackpressure";
import { generateRemediationPlan } from "./autonomousRemediation";
import { updateRuntimeContext, type RuntimeContext } from "./runtimeContext";
import { runtimeEventBus } from "./eventBus";
import type { DeadLetterQueueState } from "../dispatcher/deadLetterQueue";
import type { WorkerLeaseResult } from "../dispatcher/workerLeaseEngine";

export interface RuntimeTickInput {
  context: RuntimeContext;
  deadLetterQueue: DeadLetterQueueState;
  workerLeases: WorkerLeaseResult;
  maxConcurrentPackets?: number;
}

export function runRuntimeTick(input: RuntimeTickInput): RuntimeContext {
  const tickAt = new Date().toISOString();

  runtimeEventBus.emit("runtime_tick_started", {
    runtimeId: input.context.runtimeId,
    tickAt
  });

  const replayed = replayTelemetryLedgerFile();
  const dispatcherState = rebuildDispatcherState(replayed);
  const resumePlan = generateResumePlan(dispatcherState);
  const maxConcurrentPackets = input.maxConcurrentPackets ?? 5;
  const runtimeSnapshot = {
    dispatcherState,
    resumePlan,
    workerLeases: input.workerLeases,
    deadLetterQueue: input.deadLetterQueue,
    replayDiagnostics: {
      replayInvalidLines: dispatcherState.invalidLineCount,
      invalidPacketStatuses: dispatcherState.invalidPacketStatuses.length
    }
  };

  const schedulerPlan = generateSchedulerPlan({
    resumePlan: runtimeSnapshot.resumePlan,
    deadLetterQueue: runtimeSnapshot.deadLetterQueue,
    workerLeases: runtimeSnapshot.workerLeases,
    maxConcurrentPackets
  });

  const supervisorReport = generateSupervisorReport(
    schedulerPlan,
    runtimeSnapshot.workerLeases,
    runtimeSnapshot.deadLetterQueue,
    runtimeSnapshot.replayDiagnostics
  );

  const backpressure = evaluateRuntimeBackpressure({
    schedulerPlan,
    workerLeases: runtimeSnapshot.workerLeases,
    deadLetterQueue: runtimeSnapshot.deadLetterQueue,
    maxSchedulerActions: maxConcurrentPackets,
    maxExpiredWorkers: 2,
    maxPoisonPackets: 1
  });

  const remediationPlan = generateRemediationPlan(
    backpressure,
    supervisorReport
  );

  const runtimeStatus =
    backpressure.level === "blocked"
      ? "blocked"
      : supervisorReport.health.healthy
        ? "running"
        : "degraded";

  const updatedContext = updateRuntimeContext(input.context, {
    status: runtimeStatus,
    dispatcherState: runtimeSnapshot.dispatcherState,
    resumePlan: runtimeSnapshot.resumePlan,
    schedulerPlan,
    workerLeases: runtimeSnapshot.workerLeases,
    deadLetterQueue: runtimeSnapshot.deadLetterQueue,
    supervisorReport,
    backpressure,
    remediationPlan,
    lastTickAt: tickAt
  });

  runtimeEventBus.emit("runtime_tick_completed", {
    runtimeId: input.context.runtimeId,
    tickAt,
    status: runtimeStatus
  });

  return updatedContext;
}
