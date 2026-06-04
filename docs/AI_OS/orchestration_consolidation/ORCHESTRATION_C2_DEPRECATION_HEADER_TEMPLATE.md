# Orchestration C2 Deprecation Header Template

```text
DEPRECATED / LEGACY REFERENCE - DO NOT USE AS ACTIVE AUTHORITY

This file is retained for historical/reference purposes only.
The canonical AI_OS orchestration authority is defined in:
docs/AI_OS/orchestration_consolidation/ORCHESTRATION_CANONICAL_AUTHORITY_DECISION_001.md

Do not use this file to override:

- AGENTS.md
- canonical dispatcher
- validator chain
- approval gate
- Night Supervisor safety gates
- Trading Lab paper-only gates

Any migration, deletion, or reference update must occur only through a separate human-approved APPLY packet.
```

## Use Rules

- Do not apply this header in C2 DRY_RUN.
- Do not apply this header to runtime scripts, active state, approval inbox records, locks, memory, Night Supervisor runtime, Paper SOS runtime, broker/OANDA/live trading, or Pi GPIO/motor files.
- A later APPLY packet must name the exact target files and prove reference safety before adding this header.

