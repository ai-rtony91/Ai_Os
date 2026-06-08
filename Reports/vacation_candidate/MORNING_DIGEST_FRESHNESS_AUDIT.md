# Morning Digest Freshness Audit

Packet ID: MORNING_DIGEST_FRESHNESS_AUDIT_001
Lane: MORNING_DIGEST_FRESHNESS
Mode: DRY_RUN
Branch: feature/full-operator-relief-closed-loop-v1
Worktree: C:\Dev\Ai.Os
Audit date: 2026-06-07
Created by: Codex CLI Worker

## Executive Finding

Morning Digest is not yet trustworthy enough for 12-hour or overnight operator absence because it can display a fresh-looking latest view while its inputs come from older cycles, legacy Relay records, historical approvals, mock/dashboard examples, or a different repo state.

The failure is not one bad file. It is a missing freshness boundary between:

- digest artifact freshness,
- source evidence freshness,
- current repo/worktree state,
- Night Supervisor cycle state,
- dashboard display state,
- SOS notification state,
- approval and protected-action authority.

The shortest path is not new architecture. The shortest path is to make Morning Digest consume one source-owner freshness classification before it emits operator-facing status, dashboard cards, or SOS/no-SOS conclusions.

## Source Material Read

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `Reports/vacation_candidate/VACATION_KILLER_BLOCKERS.md`
- `Reports/vacation_candidate/VACATION_BASELINE_CLASSIFICATION.md`
- `Reports/vacation_candidate/EVIDENCE_FRESHNESS_RESOLVER_DISCOVERY.md`
- `telemetry/morning_digest/MORNING_DIGEST_LATEST.md`
- `telemetry/morning_digest/MORNING_DIGEST_STATE.json`
- `telemetry/morning_digest/PI5_PROGRESS_REPORT_LATEST.json`
- `telemetry/morning_digest/PROTECTED_ACTION_READINESS_LATEST.json`
- `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json`
- `telemetry/night_supervisor/last_notified.json`
- `telemetry/runtime/runtime_state.json`
- `automation/orchestration/reports/New-AiOsMorningBrief.ps1`
- `automation/orchestration/reports/Test-AiOsMorningBrief.DRY_RUN.ps1`
- `apps/dashboard/server.js`
- `apps/dashboard/src/runtimeVisibilityAdapter.js`
- `services/telemetry/runtimeVisibility.ts`
- Morning Digest, Morning Brief, Night Supervisor, telemetry, dashboard, SOS, Relay, and freshness references by read-only search

## Current Morning Digest Inputs

The current Morning Digest path is:

- `telemetry/morning_digest/MORNING_DIGEST_LATEST.md`
- `telemetry/morning_digest/MORNING_DIGEST_STATE.json`

Observed input behavior:

- `MORNING_DIGEST_LATEST.md` is titled `Morning Digest - 2026-06-02`.
- `MORNING_DIGEST_STATE.json` has `generated_at` of `2026-06-02T00:02:51Z`.
- It includes a `repo_state` claiming branch `main`, clean repo, no changed files, and no untracked files.
- Current observed branch is `feature/full-operator-relief-closed-loop-v1`, ahead of origin by 3, with dirty and untracked paths.
- It includes Relay approvals, Relay done records, operation glue examples, Night Supervisor config files, old reports, and bridge state as raw evidence.
- It reports `20 items completed`, `16 blocked`, `45 need approval`, and `81 evidence items seen`.

Classification: `STALE` for current operator-relief decisions, `HISTORICAL` as a prior digest artifact.

## Current Morning Brief Inputs

`automation/orchestration/reports/New-AiOsMorningBrief.ps1` reads:

- `telemetry/morning_digest/MORNING_DIGEST_LATEST.md`
- `telemetry/morning_digest/MORNING_DIGEST_STATE.json`
- `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json`
- `control/cycle/last_marker.json`
- `relay/done/*.task.json`
- `relay/error/*.task.json`
- `relay/approvals/*`
- `telemetry/night_supervisor/{date}/`
- `control/self_continuation/BACKLOG.json`
- current `git status --short`

Current Morning Brief freshness behavior:

