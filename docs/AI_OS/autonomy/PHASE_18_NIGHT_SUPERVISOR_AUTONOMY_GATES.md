# Phase 18 Night Supervisor Autonomy Gates

## Gates

1. Dispatcher preview gate: route must be `NIGHT_SUPERVISOR_PREVIEW`, `PREVIEW_ONLY`, and `RUNTIME_START_BLOCKED`.
2. Runtime context gate: expected worktree, actual cwd, Python `Path.cwd()`, and git root must match.
3. Safety gate: locks clear, dirty tree clean, forbidden paths clean.
4. Human approval gate: runtime, Paper SOS resume, controlled run, longer run, and overnight candidate each require separate approval.
5. Red-team review gate: prompt injection, secret risk, OpenAI call risk, trading/broker/Pi risk, and runtime drift must be reviewed.
6. Stop/park gate: stop point and park mechanism must be explicit before any run.

Any failed or uncertain gate fails closed.

