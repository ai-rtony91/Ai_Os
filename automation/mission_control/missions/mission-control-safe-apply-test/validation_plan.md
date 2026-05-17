# Validation Plan - Mission Control Safe Apply Test

## Safety Boundary

This mission is repo-scoped only. Do not use live trading, brokers, OANDA, API keys, secrets, startup tasks, scheduled tasks, GitHub merges, commits, pushes, or external network calls from generated runtime scripts.

## Required Checks

- Confirm generated mission_plan.json parses as JSON.
- Confirm generated Markdown files are readable and contain next safe action.
- Run PowerShell parser checks for any changed PowerShell files.
- Run relevant scoped validators for implementation PRs.
- Run git diff --check before commit.
- Confirm no secrets, broker actions, trading actions, startup tasks, or scheduled tasks were introduced.

## Proof Required

- Terminal output or validator logs for each check.
- Git status before commit and before PR review.
- PR links and CI/check status when PRs exist.
- Mismatch, UNKNOWN, or INVALID DATA notes if evidence conflicts.

## PASS/WARN/BLOCKED Rules

- PASS: required files exist, parsers pass, JSON parses, validators pass, and no blocked actions are present.
- WARN: validation is incomplete but no blocked action is observed.
- BLOCKED: any secret, broker, trading, startup, scheduled task, destructive action, or unapproved APPLY scope appears.

Next safe action: run the first worker task as DRY_RUN and attach validation proof before APPLY.