- Missing digest, digest state, or bridge state becomes `BLOCKED`.
- Empty digest, digest state, or bridge state becomes `BLOCKED`.
- Evidence older than 18 hours becomes `WARN`.
- JSON `generated_at` is used when present; otherwise file modified time is used.
- It produces a preview by default and writes only with `-Apply`.

Classification: `CURRENT` as a read-only preview tool, `BLOCKED` as a vacation proof source until it checks source-owner freshness instead of only file age and `generated_at`.

## Current Night Supervisor Inputs

Relevant Night Supervisor and bridge inputs include:

- `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json`
- `telemetry/night_supervisor/reports/night_summary_2026-06-05.json` as referenced by current progress outputs
- `automation/orchestration/night_supervisor/NIGHT_SUPERVISOR_CONFIG.json`
- `automation/orchestration/night_supervisor/NIGHT_SUPERVISOR_REPORT.schema.json`
- `automation/orchestration/night_supervisor/NIGHT_SUPERVISOR_SAFETY_POLICY.json`
- `automation/orchestration/night_supervisor/README.md`
- `automation/orchestration/night_supervisor/Invoke-AiOsAutonomyBridge.DRY_RUN.ps1`
- `telemetry/runtime/runtime_state.json`
- Relay and operation-glue source paths included in bridge state

Current Night Supervisor projection behavior:

- `AUTONOMY_BRIDGE_STATE.json` is generated at `2026-06-06T02:40:44Z`.
- It reports `NEEDS_APPROVAL`, `0 active blockers`, `1 active approval decisions`, and `99 detail evidence items seen`.
- It includes many Relay paths classified as `HISTORICAL_EVIDENCE`, `COMPLETED_RECORD`, `SAMPLE_OR_EXAMPLE`, or `NOISE`.
- It includes `telemetry/morning_digest/MORNING_DIGEST_STATE.json` as an input even though that digest state is older than the bridge state.
- It is evidence-only and blocks live trading, broker, secrets, worker launch, packet mutation, approval mutation, staging, commit, and push.

Classification: `CURRENT` as a bridge projection for the 2026-06-06 cycle, `STALE` for current repo state on 2026-06-07, and `BLOCKED` for approval/protected-action authority.

## Evidence Ownership

| Evidence area | Current owner | Morning Digest role | Classification for current decisions |
|---|---|---|---|
| Work packet state | `automation/orchestration/work_packets/` | Should consume only | `BLOCKED` until direct current read exists |
| Approval state | `automation/orchestration/approval_inbox/` | Should consume only | `BLOCKED` until canonical approval read exists |
| Worker state | `automation/orchestration/workers/` | Should consume only | `BLOCKED` until current worker state read exists |
| Validator state | `automation/orchestration/validators/` | Should consume only | `BLOCKED` if validator not current |
| Runtime projection | `telemetry/runtime/` | May summarize projection | `STALE` if generated from old events |
| Night bridge projection | `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json` | May summarize projection | `STALE` after current repo state changes |
| Morning Digest artifacts | `telemetry/morning_digest/` | Owns digest artifact only | `STALE` or `HISTORICAL` for current state |
| Relay artifacts | `relay/` and `Relay/` | Detail-only unless promoted | `HISTORICAL` by default |
| Dashboard data | `apps/dashboard/`, `services/` | Display consumer | `BLOCKED` as authority, `CURRENT` only as display |
| Reports | `Reports/` | Audit evidence | `HISTORICAL` for runtime decisions |

## Freshness Ownership

Freshness must follow the source owner, not the consuming view.

Morning Digest may own whether the digest artifact is new. It does not own whether a queue item, approval item, worker status, validator result, runtime status, or SOS condition is current.

Canonical freshness source should be the future Evidence Freshness Resolver classification over existing owners:

```text
,source owner evidence
-> resolver classification
-> Morning Digest summary
-> Dashboard display
-> SOS display/wake decision
```

The resolver must not create a queue, approval system, bridge, schema, or new authority. It should classify source evidence as `CURRENT`, `STALE`, `HISTORICAL`, `SUPERSEDED`, or `BLOCKED`.

## Stale/Current Mismatch Sources

