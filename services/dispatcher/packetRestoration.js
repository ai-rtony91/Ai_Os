const fs = require("fs");
const path = require("path");

const DEFAULT_LEDGER_PATH =
  process.env.AIOS_TELEMETRY_LEDGER || path.join("telemetry", "work_ledger.jsonl");

function parseLedgerLine(line) {
  try {
    return { event: JSON.parse(line), invalid: false };
  } catch {
    return { event: null, invalid: true };
  }
}

function loadTelemetryEvents(ledgerPath = DEFAULT_LEDGER_PATH) {
  if (!fs.existsSync(ledgerPath)) {
    return { events: [], invalidLineCount: 0 };
  }

  const content = fs.readFileSync(ledgerPath, "utf8");
  const events = [];
  let invalidLineCount = 0;

  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();

    if (!trimmed) {
      continue;
    }

    const parsed = parseLedgerLine(trimmed);

    if (parsed.invalid) {
      invalidLineCount += 1;
      continue;
    }

    events.push(parsed.event);
  }

  return { events, invalidLineCount };
}

function restorePacketsFromTelemetry(ledgerPath = DEFAULT_LEDGER_PATH) {
  const { events, invalidLineCount } = loadTelemetryEvents(ledgerPath);
  const packets = new Map();
  const approvals = new Map();
  const dispatcherState = {
    queuedPackets: [],
    waitingApprovalPackets: [],
    approvedPackets: [],
    blockedPackets: [],
    appliedPackets: [],
    pendingApprovals: []
  };

  for (const event of events) {
    const packetStatus = normalizePacketStatus(event.status || event.eventType);
    const approvalStatus = normalizeApprovalStatus(event.status || event.eventType);

    if (event.packetId) {
      packets.set(event.packetId, {
        packetId: event.packetId,
        status: packetStatus,
        risk: event.risk,
        lastEventType: event.eventType,
        lastUpdatedAt: event.ts
      });

      if (event.eventType === "packet_blocked") {
        addUnique(dispatcherState.blockedPackets, event.packetId);
      }

      if (event.eventType === "packet_applied") {
        addUnique(dispatcherState.appliedPackets, event.packetId);
      }
    }

    if (event.approvalId) {
      approvals.set(event.approvalId, {
        approvalId: event.approvalId,
        packetId: event.packetId,
        status: approvalStatus,
        risk: event.risk,
        lastUpdatedAt: event.ts
      });
    }
  }

  const restoredPackets = Array.from(packets.values());
  const pendingApprovals = Array.from(approvals.values()).filter((approval) =>
    ["pending", "waiting_approval"].includes(approval.status)
  );

  for (const packet of restoredPackets) {
    if (packet.status === "queued") {
      addUnique(dispatcherState.queuedPackets, packet.packetId);
    } else if (packet.status === "waiting_approval") {
      addUnique(dispatcherState.waitingApprovalPackets, packet.packetId);
    } else if (packet.status === "approved") {
      addUnique(dispatcherState.approvedPackets, packet.packetId);
    } else if (packet.status === "blocked") {
      addUnique(dispatcherState.blockedPackets, packet.packetId);
    } else if (packet.status === "applied" || packet.status === "dry_run") {
      addUnique(dispatcherState.appliedPackets, packet.packetId);
    }
  }

  for (const approval of pendingApprovals) {
    addUnique(dispatcherState.pendingApprovals, approval.approvalId);
  }

  const resumeCandidates = restoredPackets
    .filter((packet) => !["applied", "dry_run"].includes(packet.status))
    .map((packet) => ({
      packetId: packet.packetId,
      lastKnownStatus: packet.status,
      recommendedAction: chooseResumeAction(packet.status),
      reason: `Restored from telemetry event ${packet.lastEventType}`
    }));

  return {
    restoredAt: new Date().toISOString(),
    ledgerPath,
    sourceEventCount: events.length,
    invalidLineCount,
    restoredPackets,
    pendingApprovals,
    dispatcherState,
    resumeCandidates
  };
}

function addUnique(items, value) {
  if (!items.includes(value)) {
    items.push(value);
  }
}

function normalizePacketStatus(status) {
  if (status === "approval_requested") {
    return "waiting_approval";
  }

  if (status === "packet_blocked") {
    return "blocked";
  }

  if (status === "packet_applied") {
    return "applied";
  }

  return status;
}

function normalizeApprovalStatus(status) {
  if (status === "approval_requested") {
    return "waiting_approval";
  }

  return status;
}

function chooseResumeAction(status) {
  if (status === "waiting_approval") {
    return "wait_for_approval";
  }

  if (status === "blocked") {
    return "manual_review";
  }

  if (status === "approved") {
    return "resume_dry_run";
  }

  if (status === "queued") {
    return "requeue";
  }

  return "manual_review";
}

module.exports = {
  restorePacketsFromTelemetry
};
