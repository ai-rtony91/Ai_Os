# AIOS Production Readiness Validator

## Purpose

`Test-AiOsProductionReadiness.DRY_RUN.ps1` is a read-only validator that
consolidates production-hardening evidence into one verdict:

```text
READY | WARNING | BLOCKED
```

It exists because AI_OS production readiness evidence is spread across
orchestration validators, runtime health checks, self-build preview scaffolds,
dashboard contract tests, and safety-boundary docs.

## What It Checks

The validator checks:

- current branch and `git status --short --branch`
- whether dirty state is limited to evidence artifacts or this validator package
- required self-build preview modules
- required self-build tests
- dashboard runtime visibility contract test files
- closed-loop, executive-readiness, and queue-to-dispatch safety boundaries
- hard safety flags that keep mutation and execution authority disabled

It does not run Node, launch runtime, or invoke worker/control-plane scripts.
Node contract tests remain separate executable validation evidence when the
local environment can launch them.

## Verdicts

`READY` means required files and safety-boundary evidence are present, no
blockers are found, and no unsafe dirty state is present.

`WARNING` means the validator found review-required evidence, such as untracked
Reports or `control/review_bridge` artifacts, but did not find a production
safety blocker.

`BLOCKED` means required evidence is missing, the branch is wrong, tracked dirty
files exist outside the validator package, unsafe dirty paths are present, or a
safety flag would enable mutation or execution authority.

## Safety Boundaries

This validator is evidence-only. It always reports:

- `writes_files=false`
- `mutates_runtime=false`
- `mutates_queue=false`
- `mutates_approval=false`
- `launches_workers=false`
- `starts_scheduler=false`
- `starts_daemon=false`
- `commits=false`
- `pushes=false`
- `broker_or_live_trading=false`

It does not approve production operation, runtime launch, persistent supervisor
activation, queue mutation, approval mutation, worker launch, scheduler or
daemon activation, broker activity, live trading, commit, push, PR creation, or
merge.

Validator output is evidence only. Anthony remains the approval authority for
any protected action.
