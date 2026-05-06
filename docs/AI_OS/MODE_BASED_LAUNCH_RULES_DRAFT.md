# AI_OS Mode-Based Launch Rules Draft

## Purpose

This draft defines future mode-based launch rules without enabling launch automation. It does not approve app launch, browser launch, Codex launch, startup tasks, Task Scheduler changes, broker execution, live trading, or dashboard code changes.

## Future Launch Modes

| Mode | Purpose | Default posture |
|---|---|---|
| Work Mode | AI_OS development, debugging, review, documentation, reporting, and repo maintenance. | Codex may open only after explicit approval. |
| Trading Mode | Future trading dashboard observation and planning. | No live trading, no broker execution, Codex normally closed. |
| Retire / Shutdown Mode | End the work session safely. | Run final status/report checks only after approval. |
| Return to Work Mode | Resume from a checkpoint, report, or known stage. | Verify repo path, git status, and context before tools. |

## Codex Should Open For

- Development.
- Debugging.
- Review.
- Repo maintenance.

## Codex Should Not Open For

- Normal trading dashboard operation.
- Sensitive broker work.
- Unapproved screen recording.
- Credential, key, token, or recovery-key handling.
- Live trading or broker execution.

## Launch Safety Rules

- Select mode before any launch action.
- Show intended action before executing.
- Require human approval for each launch-capable action.
- Do not auto-open apps, browsers, broker pages, or Codex.
- Do not change startup tasks, Task Scheduler, or Windows settings.
- Do not enable live trading or broker execution.

## Known Unresolved Items

- Dashboard data source remains UNKNOWN.
- `progress_percent` formula remains UNKNOWN.
- Trading Mode boundaries need later safety review.
- Codex launch integration method remains UNKNOWN.
- Mode-based launcher could become unsafe if it opens apps or broker tools without explicit approval.
- Current dashboard is still React + Vite and not yet an operator console.
