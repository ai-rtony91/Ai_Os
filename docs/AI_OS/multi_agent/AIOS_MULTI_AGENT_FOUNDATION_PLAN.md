# AI_OS Multi-Agent Foundation Plan

Status: APPLY scaffold
Mode: local-first planning only

## Purpose

Create a safe foundation for future ChatGPT, Codex, and Claude orchestration inside AI_OS.

This plan does not enable external integrations. It defines roles, routing, approval gates, and blocked actions so future work can stay simple for the operator and safe for the project.

## User-Facing Goal

AI_OS should feel like one simple local command center.

The user should not need to understand agent internals during normal use. Basic mode should show:

- current task
- assigned lane
- safety status
- next safe action
- approval required status

Advanced agent details should stay hidden until requested.

## Agent Boundary

ChatGPT is the planning and orchestration layer.

Codex is the implementation layer after DRY_RUN and explicit APPLY approval.

Claude is review-only for now.

The human operator is the final approval authority.

## Required Flow

1. User gives a goal.
2. ChatGPT converts the goal into a clear plan or task packet.
3. AI_OS checks the task type, allowed files, blocked files, and safety boundaries.
4. Codex performs DRY_RUN inspection.
5. Human operator approves or rejects APPLY.
6. Codex implements only the approved scope.
7. Validators run.
8. Claude may review the result later, but cannot apply changes.
9. Human operator approves any commit or push separately.

## Blocked Actions

- No API keys.
- No secrets.
- No Anthropic integration.
- No OpenAI integration changes.
- No installs.
- No deployment.
- No live trading.
- No broker connection.
- No OANDA.
- No real webhooks.
- No real orders.
- No autonomous commit.
- No autonomous push.

## Trading Lab Boundary

Trading Lab remains paper-only.

Future multi-agent routing may help review paper signals, paper route previews, risk gates, scorecards, and validation reports. It must not enable broker execution, real account connection, OANDA, real webhooks, real orders, or live trading.

## Future UI Placement

Basic mode should show one compact AI Assistants card.

Advanced mode may show:

- role matrix
- routing model
- task packet schema
- validator status
- blocked action matrix
- review-only lanes

## Next Safe Action

Run the multi-agent foundation validator before any dashboard wiring.
