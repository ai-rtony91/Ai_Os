# Continuous Improvement Cycle

Status: foundation draft.

Purpose: define the AI_OS improvement loop for repo-aware work.

## Cycle

Explore -> Consolidate -> Standardize -> Automate -> Audit -> Reassess -> Repeat

## Explore

Goal: understand the current repository and operating state.

Required outputs:

- Files and folders inspected.
- Known facts.
- UNKNOWN items.
- MISMATCH items when evidence conflicts.
- Candidate risks.
- Stop point.

Do not automate during Explore.

## Consolidate

Goal: reduce scattered knowledge into a small number of canonical docs.

Required outputs:

- Current-state map.
- Manual workflow.
- Governance rules.
- Known gaps.
- Decision record when a durable rule is adopted.

Consolidation should avoid duplicate docs when a canonical file already exists.

## Standardize

Goal: define repeatable formats before code is added.

Required outputs:

- Naming rules.
- Report format.
- Validator expectations.
- Allowed and blocked paths.
- Role boundaries.
- Evidence requirements.

Standardization should keep beginner-readable workflows and avoid dashboard clutter.

## Automate

Goal: convert stable, reviewed, manual workflows into safe tooling.

Preconditions:

- Manual workflow is documented.
- Owner is identified.
- Inputs and outputs are stable.
- Validation is defined.
- Failure and rollback behavior are documented.
- Protected actions remain gated.

Automation must not bypass DRY_RUN/APPLY approval.

## Audit

Goal: compare outputs against evidence.

Required checks:

- Files changed match allowed paths.
- Validators ran or skipped with reason.
- JSON parses when JSON changed.
- PowerShell parses when PS1 changed.
- `git diff --check` passes when files changed.
- Protected actions are reported.
- Unknowns remain labeled UNKNOWN.

## Reassess

Goal: update the map after reality changes.

Required outputs:

- What changed.
- What remains unknown.
- What automation should still wait.
- What should be removed from the candidate list.
- Next safe task.

## Repeat

The cycle repeats only after the current stop point is reached and reviewed.

## Current Application

This documentation foundation is in Consolidate. It intentionally stops before Standardize and Automate implementation.

## Stop Point

Stop after the top-level documentation foundation exists and passes text validation.
