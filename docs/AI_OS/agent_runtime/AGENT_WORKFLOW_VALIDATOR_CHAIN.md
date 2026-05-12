# Agent Workflow Validator Chain

The validator chain is a set of read-only checks.

A validator is a safety check that looks for broken rules before work is saved.

## Validator Order

1. Parse JSON files.
2. Confirm required workflow states exist.
3. Confirm required task fields exist.
4. Confirm major and minor agent roles exist.
5. Confirm blocked action matrix contains required blocks.
6. Confirm queue allowed paths do not point to blocked paths.
7. Confirm no status enables live execution, broker, OANDA, API keys, or secrets.
8. Confirm no background, scheduled, startup, account login, package install, or external LLM install action is enabled.
9. Confirm dashboard fixture is local-only.
10. Print PASS or FAIL.
11. Run `git status --short --branch`.

## Required Safety Locks

- Live trading: BLOCKED
- Broker execution: BLOCKED
- OANDA execution: BLOCKED
- API keys: BLOCKED
- Secrets: BLOCKED
- Real webhooks: BLOCKED
- Real orders: BLOCKED
- External LLM install: NOT_ENABLED
- Background execution: BLOCKED
- Scheduled automation: BLOCKED
- Startup persistence: BLOCKED
- Account login systems: BLOCKED
- Financial claims: BLOCKED
- Profitability guarantees: BLOCKED

## Result Rule

PASS means the workflow files are present, parseable, and locally safe.

FAIL means the user should stop and review the printed failures before any APPLY, commit, push, install, or integration.

