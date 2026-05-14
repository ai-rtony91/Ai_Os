import type { RebuiltDispatcherState } from "./runtimeStateRebuilder";

export interface ResumeCandidate {
  packetId: string;
  reason: string;
  recommendedAction:
    | "requeue"
    | "wait_for_approval"
    | "manual_review"
    | "resume_dry_run";
}

export interface ResumePlan {
  generatedAt: string;
  candidates: ResumeCandidate[];
}

export function generateResumePlan(
  runtime: RebuiltDispatcherState
): ResumePlan {
  const candidates: ResumeCandidate[] = [];

  for (const packetId of runtime.waitingApprovalPackets) {
    candidates.push({
      packetId,
      reason: "Packet was waiting for approval before interruption",
      recommendedAction: "wait_for_approval"
    });
  }

  for (const packetId of runtime.queuedPackets) {
    candidates.push({
      packetId,
      reason: "Queued packet may safely resume dispatcher flow",
      recommendedAction: "requeue"
    });
  }

  for (const packetId of runtime.approvedPackets) {
    candidates.push({
      packetId,
      reason: "Approved packet may resume dry-run validation",
      recommendedAction: "resume_dry_run"
    });
  }

  for (const packetId of runtime.blockedPackets) {
    candidates.push({
      packetId,
      reason: "Blocked packet requires manual review",
      recommendedAction: "manual_review"
    });
  }

  return {
    generatedAt: new Date().toISOString(),
    candidates
  };
}
