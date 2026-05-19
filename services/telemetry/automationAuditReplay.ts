import { existsSync, readFileSync } from "fs";
import type { TelemetryEvent } from "./telemetryEvent";
import { parseTelemetryLedger } from "./telemetryReplay";

export type AuditTimelineCategory =
  | "packet_lifecycle"
  | "approval"
  | "policy_decision"
  | "execution"
  | "failure"
  | "recovery"
  | "telemetry";

export interface AuditTimelineEntry {
  eventId: string;
  ts: string;
  category: AuditTimelineCategory;
  eventType: string;
  source: string;
  summary: string;
  packetId?: string;
  approvalId?: string;
  status?: string;
  risk?: string;
  why: string;
  whatChanged: string;
  recoveryAction?: string;
  metadata?: Record<string, unknown>;
}

export interface PacketLifecycleAudit {
  packetId: string;
  firstSeenAt: string;
  lastSeenAt: string;
  currentStatus: string;
  risk?: string;
  eventCount: number;
  lifecycle: AuditTimelineEntry[];
}

export interface PolicyDecisionAudit {
  eventId: string;
  ts: string;
  packetId?: string;
  status?: string;
  risk?: string;
  actorId?: string;
  capability?: string;
  trustLevel?: string;
  target?: string;
  requiresApproval?: boolean;
  reason: string;
}

export interface FailureSummary {
  packetId?: string;
  eventId: string;
  ts: string;
  source: string;
  status?: string;
  reason: string;
  recoveryAction: string;
}

export interface RecoverySummary {
  blockedPackets: string[];
  failedPackets: string[];
  pendingApprovals: string[];
  replayRecommendation: string;
}

export interface AutomationAuditReplay {
  schema: "aios.automation_audit_replay.v1";
  generatedAt: string;
  ledgerPath: string;
  sourceEventCount: number;
  invalidLineCount: number;
  timeline: AuditTimelineEntry[];
  packetLifecycles: PacketLifecycleAudit[];
  policyDecisions: PolicyDecisionAudit[];
  failureSummary: FailureSummary[];
  recoverySummary: RecoverySummary;
}

function metadataFor(event: TelemetryEvent): Record<string, unknown> {
  return event.metadata ?? {};
}

function metadataString(
  metadata: Record<string, unknown>,
  key: string
): string | undefined {
  const value = metadata[key];

  return typeof value === "string" ? value : undefined;
}

function metadataBoolean(
  metadata: Record<string, unknown>,
  key: string
): boolean | undefined {
  const value = metadata[key];

  return typeof value === "boolean" ? value : undefined;
}

function categorizeEvent(event: TelemetryEvent): AuditTimelineCategory {
  if (event.eventType === "policy_decision") {
    return "policy_decision";
  }

  if (event.eventType === "approval_requested" || event.eventType === "approval_decided") {
    return "approval";
  }

  if (event.eventType === "packet_blocked") {
    return "failure";
  }

  if (event.eventType === "packet_applied") {
    return "execution";
  }

  if (event.eventType === "clean_state_checked") {
    return "recovery";
  }

  if (event.eventType === "packet_dispatched") {
    return "packet_lifecycle";
  }

  return "telemetry";
}

function explainWhy(event: TelemetryEvent): string {
  const metadata = metadataFor(event);
  const action = metadataString(metadata, "action");
  const capability = metadataString(metadata, "capability");
  const target = metadataString(metadata, "target");

  if (event.eventType === "policy_decision") {
    const scope = [capability, target].filter(Boolean).join(" on ");
    return scope ? `${event.summary} (${scope})` : event.summary;
  }

  if (event.eventType === "packet_blocked") {
    return event.summary || "Packet was blocked by automation safety controls";
  }

  if (event.eventType === "packet_applied") {
    return action ? `Action executed: ${action}` : event.summary;
  }

  return event.summary;
}

function describeChange(event: TelemetryEvent): string {
  if (event.packetId && event.status) {
    return `Packet ${event.packetId} status became ${event.status}`;
  }

  if (event.approvalId && event.status) {
    return `Approval ${event.approvalId} status became ${event.status}`;
  }

  if (event.packetId) {
    return `Packet ${event.packetId} recorded ${event.eventType}`;
  }

  return `Recorded ${event.eventType}`;
}

function recoveryActionFor(event: TelemetryEvent): string | undefined {
  if (event.eventType !== "packet_blocked") {
    return undefined;
  }

  if (event.status === "failed") {
    return "Review failure reason, retry budget, and rollback metadata before reassignment.";
  }

  return "Keep packet blocked until human review clears approval, policy, and rollback evidence.";
}

function toTimelineEntry(event: TelemetryEvent): AuditTimelineEntry {
  return {
    eventId: event.eventId,
    ts: event.ts,
    category: categorizeEvent(event),
    eventType: event.eventType,
    source: event.source,
    summary: event.summary,
    packetId: event.packetId,
    approvalId: event.approvalId,
    status: event.status,
    risk: event.risk,
    why: explainWhy(event),
    whatChanged: describeChange(event),
    recoveryAction: recoveryActionFor(event),
    metadata: event.metadata
  };
}

