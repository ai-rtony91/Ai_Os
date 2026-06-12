# AI_OS Dashboard Data Contracts

Status: canonical extracted dashboard data-contract summary
Source: legacy `docs/AI_OS/dashboard` drafts

## Purpose

This document is the canonical extracted dashboard data-contract summary for AI_OS. It preserves useful contract ideas from historical `docs/AI_OS/dashboard` draft files without claiming that the dashboard runtime is fully implemented.

Legacy `docs/AI_OS/dashboard` files are historical source material. Future dashboard work should reference this spec first, then inspect legacy drafts only when a human review needs detail not yet promoted here.

## Scope

This spec defines read-only dashboard and operator-panel contracts for:

- dashboard state,
- fixture/mock data,
- status cards,
- command center / operator panels,
- telemetry panels,
- AI assistant panel concepts,
- multi-client state access boundaries,
- static preview behavior,
- responsive/mobile behavior,
- safety boundaries.

This spec does not create UI, write JSON, run validators, approve APPLY, launch apps, open browsers, persist telemetry, connect services, access credentials, connect brokers, place trades, fire webhooks, or enable live trading.

## Dashboard State Model

Recommended dashboard state fields:

- `timestamp`
- `repo_root`
- `git_branch`
- `git_status_clean`
- `dashboard_state`
- `router_available`
- `registry_available`
- `workflow_count`
- `active_workflow`
- `last_result`
- `approval_required`
- `risk_level`
- `protected_files_changed`
- `daily_metrics_changed`
- `checkpoint_index_changed`

State values should be explicit and conservative:

- `PASS`
- `WARN`
- `FAIL`
- `UNKNOWN`
- `STALE`
- `BLOCKED`
- `COMPLETE`
- `PENDING_APPLY`
- `INVALID DATA`
- `REVIEW REQUIRED`

Missing data is `UNKNOWN`, not PASS. Conflicting evidence is `MISMATCH` or `INVALID DATA`.

## Multi-Client State Access Contract

AI_OS may support two future operator clients:

1. Web dashboard: browser-first access, protected by Cloudflare Access, with a future target of Next.js plus React Three Fiber where browser-native 3D is useful.
2. UE5 client: premium 3D/4D command-center, immersive desktop app, kiosk operator mode, and possible future launcher.

The UE5 client does not replace the web dashboard by default. Any future APPLY packet must decide whether UE5 is Phase 2 or Phase 3 after the web dashboard redesign.

State access rules:

- Live AI_OS state must be read through approved backend APIs only.
- The current candidate backend owner is `services/orchestrator/` or a later approved read-only state API.
- Clients must not read repo files, telemetry ledgers, approval inboxes, worker queues, scheduler state, local environment files, or generated runtime files directly.
- API responses should include source path or source name, timestamp, freshness, stale/invalid markers, mode, approval requirement, and next safe action where applicable.
- API responses must redact credentials, secrets, tokens, private paths, and broker/account identifiers before they reach any client.
- UE5 must not store secrets, broker keys, Azure tokens, Cloudflare tokens, repo credentials, Git credentials, API keys, private keys, recovery keys, or persistent privileged sessions.
- UE5 controls for runtime, scheduler, queues, broker, and live-trading surfaces must remain display-only or approval-request previews unless a separate approved workflow and approval gate authorizes a specific action.
- Live broker execution and live trading remain blocked.

## Fixture / Mock-Data Contract

Fixture data must be deterministic, local-only, and safe to commit.

Allowed fixture content:

- static fixture data,
- fake sample health states,
- non-secret validator status,
- non-live progress values,
- sample operator notes,
- sample checkpoint links,
- mock next actions that are clearly labeled as examples.

Blocked fixture content:

- credentials,
- tokens,
- API keys,
- broker data,
- private user data,
- browser profiles,
- live market data,
- live order paths,
- trade execution decisions.

Example top-level fixture shape:

```json
{
  "generated_at": "YYYY-MM-DDTHH:mm:ss",
  "phase": "Phase X",
  "stage": "Stage Y",
  "overall_status": "UNKNOWN",
  "validator_health": {},
  "progress": {},
  "checkpoint": {},
  "safety": {},
  "next_action": {}
}
```

## Status Card Contract

Status cards should be concise, source-backed, and safe for beginner review.

Common fields:

- `label`
- `status`
- `summary`
- `source_path`
- `last_checked`
- `stale`
- `approval_required`
- `next_safe_action`

Status cards should never infer success from missing files. They should show source paths when available.

## Validator Health Contract

Validator health panels may display:

- overall status,
- validators discovered,
- validators run,
- PASS count,
- WARN count,
- FAIL count,
- SKIPPED count,
- blockers,
- next safe action.

