# AIOS PR Landing Preview

## Purpose

`automation/orchestration/aios_pr_landing_preview.py` converts already-collected
pull request evidence into `AIOS_PR_LANDING_PREVIEW.v1`.

The preview helps AIOS decide whether an open PR is ready for a protected landing
review. It is evidence only. It does not merge, push, reset, delete branches,
mutate approvals, write reports, or call GitHub.

## Input Evidence

The planner expects local or CLI-provided evidence:

- `pr_number`
- `pr_state`
- `mergeable`
- `draft`
- `checks_status`
- `changed_files`
- `additions`
- `deletions`
- `base_branch`
- `head_branch`
- `validation_summary`
- `safety_summary`
- `local_branch_status`

## Output Contract

The output includes:

- `schema: AIOS_PR_LANDING_PREVIEW.v1`
- `landing_status: ready | blocked | rejected | no_pr`
- `merge_allowed_by_policy: false`
- `required_human_approval: true`
- check, scope, safety, and blocker evidence
- proposed read-only or dry-run readiness commands
- forbidden protected actions
- proof that no commands, merges, pushes, resets, or branch deletions occurred

## Status Rules

- `ready`: PR is open, non-draft, mergeable, based on `main`, checks passed,
  validation passed, changed-file scope is safe, safety summary is safe, and
  local branch status is safe.
- `blocked`: readiness evidence is incomplete, pending, draft, non-mergeable,
  unsafe in scope, unsafe in local status, or requires more review.
- `rejected`: PR checks or validation failed, or the PR is no longer open.
- `no_pr`: required PR evidence is missing.

## Safety Boundary

The preview may list inspection or dry-run readiness commands for a human or
separately governed runner to consider, such as `gh pr view`, `gh pr checks`,
or the existing PR merge gate in DRY_RUN mode. The Python planner itself never
runs `gh`, runs `git`, opens network connections, or starts subprocesses.

It must not execute or recommend direct protected landing actions as approved.
Human Owner approval remains required before merge, push, reset, branch deletion,
approval mutation, or local main sync.

Canonical PR landing authority remains `docs/workflows/AI_OS_PR_LANE_RUNNER.md`.
