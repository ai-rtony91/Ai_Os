import { runtimeEventBus, type RuntimeEvent } from "./eventBus";

export interface AutomationDispatchPacket {
  packetId: string;
  type: "remediation" | "policy";
  runtimeId: string;
  createdAt: string;
  priority: "low" | "medium" | "high";
  action: string;
  payload: Record<string, unknown>;
}

const automationPacketQueue: AutomationDispatchPacket[] = [];

function createPacket(
  type: AutomationDispatchPacket["type"],
  runtimeId: string,
  priority: AutomationDispatchPacket["priority"],
  action: string,
  payload: Record<string, unknown>
): AutomationDispatchPacket {
  return {
    packetId: `packet_${Date.now()}`,
    type,
    runtimeId,
    createdAt: new Date().toISOString(),
    priority,
    action,
    payload
  };
}

export function getAutomationPacketQueue(): AutomationDispatchPacket[] {
  return [...automationPacketQueue];
}

export function registerRuntimeAutomationDispatcher(): void {
  runtimeEventBus.subscribe(
    "runtime_tick_completed",
    (
      event: RuntimeEvent<{
        runtimeId: string;
        status: string;
      }>
    ) => {
      if (
        event.payload.status === "degraded" ||
        event.payload.status === "blocked"
      ) {
        const packet = createPacket(
          "remediation",
          event.payload.runtimeId,
          "high",
          "runtime_remediation",
          {
            status: event.payload.status
          }
        );

        automationPacketQueue.push(packet);

        console.log(
          `[AUTOMATION DISPATCH] queued remediation packet ${packet.packetId}`
        );
      }
    }
  );

  runtimeEventBus.subscribe(
    "policy_decision",
    (event: RuntimeEvent<any>) => {
      if (
        event.payload.status === "denied" ||
        event.payload.requiresApproval
      ) {
        const packet = createPacket(
          "policy",
          event.payload.runtimeId ?? "unknown",
          "medium",
          "policy_review",
          {
            reason: event.payload.reason
          }
        );

        automationPacketQueue.push(packet);

        console.log(
          `[AUTOMATION DISPATCH] queued policy packet ${packet.packetId}`
        );
      }
    }
  );
}