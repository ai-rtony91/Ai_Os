# AI_OS Automation Helper Layer Plan Draft

## Purpose

This draft describes the proposed automation-helper layer only. It does not create helper scripts, edit existing scripts, enable startup tasks, implement telemetry automation, or approve cleanup.

## Proposed Helper Layer

The helper layer should reduce repeated manual checks while keeping AI_OS in a DRY_RUN-first workflow. Helpers should be small, explicit, and scoped to one safe task at a time.

## Proposed Helpers

| Helper | Purpose | Initial allowed mode |
|---|---|---|
| Repo clean-status checker | Confirm the repo status before work begins. | DRY_RUN only |
| Daily progress report generator | Draft a dated work summary from approved inputs. | DRY_RUN only |
| Telemetry session row generator | Produce a draft telemetry row without editing live metrics. | DRY_RUN only |
| Codex repo-path helper | Confirm the correct AI_OS repo path before Codex work. | DRY_RUN only |
| Morning Brief planner | Plan the morning workflow without launching apps or changing startup tasks. | DRY_RUN only |
| Folder-role audit helper | Check folder-purpose notes and report missing notes. | DRY_RUN only |
| Duplicate-candidate scan helper | Produce read-only duplicate-candidate findings. | DRY_RUN only |
| Final clean-stop checker | Confirm final `git status --short --branch` before stopping work. | DRY_RUN only |

## Current Limits

- No helper scripts are approved by this draft.
- Existing automation scripts must not be edited yet.
- `Reports\DAILY_METRICS.csv` must not be edited or migrated yet.
- Startup task enablement is not approved.
- Screen recording automation is not approved.
- Broker/trading automation is not approved.
- Secret/key handling automation is not approved.

## Next Review Needed

Before implementation, each helper needs its own DRY_RUN checklist, target path collision check, safety scope, and human approval.
