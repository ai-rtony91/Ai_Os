# AIOS Self-Build APPLY Result Verifier

`automation/orchestration/aios_self_build_apply_result_verifier.py` verifies the result of one bounded local APPLY after execution evidence is provided.

It emits:

```text
AIOS_SELF_BUILD_APPLY_RESULT_VERIFIER.v1
```

The verifier consumes the selected queue item, single-action executor result, before and after git status evidence, validator results, allowed paths, and maximum file-change count.

## v1 Rules

- If `single_action_executor.command_executed` is `false`, the verifier returns `blocked` with `command_not_executed`.
- Changed files outside `allowed_paths` fail verification.
- Changed file count above `max_files_changed` fails verification.
- Missing validators fail verification.
- Failed validators fail verification.
- If all changed files are allowed and validators passed, verification passes.
- Sandbox `CreateProcessAsUserW failed: 1312` is a local runner blocker, not a code failure.

## Safety

The verifier does not execute commands, write files, write Reports, mutate queues or approvals, stage, commit, push, merge, activate schedulers or daemons, dispatch workers, launch Codex, call APIs, access the network, use broker access, use credentials, place orders, send webhooks, or perform destructive cleanup.
