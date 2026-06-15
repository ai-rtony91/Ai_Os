# AIOS Self-Build Core Status Reader

`automation/orchestration/aios_self_build_core_status_reader.py` is a pure reader/evaluator for AIOS self-build status contracts.

It summarizes dictionaries shaped like `wake_continue`, `self_build_loop_readiness`, `self_build_dry_run_driver`, queue, selector, Codex packet preview, local apply preview, stop report, and SOS policy outputs into:

```text
AIOS_SELF_BUILD_CORE_STATUS_READER.v1
```

The reader reports the current goal and mode, wake validation status, tests passed, readiness state, selected queue item, packet readiness, local apply preview readiness, SOS state, protected-action block map, preview continuation state, and the next safe action.

## v0 Rules

- `can_apply_without_human` is always `false`.
- `can_continue_preview` can be `true` only for a selected bounded `DRY_RUN` queue item.
- `review_required` is not treated as a code failure.
- Windows sandbox `CreateProcessAsUserW failed: 1312` is reported as a runner blocker, not an implementation failure.
- Protected action attempts are unsafe and require stopping.

## Safety

The reader does not write files, execute commands, launch Codex, call APIs, mutate queues or approvals, activate schedulers or daemons, use broker access, use credentials, place orders, send webhooks, commit, push, merge, or perform destructive cleanup.
