# AI_OS Agent Rules

## Scope
This file controls AI behavior for the AI_OS documentation area.

## Locked Architecture
The OMEN desktop is the local command/control foundation for AI_OS.

AI tools must work underneath the system-level AI_OS architecture, not replace it.

Codex integration is part of the AI_OS build path.

GitHub is the source-control layer.

This structure is locked unless a newer development method clearly improves the build.

## Agent Roles
ChatGPT is the architect, planner, documentation controller, and troubleshooting guide.

Codex is the repository/code implementer.

Claude Code is the secondary reviewer, refactor tool, and codebase surgeon.

GitHub is the version-control source of truth.

The user remains the execution authority.

## Operating Rules
Do not overwrite existing files without backup.

Do not generate multiple scripts at once unless explicitly requested.

Use beginner-safe steps.

Use exact paths.

Prefer one action at a time.

Stop after major changes and request confirmation.

Document major architecture changes in CURRENT_STATE, CHECKPOINT, CHANGELOG, and ARCHITECTURE records.

## Current Priority
Connect Codex to the GitHub repo and keep the AI_OS architecture aligned with the OMEN-first local system design.
## Report and Mismatch Rules

- Every APPLY or DRY_RUN action must end with a written report summary.
- If observed evidence conflicts with prior notes, mark the conflict as **MISMATCH**.
- If evidence cannot be verified against files, terminal output, or screenshots, mark it as **INVALID DATA**.
- Do not hide mismatches; log them immediately in `ERROR_LOG.md` and summarize them in the current report.
- Unknown facts must be labeled **UNKNOWN** until verified.
- Report summaries must list: Task, Files inspected, Files changed, Dry-run/APPLY result, Errors, Unknowns, and Next safe action.
