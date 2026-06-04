# OpenAI API Worker Bridge Apply Plan

Status: DRY_RUN planning artifact
Scope: next safe APPLY candidate

## Purpose

This plan defines the first future APPLY packet that can follow the OpenAI API Worker Bridge rulebook.

The APPLY packet must remain fixture-only. It must not create live OpenAI API calls.

## Recommended Next APPLY Packet

Title:

```text
AI_OS Phase 16 - OpenAI Planner Adapter Fixture Scaffold APPLY
```

Short description:

Create a local fixture-only OpenAI planner adapter scaffold that converts a sample operator goal into an inert planner preview packet. The scaffold must use local fixture input and fixture output only. It must not call OpenAI, request keys, install packages, write telemetry, launch workers, mutate approvals, or touch runtime paths.

## Proposed Allowed Paths

The future APPLY packet should use docs/fixtures-only paths, such as:

```text
docs/AI_OS/openai_api_bridge/fixtures/
docs/AI_OS/openai_api_bridge/schemas/
```

If a repo convention requires schemas under `schemas/aios/orchestration/`, the APPLY packet must ask for explicit expanded scope before touching that path.

## Proposed Files

Future APPLY may create:

- `docs/AI_OS/openai_api_bridge/fixtures/openai_planner_goal.sample.json`
- `docs/AI_OS/openai_api_bridge/fixtures/openai_planner_preview.sample.json`
- `docs/AI_OS/openai_api_bridge/schemas/openai_planner_preview.schema.json`
- `docs/AI_OS/openai_api_bridge/OPENAI_PLANNER_FIXTURE_ADAPTER_README.md`

No executable adapter should be created in the first APPLY packet unless separately approved.

## Required Constraints

The future APPLY packet must state:

- no live API call.
- no API key request.
- no `.env`.
- no package install.
- no runtime worker.
- no telemetry writes.
- no Night Supervisor writes.
- no approval inbox writes.
- no control marker writes.
- no broker files.
- no OANDA files.
- no trading execution files.
- no commit.
- no push.

## Minimum Fixture Behavior

The fixture scaffold should model:

```text
operator goal
-> safety classification
-> autonomy level recommendation
-> packet draft
-> validator recommendation
-> approval summary preview
-> stop point
```

All output must be inert sample data.

## Required Validation

The future APPLY packet should require:

- `git status --short --branch`
- JSON parse validation for created fixture/schema files.
- `git diff --check`
- path review proving only the approved docs/fixtures paths changed.
- no-secret scan.
- no-live-trading scan.
- final `git status --short --branch`.

## Explicit Non-Goals

The future APPLY packet must not:

- connect to OpenAI.
- create an API client.
- ask for `OPENAI_API_KEY`.
- create `.env`.
- install SDKs.
- add background services.
- write telemetry.
- mutate approval inbox.
- launch Codex, Claude, Relay, Night Supervisor, or other workers.
- create a commit package for execution.
- touch broker, OANDA, webhook, order, or live trading paths.

## Approval Requirements

Future APPLY requires explicit human approval naming:

- mode: `APPLY`.
- exact allowed paths.
- exact files to create.
- forbidden paths.
- validator chain.
- stop point.

Approval for this future APPLY will not approve commit, push, PR creation, merge, package install, API key setup, or live API calls.
