# Agent Operating Rules

Major Agents build the main system.
Minor Agents only unblock gaps.
Minor Agents do not redesign.
Major Agents do not stop for small gaps.
All gaps must be logged to `GLOBAL_GAP_LOG.json`.
All tasks must be tracked in `GLOBAL_TASK_QUEUE.json`.
All results must be summarized in `CODEX_SUMMARY.md`.

The user should not need to paste huge terminal dumps unless there is an error.

Blocked: broker routing, OANDA, API keys, secrets, real webhooks, real orders, live execution, installs, commits, and pushes.