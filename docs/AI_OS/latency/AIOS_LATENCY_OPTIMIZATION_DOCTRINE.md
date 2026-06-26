# AI_OS Latency Optimization Doctrine

Purpose:
Define how AI_OS optimizes latency across autonomy, packet generation, Codex validation, Night Supervisor previews, future OpenAI Responses adapter work, Trading Lab, Pi car voice, and operator experience.

## North Star

Trading Lab latency remains priority #1 because trusted/proven profitability depends on timely signal handling, clear evidence, and paper/simulation validation before any future escalation.

Trusted/proven profitability outranks feature expansion.

## Core Rules

- Live trading remains blocked.
- Use deterministic scripts before LLMs for mechanical checks.
- Use smaller models only for low-risk bounded tasks.
- Use stronger models for safety, judge, planner, and profitability reasoning.
- Parallelize only read-only or DRY_RUN work with non-overlapping files.
- APPLY remains one-at-a-time.
- User-facing progress must show current lane, blocker, and next safe action.
- Priority processing is reserved for future high-value user-facing latency-sensitive requests only.
- Priority processing must not be used for evals, batch jobs, ETL, nightly reports, telemetry bulk work, or routine background processing.
- Priority processing must not bypass approvals, validators, Trading Lab default paper/simulation safety, broker/OANDA blocks, live-trading blocks, Pi GPIO/motor blocks, or clean-state checks.

## AI_OS Latency Targets

AI_OS latency optimization should reduce:

- manual copy/paste relay time
- repeated status checking
- unnecessary LLM calls
- oversized prompts
- slow validation loops
- unclear blocker recovery
- voice response delay in future Pi car sessions

## Safety Boundary

Latency optimization must not bypass:

- allowed paths
- forbidden paths
- validator chains
- approval gates
- protected main PR lane
- Trading Lab default paper/simulation or approved demo-review status
- no broker/OANDA/live trading rule
- no Pi GPIO/motor rule
- no Night Supervisor runtime modification rule

