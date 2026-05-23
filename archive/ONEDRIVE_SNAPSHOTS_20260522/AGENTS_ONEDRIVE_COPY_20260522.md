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

### Mismatch Reports

Create a new Markdown file for each major mismatch incident.

Do not append every mismatch into one file unless it is the same unresolved incident.

Same issue still being worked = continue the same file.

New mismatch on a different day, repo, folder, branch, source, or cause = create a new `.md` file.

### Mismatch Report Naming Format

Use this format:

`Reports/daily/CODEX_REPO_MISMATCH_YYYY-MM-DD_SHORT_TOPIC.md`

Examples:

`Reports/daily/CODEX_REPO_MISMATCH_2026-05-04_OMEN_ONEDRIVE_VS_GITHUB.md`

`Reports/daily/CODEX_REPO_MISMATCH_2026-05-05_BRANCH_CONTEXT_ERROR.md`

`Reports/daily/CODEX_REPO_MISMATCH_2026-05-06_CODEX_STALE_SNAPSHOT.md`

### Current Active Mismatch File

`Reports/daily/CODEX_REPO_MISMATCH_2026-05-04.md` documents the May 4 issue where Codex/GitHub did not match the OMEN OneDrive project.

Keep that file for that incident only.

### Report Storage Rule

Curated mismatch `.md` files stay tracked in GitHub.

Raw inventory `.txt` files stay OneDrive archive-only unless summarized into Markdown.

Do not paste mismatch report text into inventory files.

Mismatch content belongs only in a mismatch `.md` file.