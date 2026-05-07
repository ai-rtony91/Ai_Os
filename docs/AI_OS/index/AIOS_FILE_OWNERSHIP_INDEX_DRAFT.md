# AI_OS File Ownership Index Draft

## Purpose

This draft defines ownership categories for AI_OS files and future outputs. It is a planning index only and does not override protected root governance files.

No protected-file edits are allowed without explicit human approval.

## Ownership Fields

Each ownership entry uses these fields:

- `path_pattern`: File or folder pattern covered by the entry.
- `owner_layer`: Governance, planning, validation, report, telemetry, dashboard, or operations layer responsible for the file type.
- `allowed_change_mode`: DRY_RUN only, approval-gated APPLY, or future approval-gated output.
- `approval_required`: Whether human approval is required before creation or modification.
- `risk_level`: LOW, MEDIUM, HIGH, or BLOCKED.
- `notes`: Boundary and handling notes.

## Ownership Categories

| path_pattern | owner_layer | allowed_change_mode | approval_required | risk_level | notes |
| --- | --- | --- | --- | --- | --- |
| `README.md`, `WHITEPAPER.md`, `ARCHITECTURE.md`, `RISK_POLICY.md`, `DEPLOYMENT.md`, `CHANGELOG.md`, `AGENTS.md`, `CLAUDE.md`, `TODO.md`, `REQUIREMENTS.md`, `SOURCE_LOG.md`, `ERROR_LOG.md`, `HALLUCINATION_LOG.md`, `DAILY_REPORT.md`, `AAR.md` | root governance files | Protected; explicit approval only | YES | HIGH | Authoritative governance and reporting files. Do not edit without explicit approval and backup rules where applicable. |
| `docs/AI_OS/**/*.md`, `docs/AI_OS/**/*.txt`, `docs/AI_OS/**/*.json` | docs/AI_OS planning files | DRY_RUN-governed creation or approval-gated APPLY | YES | MEDIUM | Planning and draft architecture files. Must not override protected root authority. |
| `automation/**/*.DRY_RUN.ps1`, `automation/**/*.DRY_RUN.py` | automation DRY_RUN validators | DRY_RUN-governed creation; must not write files | YES | MEDIUM | Validators may inspect files, parse JSON, check git status, and print PASS/FAIL summaries. |
| `Reports/health/**/*.txt`, `Reports/health/**/*.md`, `Reports/health/**/*.json` | Reports/health checkpoint reports | DRY_RUN-governed creation or approval-gated APPLY | YES | LOW | Checkpoint reports must summarize evidence and safety boundaries. |
| `Reports/daily/**/*.txt`, `Reports/daily/**/*.md`, `Reports/daily/**/*.json` | Reports/daily progress outputs | Approval-gated output | YES | MEDIUM | Daily progress outputs must not hide errors or mismatches. |
| `telemetry/**/*` | future telemetry outputs | Future approval-gated output only | YES | HIGH | No telemetry writer is active. Future telemetry must avoid secrets, broker data, and private user data unless explicitly approved under separate governance. |
| `dashboard/**/*`, `ui/**/*`, `web/**/*` | future dashboard outputs | Future approval-gated output only | YES | HIGH | No dashboard writer is active. Future dashboard outputs require static preview approval before any production behavior. |

## Protected File Rule

Protected root files remain authoritative. Edits to protected root files require explicit human approval and must follow the project backup and reporting rules. This ownership draft does not grant permission to edit those files.