Rules:

- any FAIL means dashboard status should show BLOCKED,
- WARN means REVIEW REQUIRED,
- PASS with zero validators is INVALID DATA,
- missing health source means UNKNOWN.

## Checkpoint and Next Action Contract

Checkpoint panels may display:

- date,
- mode,
- phase or stage,
- summary,
- safety status,
- source path,
- next safe action.

Next action source priority:

1. approved operator workflow,
2. latest validated checkpoint or audit,
3. latest validated status/health summary,
4. `UNKNOWN` if no source can be verified.

The dashboard may display a next action later, but it must not execute it.

## Command Center / Operator Panel Contract

The command center is concept-only until separately approved.

Operator panels may include:

- system status,
- validator-first status,
- protected-file status,
- blocked-action status,
- work packets,
- approval inbox,
- worker status,
- commit package recommendation,
- telemetry/work intelligence,
- next safe action,
- safety reminders.

Future maturity levels:

1. static preview,
2. fixture-backed visibility,
3. mock action registry,
4. approval-gated local automation, future only,
5. service integration, future only.

Dashboard production outputs require separate approval.

## Telemetry Panel Contract

Telemetry panels should be evidence displays, not telemetry collectors.

Potential display fields:

- evidence scope,
- git commit count,
- tracked file count,
- checkpoint count,
- daily report count,
- progress file count,
- dashboard mock-data file count,
- partial duration minutes,
- complete lifetime time spent: `UNKNOWN` until verified,
- complete lifetime bytes changed: `UNKNOWN` until verified,
- validator status,
- safety status.

No background collector, persistence writer, external service, or live telemetry pipeline is approved by this spec.

## AI Assistant Panel Contract

The AI assistant panel is concept-only unless separately approved.

Potential inputs:

- current phase and stage,
- latest checkpoint or audit summary,
- progress status,
- validator health status,
- safety status,
- next safe action,
- operator question,
- local mock assistant fixture.

Potential outputs:

- assistant message,
- next safe action,
- safety reminder,
- blocked-action explanation,
- source reference,
- approval requirement.

The panel must not connect live AI APIs, send secrets, run commands, write files, approve APPLY, or trigger automation without explicit future approval.

## Static Preview Contract

The static preview is read-only dashboard planning and fixture review.

It may guide:

- operator cockpit review,
- dashboard fixture review,
- dashboard rendering prep,
- panel taxonomy,
- safety copy,
- visual hierarchy.

It must not create production dashboard output, report writing, telemetry writing, protected file edits, startup automation, broker/trading systems, credentials, git staging, commits, or pushes.

## Responsive / Mobile Menu Contract

Mobile and responsive behavior should:

- collapse status cards into a single-column stack on narrow screens,
- keep safety, validator failure, blocked status, and next action above lower-priority metrics,
- prevent horizontal scrolling for status content,
- keep labels short and scannable,
- preserve existing sidebar and drawer behavior unless a future approved implementation changes it,
- show UNKNOWN when data is missing,
- show INVALID DATA when JSON cannot be parsed,
- show BLOCKED when safety or validation prevents work.

## Visual and Layout Guidance

The dashboard may explore an operator cockpit with:

- left navigation,
- top system status bar,
- center analytics/status region,
- right alert/help region,
- lower read-only readiness region,
- modular widgets,
- low latency goals,
- dark mode,
- restrained glass, parallax, and glow concepts,
- responsive and multi-monitor planning.

Visual effects must preserve readability, accessibility, and low-GPU-impact goals. Effects are concept-only until a future dashboard implementation pass is approved.

## Safety Boundaries

The dashboard must stay:

- read-only by default,
- fixture-only until approved sources exist,
- local-first,
- explicit about DRY_RUN vs APPLY,
- explicit about missing, stale, invalid, or conflicting data.

Out of scope:

- live broker execution,
- OANDA or broker account connections,
- real webhooks,
- real orders,
- live order paths,
- secrets or API keys,
- live market data,
- credential access,
- dashboard-triggered APPLY,
- hidden background services,
- deployment or publishing automation.

Trading Lab dashboard surfaces must remain paper-only unless a separate governance change approves otherwise.

## Human Review Items

- Decide which exact source paths replace legacy `Reports/` references after PR #180 archive moves.
- Decide whether `apps/dashboard` should own implementation docs while this spec owns contracts.
- Decide whether any legacy dashboard fixture JSON should be promoted to `apps/dashboard/mock-data`.
- Decide whether the command center remains display-only or becomes a future approval-gated workflow surface.
- Decide whether AI assistant concepts remain local/mock-only.
