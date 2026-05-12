# Phase 15.1 Agent Orchestration Runtime Core

## Purpose

Phase 15.1 creates the first local AI_OS agent runtime. Runtime means a local control layer that decides which safe work packet should happen next.

Orchestration means routing work to the right file, agent, and validator. A validator is a safety check that looks for broken rules before work is saved.

## Current Saved Base

The runtime builds on the current saved AI_OS and Trading Lab base:

- Phase 14.4 paper strategy evidence analyzer
- Trading Lab mock workflow evidence package
- Trading Lab modular dashboard window system
- Trading Lab paper backend kit
- Product readiness and progression docs
- Dashboard brand assets

## Problem Being Solved

The project has many useful parts, but larger builds need a safer control layer. Without a local runtime, work can become scattered across docs, mock data, validators, dashboard fixtures, and backend plans.

This phase creates a simple file-based system so each task has one owner, one allowed path set, one blocked path set, one expected output, one validation step, and one next action.

## Runtime Workflow

USER_GOAL_RECEIVED
-> TASK_CLASSIFIED
-> AGENT_SELECTED
-> OWNERSHIP_CHECKED
-> TASK_QUEUED
-> AGENT_OUTPUT_EXPECTED
-> VALIDATION_RUN
-> SUMMARY_WRITTEN
-> NEXT_ACTION_WRITTEN
-> USER_APPROVAL_REQUIRED

## Agent Routing Model

Major agents own large work areas. Minor agents fix gaps inside those areas.

Major agents:

- architecture_agent
- trading_research_agent
- backtest_agent
- risk_gate_agent
- ui_agent
- integration_agent
- automation_agent
- reporting_agent

Minor agents:

- scaffold_gap_agent
- schema_gap_agent
- validator_gap_agent
- mock_data_agent
- naming_agent
- docs_patch_agent
- cleanup_agent
- dependency_notes_agent

## Major vs Minor Agent Rules

Major agents own the main lane. Minor agents can help fill missing pieces, but they cannot exceed the major agent ownership boundary.

No agent can touch blocked paths. No agent can enable live trading, broker execution, OANDA execution, API keys, secrets, real webhooks, real orders, external LLM installs, background execution, scheduled trading, startup persistence, or account login systems.

## Safety Boundary

This phase is local and file-based only.

- Live execution: BLOCKED
- Broker execution: BLOCKED
- OANDA execution: BLOCKED
- API keys and secrets: BLOCKED
- Real webhooks and real orders: BLOCKED
- External LLM install: NOT ENABLED
- Background execution: BLOCKED

## Time-of-No-Return Warning

Docs, fixtures, local queues, and local validators are easy to change before commit. After commit, file names, schema names, and dashboard fixture paths become harder to change because other work may start depending on them.

Never rush live trading, broker connections, API keys, user login, payments, Play Store financial declarations, or public app release steps.

## What Is Created In This Phase

This phase creates agent runtime docs, schema, queue, status, gap log, ownership rules, validation report, next action, Codex summary, Trading Lab bridge note, LLM worker boundary, non-technical operator guide, read-only PowerShell scripts, dashboard mock-data fixture, and shared Trading Lab bridge references where safe.

## What Remains Future

Future phases may add a local paper bot runner, local chart panel, TradingView external handoff buttons, TradersPost external handoff buttons, stronger validator chains, and a dashboard runtime status panel.

Those future phases must stay paper-only unless a separate reviewed and approved safety phase changes the boundary.

## Next Safe Action

Run the Phase 15.1 agent runtime readiness validator, then choose one queued build task.

