# AIOS Self-Build APPLY Approval Gate

`automation/orchestration/aios_self_build_apply_approval_gate.py` is a pure evaluator for local allowlisted APPLY approval.

It returns:

```text
AIOS_SELF_BUILD_APPLY_APPROVAL_GATE.v1
```

The gate compares a selected self-build queue item with an approval request and reports whether a local allowlisted APPLY may be prepared.

## v0 Rules

- `can_apply_without_human` is always `false`.
- `local_allowlisted_apply_allowed` can be `true` only when Anthony Meza approval is present, the approval token is present, the requested action matches the selected queue action, requested write paths stay inside the queue item's `allowed_paths`, validators exist, and no protected action is requested.
- Missing approval returns `review_required`.
- Protected action requests return `rejected`.
- Paths outside the selected queue item's allowed scope return `rejected`.
- Windows sandbox `CreateProcessAsUserW failed: 1312` is a runner blocker, not an implementation failure.

## Safety

The gate does not execute commands, write files, access the network, launch Codex, call APIs, mutate queues or approvals, activate schedulers or daemons, dispatch workers, stage, commit, push, merge, use broker access, use credentials, place orders, send webhooks, or perform destructive cleanup.
