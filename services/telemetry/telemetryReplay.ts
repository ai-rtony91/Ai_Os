import { existsSync, readFileSync } from "fs";
import type { TelemetryEvent } from "./telemetryEvent";

export interface ReplayedRuntimeState {
  packets: Record<string, {
    packetId: string;
    status: string;
    risk?: string;
    lastEventType: string;
    lastUpdatedAt: string;
  }>;
  approvals: Record<string, {
    approvalId: string;
    packetId?: string;
    status: string;
    risk?: string;
    lastUpdatedAt: string;
  }>;
  blockedPackets: string[];
  appliedPackets: string[];
  eventCount: number;
  invalidLineCount: number;
}

export interface TelemetryInspection {
  events: TelemetryEvent[];
  replayedState: ReplayedRuntimeState;
  invalidLineCount: number;
  lastEventAt?: string;
}

export function parseTelemetryLedger(content: string): {
  events: TelemetryEvent[];
  invalidLineCount: number;
} {
  const events: TelemetryEvent[] = [];
  let invalidLineCount = 0;

  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();

    if (!trimmed) {
      continue;
    }

    try {
      events.push(JSON.parse(trimmed) as TelemetryEvent);
    } catch {
      invalidLineCount += 1;
    }
  }

  return { events, invalidLineCount };
}

export function replayTelemetryEvents(
  events: TelemetryEvent[],
  invalidLineCount = 0
): ReplayedRuntimeState {
  const state: ReplayedRuntimeState = {
    packets: {},
    approvals: {},
    blockedPackets: [],
    appliedPackets: [],
    eventCount: events.length,
    invalidLineCount
  };

  for (const event of events) {
    if (event.packetId) {
      state.packets[event.packetId] = {
        packetId: event.packetId,
        status: event.status ?? event.eventType,
        risk: event.risk,
        lastEventType: event.eventType,
        lastUpdatedAt: event.ts
      };
    }

    if (event.approvalId) {
      state.approvals[event.approvalId] = {
        approvalId: event.approvalId,
        packetId: event.packetId,
        status: event.status ?? event.eventType,
        risk: event.risk,
        lastUpdatedAt: event.ts
      };
    }

    if (event.eventType === "packet_blocked" && event.packetId) {
      state.blockedPackets.push(event.packetId);
    }

    if (event.eventType === "packet_applied" && event.packetId) {
      state.appliedPackets.push(event.packetId);
    }
  }

  state.blockedPackets = [...new Set(state.blockedPackets)];
  state.appliedPackets = [...new Set(state.appliedPackets)];

  return state;
}

function findLastEventAt(events: TelemetryEvent[]): string | undefined {
  const timestamps = events
    .map((event) => event.ts)
    .filter(Boolean)
    .sort();

  return timestamps[timestamps.length - 1];
}

export function inspectTelemetryEvents(
  events: TelemetryEvent[],
  invalidLineCount = 0
): TelemetryInspection {
  return {
    events,
    replayedState: replayTelemetryEvents(events, invalidLineCount),
    invalidLineCount,
    lastEventAt: findLastEventAt(events)
  };
}

export function inspectTelemetryLedgerContent(
  content: string
): TelemetryInspection {
  const { events, invalidLineCount } = parseTelemetryLedger(content);

  return inspectTelemetryEvents(events, invalidLineCount);
}

export function inspectTelemetryLedgerFile(
  ledgerPath = "telemetry/work_ledger.jsonl"
): TelemetryInspection {
  if (!existsSync(ledgerPath)) {
    return inspectTelemetryEvents([]);
  }

  return inspectTelemetryLedgerContent(readFileSync(ledgerPath, "utf-8"));
}

export function replayTelemetryLedgerFile(
  ledgerPath = "telemetry/work_ledger.jsonl"
): ReplayedRuntimeState {
  if (!existsSync(ledgerPath)) {
    return replayTelemetryEvents([]);
  }

  const content = readFileSync(ledgerPath, "utf-8");
  const { events, invalidLineCount } = parseTelemetryLedger(content);

  return replayTelemetryEvents(events, invalidLineCount);
}
