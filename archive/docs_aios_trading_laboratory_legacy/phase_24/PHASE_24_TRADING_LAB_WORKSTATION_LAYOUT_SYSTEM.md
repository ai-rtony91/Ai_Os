# Phase 24 Trading Lab Workstation Layout System

## Purpose

Phase 24 turns Trading Lab into the main professional forex workstation surface for AI_OS. It is paper-only, local mock-data only, and focused on fast scanning, low mental load, risk-first review, latency awareness, journal, replay, and scorecard loops.

## Workstation Areas

- Top bar: selected pair, session, market state, latency status, risk status, validation state, paper mode.
- Left panel: watchlist, forex pairs, session tracker, economic events, alerts, workspace profiles.
- Center panel: primary next action, compact workflow rail, current workflow step, signal intake, market context, paper execution flow, AI guidance summary.
- Right panel: risk gate anchor, max risk, block reason, paper-only state, position model, confluence score, setup checklist, one compact live blocked lock.
- Bottom panel: journal, replay, scorecard, paper metrics, validation log.

## Required Paper Workflow

Signal Intake -> Market Context -> Risk Gate -> Paper Result -> Journal -> Replay -> Scorecard.

## Workspace Profiles

- Scalp Mode
- Swing Mode
- Replay Mode
- Review Mode
- Learning Mode
- News Session Mode

## Latency Requirement

Latency reduction is a core trading-system requirement. Phase 24 measures workflow delay without treating AI review as an execution dependency.

Required latency fields are nested in `apps/dashboard/mock-data/trading-lab-workstation.example.json`:

- `signal_source_time`
- `alert_received_time`
- `validation_start_time`
- `validation_end_time`
- `ai_review_start_time`
- `ai_review_end_time`
- `route_preview_time`
- `paper_execution_time`
- `total_delay_seconds`
- `stale_status`
- `delayed_reason`
- `user_decision_time_seconds`

## Safety Boundaries

These states must remain `BLOCKED`:

- live trading
- broker
- OANDA
- API keys
- real webhooks
- real orders
- AI-assisted execution

No broker, OANDA, real webhook, real order, account connection, credential, API key, autonomous execution, or live trading path is enabled by this phase.

## UI Rules

- Trading Lab route renders the workstation layout first.
- The center panel visually promotes primary next action and current workflow step.
- The top bar order is Pair -> Session -> Market -> Latency -> Risk -> Validation -> Paper Mode.
- Full latency detail and repeated safety locks are reduced in the first workstation view.
- Advanced diagnostics stay collapsed.
- External platform details remain hidden by default.
- Start screen remains clean.
- Music dock, Work rail, and Personal rail remain separate and untouched.
- Do not create duplicate panels or duplicate player surfaces.
