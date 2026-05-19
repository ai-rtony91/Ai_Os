import type { DeadLetterQueueState } from "./deadLetterQueue";
import { listRetryableDeadLetters, listPoisonPackets } from "./deadLetterQueue";
import type { ResumePlan } from "./packetResumeEngine";
import type { PacketQueueSnapshot } from "./packetQueue";
import type { WorkerLeaseResult } from "./workerLeaseEngine";

export interface SchedulerInput {
  resumePlan: ResumePlan;
  deadLetterQueue: DeadLetterQueueState;
  workerLeases: WorkerLeaseResult;
  maxConcurrentPackets: number;
  packetQueueSnapshot?: PacketQueueSnapshot;
}

export interface ScheduledAction {
  packetId: string;
  action:
    | "dispatch"
    | "wait_for_approval"
    | "resume_dry_run"
    | "retry"
    | "manual_review";
  reason: string;
  priority: number;
}

export interface SchedulerPlan {
  actions: ScheduledAction[];
  poisonPackets: string[];
  reclaimablePackets: string[];
  generatedAt: string;
}

function priorityForAction(action: ScheduledAction["action"]): number {
  switch (action) {
    case "manual_review":
      return 100;
    case "wait_for_approval":
      return 80;
    case "resume_dry_run":
      return 60;
    case "retry":
      return 50;
    case "dispatch":
      return 40;
  }
}

export function generateSchedulerPlan(input: SchedulerInput): SchedulerPlan {
  const actions: ScheduledAction[] = [];
  const poisonPackets = listPoisonPackets(input.deadLetterQueue).map(
    (packet) => packet.packetId
  );
  const retryablePackets = listRetryableDeadLetters(input.deadLetterQueue).map(
    (packet) => packet.packetId
  );
  const reclaimablePackets = input.workerLeases.reclaimablePackets;

  if (input.packetQueueSnapshot) {
    for (const record of input.packetQueueSnapshot.records) {
      if (record.status === "queued" || record.status === "scheduled") {
        actions.push({
          packetId: record.packetId,
          action: "dispatch",
          reason: record.lastReason ?? "Packet is dispatchable from canonical queue",
          priority: priorityForAction("dispatch")
        });
      }

      if (record.status === "waiting_approval") {
        actions.push({
          packetId: record.packetId,
          action: "wait_for_approval",
          reason: record.lastReason ?? "Packet is waiting for approval in canonical queue",
          priority: priorityForAction("wait_for_approval")
        });
      }

      if (record.status === "approved" || record.status === "dry_run") {
        actions.push({
          packetId: record.packetId,
          action: "resume_dry_run",
          reason: record.lastReason ?? "Packet can resume validation from canonical queue",
          priority: priorityForAction("resume_dry_run")
        });
      }

      if (record.status === "retrying" || record.status === "failed") {
        actions.push({
          packetId: record.packetId,
          action: "retry",
          reason: record.lastReason ?? "Packet is retryable from canonical queue",
          priority: priorityForAction("retry")
        });
      }

      if (record.status === "dead_letter" || record.status === "manual_review") {
        actions.push({
          packetId: record.packetId,
          action: "manual_review",
          reason: record.lastReason ?? "Packet requires manual review from canonical queue",
          priority: priorityForAction("manual_review")
        });
      }
    }
  }

  for (const candidate of input.resumePlan.candidates) {
    const action =
      candidate.recommendedAction === "requeue"
        ? "dispatch"
        : candidate.recommendedAction;

    actions.push({
      packetId: candidate.packetId,
      action,
      reason: candidate.reason,
      priority: priorityForAction(action)
    });
  }

  for (const packetId of retryablePackets) {
    actions.push({
      packetId,
      action: "retry",
      reason: "Packet is retryable and within retry budget",
      priority: priorityForAction("retry")
    });
  }

  for (const packetId of poisonPackets) {
    actions.push({
      packetId,
      action: "manual_review",
      reason: "Packet is poison or exceeded retry budget",
      priority: priorityForAction("manual_review")
    });
  }

  for (const packetId of reclaimablePackets) {
    actions.push({
      packetId,
      action: "dispatch",
      reason: "Packet was reclaimed from expired worker lease",
      priority: priorityForAction("dispatch")
    });
  }

  const deduped = new Map<string, ScheduledAction>();

  for (const action of actions) {
    const existing = deduped.get(action.packetId);

    if (!existing || action.priority > existing.priority) {
      deduped.set(action.packetId, action);
    }
  }

  const scheduledActions = [...deduped.values()]
    .sort((a, b) => b.priority - a.priority)
    .slice(0, Math.max(0, input.maxConcurrentPackets));

  return {
    actions: scheduledActions,
    poisonPackets: [...new Set(poisonPackets)],
    reclaimablePackets: [...new Set(reclaimablePackets)],
    generatedAt: new Date().toISOString()
  };
}
