# 05_RULES_AND_GUARDRAILS

## Core Safety Rules
- No file deletion, renaming, or moving.
- No secret/key/credential edits.
- No protected system reconfiguration.
- No broker orders or live-trading enablement.

## Documentation Discipline
- Use exact paths.
- Keep actions bounded and auditable.
- Mark unknown facts as `UNKNOWN`.
- Mark conflicting evidence as `INVALID DATA`.

## Workflow Discipline
- Prefer one major action at a time.
- Verify outputs before proceeding.
- Avoid redundant regeneration of unchanged content.
- Keep AI_OS system docs separate from trading execution logic unless explicitly justified.

## Quality Gates
Before completion:
1. Scope check passed
2. Architecture lock respected
3. No protected actions performed
4. Report format completed
