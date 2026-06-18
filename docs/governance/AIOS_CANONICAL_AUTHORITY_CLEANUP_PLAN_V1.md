# AIOS Canonical Authority Cleanup Plan V1

## Status

Status: CLEANUP_PLAN

Zone: GOVERNANCE

Human Owner: Anthony Meza

## Purpose

Define the cleanup plan AIOS will use to identify duplicate, stale, conflicting, or false-canonical authority files before more dashboard, broker, Supertrend, watchlist, or autonomy implementation work proceeds.

This document is a plan only. It does not edit, retire, redirect, rename, consolidate, delete, promote, or replace any existing file. Future cleanup work requires a separate scoped packet, Human Owner approval where required, exact allowed paths, exact forbidden paths, validation, and a stop point.

## Authority Boundary

This plan works under:

- `AGENTS.md`
- `README.md`
- `docs/governance/source-of-truth-map.md`
- `docs/forex_delivery/AIOS_MASTER_OPERATOR_DASHBOARD_FOREX_AUTONOMY_BACKLOG_V1.md`
- `docs/forex_delivery/AIOS_AUTO_EXIT_INTELLIGENCE_GATE_V1.md`
- `docs/forex_delivery/AIOS_PL_TRUTH_LAYER_REQUIREMENTS_V1.md`
- `docs/dashboard/AIOS_MINIMAL_OPERATOR_DASHBOARD_CONTRACT_V1.md`
- `docs/security/AIOS_SECRET_PERSISTENCE_RUNTIME_BRIDGE_CONTRACT_V1.md`

If this plan conflicts with root governance, source-of-truth ownership, risk policy, security authority, or Human Owner approval requirements, the stricter and higher authority wins.

## Core Rule

One domain gets one canonical authority source.

Redirect files may exist only when they clearly point to the canonical authority and do not create a competing instruction source. Stale files must not claim active authority. Duplicate status files must not conflict. Duplicate authority must be resolved before implementation work relies on that domain.

## Scope Boundary

- This packet creates the cleanup plan only.
- This packet does not edit existing files.
- This packet does not retire existing files.
- This packet does not redirect existing files.
- This packet does not delete existing files.
- This packet does not rename existing files.
- This packet does not approve broad cleanup.
- This packet does not authorize broker/API work, live trading, dashboard implementation, validator changes, runtime mutation, secret access, staging, committing, pushing, or PR creation.

## Domains

Future audit and cleanup packets must classify these domains:

- forex delivery
- live-trade evidence
- P/L truth
- auto-exit
- dashboard truth
- dashboard UI/operator
- secret handling
- runtime/orchestration
- broker bridge
- backup/snapshot
- legal/data
- SOS/escalation
- Supertrend/signal
- watchlist/chart

## Audit Output Model

Future cleanup packets must produce one structured record per domain:

```text
DOMAIN:
CANONICAL_FILE:
DUPLICATE_CANDIDATES:
STALE_CANDIDATES:
FALSE_CANONICAL_CANDIDATES:
REDIRECT_CANDIDATES:
CONFLICT_NOTES:
RECOMMENDED_ACTION:
HUMAN_APPROVAL_REQUIRED: true/false
```

`CANONICAL_FILE` must identify the single active authority for the domain or report `UNKNOWN` if no current authority can be safely selected.

`CONFLICT_NOTES` must identify any competing claims, stale status, unsafe instructions, or implementation assumptions that would confuse future workers.

`HUMAN_APPROVAL_REQUIRED` must be `true` when the recommended action would edit, retire, redirect, rename, delete, consolidate, promote, or otherwise change an authority-bearing file.

## Allowed Actions

Future cleanup packets may recommend only these action types:

- KEEP_CANONICAL
- MARK_STALE
- ADD_REDIRECT
- CONSOLIDATE
- RETIRE
- RENAME
- NO_ACTION

Recommendations are not execution authority. Each action must be approved and packetized before it changes the repo.

## Rules

- dashboard displays truth
- dashboard does not create truth
- reports are not automatically authority
- evidence is not strategy authority
- evidence files record truth; they do not become strategy authority
- stale files must not claim authority
- duplicate authority must be resolved before implementation
- one domain must not have two active canonical heads
- root authority and source-of-truth maps win over drafts, generated reports, archives, and stale source material
- redirect files must point clearly to the canonical authority and must not contain competing instructions
- duplicate status files must be reconciled before future implementation relies on them

## Fail-Closed Governance Rules

AIOS must block future implementation work for a domain if:

- two files claim canonical authority for the same domain
- dashboard has multiple truth sources
- live-trade evidence conflicts with P/L truth rules
- secret-handling docs conflict with the secret bridge contract
- broker bridge docs conflict with no-secret-output rules
- legal/data usage is unclear
- implementation would bypass a newer canonical authority
- a stale file still claims active authority
- reports or generated evidence are being treated as authority without promotion

## Relationship To Landed Authorities

Active authority inputs for this cleanup plan include:

- `AIOS_MASTER_OPERATOR_DASHBOARD_FOREX_AUTONOMY_BACKLOG_V1`
- `AIOS_AUTO_EXIT_INTELLIGENCE_GATE_V1`
- `AIOS_PL_TRUTH_LAYER_REQUIREMENTS_V1`
- `AIOS_MINIMAL_OPERATOR_DASHBOARD_CONTRACT_V1`
- `AIOS_SECRET_PERSISTENCE_RUNTIME_BRIDGE_CONTRACT_V1`

These documents guide the next AIOS phase. This cleanup plan does not replace them. It defines how future packets should find and resolve duplicate or stale authority around them.

## Future Execution Packets

Future cleanup work should be separated into scoped packets:

- `AIOS-CANONICAL-AUTHORITY-AUDIT-REPORT-V1`
- `AIOS-DASHBOARD-AUTHORITY-DEDUPLICATION-V1`
- `AIOS-FOREX-EVIDENCE-CHAIN-DEDUPLICATION-V1`
- `AIOS-SECRET-HANDLING-AUTHORITY-DEDUPLICATION-V1`
- `AIOS-SOURCE-OF-TRUTH-MAP-UPDATE-V1`

Each future packet must identify exact files, allowed paths, forbidden paths, expected edits, validation, approval authority, and stop point before APPLY work begins.

## Success Criteria

This cleanup plan succeeds when future AIOS workers can:

- identify the canonical authority for each domain
- identify stale or duplicate authority candidates without guessing
- separate reports, evidence, drafts, and generated outputs from true authority
- block implementation when authority conflicts are unresolved
- recommend one explicit next action per domain
- keep cleanup work approval-gated and reversible where practical

## Stop Conditions

Stop cleanup or implementation work if:

- the canonical file for a domain is unknown
- two or more files claim active authority for the same domain
- a cleanup action would touch files outside its approved paths
- a recommendation would delete, rename, retire, redirect, or consolidate files without Human Owner approval
- dashboard truth, P/L truth, auto-exit, secret handling, broker bridge, or legal/data authority is unclear
- broker/API calls, live trading, secret access, dashboard implementation, runtime mutation, validator changes, staging, committing, pushing, or PR creation are requested without separate approval
