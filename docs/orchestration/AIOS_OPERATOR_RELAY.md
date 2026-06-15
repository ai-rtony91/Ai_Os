# AIOS Operator Relay

`aios_operator_relay.py` defines the file-contract bridge between ChatGPT-style
planning and Codex-style execution packets without using API calls.

It accepts resume state, CLI result ingest output, and an optional next build
plan, then emits `AIOS_OPERATOR_RELAY.v1` with relay status, human-action
requirements, Codex prompt readiness, a pasteback summary, next safe action, and
safety flags.

Persistence is explicit only and bounded to `Reports/aios_relay/`. The relay
does not launch Codex, dispatch workers, mutate queues or approvals, activate
schedulers or daemons, touch broker/live trading, stage, commit, push, or merge.
