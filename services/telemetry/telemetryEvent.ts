export type TelemetryEventType =
  | "packet_dispatched"
  | "approval_requested"
  | "approval_decided"
  | "clean_state_checked"
  | "packet_blocked"
  | "packet_applied";

export interface TelemetryEvent {
  eventId: string;
  eventType: TelemetryEventType;
  system: "AI_OS";
  source: string;
  summary: string;
  packetId?: string;
  approvalId?: string;
  status?: string;
  risk?: string;
  ts: string;
  metadata?: Record<string, unknown>;
}

export function createTelemetryEvent(
  eventType: TelemetryEventType,
  source: string,
  summary: string,
  metadata: Partial<TelemetryEvent> = {}
): TelemetryEvent {
  return {
    eventId: `evt_${Date.now()}`,
    eventType,
    system: "AI_OS",
    source,
    summary,
    ts: new Date().toISOString(),
    ...metadata
  };
}

export function serializeTelemetryEvent(event: TelemetryEvent): string {
  return JSON.stringify(event);
}
