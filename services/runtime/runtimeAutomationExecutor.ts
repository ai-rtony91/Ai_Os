import {
  getAutomationPacketQueue,
  type AutomationDispatchPacket
} from "./runtimeAutomationDispatcher";

import { writeTelemetryEvent } from "../telemetry/telemetryWriter";

export interface AutomationExecutionResult {
  packetId: string;
  success: boolean;
  executedAt: string;
  message: string;
}

const executionLedger: AutomationExecutionResult[] = [];

function executePacket(
  packet: AutomationDispatchPacket
): AutomationExecutionResult {
  console.log(
    `[AUTOMATION EXECUTOR] executing ${packet.packetId} (${packet.action})`
  );

  const result: AutomationExecutionResult = {
    packetId: packet.packetId,
    success: true,
    executedAt: new Date().toISOString(),
    message: `Executed action ${packet.action}`
  };

  writeTelemetryEvent(
    "packet_applied",
    "runtimeAutomationExecutor",
    `Executed automation packet ${packet.packetId}`,
    {
      packetId: packet.packetId,
      status: "executed",
      metadata: {
        action: packet.action,
        priority: packet.priority,
        runtimeId: packet.runtimeId
      }
    }
  );

  return result;
}

export function processAutomationQueue(): void {
  const queue = getAutomationPacketQueue();

  while (queue.length > 0) {
    const packet = queue.shift();

    if (!packet) {
      continue;
    }

    const result = executePacket(packet);
    executionLedger.push(result);

    console.log(`[AUTOMATION EXECUTOR] completed ${packet.packetId}`);
  }
}

export function getExecutionLedger(): AutomationExecutionResult[] {
  return [...executionLedger];
}
