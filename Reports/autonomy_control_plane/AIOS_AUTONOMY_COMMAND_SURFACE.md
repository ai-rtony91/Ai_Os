# AIOS Autonomy Command Surface (DRY-RUN only)

This document lists approved DRY-RUN command entry points for the autonomy lane.

## Safe command surface

- `.\aios.ps1 -Mode autonomy -Goal "..."`
  - Intake a high-level goal and generate a validated proposal.
- `.\aios.ps1 -Mode packet -Path "..."`
  - Process an existing packet through governance checks and dry-run execution.
- `.\aios.ps1 -Mode forex-build -Goal "..."`
  - Route a goal to the Forex Training Lab paper-first builder path.
- `.\aios.ps1 -Mode autonomy-status`
  - Generate autonomy status and blocker report.
- `.\aios.ps1 -Mode autonomy-next`
  - Compute next safe autonomy action.

## Safety constraints

- DRY-RUN mode only.
- No APPLY execution from these commands.
- No live trading integration.
- No merges or force-push operations.
- No broker or secret mutation.

## Approval expectation

- Protected or security-sensitive actions are expected to stop for operator review.
- Human approval remains required for actions outside dry-run scope.
