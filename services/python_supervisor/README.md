# AI_OS Python Supervisor Skeleton

This folder is a standard-library-only skeleton for the future supervised local autonomy runtime.

It is not a daemon, not an MCP server, not a command executor, not a scheduler, and not an API client. It does not start workers, mutate queues, mutate approvals, run subprocesses, call networks, read secrets, trade, deploy, commit, push, or merge.

## Supervisor role

The supervisor will eventually coordinate packet intake, command request previews, worker routing recommendations, approval state reads, telemetry receipts, and recovery summaries.

## Queue role

The queue reader will eventually load approved queue evidence and normalize it into a common shape. It must not move queue items or change queue state in this skeleton.

## Telemetry role

The telemetry writer currently builds in-memory preview events only. Future APPLY work may add append-only writes after schema validation and approval.

## Worker routing role

The worker router chooses a suggested worker from packet metadata and registry evidence. It does not launch Codex, terminals, daemons, or subprocesses.

## Future MCP role

MCP may become the local bridge between ChatGPT and AI_OS state. The first version must be read-only and fail closed.

## Future approval role

Approval integration must read approval state without granting approval. Execution, queue mutation, commits, pushes, PR creation, merges, secrets, cloud actions, and trading remain human-gated.
