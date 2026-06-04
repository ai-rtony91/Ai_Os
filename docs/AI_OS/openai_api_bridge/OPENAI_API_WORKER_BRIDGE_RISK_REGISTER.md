# OpenAI API Worker Bridge Risk Register

Status: DRY_RUN planning artifact
Scope: bridge safety risks and mitigations

## Risk Summary

The OpenAI API Worker Bridge can reduce manual relay work, but it also creates risk if planning output is mistaken for authority.

Primary control: the bridge may draft, classify, and summarize. It must not execute, approve, mutate protected state, store secrets, or touch trading execution.

## Risk Register

| ID | Risk | Severity | Mitigation | Status |
| --- | --- | --- | --- | --- |
| OAI-BRIDGE-001 | Planner output is treated as approval. | HIGH | Mark output as evidence only; require approval inbox and human approval for APPLY/protected actions. | BLOCKED from automation |
| OAI-BRIDGE-002 | API key or secret appears in docs, fixtures, logs, or prompts. | HIGH | Use environment variable names only; no `.env`; no key logging; no key fixtures. | BLOCKED |
| OAI-BRIDGE-003 | Live OpenAI API call is added before governance is approved. | HIGH | Fixture-only first APPLY; no SDK install; no API client. | BLOCKED |
| OAI-BRIDGE-004 | Bridge mutates Night Supervisor runtime evidence. | HIGH | Forbid `telemetry/night_supervisor/`, `control/`, locks, memory, approval inbox, telemetry, and Night Supervisor runtime paths. | BLOCKED |
| OAI-BRIDGE-005 | Bridge bypasses `AGENTS.md` prompt routing or execution token rules. | HIGH | Require Codex-ready packets to preserve routing marker, execution token, identity fields, lane, validator chain, and stop point. | BLOCKED |
| OAI-BRIDGE-006 | Bridge creates duplicate authority. | MEDIUM | Run duplicate-intent search before new docs or folders; link to existing source docs. | MITIGATED |
| OAI-BRIDGE-007 | Bridge launches workers or starts background automation. | HIGH | Planning layer only; worker launch blocked until separate governance. | BLOCKED |
| OAI-BRIDGE-008 | Bridge writes approval records or changes packet state. | HIGH | Approval summaries only; approval inbox mutation blocked. | BLOCKED |
| OAI-BRIDGE-009 | Bridge enables broker, OANDA, live trading, webhooks, or real orders. | CRITICAL | Mark any such scope `BLOCKED`; Trading Lab remains paper-only. | BLOCKED |
| OAI-BRIDGE-010 | Validator success is interpreted as execution permission. | HIGH | Validators are evidence only; protected actions require explicit human approval. | BLOCKED from auto-execution |
| OAI-BRIDGE-011 | Generated packet has incomplete identity or stop fields. | MEDIUM | Packet must include identity marker, supervisor, worker, zone, lane, paths, approval authority, validator chain, and stop point. | REVIEW_REQUIRED |
| OAI-BRIDGE-012 | Future APPLY expands into runtime or schema paths without approval. | MEDIUM | First APPLY stays inside approved docs/fixtures path; expanded schema path requires explicit scope expansion. | REVIEW_REQUIRED |

## Severity Rules

Use:

- `CRITICAL` for broker, OANDA, live trading, real orders, real webhooks, or credential exposure.
- `HIGH` for protected action bypass, Night Supervisor interference, approval mutation, secret handling, or runtime mutation.
- `MEDIUM` for duplicate authority, incomplete packets, unclear ownership, or scope expansion.
- `LOW` for wording, formatting, or non-authority documentation drift.

## Required Risk Controls

Every future bridge packet must include:

- allowed paths.
- forbidden paths.
- mode.
- lane.
- branch.
- worktree.
- approval authority.
- validator chain.
- stop point.
- secret handling statement.
- trading safety statement.
- Night Supervisor non-interference statement when relevant.

## Blocked Escalations

The following remain blocked until future governance approval:

- live OpenAI API calls.
- API key setup.
- package installs.
- runtime worker bridge.
- approval inbox writer.
- command executor.
- commit package executor.
- autonomous PR creation.
- telemetry writer.
- Night Supervisor integration.
- broker/OANDA/trading adapter.

## Review Trigger

Re-review this risk register before any future APPLY packet that:

- creates fixtures.
- creates schemas.
- adds executable code.
- changes allowed paths.
- mentions API credentials.
- mentions external APIs.
- touches runtime, telemetry, control, approvals, locks, memory, broker, OANDA, or trading.
