# AI_OS Active Supervision

Phase 16.56-70 adds a read-only supervisor dashboard for operator routing.

The dashboard watches repo state, GitHub state when available, validation needs, blocked paths, and lane recommendations. It does not change files and does not automate commits, pushes, merges, issues, PRs, workers, scheduled tasks, startup tasks, broker work, OANDA work, API keys, webhooks, real orders, or live trading.

## Files

- `Show-AiOsSupervisorDashboard.ps1` prints the active supervision dashboard.
- `aios_supervision_rules.example.json` stores example routing and risk rules.

## Lanes

- `COMMAND DECK`: Git, GitHub CLI, issues, PRs, approvals, merge decisions, and blocked-state review.
- `BUILD ENGINE`: Codex work lane after an APPLY prompt is explicitly approved.
- `VALIDATION DECK`: git diff checks, JSON validation, PowerShell parse checks, and repo clean checks.

## Risk Levels

- `SAFE`: no blocking local condition is visible.
- `WATCH`: local-only GitHub mode or minor review item is visible.
- `WARNING`: validation or approval work is needed.
- `BLOCKED`: protected or unsafe work is visible and operator review is required.

## Run

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1
```

## Safety

This dashboard is for visibility and routing only. The operator remains responsible for approving commits, pushes, merges, branch work, issue work, PR work, and any future automation changes.
