# Commit Package Runtime Model

Commit packages keep AI_OS changes small, traceable, and human-approved.

A commit package describes what may be staged. It does not stage files by itself.

## Runtime Flow

1. APPLY completes after human approval.
2. Validators confirm changed files match approved files.
3. A commit package is drafted from approved packet evidence.
4. Dirty repo state is reviewed.
5. Exact files allowed to stage are listed.
6. Operator reviews package.
7. Package may become `READY_FOR_COMMIT`.
8. Human approves commit.
9. Human separately approves push.

## Commit Package Rules

- Human approval is required before commit.
- Human approval is required before push.
- Stage exact approved files only.
- Never use `git add .`.
- Never use `git add -A`.
- Do not include unrelated dirty files.
- Untracked files require review.
- Dirty repo state blocks readiness unless reviewed and isolated.

## Required Statuses

- `DRAFT`
- `VALIDATING`
- `READY_FOR_REVIEW`
- `READY_FOR_COMMIT`
- `APPROVED_FOR_COMMIT`
- `COMMITTED`
- `PUSH_READY`
- `PUSHED`
- `BLOCKED`
- `REVIEW_REQUIRED`

## Readiness Rule

A package can be `READY_FOR_COMMIT` only when approval evidence, validator evidence, staged-file plan, and dirty repo isolation all pass.

