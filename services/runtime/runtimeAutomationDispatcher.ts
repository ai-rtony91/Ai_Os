import { runtimeEventBus, type RuntimeEvent } from "./eventBus";
import { submitApproval } from "../approvals/approvalInbox";

export type SafeExecutionState =
  | "queued"
  | "scheduled"
  | "executing"
  | "retrying"
  | "failed"
  | "blocked"
  | "completed"
  | "rolled_back";

export interface RollbackMetadata {
  strategy: "none" | "manual" | "git_restore" | "compensating_action";
  rollbackRef?: string | null;
  preparedAt: string;
  notes?: string | null;
}

export interface AutomationDispatchPacket {
  packetId: string;
  type: "remediation" | "policy";
  runtimeId: string;
  createdAt: string;
  priority: "low" | "medium" | "high";
  action: string;
  payload: Record<string, unknown>;
  state: SafeExecutionState;
  retryCount: number;
  executionCount: number;
  maxRetries: number;
  maxExecutions: number;
  approvalRequired: boolean;
  approvalGranted: boolean;
  lockedBy?: string | null;
  lockedAt?: string | null;
  rollback: RollbackMetadata;
}

const automationPacketQueue: AutomationDispatchPacket[] = [];
let queueLockedBy: string | null = null;
let packetSequence = 0;

function createRollbackMetadata(action: string): RollbackMetadata {
  return {
    strategy: action === "runtime_remediation" ? "manual" : "none",
    rollbackRef:
      action === "runtime_remediation"
        ? "Review remediation telemetry and restore prior runtime state manually"
        : null,
    preparedAt: new Date().toISOString(),
    notes: "Rollback must be prepared before APPLY execution"
  };
}

function createPacket(
  type: AutomationDispatchPacket["type"],
  runtimeId: string,
  priority: AutomationDispatchPacket["priority"],
  action: string,
  payload: Record<string, unknown>
): AutomationDispatchPacket {
  packetSequence += 1;

  return {
    packetId: `packet_${Date.now()}_${packetSequence}`,
    type,
    runtimeId,
    createdAt: new Date().toISOString(),
    priority,
    action,
    payload,
    state: "queued",
    retryCount: 0,
    executionCount: 0,
    maxRetries: type === "remediation" ? 2 : 0,
    maxExecutions: 1,
    approvalRequired: priority === "high" || type === "policy",
    approvalGranted: false,
    lockedBy: null,
    lockedAt: null,
    rollback: createRollbackMetadata(action)
  };
}

function submitPacketApproval(packet: AutomationDispatchPacket): void {
  if (!packet.approvalRequired) {
    return;
  }

  submitApproval({
    approvalId: `approval_${packet.packetId}`,
    packetId: packet.packetId,
    title: `Approve ${packet.action}`,
    actionType:
      packet.action === "runtime_remediation"
        ? "runtime_remediation"
        : "policy_review",
    risk: packet.priority === "high" ? "high" : "medium",
    status: "pending",
    summary: `Approval gate for ${packet.action}`,
    targetFiles: [],
    commandPreview: null,
    rollbackRef: packet.rollback.rollbackRef ?? null,
    rollbackPrepared: Boolean(packet.rollback.preparedAt),
    executionLimits: {
      maxRetries: packet.maxRetries,
      maxExecutions: packet.maxExecutions
    },
    requestedAt: new Date().toISOString(),
    decidedAt: null,
    decision: null
  });
}

export function getAutomationPacketQueue(): AutomationDispatchPacket[] {
  return [...automationPacketQueue];
}

export function claimAutomationQueue(
  workerId: string,
  maxPackets: number
): AutomationDispatchPacket[] {
  if (queueLockedBy && queueLockedBy !== workerId) {
    return [];
  }

  queueLockedBy = workerId;

  const claimLimit = Math.max(0, maxPackets);
  const claimed: AutomationDispatchPacket[] = [];

  for (const packet of automationPacketQueue) {
    if (claimed.length >= claimLimit) {
      break;
    }

    if (packet.lockedBy || packet.state === "executing") {
      continue;
    }

    if (
      packet.state !== "queued" &&
      packet.state !== "scheduled" &&
      packet.state !== "retrying"
    ) {
      continue;
    }

    packet.state = "scheduled";
    packet.lockedBy = workerId;
    packet.lockedAt = new Date().toISOString();
    claimed.push({ ...packet });
  }

  return claimed;
}

export function completeAutomationPacket(
  packetId: string,
  workerId: string,
  nextState: SafeExecutionState
): AutomationDispatchPacket | undefined {
  const packetIndex = automationPacketQueue.findIndex(
    (packet) => packet.packetId === packetId
  );

  if (packetIndex < 0) {
    return undefined;
  }

  const packet = automationPacketQueue[packetIndex];

  if (packet.lockedBy !== workerId) {
    return { ...packet };
  }

  packet.state = nextState;
  packet.lockedBy = null;
  packet.lockedAt = null;

  if (
    nextState === "completed" ||
    nextState === "blocked" ||
    nextState === "failed" ||
    nextState === "rolled_back"
  ) {
    automationPacketQueue.splice(packetIndex, 1);
  }

  return { ...packet };
}

export function releaseAutomationQueue(workerId: string): void {
  for (const packet of automationPacketQueue) {
    if (packet.lockedBy === workerId) {
      packet.lockedBy = null;
      packet.lockedAt = null;

      if (packet.state === "scheduled" || packet.state === "executing") {
        packet.state = "queued";
      }
    }
  }

  if (queueLockedBy === workerId) {
    queueLockedBy = null;
  }
}

export function isAutomationQueueLocked(): boolean {
  return queueLockedBy !== null;
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
        submitPacketApproval(packet);

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
        submitPacketApproval(packet);

        console.log(
          `[AUTOMATION DISPATCH] queued policy packet ${packet.packetId}`
        );
      }
    }
  );
}
