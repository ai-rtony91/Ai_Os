# AIOS Build Intent Router

Schema: `AIOS_BUILD_INTENT_ROUTER.v1`

`automation/orchestration/aios_build_intent_router.py` maps a user goal into an enabled AIOS mode and safe next routing status.

Current routing:

- Forex wording routes to `forex` and `forex-paper-bot`.
- Dashboard wording is reserved until a control-plane reader exists.
- Game wording is future mode, not enabled.
- Unknown wording requires human clarification.
- Broker, live trading, credential, real order, or webhook wording is blocked.

The router is read-only. It does not execute commands, call APIs, launch runtimes, or mutate queues, approvals, or repo files.
