# AI_OS Full Project Refactor Recommendations Draft

## Purpose

This draft lists future refactor recommendations from the Stage 47 full project audit. It does not modify files.

## Must-Fix

- No must-fix item blocks continued DRY_RUN planning if the repo is clean and protected-file checks remain clean.
- Before production dashboard UI, create a formal security threat model.
- Before APPLY writers, create shared schema validation and protected-file guard utilities.
- Before telemetry persistence, create a telemetry schema, retention policy, and approval gate.
- Before any broker or trading integration, create a separate trading-system risk review, paper-trading validation, broker sandbox validation, rollback plan, and audit logging plan.

## Should-Fix

- Create a documentation index for dashboard, telemetry, reporting, writer, approval, trading, and audit areas.
- Standardize validator output sections and helper logic.
- Centralize protected-path lists to avoid drift.
- Create checkpoint mismatch handling rules for prompts that reference older commits.
- Add stronger JSON schema validation for fixture files.

## Nice-To-Have

- Create a naming glossary for Stage files and suffixes.
- Create a dashboard roadmap visual map.
- Add a machine-readable registry of validators and prerequisites.
- Add a future UI dependency selection checklist.
- Add demo evidence checklist fixtures before any screenshot or video capture.

## Continue-Without-Change

- Continue using DRY_RUN-first architecture.
- Continue blocking production dashboard outputs until separate approval.
- Continue preserving protected root files and protected reports.
- Continue keeping trading execution, broker routing, credential access, report writing, telemetry writing, startup automation, screenshots, videos, and hidden background services blocked.
- Continue separating AI_OS platform planning from future trading-system execution.