1. `MORNING_DIGEST_LATEST.md` says `2026-06-02`, while current date is `2026-06-07`.
2. `MORNING_DIGEST_STATE.json` records repo state as `main` and clean, while current observed state is feature branch with dirty/untracked files.
3. `AUTONOMY_BRIDGE_STATE.json` is newer than the digest state but still includes older digest state as a source input.
4. `PI5_PROGRESS_REPORT_LATEST.json` explicitly warns that Morning Digest markdown is stale and still dated `2026-06-02`.
5. `PI5_PROGRESS_REPORT_LATEST.json` says approval counts differ after noise filtering: active `1`, bridge `1`, digest `45`.
6. Relay approvals from 2026-05-30 and 2026-05-31 still appear as blocked or approval-needed items in older digest outputs.
7. Relay `done`, `processed`, `outbox`, and `reports` records are mixed with active-looking status labels.
8. Dashboard can serve `AUTONOMY_BRIDGE_STATE.json` live, but dashboard display still has mock-source and projection-source split risk.
9. `last_notified.json` records a `BLOCKED` notification from `2026-06-02`; it cannot prove the blocker remains current or resolved.
10. `runtime_state.json` reports runtime freshness as fresh while active packet evidence is stale, proving projection freshness and source freshness can diverge.

## Dashboard Dependency On Digest Data

Dashboard dependencies discovered:

- `apps/dashboard/server.js` serves `/live-data/autonomy_bridge_state.json` from `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json`.
- `AUTONOMY_BRIDGE_STATE.json` includes `dashboard_cards` with `details_ref` to `telemetry/morning_digest/MORNING_DIGEST_LATEST.md`.
- `apps/dashboard/src/runtimeVisibilityAdapter.js` supports `MOCK_DATA`, `LOCAL_API_READ_ONLY`, and `UNKNOWN` source labels.
- The dashboard adapter warns not to treat stale telemetry as proof that no night runtime activity occurred.
- Dashboard mock data includes stale workers, SOS alerts, approval queues, and runtime visibility examples.

Dashboard must not treat Morning Digest as a source of current truth. It should display Morning Digest as a summary only after the resolver marks its source inputs current.

## SOS Dependency On Digest Data

SOS-related evidence discovered:

- `telemetry/morning_digest/PROTECTED_ACTION_READINESS_LATEST.json` emits `display_alert`, `sos_wake_required`, and `wake_class`.
- `telemetry/morning_digest/PI5_PROGRESS_REPORT_LATEST.json` emits `display_alert=true`, `sos_wake_required=false`, and stale state warnings.
- `telemetry/night_supervisor/last_notified.json` records a prior `BLOCKED` key from `2026-06-02T00:02:51Z`.
- `relay/reports/SOS_OUTBOX/SOS_20260602_072336_795.md` and `Relay/reports/SOS_OUTBOX/SOS_20260602_072336_795.md` exist as historical SOS evidence references.
- `Invoke-AiOsAutonomyBridge.DRY_RUN.ps1` references `display_alert`, `sos_wake_required`, and `ALERT_LATEST.md`.

SOS must not depend on digest artifact age alone. It needs current unsuperseded blocker evidence. A stale digest should never suppress SOS, and a historical SOS file should never re-wake Anthony without a current blocker transition.

## Canonical Current-State Source

Current-state source should be:

- Canonical queue/packet owner for packet state.
- Canonical approval inbox for approval state.
- Canonical validator evidence for validation state.
- Canonical worker state for worker health and lease state.
- Current Git preflight for branch/worktree status.
- Night Supervisor only as the current cycle projection.
- Morning Digest only as a consumer-facing brief.
- Dashboard only as a display surface.
- Relay only as legacy fallback or historical evidence unless explicitly promoted.

Morning Digest is not canonical current state.

## Canonical Freshness Source

Canonical freshness source should be a resolver classification applied to source-owner evidence.

Minimum fields needed per evidence item:

- source path
- source owner
- source type
- source timestamp
- projection timestamp
- packet ID or cycle ID when present
- branch/worktree when repo state matters
- source hash or dedupe key
- current decision purpose
- classification
- classification basis
- superseded-by path or event when applicable
- next safe action

## Canonical Stale-State Rules

