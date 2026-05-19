import { runtimeEventBus, type RuntimeEvent } from "./eventBus";
import { submitApproval } from "../approvals/approvalInbox";
import {
  claimPackets,
  createPacketQueueState,
  enqueuePacket,
  getQueueSnapshot,
  releasePacketClaims,
  removeTerminalPackets,
  setPacketQueueStatus,
  completePacket,
  type PacketExecutionStatus,
  type PacketQueueRecord,
  type PacketQueueSnapshot,
  type PacketQueueState
} from "../dispatcher/packetQueue";

export type SafeExecutionState = PacketExecutionStatus;

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

let automationPacketQueue: PacketQueueState<AutomationDispatchPacket> =
  createPacketQueueState<AutomationDispatchPacket>();
let queueLockedBy: string | null = null;
let packetSequence = 0;

function packetFromQueueRecord(
  record: PacketQueueRecord<AutomationDispatchPacket>
): AutomationDispatchPacket {
  return {
    ...record.packet,
    state: record.status as SafeExecutionState,
    retryCount: record.retryCount,
    maxRetries: record.maxRetries ?? record.packet.maxRetries,
    lockedBy: record.claimedBy ?? null,
    lockedAt: record.claimedAt ?? null
  };
}

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
  return automationPacketQueue.records.map(packetFromQueueRecord);
}

export function getAutomationPacketQueueSnapshot(): PacketQueueSnapshot<AutomationDispatchPacket> {
  return getQueueSnapshot(automationPacketQueue);
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
  const result = claimPackets(automationPacketQueue, {
    workerId,
    maxPackets: claimLimit
  });

  automationPacketQueue = result.state;

  return (result.records ?? []).map(packetFromQueueRecord);
}

export function completeAutomationPacket(
  packetId: string,
  workerId: string,
  nextState: SafeExecutionState
): AutomationDispatchPacket | undefined {
  const existing = automationPacketQueue.records.find(
    (record) => record.packetId === packetId
  );

  if (!existing) {
    return undefined;
  }

  if (existing.claimedBy !== workerId) {
    return packetFromQueueRecord(existing);
  }

  const result = completePacket(
    automationPacketQueue,
    packetId,
    workerId,
    nextState
  );

  if (
    nextState === "completed" ||
    nextState === "blocked" ||
    nextState === "failed" ||
    nextState === "rolled_back"
  ) {
    automationPacketQueue = removeTerminalPackets(result.state);
  } else {
    automationPacketQueue = result.state;
  }

  return result.record ? packetFromQueueRecord(result.record) : undefined;
}

export function markAutomationPacketState(
  packetId: string,
  workerId: string,
  nextState: SafeExecutionState
): AutomationDispatchPacket | undefined {
  const existing = automationPacketQueue.records.find(
    (record) => record.packetId === packetId
  );

  if (!existing) {
    return undefined;
  }

  if (existing.claimedBy !== workerId) {
    return packetFromQueueRecord(existing);
  }

  const result = setPacketQueueStatus(
    automationPacketQueue,
    packetId,
    nextState
  );
  automationPacketQueue = result.state;

  return result.record ? packetFromQueueRecord(result.record) : undefined;
}

export function releaseAutomationQueue(workerId: string): void {
  const result = releasePacketClaims(automationPacketQueue, workerId);
  automationPacketQueue = result.state;

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

        const result = enqueuePacket(automationPacketQueue, packet, {
          status: "queued",
          maxRetries: packet.maxRetries,
          reason: "Runtime remediation packet created"
        });
        automationPacketQueue = result.state;
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

        const result = enqueuePacket(automationPacketQueue, packet, {
          status: "queued",
          maxRetries: packet.maxRetries,
          reason: "Policy review packet created"
        });
        automationPacketQueue = result.state;
        submitPacketApproval(packet);

        console.log(
          `[AUTOMATION DISPATCH] queued policy packet ${packet.packetId}`
        );
      }
    }
  );
}
