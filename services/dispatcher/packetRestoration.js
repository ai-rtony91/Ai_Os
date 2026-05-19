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

  for (const event of events) {
    if (event.packetId) {
      packets.set(event.packetId, {
        packetId: event.packetId,
        status: event.status || event.eventType,
        risk: event.risk,
        lastEventType: event.eventType,
        lastUpdatedAt: event.ts
      });
    }

    if (event.approvalId) {
      approvals.set(event.approvalId, {
        approvalId: event.approvalId,
        packetId: event.packetId,
        status: event.status || event.eventType,
        risk: event.risk,
        lastUpdatedAt: event.ts
      });
    }
  }

  const restoredPackets = Array.from(packets.values());
  const pendingApprovals = Array.from(approvals.values()).filter((approval) =>
    ["pending", "waiting_approval", "approval_requested"].includes(approval.status)
  );

  const resumeCandidates = restoredPackets
    .filter((packet) => !["applied", "packet_applied"].includes(packet.status))
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
    resumeCandidates
  };
}

function chooseResumeAction(status) {
  if (status === "waiting_approval" || status === "approval_requested") {
    return "wait_for_approval";
  }

  if (status === "blocked" || status === "packet_blocked") {
    return "manual_review";
  }

  if (status === "approved") {
    return "resume_dry_run";
  }

  return "requeue";
}

module.exports = {
  restorePacketsFromTelemetry
};
