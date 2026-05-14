import { appendFileSync, existsSync, mkdirSync } from "fs";
import { dirname } from "path";
import { createTelemetryEvent, serializeTelemetryEvent } from "./telemetryEvent";

const memoryLedger: string[] = [];
const defaultLedgerPath = "telemetry/work_ledger.jsonl";

function ensureLedgerPath(path: string): void {
  const directory = dirname(path);

  if (!existsSync(directory)) {
    mkdirSync(directory, { recursive: true });
  }
}

export function writeTelemetryEvent(
  eventType: Parameters<typeof createTelemetryEvent>[0],
  source: string,
  summary: string,
  metadata = {},
  ledgerPath: string = defaultLedgerPath
): string {
  const event = createTelemetryEvent(eventType, source, summary, metadata);
  const line = serializeTelemetryEvent(event);

  memoryLedger.push(line);

  ensureLedgerPath(ledgerPath);
  appendFileSync(ledgerPath, `${line}\n`, {
    encoding: "utf-8"
  });

  return line;
}

export function listTelemetryEvents(): string[] {
  return [...memoryLedger];
}
