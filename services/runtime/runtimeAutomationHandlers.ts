import { runtimeEventBus, type RuntimeEvent } from "./eventBus";
import { generateRemediationPlan } from "./autonomousRemediation";
import type { SupervisorReport } from "../supervisor/runtimeSupervisor";
import type { BackpressureDecision } from "./runtimeBackpressure";

function createEmptySupervisorReport(): SupervisorReport {
  const generatedAt = new Date().toISOString();

  return {
    health: {
      schedulerActions: 0,
      staleWorkers: 0,
      expiredWorkers: 0,
      reclaimablePackets: 0,
      retryablePackets: 0,
      poisonPackets: 0,
      healthy: true,
      generatedAt
    },
    alerts: []
  };
}

export function registerRuntimeAutomationHandlers(): void {
  runtimeEventBus.subscribe("policy_decision", (event: RuntimeEvent<any>) => {
    console.log(`[AUTOMATION] Policy decision for packet ${event.payload.packetId || "N/A"}: allowed=${event.payload.status}, reason=${event.payload.reason}`);
    if (event.payload.status === "denied" || event.payload.requiresApproval) {
      const dummySupervisor = createEmptySupervisorReport();
      const dummyBackpressure: BackpressureDecision = {
        throttled: true,
        level: "soft",
        reason: "",
        allowedConcurrentPackets: 1,
        checkedAt: new Date().toISOString()
      };
      const plan = generateRemediationPlan(dummyBackpressure, dummySupervisor);
      console.log(`[AUTOMATION] Generated remediation plan for policy denial:`, plan);
    }
  });

  runtimeEventBus.subscribe("runtime_tick_completed", (event: RuntimeEvent<{ runtimeId: string; tickAt: string; status: string }>) => {
    console.log(`[AUTOMATION] Tick completed for runtime ${event.payload.runtimeId} at ${event.payload.tickAt} with status ${event.payload.status}`);
    if (event.payload.status === "degraded" || event.payload.status === "blocked") {
      const dummySupervisor = createEmptySupervisorReport();
      const dummyBackpressure: BackpressureDecision = {
        throttled: true,
        level: "soft",
        reason: "",
        allowedConcurrentPackets: 1,
        checkedAt: new Date().toISOString()
      };
      const plan = generateRemediationPlan(dummyBackpressure, dummySupervisor);
      console.log(`[AUTOMATION] Generated remediation plan for tick status:`, plan);
    }
  });
}
