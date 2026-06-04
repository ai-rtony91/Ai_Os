# OpenAI Planner Fixture Scaffold

Status: APPLY fixture/docs-only scaffold
Task: AI_OS Phase 16 - OpenAI Planner Adapter Fixture Scaffold APPLY

## Purpose

This scaffold defines the first local-only OpenAI planner fixture layer for AI_OS.

It does not call OpenAI. It does not request an API key. It does not install packages. It does not create runtime workers. It does not mutate telemetry, control, approval, lock, memory, broker, OANDA, or trading execution paths.

## Files

| File | Purpose |
| --- | --- |
| `fixtures/PLANNER_INPUT_EXAMPLE_001.json` | Example local planner input for a safe docs/fixtures task. |
| `fixtures/PLANNER_OUTPUT_EXAMPLE_001.json` | Example inert planner output that classifies the task and drafts packet metadata. |
| `schemas/OPENAI_PLANNER_INPUT.schema.json` | JSON schema for planner input fixtures. |
| `schemas/OPENAI_PLANNER_OUTPUT.schema.json` | JSON schema for planner output fixtures. |
| `VALIDATION_REPORT_001.md` | Validation evidence for this scaffold. |

## Safety Boundary

The fixture scaffold is allowed to model:

- approved repo context.
- safety classification.
- autonomy level classification.
- Codex packet preview fields.
- validator recommendations.
- approval summary concepts.
- stop points.

The fixture scaffold is blocked from:

- live OpenAI API calls.
- API keys or secrets.
- `.env` creation.
- package installs.
- runtime mutation.
- telemetry writes.
- Night Supervisor writes.
- approval inbox writes.
- lock or memory writes.
- broker, OANDA, live trading, real orders, or webhook execution.
- commit or push.

## Required Safety Fields

Every planner input and output fixture must include:

- `mode`
- `autonomy_level`
- `allowed_paths`
- `forbidden_paths`
- `requires_human_approval`
- `live_trading_status`
- `broker_execution_status`
- `secret_handling_status`
- `validator_chain`
- `stop_point`
- `recommended_next_action`

## Current Mode

```text
FIXTURE_ONLY
```

## Current Autonomy Level

```text
Level 3 - fixture/docs proposal
```

## Next Safe Action

Review the fixture scaffold. A later packet may propose a non-executable local preview adapter that reads these fixtures and prints a planner preview, but that later packet must still avoid live API calls, API keys, package installs, runtime mutation, telemetry writes, broker paths, OANDA paths, and trading execution.
