# AI_OS Autonomy Speed Routing Rules

Purpose:
Define how AI_OS chooses fast, safe routing without weakening governance.

## Routing Order

1. Deterministic script or schema check.
2. Existing validator.
3. Structured fixture or cached report.
4. Smaller model for low-risk bounded wording or classification.
5. Stronger model for planner, judge, safety, or profitability reasoning.
6. Human approval for protected actions.

## Parallelism Rule

Parallelize only when work is:

- read-only
- DRY_RUN
- non-overlapping by file path
- not touching runtime state
- not touching secrets
- not touching broker/OANDA/live trading
- not touching Pi GPIO/motor

APPLY remains one-at-a-time.

## Progress Rule

User-facing progress must show:

- current lane
- current blocker, if any
- next safe action

## LLM Use Rule

Do not default to an LLM. Use deterministic scripts before LLMs for mechanical checks such as JSON parsing, path checks, git status, schema field checks, and forbidden-content scans.

## Priority Processing

Priority processing is a future speed lane for high-value user-facing latency-sensitive requests. It is blocked for evals, batch jobs, ETL, nightly reports, telemetry bulk work, and routine background processing.

Priority processing cannot override:

- human approval
- validator gates
- Trading Lab default paper/simulation safety
- broker/OANDA/live trading blocks
- Pi GPIO/motor blocks
- Night Supervisor runtime boundaries
- clean-state verification

