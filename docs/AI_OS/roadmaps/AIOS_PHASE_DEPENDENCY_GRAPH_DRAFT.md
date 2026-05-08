# AI_OS Phase Dependency Graph Draft

Status: DRAFT
Mode: DRY_RUN-derived planning artifact

## Purpose

This file defines the safe dependency order for evolving AI_OS from the current scaffold state into a deployable AI-assisted trading infrastructure platform. It does not approve APPLY, deployment, broker integration, credentials, or live trading.

## Current Position

Current active work is Phase 13 dashboard UI implementation, with Stage 13.3 tool registry install and detection readiness committed locally and Stage 13.4 planned for fixture-only dashboard wire-up.

The roadmap phases below are strategic capability phases, not a replacement for existing stage numbers.

## Dependency Graph

```text
PHASE 01 FOUNDATION GOVERNANCE HARDENING
  -> PHASE 02 CONTEXT PERSISTENCE + MEMORY SYSTEMS
  -> PHASE 03 SCAFFOLD NORMALIZATION
  -> PHASE 04 DASHBOARD + HUMAN CONTROL LAYER
  -> PHASE 05 REPORTING + TELEMETRY ENGINE
  -> PHASE 06 TOOL REGISTRY + AGENT CONTROL
  -> PHASE 07 SIGNAL INTELLIGENCE SYSTEMS
  -> PHASE 08 EXECUTION ENGINE
  -> PHASE 09 AI VALIDATION LAYER
  -> PHASE 10 AZURE PRODUCTION HARDENING
  -> PHASE 11 AUTONOMOUS AI_OS OPERATIONS
  -> PHASE 12 COMMERCIALIZATION + PLATFORMIZATION
```

## Parallel Work Allowed

Some phases can advance in DRY_RUN planning at the same time, but APPLY sequencing must remain gated.

| Capability | Can Plan In Parallel | Can APPLY Before Dependency Complete |
| --- | --- | --- |
| Governance docs | Yes | Yes, with protected-file approval |
| Context packets | Yes | Yes, if no protected overwrite |
| Scaffold inventory | Yes | Yes, non-destructive only |
| Dashboard fixture UI | Yes | Yes, after UI dry-run |
| Telemetry preview | Yes | Yes, fixture-only |
| Tool registry display | Yes | Yes, fixture-only |
| Signal schema | Yes | Yes, no live data |
| Backtesting ingestion | Yes | Only after schema approval |
| Execution engine | Planning only | No |
| AI validation | Planning only | No runtime until signal/risk gates |
| Azure production | Planning only | No deployment |
| Autonomy | Planning only | No autonomous APPLY |
| Commercialization | Planning only | No platform launch |

## Critical Blocking Dependencies

### Execution Blockers

- Trading readiness boundary must remain enforced.
- `execution_allowed` must remain false until separate approval.
- Paper-trading evidence must exist before broker sandbox work.
- Risk controls must be validated before broker abstraction.
- AI validation must block trades before any execution pipeline.

### Azure Blockers

- Secrets model must be approved.
- Auth model must be approved.
- Observability and rollback must be defined.
- CI/CD must include safety gates.
- No public endpoint before governance review.

### Dashboard Blockers

- Dashboard must remain read-only until action approval model is implemented.
- Fixture sources must be validated before live adapters.
- Static preview and React parity must be addressed before production dashboard decisions.

### Autonomy Blockers

- No self-healing APPLY.
- No autonomous protected-file edits.
- No autonomous cleanup.
- No unattended trading, deployment, secrets, or git push.

## Phase Gate Requirements

### Gate 01: Governance Ready

- Protected file policy confirmed.
- Source-of-truth map created.
- Duplicate prevention rules documented.
- MISMATCH and INVALID DATA rules operational.

### Gate 02: Continuity Ready

- Checkpoint format normalized.
- Recovery packets defined.
- Session handoff workflow tested in DRY_RUN.
- Operator continuity fields defined.

### Gate 03: Scaffold Ready

- Folder ownership map reviewed.
- Schema registry drafted.
- Duplicate candidates listed without destructive actions.
- Missing purpose-note candidates handled by dry-run plan.

### Gate 04: Dashboard Ready

- Fixture-driven panels visible.
- Mobile behavior validated.
- Approval gates displayed.
- No live API, credential, deployment, broker, or trading action.

### Gate 05: Telemetry Ready

- Telemetry schema approved.
- Retention policy drafted.
- Report writer boundaries approved.
- Dashboard metrics sourced from safe fixtures.

### Gate 06: Agent Control Ready

- Tool registry health visible.
- Agent permissions documented.
- Agent audit log plan exists.
- Multi-agent APPLY requires human approval.

### Gate 07: Signal Ready

- Signal schema validated.
- Strategy registry validated.
- Backtest evidence rules approved.
- Historical replay fixture validated.

### Gate 08: Execution Design Ready

- Broker abstraction is design-only.
- OANDA readiness checklist complete.
- Risk controls validated with fixtures.
- Fail-safe matrix complete.

### Gate 09: AI Validation Ready

- Deterministic validators precede AI review.
- Confidence scoring rules reviewed.
- Disagreement handling defined.
- Trade blocking logic validated.

### Gate 10: Azure Ready

- Key Vault and managed identity design approved.
- CI/CD safety gates approved.
- Observability and rollback approved.
- Auth and backup plan approved.

### Gate 11: Autonomy Ready

- Self-audit is read-only.
- Repair proposals require approval.
- Bootstrap engine cannot self-replicate without approval.
- Stop conditions tested.

### Gate 12: Platform Ready

- Tenant isolation design approved.
- Privacy and compliance review complete.
- Operator onboarding complete.
- Hosted vs local deployment model chosen.

## Immediate Dependency Recommendation

The next safe dependency is:

```text
Phase 04 dashboard fixture work -> Stage 13.4 Tool Registry Dashboard UI Wire-Up
```

This is safe only if it remains fixture-only and does not call real APIs, accounts, installs, secrets, deployment paths, broker paths, or live detection.
