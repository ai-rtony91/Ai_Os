import { runtimeEventBus, type RuntimeEvent } from "./eventBus";
import { submitApproval } from "../approvals/approvalInbox";

export type ExecutionMode = "dry_run" | "apply";

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
  mode: ExecutionMode;
  state: SafeExecutionState;
  idempotencyKey: string;
  retryCount: number;
  executionCount: number;
  maxRetries: number;
  maxExecutions: number;
  approvalRequired: boolean;
  approvalGranted: boolean;
  approvalId?: string | null;
  approvalDecidedAt?: string | null;
  approvalDecision?: string | null;
  lockedBy?: string | null;
  lockedAt?: string | null;
  lockExpiresAt?: string | null;
  rollback: RollbackMetadata;
}

const automationPacketQueue: AutomationDispatchPacket[] = [];
const closedIdempotencyKeys = new Set<string>();
let queueLockedBy: string | null = null;
let queueLockedAt: string | null = null;
let packetSequence = 0;
let dispatcherRegistered = false;
const defaultQueueLockLeaseMs = 30000;
const terminalStates: SafeExecutionState[] = [
  "completed",
  "blocked",
  "failed",
  "rolled_back"
];

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

function stableSerialize(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableSerialize(item)).join(",")}]`;
  }

  if (value && typeof value === "object") {
    return `{${Object.entries(value as Record<string, unknown>)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, item]) => `${JSON.stringify(key)}:${stableSerialize(item)}`)
      .join(",")}}`;
  }

  return JSON.stringify(value);
}

function createIdempotencyKey(
  type: AutomationDispatchPacket["type"],
  runtimeId: string,
  action: string,
  payload: Record<string, unknown>
): string {
  return `${type}:${runtimeId}:${action}:${stableSerialize(payload)}`;
}

function createPacket(
  type: AutomationDispatchPacket["type"],
  runtimeId: string,
  priority: AutomationDispatchPacket["priority"],
  action: string,
  payload: Record<string, unknown>,
  mode: ExecutionMode = "dry_run"
): AutomationDispatchPacket {
  packetSequence += 1;
  const idempotencyKey = createIdempotencyKey(type, runtimeId, action, payload);

  return {
    packetId: `packet_${Date.now()}_${packetSequence}`,
    type,
    runtimeId,
    createdAt: new Date().toISOString(),
    priority,
    action,
    payload,
    mode,
    state: "queued",
    idempotencyKey,
    retryCount: 0,
    executionCount: 0,
    maxRetries: type === "remediation" ? 2 : 0,
    maxExecutions: 1,
    approvalRequired: priority === "high" || type === "policy",
    approvalGranted: false,
    approvalId: null,
    approvalDecidedAt: null,
    approvalDecision: null,
    lockedBy: null,
    lockedAt: null,
    lockExpiresAt: null,
    rollback: createRollbackMetadata(action)
  };
}

function submitPacketApproval(packet: AutomationDispatchPacket): void {
  if (!packet.approvalRequired) {
    return;
  }

  const approval = submitApproval({
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

  packet.approvalId = approval.approvalId;
}

function enqueueAutomationPacket(packet: AutomationDispatchPacket): AutomationDispatchPacket | null {
  if (closedIdempotencyKeys.has(packet.idempotencyKey)) {
    return null;
  }

  const duplicate = automationPacketQueue.find(
    (item) =>
      item.idempotencyKey === packet.idempotencyKey &&
      !terminalStates.includes(item.state)
  );

  if (duplicate) {
    return null;
  }

  automationPacketQueue.push(packet);
  submitPacketApproval(packet);

  return packet;
}

function queueLockExpired(now: Date): boolean {
  if (!queueLockedAt) {
    return false;
  }

  return now.getTime() - new Date(queueLockedAt).getTime() > defaultQueueLockLeaseMs;
}

function reclaimExpiredLocks(now: Date): void {
  for (const packet of automationPacketQueue) {
    if (!packet.lockExpiresAt) {
      continue;
    }

    if (new Date(packet.lockExpiresAt).getTime() > now.getTime()) {
      continue;
    }

    packet.lockedBy = null;
    packet.lockedAt = null;
    packet.lockExpiresAt = null;

    if (packet.state === "scheduled" || packet.state === "executing") {
      packet.state = "queued";
    }
  }

  if (queueLockedBy && queueLockExpired(now)) {
    queueLockedBy = null;
    queueLockedAt = null;
  }
}

export function getAutomationPacketQueue(): AutomationDispatchPacket[] {
  return [...automationPacketQueue];
}

export function claimAutomationQueue(
  workerId: string,
  maxPackets: number,
  lockLeaseMs = defaultQueueLockLeaseMs
): AutomationDispatchPacket[] {
  const now = new Date();
  reclaimExpiredLocks(now);

  if (queueLockedBy && queueLockedBy !== workerId) {
    return [];
  }

  queueLockedBy = workerId;
  queueLockedAt = now.toISOString();

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
    packet.lockedAt = now.toISOString();
    packet.lockExpiresAt = new Date(now.getTime() + lockLeaseMs).toISOString();
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
  packet.lockExpiresAt = null;

  if (
    nextState === "completed" ||
    nextState === "blocked" ||
    nextState === "failed" ||
    nextState === "rolled_back"
  ) {
    closedIdempotencyKeys.add(packet.idempotencyKey);
    automationPacketQueue.splice(packetIndex, 1);
  }

  return { ...packet };
}

export function releaseAutomationQueue(workerId: string): void {
  for (const packet of automationPacketQueue) {
    if (packet.lockedBy === workerId) {
      packet.lockedBy = null;
      packet.lockedAt = null;
      packet.lockExpiresAt = null;

      if (packet.state === "scheduled" || packet.state === "executing") {
        packet.state = "queued";
      }
    }
  }

  if (queueLockedBy === workerId) {
    queueLockedBy = null;
    queueLockedAt = null;
  }
}

export function isAutomationQueueLocked(): boolean {
  return queueLockedBy !== null;
}

export function registerRuntimeAutomationDispatcher(): void {
  if (dispatcherRegistered) {
    return;
  }

  dispatcherRegistered = true;

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

        const queuedPacket = enqueueAutomationPacket(packet);

        if (!queuedPacket) {
          console.log(
            `[AUTOMATION DISPATCH] duplicate remediation packet skipped for ${packet.runtimeId}`
          );
          return;
        }

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

        const queuedPacket = enqueueAutomationPacket(packet);

        if (!queuedPacket) {
          console.log(
            `[AUTOMATION DISPATCH] duplicate policy packet skipped for ${packet.runtimeId}`
          );
          return;
        }

        console.log(
          `[AUTOMATION DISPATCH] queued policy packet ${packet.packetId}`
        );
      }
    }
  );
}
