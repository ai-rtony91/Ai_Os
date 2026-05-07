# AIOS_OPERATOR_PREFERENCES_AND_WORKFLOW_CANONICAL

## PURPOSE
Canonical operator workflow preferences and execution standards for AI_OS development sessions.

## CORE EXECUTION RULES
- Prefer DRY_RUN before APPLY.
- Never assume system state without verification.
- Verify before create, move, rename, overwrite, or delete.
- Human approval required before destructive actions.
- One safe step at a time unless larger batch explicitly approved.
- Prefer consolidated work-orders when operationally safe.
- Preserve governance documents and protected root files.
- Use explicit full paths whenever possible.
- Maintain beginner-safe operational guidance.
- Preserve validation/report evidence after execution.

## APPROVAL FLOW
1. DRY_RUN
2. Human review
3. APPLY approval
4. Verification
5. Git commit
6. Git push
7. Final clean-status verification

## PROTECTED AREAS
- Root governance documents
- Production trading execution logic
- Credential storage locations
- Startup automation
- Telemetry persistence writers
- Broker execution pathways

## OPERATOR PRIORITIES
- Stability over speed
- Deterministic execution
- Auditability
- Recoverability
- Low operational chaos
- Human-readable structure
