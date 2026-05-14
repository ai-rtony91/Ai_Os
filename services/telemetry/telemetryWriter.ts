import { createTelemetryEvent, serializeTelemetryEvent } from "./telemetryEvent";

const memoryLedger: string[] = [];

export function writeTelemetryEvent(
  eventType: Parameters<typeof createTelemetryEvent>[0],
  source: string,
  summary: string,
  metadata = {}
): string {
  const event = createTelemetryEvent(eventType, source, summary, metadata);
  const line = serializeTelemetryEvent(event);

  memoryLedger.push(line);
  return line;
}

export function listTelemetryEvents(): string[] {
  return [...memoryLedger];
}
