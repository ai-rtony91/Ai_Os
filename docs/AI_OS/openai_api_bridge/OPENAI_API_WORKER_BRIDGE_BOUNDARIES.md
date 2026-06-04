# OpenAI API Worker Bridge Boundaries

Status: DRY_RUN planning artifact
Scope: docs-only boundary definition

## Boundary Summary

The OpenAI API Worker Bridge is a planning and packet-generation boundary. It may prepare inert guidance. It must not become an execution engine.

## Allowed Inputs

Allowed inputs:

- approved repo context.
- source-of-truth docs.
- workflow docs.
- validator runbooks.
- packet templates.
- fixture-only examples.
- operator-provided goals.

Blocked inputs:

- real API keys.
- secrets.
- `.env` files.
- browser session data.
- broker credentials.
- live trading credentials.
- private account pages.

## Allowed Outputs

Allowed outputs:

- repo summaries.
- safety classifications.
- Codex-ready packet drafts.
- validator recommendations.
- approval summaries.
- fixture-only planning data.
- docs-only integration plans.
- exact next safe action text.

Blocked outputs:

- live API requests.
- generated credentials.
- `.env` files.
- package install scripts for immediate execution.
- real webhooks.
- broker calls.
- trading orders.
- direct runtime mutations.
- approval record mutations.
- commit, push, merge, or PR execution.

## Allowed Paths For This DRY_RUN

Only this path may be created or edited by this packet:

```text
docs/AI_OS/openai_api_bridge/
```

## Forbidden Paths

This bridge rulebook blocks writes to:

```text
telemetry/night_supervisor/
control/
automation/orchestration/locks/
automation/orchestration/approval_inbox/
automation/orchestration/memory/
telemetry/
automation/orchestration/night_supervisor/
```

It also blocks broker files, OANDA files, live trading files, secret files, `.env` files, and Git configuration files.

## Protected Action Boundary

The bridge must never perform protected actions.

Protected actions include:

- `git add`
- `git commit`
- `git push`
- `gh pr create`
- `gh pr merge`
- `git merge`
- `git reset`
- `git clean`
- branch deletion
- file deletion
- package installation
- credential creation
- external service calls

The bridge may prepare a preview for a protected action only when the preview is inert and clearly marked as requiring future human approval.

## Approval Boundary

The bridge may prepare an approval summary. It must not create, update, approve, reject, expire, complete, or archive approval inbox records.

Approval remains human-owned. Validator output remains evidence only.

## Validator Boundary

The bridge may suggest validators, including:

- `git status --short --branch`
- `git diff --check`
- allowed path checks.
- forbidden path checks.
- no-secret checks.
- no-live-trading checks.
- markdown existence checks.
- final git status checks.

It must not treat validator success as permission to APPLY, commit, push, merge, or mutate protected state.

## Runtime Boundary

The bridge must not:

- launch workers.
- schedule tasks.
- create startup persistence.
- write runtime state.
- update telemetry.
- mutate Night Supervisor output.
- update control markers.
- update worker memory.

Runtime integration requires a separate future governance pass and explicit APPLY approval.

## Trading Boundary

The bridge must mark the following as `BLOCKED`:

- broker API calls.
- OANDA calls.
- live trading.
- real orders.
- real webhooks.
- broker credentials.
- production order routing.
- LLM-driven trade execution.

Paper-only planning and fixture-only analysis remain possible only when separately scoped.
