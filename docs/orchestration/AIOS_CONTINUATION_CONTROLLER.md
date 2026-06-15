# AIOS Continuation Controller

Schema: `AIOS_CONTINUATION_CONTROLLER.v1`

`automation/orchestration/aios_continuation_controller.py` combines resume state, control-plane status, bounded executor handoff, bounded executor readiness, and the mode registry into one continuation decision.

Controller outcomes:

- `execute_existing_tool_after_human_approval` when the productive executor already supports the ready action.
- `build_executor_support_packet` when a ready handoff exists but the productive executor does not support the action yet.
- `human_review` when the route is stopped, mode is unsupported, or readiness is incomplete.
- `sos_stop` when a safety blocker is present.

Current expected Forex behavior:

- `build_forex_risk_controls` is supported by the productive executor.
- `build_forex_paper_execution_simulator` requires a Codex packet to add executor support.

The controller does not write files, launch Codex, execute commands, call APIs, or mutate repo state.
