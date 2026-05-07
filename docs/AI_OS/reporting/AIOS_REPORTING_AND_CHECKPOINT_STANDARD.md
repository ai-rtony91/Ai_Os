# AIOS_REPORTING_AND_CHECKPOINT_STANDARD

## PURPOSE
Defines standard reporting and checkpoint methodology for AI_OS.

## REQUIRED REPORT ELEMENTS
- Date
- Stage
- Status
- Actions taken
- Files changed
- Validation results
- Errors encountered
- Risk observations
- Next steps
- Progress percentage

## REPORT TYPES
- DAILY_REPORT
- CHECKPOINT
- HEALTH_REPORT
- VALIDATOR_REPORT
- INCIDENT_REPORT
- AAR

## REPORTING RULES
- Preserve chronological evidence.
- Prefer human-readable summaries.
- Avoid oversized spreadsheet cells.
- Maintain deterministic formatting.
- Preserve DRY_RUN vs APPLY distinction.

## REQUIRED VALIDATION BEFORE CHECKPOINT
- Git status verification
- File existence verification
- Validator completion
- Push verification
- Final clean-state verification

## FUTURE TELEMETRY GOALS
- Automated metrics
- Session duration
- Progress tracking
- Character-count telemetry
- Report aggregation
- Snapshot indexing

## CURRENT RESTRICTION
Telemetry persistence remains non-production and approval-gated.
