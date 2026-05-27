# AI_OS API Integration Safety Workflow

This workflow defines the first safe boundary for future AI_OS integrations with Tasker, Azure, Bitwarden, OpenAI planner APIs, and Claude planner APIs.

API integration is not execution authority. API output, planner output, adapter output, controller output, and generated preview files are evidence only. They do not approve APPLY, staging, commit, push, PR creation, merge, deployments, secret access, broker actions, or trading actions.

## Initial Scope

The first API integration stage is limited to Level 1 and Level 2 under `docs/governance/AI_OS_AUTONOMY_LEVELS.md`.

Allowed initially:

- read-only status checks
- local fixture previews
- generated preview packets
- generated report evidence
- planner recommendations that remain inert

Blocked initially:

- real API calls unless a later packet explicitly authorizes a read-only adapter
- API key usage
- `.env` files in the repo
- real keys in prompts, logs, telemetry, reports, fixtures, or preview output
- approval mutation
- queue mutation
- worker launch
- auto APPLY
- auto commit
- auto push
- auto PR creation
- auto merge
- broker/OANDA/live trading/webhook/secrets/dashboard scope

## Integration Patterns

### Tasker

Tasker starts read-only and notification-only.

Safe early behavior:

- inspect local fixture data
- prepare task summary previews
- prepare notification text previews
- report what a future notification would say

Tasker must not create, update, delete, complete, schedule, or send tasks without a later approval-gated executor design.

### Azure

Azure starts read-only and status-only.

Safe early behavior:

- inspect local fixture data
- summarize expected status fields
- prepare cloud readiness preview output

Azure must not authenticate, create resources, change configuration, deploy, rotate secrets, restart services, or mutate subscriptions in this stage.

### Bitwarden

Bitwarden starts metadata-only.

Safe early behavior:

- reference secret names or placeholder identifiers only
- validate that a required secret label is declared as missing or present from fixture evidence
- never print secret values

Bitwarden must not unlock vaults, read secret values, rotate keys, export vault data, or place credentials in prompts, logs, telemetry, reports, or fixtures.

### OpenAI Planner API

OpenAI planner integration starts as planner-output only.

Safe early behavior:

- use local fixtures instead of live API calls
- emit a planner preview schema
- recommend a packet, mode, lane, validator set, and stop condition

OpenAI output must not execute commands, mutate files, create approvals, launch workers, stage, commit, push, create PRs, merge, or touch protected scope.

### Claude Planner API

Claude planner integration follows the same planner-output-only boundary.

Safe early behavior:

- use local fixtures instead of live API calls
- emit a planner preview schema
- recommend bounded next packets

Claude output must not execute commands, mutate files, create approvals, launch workers, stage, commit, push, create PRs, merge, or touch protected scope.

## Level Mapping

Level 1-2 allowed:

- read-only status
- summaries
- local fixture adapters
- generated previews
- generated report evidence

Level 4 required:

- any exact approved mutation
- staging exact named files
- committing exact approved files
- pushing exact approved branch
- creating exact approved PR

Level 5 hard gate:

- secrets
- key rotation
- deployments
- broker/OANDA
- live trading
- autonomous merge or push
- real webhooks
- real orders
- destructive repo actions
- branch protection changes
- governance authority changes

## Secret Handling

Secrets are referenced, never printed.

Rules:

- no `.env` in repo
- no real keys in prompts
- no real keys in logs
- no real keys in telemetry
- no real keys in fixtures
- no real keys in generated previews
- no autonomous secret access
- no autonomous key rotation

## Rollout Order

1. Docs-only safety workflow.
2. Fake/local fixture adapters.
3. Read-only Tasker preview.
4. Read-only Azure status preview.
5. Bitwarden metadata validator.
6. OpenAI/Claude planner schema.
7. Approval-gated executor design later.

## Stop Conditions

Stop if a request asks for:

- real API credentials
- `.env` creation
- external model API calls
- cloud deployment
- secret reads or key rotation
- approval mutation
- queue mutation
- autonomous execution
- staging, commit, push, PR creation, or merge without explicit approval
- broker/OANDA/live trading/webhook/real-order scope

Next safe action: use fixture-only previews until the preview layer is stable and separately reviewed.
