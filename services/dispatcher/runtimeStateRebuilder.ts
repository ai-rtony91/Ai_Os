import type { ReplayedRuntimeState } from "../telemetry/telemetryReplay";

export interface RebuiltDispatcherState {
  queuedPackets: string[];
  dryRunPackets: string[];
  waitingApprovalPackets: string[];
  approvedPackets: string[];
  blockedPackets: string[];
  appliedPackets: string[];
  pendingApprovals: string[];
  invalidPacketStatuses: Array<{
    packetId: string;
    status: string;
    lastEventType: string;
  }>;
  rebuiltAt: string;
  sourceEventCount: number;
  invalidLineCount: number;
}

function normalizePacketStatus(
  status: string,
  lastEventType: string
): string {
  if (lastEventType === "approval_requested") {
    return "waiting_approval";
  }

  if (lastEventType === "packet_blocked") {
    return "blocked";
  }

  if (lastEventType === "packet_applied") {
    return status === "dry_run" ? "dry_run" : "applied";
  }

  return status;
}

function uniqueSorted(items: string[]): string[] {
  return [...new Set(items)].sort((a, b) => a.localeCompare(b));
}

export function rebuildDispatcherState(
  replayed: ReplayedRuntimeState
): RebuiltDispatcherState {
  const queuedPackets: string[] = [];
  const dryRunPackets: string[] = [];
  const waitingApprovalPackets: string[] = [];
  const approvedPackets: string[] = [];
  const blockedPackets: string[] = [];
  const appliedPackets: string[] = [];
  const pendingApprovals: string[] = [];
  const invalidPacketStatuses: RebuiltDispatcherState["invalidPacketStatuses"] = [];

  for (const packet of Object.values(replayed.packets)) {
    const status = normalizePacketStatus(packet.status, packet.lastEventType);

    switch (status) {
      case "queued":
        queuedPackets.push(packet.packetId);
        break;

      case "dry_run":
        dryRunPackets.push(packet.packetId);
        break;

      case "waiting_approval":
        waitingApprovalPackets.push(packet.packetId);
        break;

      case "approved":
        approvedPackets.push(packet.packetId);
        break;

      case "blocked":
        blockedPackets.push(packet.packetId);
        break;

      case "applied":
        appliedPackets.push(packet.packetId);
        break;

      default:
        invalidPacketStatuses.push({
          packetId: packet.packetId,
          status: packet.status,
          lastEventType: packet.lastEventType
        });
        break;
    }
  }

  for (const approval of Object.values(replayed.approvals)) {
    if (
      approval.status === "pending" ||
      approval.status === "waiting_approval" ||
      approval.status === "approval_requested"
    ) {
      pendingApprovals.push(approval.approvalId);
    }
  }

  return {
    queuedPackets: uniqueSorted(queuedPackets),
    dryRunPackets: uniqueSorted(dryRunPackets),
    waitingApprovalPackets: uniqueSorted(waitingApprovalPackets),
    approvedPackets: uniqueSorted(approvedPackets),
    blockedPackets: uniqueSorted(blockedPackets),
    appliedPackets: uniqueSorted(appliedPackets),
    pendingApprovals: uniqueSorted(pendingApprovals),
    invalidPacketStatuses: invalidPacketStatuses.sort((a, b) =>
      a.packetId.localeCompare(b.packetId)
    ),
    rebuiltAt: new Date().toISOString(),
    sourceEventCount: replayed.eventCount,
    invalidLineCount: replayed.invalidLineCount
  };
}
