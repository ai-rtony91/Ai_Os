export type TelemetryEventShape = "legacy" | "canonical" | "mixed" | "unknown";

export interface TelemetryEventValidationResult {
  isValid: boolean;
  shape: TelemetryEventShape;
  warnings: string[];
  errors: string[];
  missingCanonicalFields: string[];
}

const legacyFields = [
  "eventId",
  "eventType",
  "status",
  "ts",
  "source",
  "system",
  "summary",
  "packetId",
  "approvalId",
  "risk"
] as const;

const requiredLegacyCoreFields = [
  "eventId",
  "eventType",
  "ts",
  "source",
  "system",
  "summary"
] as const;

const canonicalFields = [
  "event_id",
  "timestamp_utc",
  "event_type",
  "source",
  "actor",
  "lane",
  "repo_path",
  "branch",
  "mode",
  "authority_token",
  "authority_note",
  "input_reference",
  "output_reference",
  "result",
  "risk_level",
  "next_safe_action",
  "validation_status"
] as const;

const requiredCanonicalCoreFields = [
  "event_id",
  "timestamp_utc",
  "event_type",
  "source",
  "result",
  "validation_status"
] as const;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasAnyField(record: Record<string, unknown>, fields: readonly string[]): boolean {
  return fields.some((field) => Object.prototype.hasOwnProperty.call(record, field));
}

function hasString(record: Record<string, unknown>, field: string): boolean {
  return typeof record[field] === "string" && record[field].trim().length > 0;
}

function isIsoTimestamp(value: unknown): boolean {
  return typeof value === "string" && value.trim().length > 0 && !Number.isNaN(Date.parse(value));
}

function getMissingFields(record: Record<string, unknown>, fields: readonly string[]): string[] {
  return fields.filter((field) => !Object.prototype.hasOwnProperty.call(record, field));
}

function detectShape(record: Record<string, unknown>): TelemetryEventShape {
  const hasLegacy = hasAnyField(record, legacyFields);
  const hasCanonical = hasAnyField(record, canonicalFields);

  if (hasLegacy && hasCanonical) {
    return "mixed";
  }

  if (hasCanonical) {
    return "canonical";
  }

  if (hasLegacy) {
    return "legacy";
  }

  return "unknown";
}

function addFieldTypeErrors(
  record: Record<string, unknown>,
  fields: readonly string[],
  errors: string[]
): void {
  for (const field of fields) {
    if (Object.prototype.hasOwnProperty.call(record, field) && !hasString(record, field)) {
      errors.push(`${field} must be a non-empty string when present.`);
    }
  }
}

export function validateTelemetryEvent(input: unknown): TelemetryEventValidationResult {
  const warnings: string[] = [];
  const errors: string[] = [];

  if (!isRecord(input)) {
    return {
      isValid: false,
      shape: "unknown",
      warnings,
      errors: ["Telemetry event must be a JSON object."],
      missingCanonicalFields: [...canonicalFields]
    };
  }

  const shape = detectShape(input);
  const missingCanonicalFields = getMissingFields(input, canonicalFields);

  if (shape === "unknown") {
    errors.push("Telemetry event does not match legacy camelCase or canonical snake_case shape.");
  }

  if (shape === "legacy" || shape === "mixed") {
    const missingLegacyCoreFields = getMissingFields(input, requiredLegacyCoreFields);

    if (missingLegacyCoreFields.length > 0) {
      errors.push(`Legacy telemetry event is missing required field(s): ${missingLegacyCoreFields.join(", ")}.`);
    }

    addFieldTypeErrors(input, requiredLegacyCoreFields, errors);

    if (Object.prototype.hasOwnProperty.call(input, "ts") && !isIsoTimestamp(input.ts)) {
      errors.push("Legacy telemetry ts must be an ISO 8601 timestamp.");
    }

    if (Object.prototype.hasOwnProperty.call(input, "system") && input.system !== "AI_OS") {
      errors.push("Legacy telemetry system must be AI_OS.");
    }

    if (missingCanonicalFields.length > 0) {
      warnings.push("Event uses legacy camelCase telemetry fields and is missing canonical snake_case fields.");
    }
  }

  if (shape === "canonical" || shape === "mixed") {
    const missingCanonicalCoreFields = getMissingFields(input, requiredCanonicalCoreFields);

    if (missingCanonicalCoreFields.length > 0) {
      errors.push(`Canonical telemetry event is missing required core field(s): ${missingCanonicalCoreFields.join(", ")}.`);
    }

    addFieldTypeErrors(input, requiredCanonicalCoreFields, errors);

    if (
      Object.prototype.hasOwnProperty.call(input, "timestamp_utc") &&
      !isIsoTimestamp(input.timestamp_utc)
    ) {
      errors.push("Canonical telemetry timestamp_utc must be an ISO 8601 timestamp.");
    }

    if (missingCanonicalFields.length > 0) {
      warnings.push(`Canonical telemetry event is missing target field(s): ${missingCanonicalFields.join(", ")}.`);
    }
  }

  if (shape === "mixed") {
    warnings.push("Event contains both legacy camelCase and canonical snake_case telemetry fields.");
  }

  return {
    isValid: errors.length === 0,
    shape,
    warnings,
    errors,
    missingCanonicalFields
  };
}

export function summarizeTelemetryValidation(
  results: TelemetryEventValidationResult[]
): Pick<TelemetryEventValidationResult, "isValid" | "warnings" | "errors" | "missingCanonicalFields"> {
  const warnings = results.flatMap((result) => result.warnings);
  const errors = results.flatMap((result) => result.errors);
  const missingCanonicalFields = [...new Set(results.flatMap((result) => result.missingCanonicalFields))];

  return {
    isValid: errors.length === 0,
    warnings,
    errors,
    missingCanonicalFields
  };
}
