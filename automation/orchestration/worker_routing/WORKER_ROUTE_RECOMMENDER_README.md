# AI_OS Worker Route Recommender

This folder contains the first repo-owned supervisor-to-worker routing bridge.

The supervisor does not chat directly with Codex, Claude, validators, or the Human Owner yet. It routes by producing machine-readable recommendations that another approved lane can review.

## Routing Model

- East builds.
- West reviews.
- Validators verify.
- Human approves.

`services/python_supervisor/worker_route_recommender.py` reads git status and scans packet text from:

- `automation/orchestration/work_packets/`
- `work_packets/`

It recommends one of:

- `CODEX_EAST` for build, APPLY, code, script, implementation, or test work.
- `CLAUDE_WEST` for review, architecture, risk, design, critique, or strategy.
- `VALIDATOR` for validation, parse, test, check, or audit work.
- `HUMAN_OWNER` for approval, merge, push, secrets, broker, live trading, destructive actions, or uncertain routes.

## Safety

The recommender is read-only by default and emits JSON to stdout.

It does not:

- execute packets
- launch workers
- call Codex
- call Claude
- mutate queues
- edit worker packets
- approve work
- commit
- push
- merge
- touch broker, OANDA, API-key, live-order, or trading paths

If `--write-report` is explicitly passed, it writes only:

```text
automation/orchestration/worker_routing/latest_worker_route_recommendation.json
```

## Why This Matters

This is the first bridge toward AI_OS autonomy because it gives the supervisor a structured way to say who should handle the next task without pretending that routing is execution.

The output is evidence for the operator and future orchestration layers. It is not approval, not a worker launch, and not a command executor.
