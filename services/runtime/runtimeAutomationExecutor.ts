import {
  claimAutomationQueue,
  completeAutomationPacket,
  releaseAutomationQueue,
  type AutomationDispatchPacket,
  type SafeExecutionState
} from "./runtimeAutomationDispatcher";

import {
  executionAllowed,
  type Capability
} from "../policy/policyEngine";
import { getApproval } from "../approvals/approvalInbox";
import { isApprovalGranted } from "../approvals/approvalDecision";
import { writeTelemetryEvent } from "../telemetry/telemetryWriter";

export interface AutomationExecutionResult {
  packetId: string;
  success: boolean;
  executedAt: string;
  message: string;
  state: SafeExecutionState;
  retryCount: number;
  executionCount: number;
}

const executionLedger: AutomationExecutionResult[] = [];
const executorId = "runtimeAutomationExecutor";

function capabilityForPacket(packet: AutomationDispatchPacket): Capability {
  if (packet.action === "runtime_remediation") {
    return "runtime_remediation";
  }

  if (packet.action === "policy_review") {
    return "policy_review";
  }

  return "system_command";
}

function riskForPacket(packet: AutomationDispatchPacket): "low" | "medium" | "high" | "blocked" {
  if (packet.action === "trading_order") {
    return "blocked";
  }

  if (packet.priority === "high") {
    return "high";
  }

  if (packet.priority === "medium") {
    return "medium";
  }

  return "low";
}

function approvalGrantedForPacket(packet: AutomationDispatchPacket): boolean {
  if (packet.approvalGranted) {
    return true;
  }

  const approval = getApproval(`approval_${packet.packetId}`);

  return approval ? isApprovalGranted(approval) : false;
}

function blockPacket(
  packet: AutomationDispatchPacket,
  reason: string,
  state: SafeExecutionState = "blocked"
): AutomationExecutionResult {
  const result: AutomationExecutionResult = {
    packetId: packet.packetId,
    success: false,
    executedAt: new Date().toISOString(),
    message: reason,
    state,
    retryCount: packet.retryCount,
    executionCount: packet.executionCount
  };

  completeAutomationPacket(packet.packetId, executorId, state);

  writeTelemetryEvent(
    "packet_blocked",
    "runtimeAutomationExecutor",
    reason,
    {
      packetId: packet.packetId,
      status: state,
      metadata: {
        action: packet.action,
        retryCount: packet.retryCount,
        executionCount: packet.executionCount
      }
    }
  );

  return result;
}

function executePacket(
  packet: AutomationDispatchPacket
): AutomationExecutionResult {
  const policyDecision = executionAllowed({
    actorId: executorId,
    trustLevel: "maintainer",
    packetId: packet.packetId,
    capability: capabilityForPacket(packet),
    target: packet.action,
    risk: riskForPacket(packet),
    approvalGranted: approvalGrantedForPacket(packet),
    executionCount: packet.executionCount,
    retryCount: packet.retryCount,
    maxExecutions: packet.maxExecutions,
    maxRetries: packet.maxRetries,
    rollbackPrepared: Boolean(packet.rollback?.preparedAt)
  });

  if (!policyDecision.allowed) {
    return blockPacket(packet, policyDecision.reason);
  }

  packet.state = packet.retryCount > 0 ? "retrying" : "executing";
  packet.executionCount += 1;

  console.log(
    `[AUTOMATION EXECUTOR] executing ${packet.packetId} (${packet.action})`
  );

  const result: AutomationExecutionResult = {
    packetId: packet.packetId,
    success: true,
    executedAt: new Date().toISOString(),
    message: `Executed action ${packet.action}`,
    state: "completed",
    retryCount: packet.retryCount,
    executionCount: packet.executionCount
  };

  completeAutomationPacket(packet.packetId, executorId, "completed");

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
        runtimeId: packet.runtimeId,
        retryCount: packet.retryCount,
        executionCount: packet.executionCount,
        rollbackStrategy: packet.rollback.strategy
      }
    }
  );

  return result;
}

export function processAutomationQueue(maxPackets = 1): void {
  const queue = claimAutomationQueue(executorId, maxPackets);

  try {
    for (const packet of queue) {
      if (packet.retryCount > packet.maxRetries) {
        const result = blockPacket(
          packet,
          "Packet retry limit exceeded",
          "failed"
        );

        executionLedger.push(result);
        continue;
      }

      if (packet.executionCount >= packet.maxExecutions) {
        const result = blockPacket(
          packet,
          "Packet execution count exceeded",
          "blocked"
        );

        executionLedger.push(result);
        continue;
      }

      const result = executePacket(packet);
      executionLedger.push(result);

      console.log(`[AUTOMATION EXECUTOR] ${result.state} ${packet.packetId}`);
    }
  } finally {
    releaseAutomationQueue(executorId);
  }
}

export function getExecutionLedger(): AutomationExecutionResult[] {
  return [...executionLedger];
}
