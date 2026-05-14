# AI_OS Validator Chain Plan

## Required Checks

1. Read `git status --short --branch`.
2. Confirm branch state.
3. List changed files.
4. Check allowed paths.
5. Check blocked paths.
6. Check protected root files.
7. Scan for broker, OANDA, API key, secret, credential, webhook, and live trading paths.
8. Parse changed JSON files.
9. Confirm required Markdown files exist.
10. Run `git diff --check`.
11. Confirm expected changed files.
12. Confirm exact-file staging plan.
13. Confirm report generation.
14. Report clean-state result after separately approved commit and push work.

## Status Values

- `PASS`
- `FAIL`
- `BLOCKED`
- `REVIEW_REQUIRED`

Validators are report-only and must end with one next safe action.