function buildPacketLifecycles(
  timeline: AuditTimelineEntry[]
): PacketLifecycleAudit[] {
  const packets = new Map<string, AuditTimelineEntry[]>();

  for (const entry of timeline) {
    if (!entry.packetId) {
      continue;
    }

    const packetEvents = packets.get(entry.packetId) ?? [];
    packetEvents.push(entry);
    packets.set(entry.packetId, packetEvents);
  }

  return [...packets.entries()]
    .map(([packetId, lifecycle]) => {
      const sorted = [...lifecycle].sort((a, b) => a.ts.localeCompare(b.ts));
      const last = sorted[sorted.length - 1];

      return {
        packetId,
        firstSeenAt: sorted[0].ts,
        lastSeenAt: last.ts,
        currentStatus: last.status ?? last.eventType,
        risk: last.risk,
        eventCount: sorted.length,
        lifecycle: sorted
      };
    })
    .sort((a, b) => b.lastSeenAt.localeCompare(a.lastSeenAt));
}

function buildPolicyDecisionAudit(
  timeline: AuditTimelineEntry[]
): PolicyDecisionAudit[] {
  return timeline
    .filter((entry) => entry.eventType === "policy_decision")
    .map((entry) => {
      const metadata = entry.metadata ?? {};

      return {
        eventId: entry.eventId,
        ts: entry.ts,
        packetId: entry.packetId,
        status: entry.status,
        risk: entry.risk,
        actorId: metadataString(metadata, "actorId"),
        capability: metadataString(metadata, "capability"),
        trustLevel: metadataString(metadata, "trustLevel"),
        target: metadataString(metadata, "target"),
        requiresApproval: metadataBoolean(metadata, "requiresApproval"),
        reason: entry.summary
      };
    });
}

function buildFailureSummary(timeline: AuditTimelineEntry[]): FailureSummary[] {
  return timeline
    .filter((entry) => entry.category === "failure" || entry.status === "failed")
    .map((entry) => ({
      packetId: entry.packetId,
      eventId: entry.eventId,
      ts: entry.ts,
      source: entry.source,
      status: entry.status,
      reason: entry.why,
      recoveryAction:
        entry.recoveryAction ??
        "Review event context before retry, reassignment, APPLY, commit, or push."
    }));
}

function buildRecoverySummary(
  timeline: AuditTimelineEntry[]
): RecoverySummary {
  const blockedPackets = new Set<string>();
  const failedPackets = new Set<string>();
  const pendingApprovals = new Set<string>();

  for (const entry of timeline) {
    if (entry.packetId && (entry.status === "blocked" || entry.eventType === "packet_blocked")) {
      blockedPackets.add(entry.packetId);
    }

    if (entry.packetId && entry.status === "failed") {
      failedPackets.add(entry.packetId);
    }

    if (
      entry.approvalId &&
      (entry.status === "pending" || entry.status === "waiting_approval")
    ) {
      pendingApprovals.add(entry.approvalId);
    }
  }

  const hasRecoveryWork =
    blockedPackets.size > 0 || failedPackets.size > 0 || pendingApprovals.size > 0;

  return {
    blockedPackets: [...blockedPackets],
    failedPackets: [...failedPackets],
    pendingApprovals: [...pendingApprovals],
    replayRecommendation: hasRecoveryWork
      ? "Human review required before resume, retry, APPLY, commit, or push."
      : "No blocked, failed, or pending approval events found in the replayed ledger."
  };
}

export function buildAutomationAuditReplay(
  events: TelemetryEvent[],
  invalidLineCount = 0,
  ledgerPath = "telemetry/work_ledger.jsonl"
): AutomationAuditReplay {
  const timeline = events
    .map(toTimelineEntry)
    .sort((a, b) => a.ts.localeCompare(b.ts));

  return {
    schema: "aios.automation_audit_replay.v1",
    generatedAt: new Date().toISOString(),
    ledgerPath,
    sourceEventCount: events.length,
    invalidLineCount,
    timeline,
    packetLifecycles: buildPacketLifecycles(timeline),
    policyDecisions: buildPolicyDecisionAudit(timeline),
    failureSummary: buildFailureSummary(timeline),
    recoverySummary: buildRecoverySummary(timeline)
  };
}

export function buildAutomationAuditReplayFromLedger(
  ledgerPath = "telemetry/work_ledger.jsonl"
): AutomationAuditReplay {
  if (!existsSync(ledgerPath)) {
    return buildAutomationAuditReplay([], 0, ledgerPath);
  }

  const content = readFileSync(ledgerPath, "utf-8");
  const { events, invalidLineCount } = parseTelemetryLedger(content);

  return buildAutomationAuditReplay(events, invalidLineCount, ledgerPath);
}
