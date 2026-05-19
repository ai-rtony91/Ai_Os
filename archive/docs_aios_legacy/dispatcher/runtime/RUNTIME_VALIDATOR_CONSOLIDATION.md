# Runtime Validator Consolidation

The runtime should use one validator chain.

Individual validators may be separate scripts, but the validator router decides which checks run and in what order.

## Validator Chain

1. Read `git status --short --branch`.
2. Check packet allowed paths.
3. Check blocked paths.
4. Check protected root files.
5. Check broker, OANDA, API key, live trading, and real webhook terms.
6. Validate packet schema.
7. Validate lock schema.
8. Validate worker session schema.
9. Validate heartbeat schema.
10. Validate approval schema.
11. Validate commit package schema.
12. Validate status output schema.
13. Validate recovery schema.
14. Parse changed JSON files.
15. Parse changed PowerShell files.
16. Run `git diff --check`.
17. Confirm changed files match approved files.
18. Confirm exact-file staging only.

## Dirty Repo Handling

A dirty repo does not block DRY_RUN.

A dirty repo does block commit packaging unless every changed file is reviewed and belongs to the approved package.

Untracked `??` files must be marked `REVIEW_REQUIRED`.

## REVIEW_REQUIRED Escalation

Use `REVIEW_REQUIRED` when:

- a file is outside allowed paths
- a protected file appears in a change set
- a lock overlaps another active lock
- a worker heartbeat is stale
- JSON cannot parse
- PowerShell cannot parse
- broker or live trading terms appear unexpectedly
- dirty repo state includes unrelated files
- approval is missing

## Human Control

Validators report and block. They do not edit files, stage files, commit, push, or approve work.

