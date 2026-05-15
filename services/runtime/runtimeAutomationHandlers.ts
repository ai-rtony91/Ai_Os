import { runtimeEventBus, type RuntimeEvent } from "./eventBus";
import { generateRemediationPlan } from "./autonomousRemediation";
import type { SupervisorReport } from "../supervisor/runtimeSupervisor";
import type { BackpressureDecision } from "./runtimeBackpressure";

export function registerRuntimeAutomationHandlers(): void {
  runtimeEventBus.subscribe("policy_decision", (event: RuntimeEvent<any>) => {
    console.log(`[AUTOMATION] Policy decision for packet ${event.payload.packetId || "N/A"}: allowed=${event.payload.status}, reason=${event.payload.reason}`);
    if (event.payload.status === "denied" || event.payload.requiresApproval) {
      const dummySupervisor: SupervisorReport = { health: { healthy: true, poisonPackets: 0, reclaimablePackets: 0 } };
      const dummyBackpressure: BackpressureDecision = { level: "soft", reason: "", maxSchedulerActions: 5, maxExpiredWorkers: 2, maxPoisonPackets: 1 };
      const plan = generateRemediationPlan(dummyBackpressure, dummySupervisor);
      console.log(`[AUTOMATION] Generated remediation plan for policy denial:`, plan);
    }
  });

  runtimeEventBus.subscribe("runtime_tick_completed", (event: RuntimeEvent<{ runtimeId: string; tickAt: string; status: string }>) => {
    console.log(`[AUTOMATION] Tick completed for runtime ${event.payload.runtimeId} at ${event.payload.tickAt} with status ${event.payload.status}`);
    if (event.payload.status === "degraded" || event.payload.status === "blocked") {
      const dummySupervisor: SupervisorReport = { health: { healthy: true, poisonPackets: 0, reclaimablePackets: 0 } };
      const dummyBackpressure: BackpressureDecision = { level: "soft", reason: "", maxSchedulerActions: 5, maxExpiredWorkers: 2, maxPoisonPackets: 1 };
      const plan = generateRemediationPlan(dummyBackpressure, dummySupervisor);
      console.log(`[AUTOMATION] Generated remediation plan for tick status:`, plan);
    }
  });
}