| Evidence type | Current rule | Stale rule |
|---|---|---|
| Digest markdown | Current only for same digest window and current source inputs | Stale if older than 18 hours or source inputs are stale |
| Digest state JSON | Current only when `generated_at` and source inputs match active cycle | Stale if older than bridge/current state or source mismatch exists |
| Bridge state | Current only for latest Night Supervisor cycle and unchanged repo/queue/approval state | Stale after newer repo, queue, approval, worker, validator, or cycle evidence |
| Runtime state | Current only for projection heartbeat | Source evidence can still be stale |
| Git state | Current only at time of check | Stale after mutation, branch switch, staging, commit, or 15 minutes for decisions |
| Relay record | Historical by default | Current only if explicitly promoted by current owner evidence |
| Approval evidence | Current only for exact action/scope/session and unconsumed state | Stale if expired, consumed, mismatched, historical, or moved |
| SOS notification | Current only for unsuperseded active blocker | Stale if blocker resolved, newer blocker exists, or last notification is old |

## Digest Freshness Rules

Morning Digest should classify itself as:

- `CURRENT` only when artifact age is inside the digest window and every status-impacting source input is `CURRENT`.
- `STALE` when artifact age is old, source inputs are old, branch/worktree differs, or digest counts differ from current bridge/approval evidence.
- `HISTORICAL` when it is a prior digest kept for reference.
- `SUPERSEDED` when a newer digest for the same purpose exists.
- `BLOCKED` when source freshness cannot be determined for a decision that affects 12-hour or overnight absence.

## Morning Brief Freshness Rules

Morning Brief should:

- Preserve its current preview-by-default behavior.
- Keep the 18-hour artifact freshness check as a shallow check.
- Add source-owner freshness from the resolver before claiming readiness.
- Report projection freshness and source freshness separately.
- Treat Relay historical records as detail-only.
- Report stale `MORNING_DIGEST_LATEST.md` as `STALE`, not merely `WARN`, when used for vacation readiness.
- Report missing current queue/approval/validator source state as `BLOCKED` for vacation readiness.

## Night Supervisor Freshness Rules

Night Supervisor should:

- Treat the active cycle projection as current only for its cycle.
- Treat proposed runtime state as projection, not active authority.
- Mark stale source evidence as blocking unattended continuation when the source affects queue, approval, validator, worker, SOS, or protected actions.
- Keep approval-needed and protected-action stop points as evidence-only.
- Never let current bridge generation time make stale digest, Relay, or approval records current.

## Evidence Path Classification

