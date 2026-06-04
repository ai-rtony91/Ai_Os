# Phase 17 Safety Rules

Status: DRY_RUN safety rules

## Hard Blocks

- No real OpenAI call.
- No API key.
- No `.env` creation or read.
- No package install.
- No network.
- No runtime autonomy.
- No real approval inbox write.
- No telemetry runtime write.
- No Night Supervisor modification.
- No broker, OANDA, or live trading.
- No real orders.
- No webhook execution.
- No commit, push, merge, rebase, or force push unless separately approved.

## Lane Rules

- Use one APPLY lane at a time.
- Start from a clean repo precheck.
- Verify user directory, `pwd`, repo root, branch, worktree, and intended path before runtime-sensitive work.
- Preview output is evidence only.
- Human approval remains required for APPLY and protected actions.

## Night Supervisor Rule

Phase 17 packets must not touch:

- `telemetry/night_supervisor/`
- `automation/orchestration/night_supervisor/`
- `automation/orchestration/locks/`
- `control/`

## Paper SOS Failure Lesson

Paper SOS failed because Python `Path.cwd()` resolved to `C:\Dev\Ai.Os` instead of `C:\Dev\aios-paper-sos-runtime-closeout`.

Future runtime packets must verify before execution:

- `USERPROFILE`
- `pwd`
- `git rev-parse --show-toplevel`
- expected worktree
- Python `Path.cwd()`
- profile path exists

If any value does not match the packet, stop before execution.
