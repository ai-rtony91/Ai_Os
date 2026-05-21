import type { WorkPacket } from "./dispatcher";
import { submitApproval } from "../approvals/approvalInbox";

export function routePacketApproval(packet: WorkPacket) {
  if (!packet.requiresApproval) {
    return null;
  }

  return submitApproval({
    approvalId: `approval_${packet.packetId}`,
    packetId: packet.packetId,
    title: `Approve ${packet.title}`,
    actionType: packet.risk === "high" ? "system_command" : "file_write",
    risk: packet.risk,
    status: "pending",
    summary: packet.goal,
    targetFiles: packet.allowedFiles,
    commandPreview: null,
    rollbackRef: "git restore <target-files>",
    rollbackPrepared: true,
    executionLimits: {
      maxRetries: 0,
      maxExecutions: 1
    },
    requestedAt: new Date().toISOString(),
    decidedAt: null,
    decision: null
  });
}
