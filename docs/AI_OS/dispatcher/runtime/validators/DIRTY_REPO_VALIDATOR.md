# Dirty Repo Validator

## Purpose

This validator checks whether the repository already has modified or untracked files.

A dirty repo is not automatically wrong. It becomes risky when a package is about to be committed.

## Inputs

Future validator inputs:

- output from `git status --short --branch`
- approved package file list
- current runtime stage

## PASS Logic

Return `PASS` when:

- the repo has no modified or untracked files outside the approved package
- every changed file is expected for the current package

## FAIL Logic

Return `FAIL` when:

- `git status --short --branch` cannot be read
- changed file paths cannot be parsed
- the approved package file list is missing during commit packaging

## BLOCKED Logic

Return `BLOCKED` before commit packaging when:

- unrelated changed files are present
- untracked files are present and not approved
- blocked paths are dirty
- protected root files are dirty

## REVIEW_REQUIRED Logic

Return `REVIEW_REQUIRED` when:

- the repo is dirty during DRY_RUN
- the repo is dirty during APPLY
- a changed file may be related but is not confirmed
- untracked files exist and need review

## Example: Dirty But Reviewable

```text
## main...origin/main
 M docs/AI_OS/dispatcher/runtime/validators/DIRTY_REPO_VALIDATOR.md
?? Reports/dispatcher/runtime/validators/dirty_repo_validation.example.json
```

Status:

`REVIEW_REQUIRED`

Reason:

The files are inside the allowed package path but must still be reviewed before staging.

## Example: Dirty And Blocked

```text
## main...origin/main
 M automation/operator/Start-AIOSWorkerQueueRunner.ps1
?? Reports/security/
```

Status:

`BLOCKED` for commit packaging.

Reason:

The dirty files are outside this package and include blocked paths.

## Next Safe Action Examples

- `Review all dirty files before commit packaging.`
- `Do not stage unrelated files.`
- `Run git status --short --branch again after validation fixes.`

