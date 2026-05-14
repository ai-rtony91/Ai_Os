# AI_OS Clean State Verifier Plan

The clean-state verifier should report repository status before packet assignment, APPLY, staging, commit, or push.

## Checks

- branch name
- upstream branch
- ahead or behind status
- untracked files
- modified files
- staged files
- last commit hash
- push status
- dirty state reason
- protected-file status
- blocked-path status
- next safe action

## Results

- `CLEAN`
- `DIRTY_REVIEW_REQUIRED`
- `BLOCKED`
- `UNKNOWN`

The verifier is report-only. It must not change repository state.