| Evidence path | Current observed role | Classification | Reason |
|---|---|---|---|
| `telemetry/morning_digest/MORNING_DIGEST_LATEST.md` | Operator digest markdown | `STALE` | Dated `2026-06-02`; current date is `2026-06-07`; repo state inside does not match current branch/worktree. |
| `telemetry/morning_digest/MORNING_DIGEST_STATE.json` | Digest source state | `STALE` | `generated_at` is `2026-06-02T00:02:51Z`; records branch `main` clean while current branch is feature branch dirty. |
| `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json` | Bridge projection | `STALE` | Newer than digest but still from `2026-06-06`; includes stale digest and historical Relay inputs; not current for 2026-06-07 branch state. |
| `telemetry/morning_digest/PI5_PROGRESS_REPORT_LATEST.json` | Display progress projection | `STALE` | Generated `2026-06-06`; explicitly lists stale digest warnings and old repo state. |
| `telemetry/morning_digest/PROTECTED_ACTION_READINESS_LATEST.json` | Protected action readiness projection | `STALE` | Recommendation-only output from `2026-06-06`; cannot authorize current protected actions. |
| `telemetry/runtime/runtime_state.json` | Runtime visibility projection | `STALE` for source, `HISTORICAL` for current decisions | Generated `2026-06-01`; packet evidence inside is already marked stale. |
| `telemetry/night_supervisor/last_notified.json` | Notification dedupe marker | `HISTORICAL` | Last key from `2026-06-02`; cannot prove current blocker state or suppress current SOS. |
| `relay/reports/ALERT_LATEST.md` | Legacy latest alert | `HISTORICAL` | Relay latest files are legacy fallback and can be superseded by newer bridge/digest evidence. |
| `relay/reports/SOS_OUTBOX/SOS_20260602_072336_795.md` | Prior SOS file | `HISTORICAL` | Prior SOS evidence only; not current blocker proof. |
| `Relay/reports/SOS_OUTBOX/SOS_20260602_072336_795.md` | Duplicate-casing prior SOS file | `HISTORICAL` | Same historical risk plus Windows casing ambiguity. |
| `relay/reports/MORNING_BRIEF_2026-06-01.md` | Prior Relay morning brief | `HISTORICAL` | Old Relay report, detail-only. |
| `Relay/reports/MORNING_BRIEF_2026-06-01.md` | Duplicate-casing prior brief | `HISTORICAL` | Old Relay report plus casing ambiguity. |
| `automation/orchestration/reports/New-AiOsMorningBrief.ps1` | Morning Brief generator | `CURRENT` as inspected source, `BLOCKED` as proof owner | Existing generator is readable and preview-safe, but not source-owner freshness complete. |
| `automation/orchestration/reports/Test-AiOsMorningBrief.DRY_RUN.ps1` | Morning Brief dry-run validator | `CURRENT` as validator script, `BLOCKED` as vacation proof | Proves preview/no-write behavior, not current source trust. |
| `apps/dashboard/server.js` | Dashboard local server | `CURRENT` as display source, `BLOCKED` as authority | Can serve bridge JSON but does not classify source freshness. |
| `apps/dashboard/src/runtimeVisibilityAdapter.js` | Dashboard runtime adapter | `CURRENT` as display source | Includes source labels and stale warning text; still display-only. |
| `services/telemetry/runtimeVisibility.ts` | Runtime visibility logic | `CURRENT` as service logic | Defines fresh/stale/unknown for runtime heartbeat, not full evidence ownership. |
| `relay/approvals/*.approval.*` | Legacy approval evidence | `HISTORICAL` | Relay legacy fallback; not canonical approval authority. |
| `control/operation_glue/APPROVAL_INBOX.json` | Operation glue approval reference | `SUPERSEDED` or `HISTORICAL` | Canonical harness selected `automation/orchestration/approval_inbox/`; operation glue is not current owner. |
| `automation/orchestration/approval_inbox/` | Canonical approval owner | `BLOCKED` in this audit | Protected path was not inspected deeply under report-only scope; must be read in a later dedicated proof. |
| `automation/orchestration/work_packets/` | Canonical packet owner | `BLOCKED` in this audit | Protected path was not inspected deeply under report-only scope; must be read in a later dedicated proof. |
| `Reports/vacation_candidate/EVIDENCE_FRESHNESS_RESOLVER_DISCOVERY.md` | Freshness discovery report | `CURRENT` for this audit, `HISTORICAL` for runtime | Current supporting report, not runtime authority. |
| `Reports/vacation_candidate/VACATION_BASELINE_CLASSIFICATION.md` | Dirty baseline report | `STALE` for current Git state if any mutation occurs | Current enough for this audit context, but not a runtime proof. |

## Root Causes Of Stale Digest Behavior

1. Morning Digest has no source-owner freshness gate.
2. `*_LATEST.*` file naming is treated like currentness even when contents are old.
3. Digest generation time and source evidence time are not separated.
4. Bridge state can be newer than digest state while still consuming stale digest inputs.
5. Relay historical and sample records are mixed with active-looking statuses.
6. Current Git state is not bound to digest validity.
7. Dashboard cards link to digest detail without resolver classification.
8. SOS dedupe state can outlive the blocker evidence it represents.
9. Approval counts differ across digest, bridge, and filtered approval-intelligence outputs.
10. Morning Brief shallow freshness checks do not prove queue, approval, validator, worker, or SOS source truth.

## Top 10 Freshness Defects

