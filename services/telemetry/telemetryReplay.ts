import { existsSync, readFileSync } from "fs";
import { statSync } from "fs";
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
  ledger: {
    path?: string;
    exists: boolean;
    sizeBytes: number;
    modifiedAt?: string;
    lineCount: number;
    validLineCount: number;
    invalidLineCount: number;
    empty: boolean;
  };
}

export function parseTelemetryLedger(content: string): {
  events: TelemetryEvent[];
  invalidLineCount: number;
  lineCount: number;
} {
  const events: TelemetryEvent[] = [];
  let invalidLineCount = 0;
  let lineCount = 0;

  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();

    if (!trimmed) {
      continue;
    }

    lineCount += 1;

    try {
      events.push(JSON.parse(trimmed) as TelemetryEvent);
    } catch {
      invalidLineCount += 1;
    }
  }

  return { events, invalidLineCount, lineCount };
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
  invalidLineCount = 0,
  ledger: Partial<TelemetryInspection["ledger"]> = {}
): TelemetryInspection {
  const lineCount = ledger.lineCount ?? events.length + invalidLineCount;

  return {
    events,
    replayedState: replayTelemetryEvents(events, invalidLineCount),
    invalidLineCount,
    lastEventAt: findLastEventAt(events),
    ledger: {
      exists: ledger.exists ?? true,
      sizeBytes: ledger.sizeBytes ?? 0,
      lineCount,
      validLineCount: events.length,
      invalidLineCount,
      empty: lineCount === 0,
      path: ledger.path,
      modifiedAt: ledger.modifiedAt
    }
  };
}

export function inspectTelemetryLedgerContent(
  content: string
): TelemetryInspection {
  const { events, invalidLineCount, lineCount } = parseTelemetryLedger(content);

  return inspectTelemetryEvents(events, invalidLineCount, {
    exists: true,
    sizeBytes: Buffer.byteLength(content, "utf-8"),
    lineCount
  });
}

export function inspectTelemetryLedgerFile(
  ledgerPath = "telemetry/work_ledger.jsonl"
): TelemetryInspection {
  if (!existsSync(ledgerPath)) {
    return inspectTelemetryEvents([], 0, {
      path: ledgerPath,
      exists: false,
      sizeBytes: 0,
      lineCount: 0
    });
  }

  const stats = statSync(ledgerPath);
  const inspection = inspectTelemetryLedgerContent(readFileSync(ledgerPath, "utf-8"));

  return {
    ...inspection,
    ledger: {
      ...inspection.ledger,
      path: ledgerPath,
      exists: true,
      sizeBytes: stats.size,
      modifiedAt: stats.mtime.toISOString()
    }
  };
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
