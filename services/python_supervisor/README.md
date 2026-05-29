# AI_OS Python Supervisor Skeleton

This folder is a standard-library-only skeleton for the future supervised local autonomy runtime.

It is not a daemon, not an MCP server, not a command executor, not a scheduler, and not an API client. It does not start workers, mutate queues, mutate approvals, run subprocesses, call networks, read secrets, trade, deploy, commit, push, or merge.

## Supervisor role

The supervisor will eventually coordinate packet intake, command request previews, worker routing recommendations, approval state reads, telemetry receipts, and recovery summaries.

## Queue role

The queue reader will eventually load approved queue evidence and normalize it into a common shape. It must not move queue items or change queue state in this skeleton.

## Telemetry role

The telemetry writer currently builds in-memory preview events only. Future APPLY work may add append-only writes after schema validation and approval.

## Contract normalizer role

The contract normalizer reads existing DRY_RUN/report JSON evidence and emits one normalized `orchestration_result_contract`-compatible object. It is read-only and report-only. It must not write files, start subprocesses, mutate packets, mutate approvals, launch workers, run schedulers, stage files, commit, push, merge, or control runtime behavior.

## Worker routing role

The worker router chooses a suggested worker from packet metadata and registry evidence. It does not launch Codex, terminals, daemons, or subprocesses.

## Future MCP role

MCP may become the local bridge between ChatGPT and AI_OS state. The first version must be read-only and fail closed.

## Future approval role

Approval integration must read approval state without granting approval. Execution, queue mutation, commits, pushes, PR creation, merges, secrets, cloud actions, and trading remain human-gated.

## Effector layer (downstream of the Codex V2 spine)

The Codex V2 spine (`automation/orchestration/supervisor_engine_v2.py` with `approval_officer`, `lock_manager`, `packet_dispatcher`) is the canonical, read-only/preview Night Supervisor. It owns queue scanning, routing, lock evidence, approval evidence, dispatch preview, and telemetry preview, and emits `routing_contracts`.

The effector layer sits strictly AFTER that spine and is the only part that can invoke the PowerShell hand-scripts. It never re-reads the approval inbox or re-scans locks; it trusts the contract verdict. See `docs/architecture/AI_OS_NIGHT_SUPERVISOR_AUTONOMY_WIRING.md`.

- `effector_intent.py` — builds blocked-by-default effector intents from approved `routing_contracts`.
- `effector_dispatcher.py` — the only module that may invoke an effector, and only when all six gates pass at once (kill switch clear, effector actionable, capability allowlisted, execution enabled, env armed, contract cleared).
- `effector_stage.py` — a single-pass stage (not a daemon, not a second supervisor) that runs the V2 spine then the effector dispatch.

Default state on a fresh checkout is fully blocked: empty capability allowlist, execution disabled. The kill switch `AIOS_NIGHT_SUPERVISOR_DISABLE=1` overrides everything. Commit/push/merge are intentionally NOT effectors and remain with the human-invoked operator loop.
