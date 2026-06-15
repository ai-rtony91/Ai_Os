# AIOS Safe PR Auto-Land Policy

Schema: `AIOS_SAFE_PR_AUTOLAND_POLICY.v1`

`automation/orchestration/aios_safe_pr_autoland_policy.py` converts local or CLI-provided PR evidence into a preview-only auto-land eligibility decision. It does not call `gh`, call `git`, access the network, merge, push, delete branches, reset local state, mutate approvals, mutate queues, start schedulers, start daemons, or dispatch workers.

## Inputs

- `pr_number`
- `pr_state`
- `draft`
- `mergeable`
- `checks_status`
- `changed_files`
- `additions`
- `deletions`
- `base_branch`
- `head_branch`
- `head_sha`
- `expected_head_sha`
- `safety_summary`
- `validation_summary`

## SAFE_AUTO_LAND_ELIGIBLE

A PR is eligible only when all required conditions pass:

- PR state is open.
- PR is not draft.
- PR is mergeable.
- Checks status is success.
- Base branch is `main`.
- Head branch is not `main`.
- `expected_head_sha` matches `head_sha`.
- Changed files stay inside allowed automation, docs, or tests paths.
- Changed files do not touch protected files, governance paths, Reports, review bridge, credentials, broker paths, live trading paths, order paths, webhook paths, approval mutation paths, queue mutation paths, scheduler paths, or daemon paths.
- Safety summary has no high-risk flags.
- Validation summary is not failed.

## Preview Plan

When eligible, the planner returns these proposed commands as evidence only:

```powershell
gh pr checks <PR_NUMBER>
gh pr merge <PR_NUMBER> --squash --delete-branch
git fetch origin
git reset --hard origin/main
git status --short --branch
```

The planner never executes those commands. Protected landing actions remain governed by the AI_OS PR lane and current-session human approval.

## Safety Contract

The output keeps `commands_executed` empty and all performed-action booleans false:

- `merges_performed`
- `pushes_performed`
- `branches_deleted`
- `resets_performed`

Blocked and rejected outputs return no proposed landing commands. A rejected output sets `human_wake_required` to true and reports the rejection in `sos_reason`.
