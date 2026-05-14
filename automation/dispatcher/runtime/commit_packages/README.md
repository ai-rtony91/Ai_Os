# Commit Package Runtime

This folder is reserved for the AI_OS commit package runtime scaffold.

Current scope:

- Documentation and example records only.
- No executable staging automation.
- No automatic commit.
- No automatic push.

Commit package rules:

- Human approval is required before commit.
- Human approval is required before push.
- Stage exact approved files only.
- Never use `git add .`.
- Never use `git add -A`.
- Dirty repo state blocks commit readiness unless every changed file is reviewed.
- Untracked files are `REVIEW_REQUIRED`.

Required package states:

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

Every package and staging verification record must include `next_safe_action`.

