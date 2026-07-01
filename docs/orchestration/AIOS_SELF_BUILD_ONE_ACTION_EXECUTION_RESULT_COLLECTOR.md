# AIOS Self-Build One-Action Execution Result Collector

`aios_self_build_one_action_execution_result_collector.py` is a pure result consumer for the self-build-core one-action APPLY chain.

Schema:

```text
AIOS_SELF_BUILD_ONE_ACTION_EXECUTION_RESULT_COLLECTOR.v1
```

The collector consumes:

- selected self-build queue item
- APPLY approval gate output
- local APPLY executor bridge output
- single-action executor output
- one-action execution controller output
- one-action APPLY runner output
- one-action execute gate output
- one-action local APPLY executor output
- apply result verifier output
- optional post-validation results

It does not run commands, write files, write reports, mutate queues, mutate approvals, stage, commit, push, merge, activate workers, call APIs, touch broker systems, use credentials, place orders, send webhooks, access the network, or delete files.

## Status Model

`collector_status: blocked` means required execution evidence is not available yet. In the default DRY_RUN driver path this is expected because `one_action_local_apply_executor.command_executed` remains `false`.

`collector_status: rejected` means execution evidence exists or input evidence was supplied, but it failed a safety or validation check. Examples include mismatched selected action, changed files outside allowed paths, failed validators, nonzero command return code, protected action requests, or verifier failure.

`collector_status: collected` means the collector observed one executed bounded command, zero return code, passed verifier evidence, bounded changed files, validators present, and no protected action request.

## Output

Important fields:

- `selected_action`
- `command_executed`
- `command_returncode`
- `changed_files`
- `allowed_paths`
- `unexpected_files`
- `validators`
- `validator_records`
- `validators_passed`
- `validators_failed`
- `result_safe_to_report`
- `result_safe_to_package`
- `rejection_reasons`
- `next_safe_action`
- `safety`

`result_safe_to_package` can be `true` only when `collector_status` is `collected`, the local executor reports `command_executed: true`, and the apply result verifier reports `verifier_status: passed`.

Packaging, staging, commit, push, merge, publishing, and any protected action still require separate approval gates. A collected result is evidence, not permission to publish.

## DRY_RUN Driver Integration

The self-build DRY_RUN driver always includes `one_action_execution_result_collector` in its JSON report after `one_action_local_apply_executor`.

Because the driver passes `executor_options.execute: false` and no real command runner to the local executor, the collector normally reports:

```text
collector_status: blocked
command_executed: false
result_safe_to_package: false
```

This is intentional. The collector closes the result-consumer model without weakening the execution gate.