| Rank | Defect | Impact | Fastest fix |
|---:|---|---|---|
| 1 | Digest says branch `main` clean while actual branch is feature branch dirty | False current-state confidence | Bind digest validity to current Git preflight. |
| 2 | Digest markdown is five days old | Stale operator handoff | Mark digest `STALE` past 18 hours or superseded cycle. |
| 3 | Digest state is older than bridge state | Mixed-cycle reporting | Require one active cycle ID across digest and bridge. |
| 4 | Bridge includes stale digest as source input | Fresh projection from stale source | Separate projection freshness from source freshness. |
| 5 | Relay historical approvals inflate approval counts | False approval burden | Filter Relay historical records to detail-only. |
| 6 | Digest says 45 approvals while bridge/progress say 1 active approval | Conflicting operator action | Use canonical approval owner and filtered projection count. |
| 7 | `last_notified.json` can suppress or confuse current SOS | Missed wake or duplicate wake | Tie notification dedupe to active blocker hash and freshness. |
| 8 | Dashboard can display bridge cards with stale digest detail refs | False live cockpit | Display resolver classification beside every card. |
| 9 | Runtime freshness can be fresh while packet evidence is stale | Misleading health | Show runtime heartbeat freshness separately from evidence freshness. |
| 10 | Morning Brief validates preview/no-write but not source freshness | Insufficient vacation proof | Add resolver-based source checks to Morning Brief proof. |

## Fastest Fix Sequence

1. Create Morning Digest freshness acceptance tests as report-only evidence.
2. Build a preview-only Evidence Freshness Resolver scaffold with fixtures for digest, bridge, Relay, runtime, dashboard, approval, and SOS cases.
3. Add a no-write Morning Digest freshness proof that reads current digest inputs and emits resolver classifications.
4. Require digest and bridge cycle alignment before Morning Digest can be `CURRENT`.
5. Treat stale or unknown source freshness as `BLOCKED` for 12-hour and overnight readiness.
6. Mark Relay records historical by default unless current canonical owner evidence promotes the exact item.
7. Mark dashboard cards display-only unless resolver classification says source inputs are current.
8. Tie SOS `last_notified` to current blocker hash and expire it when blocker evidence is stale or superseded.
9. Rerun 12-hour dry-run proof with current branch/worktree state.
10. Use the proof result as Morning Digest's vacation-readiness gate.

## Vacation-Readiness Impact

| Absence window | Impact of current digest state |
|---|---|
| 4 hours | Manageable if Anthony checks current Git/status manually first; digest alone is not enough. |
| 12 hours | Blocking. Digest cannot yet prove current queue, approval, validator, worker, and SOS state. |
| Overnight | Blocking. Stale digest and stale SOS dedupe can hide or misclassify blockers. |
| Weekend | Hard blocking. Multi-cycle evidence expiration and superseded detection are not proven. |

Updated readiness implication:

- 4-hour readiness remains near baseline-classified level if digest is treated as historical.
- 12-hour readiness should not advance until digest and bridge source freshness agree.
- Overnight readiness should not advance until SOS uses current unsuperseded blocker evidence.
- Weekend readiness should not advance until digest freshness survives multiple cycles.

## Exact Next APPLY Packet Recommendation

Packet ID: MORNING_DIGEST_FRESHNESS_ACCEPTANCE_TESTS_001
Mode: APPLY report-only
Allowed path: `Reports/vacation_candidate/`
Create only: `Reports/vacation_candidate/MORNING_DIGEST_FRESHNESS_ACCEPTANCE_TESTS.md`

Required report contents:

- PASS cases for current digest, aligned bridge state, current Git state, and current source evidence.
- FAIL cases for stale digest markdown, stale digest state, branch/worktree mismatch, stale Relay approval, historical SOS, stale `last_notified`, and fresh projection from stale source.
- Classification matrix for `CURRENT`, `STALE`, `HISTORICAL`, `SUPERSEDED`, and `BLOCKED`.
- Minimum acceptance threshold for 12-hour and overnight readiness.
- Exact future preview-only scaffold boundary for a resolver-backed Morning Digest proof.

## Recommendation

Recommendation: VALIDATE, then BUILD.

Do not edit Morning Digest, Dashboard, Night Supervisor, Relay, or SOS code yet. First prove the classification rules in a report-only acceptance suite. Then build a preview-only resolver proof that can classify the current digest artifacts without writing queues, approvals, telemetry, schemas, or bridges.

Status: DRY_RUN audit complete. No source code, scripts, schemas, queues, approvals, bridges, commits, pushes, or telemetry writes were created.
