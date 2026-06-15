# AIOS Self-Build Run Summary View

`automation/orchestration/aios_self_build_run_summary_view.py` converts AIOS self-build driver or core-status JSON into a compact operator-facing summary.

The output schema is:

```text
AIOS_SELF_BUILD_RUN_SUMMARY_VIEW.v1
```

It reports the headline, current goal, selected next action, readiness state, test count, packet readiness, local apply preview readiness, preview continuation state, SOS state, stop reason, next safe action, protected-action summary, and safety flags.

## v0 Rules

- The view is pure and read-only.
- `can_apply_without_human` is always `false`.
- `review_required` is not a code failure.
- Windows sandbox `CreateProcessAsUserW failed: 1312` is a runner blocker, not an implementation failure.
- Protected actions remain blocked.

## Safety

The view does not execute commands, write files, access the network, launch Codex, call APIs, mutate queues or approvals, activate schedulers or daemons, dispatch workers, stage, commit, push, merge, use broker access, use credentials, place orders, send webhooks, or perform destructive cleanup.
