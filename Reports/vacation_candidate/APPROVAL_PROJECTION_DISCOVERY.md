# Approval Projection Discovery

Packet ID: APPROVAL_PROJECTION_DISCOVERY_001
Lane: APPROVAL_PROJECTION_DISCOVERY
Mode: DRY_RUN
Branch: feature/full-operator-relief-closed-loop-v1
Worktree: C:\Dev\Ai.Os
Audit date: 2026-06-07
Created by: Codex CLI Worker

## Executive Finding

AI_OS has one canonical approval owner and many approval projections. The risk is that projection surfaces can look like approval authority, especially during vacation-mode reporting.

Canonical approval owner:

```text
automation/orchestration/approval_inbox/
```

Most other approval-related paths are display, telemetry, legacy Relay evidence, examples, service-local in-memory stores, or recommendation-only summaries. They can help Anthony see what needs review, but they must not approve APPLY, commit, push, merge, worker launch, scheduler creation, live trading, broker/API paths, secrets, or governance changes.

The approval projection layer should answer one question:

```text
What approval evidence should be shown to the operator, and what is its freshness/status?
```

It must not answer:

```text
Is this approved to execute?
```

That remains Anthony-owned and protected-action-gated.

## Source Material Read

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `Reports/vacation_candidate/VACATION_KILLER_BLOCKERS.md`
- `Reports/vacation_candidate/VACATION_BASELINE_CLASSIFICATION.md`
- `Reports/vacation_candidate/EVIDENCE_FRESHNESS_RESOLVER_DISCOVERY.md`
- `Reports/vacation_candidate/MORNING_DIGEST_FRESHNESS_AUDIT.md`
- `automation/orchestration/approval_inbox/APPROVAL_STATUS_RULES_001.md`
- `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
- `control/operation_glue/APPROVAL_INBOX.json`
- `telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.json`
- `apps/dashboard/mock-data/aios-approval-inbox-v1.example.json`
- `services/python_supervisor/approval_projector.py`
- `services/python_supervisor/approval_queue.py`
- `services/approvals/approvalInbox.ts`
- `services/approvals/approvalDecision.ts`
- `automation/orchestration/night_supervisor/Invoke-AiOsApprovalQueue.DRY_RUN.ps1`
- `automation/orchestration/approval_runner/README.md`
- Approval-related paths by read-only `rg --files` and `rg -n`

## Canonical Approval Owner

`automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json` explicitly declares:

- schema: `AIOS_APPROVAL_INBOX.v1`
- `authority_status`: `active_authority`
- `authority_scope`: `automation/orchestration/approval_inbox/`
- `approval_authority`: `Anthony Meza / Human Owner`
- active sources:
  - `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
  - `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
  - `automation/orchestration/approval_inbox/APPROVAL_STATUS_RULES_001.md`

It also states that Relay, Operation Glue, telemetry, Night Supervisor, Autonomy Bridge, and dashboard outputs are evidence or projection surfaces only.

Classification: `CANONICAL`.

## Canonical Approval Source

Canonical approval source should be:

```text
automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json
automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json
automation/orchestration/approval_inbox/APPROVAL_STATUS_RULES_001.md
```

These files define the active approval inbox, the current APPLY gate item, and status vocabulary.

Canonical approval does not automatically authorize protected actions. Even `approved_for_apply` is scoped only to the exact packet, allowed paths, validators, and risk notes. Commit and push remain separate approvals.

## Approval Projections

| Projection | Role | Authority risk |
|---|---|---|
| `telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.json` | Recommendation-only active approval card | Low if `approval_authority=false` remains visible |
| `telemetry/morning_digest/MORNING_BRIEF_V2_LATEST.json` | Operator summary of approval need | Medium because it embeds a future packet and counts cards |
| `telemetry/morning_digest/PROTECTED_ACTION_READINESS_LATEST.json` | Protected-action classification examples | Medium because it names protected actions |
| `telemetry/morning_digest/OPENAI_*_LATEST.*` | Recommendation-only OpenAI boundary summaries | Medium because external/API wording can be mistaken for permission |
| `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json` | Bridge projection of active approval count | Medium because dashboard can read it live |
| `services/python_supervisor/approval_projector.py` | Projection-only unifier into `telemetry/approvals/UNIFIED_APPROVALS.json` | Medium if output is treated as source authority |
| `services/python_supervisor/approval_queue.py` | Relay approval projection for Night Supervisor | Medium because it can write telemetry in APPLY mode |
| `automation/orchestration/night_supervisor/Invoke-AiOsApprovalQueue.DRY_RUN.ps1` | Approval queue preview wrapper | Low in DRY_RUN, blocked on non-main |
| `apps/dashboard/mock-data/*approval*` | UI fixture/display examples | High if displayed as active state |
| `services/approvals/*.ts` | In-memory service approval model | Medium-high because it can mutate in process and write telemetry |

## Approval Duplicates

Duplicate or competing approval surfaces discovered:

- `automation/orchestration/approval_inbox/`
- `automation/orchestration/approval_inbox/archive/`
- `automation/orchestration/approval_inbox/AIOS_APPROVAL_QUEUE.example.json`
- `automation/orchestration/approvals/APPROVE_PR_*.json`
- `relay/approvals/`
- `Relay/approvals/`
- `control/operation_glue/APPROVAL_INBOX.json`
- `telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.*`
- `telemetry/morning_digest/PROTECTED_ACTION_READINESS_LATEST.*`
- `telemetry/approvals/UNIFIED_APPROVALS.json` as planned projector output
- `apps/dashboard/mock-data/aios-approval-inbox-v1.example.json`
- `apps/dashboard/mock-data/night_supervisor_approval_queue.sample.json`
- `services/approvals/approvalInbox.ts` in-memory store

Only `automation/orchestration/approval_inbox/` should remain canonical. Everything else should be projected, historical, example, or blocked from authority use.

## Approval Consumers

| Consumer | What it needs | Boundary |
|---|---|---|
| Night Supervisor | current approval count, stale/unsafe approval risk, next safe action | Evidence only; no approval mutation |
| Morning Digest | human-needed cards, approval freshness, stale/noise filtering | Summary only; no approval authority |
| Dashboard | display cards and detail refs | Display only; no approve buttons without separate approved workflow |
| SOS | wake only when approval blocks safe continuation or protected action needs Anthony | Wake classification only; no approval decision |
| Codex final evidence adapter | parse final report approval-needed status | Evidence only |
| ChatGPT packet adapter | classify approval-required packet fields | Preview only, executable=false |
| Protected Action Gate | decide whether action may be presented for explicit approval | Does not replace Anthony |
| Commit/Push Gate | verify commit or push readiness | Does not grant commit or push without explicit approval |

## Projection Rules

1. Projection output must include `approval_authority=false` unless it is the canonical approval owner.
2. Projection output must include `approval_mutation=false`.
3. Projection output must include `recommendation_only=true`.
4. Projection output must include source paths and source timestamps.
5. Projection output must preserve the canonical source path when referencing an active approval.
6. Projection output must not widen approval scope.
7. Projection output must not convert `completed`, `expired`, `historical`, `sample`, or `example` records into pending approvals.
8. Projection output must show stale and superseded status.
9. Projection output must never write to `automation/orchestration/approval_inbox/`.
10. Projection output must never execute, stage, commit, push, merge, create PRs, launch workers, create schedulers, call APIs, touch secrets, or touch broker/live trading paths.

## Freshness Rules

Approval evidence is fresh only when:

- It is read from the canonical approval source or has a current canonical source ref.
- The source file timestamp and source content match the current decision context.
- The approval status is not `completed`, `expired`, `rejected`, malformed, or stale.
- The approval is exact to packet ID, action type, allowed paths, branch/worktree, validators, and stop point.
- The worktree has not changed since the approval evidence was generated.
- The approval has not been consumed by a completed action.
- The current session or approval record explicitly allows reuse.

Approval projection freshness is separate from approval source freshness. A fresh projection can report stale approval evidence.

## Stale Approval Rules

Classify approval evidence as stale when:

- It refers to a prior branch, prior dirty state, prior packet, or prior broad scope.
- It predates a relevant file mutation or validator rerun.
- It is from Relay, Operation Glue, telemetry, dashboard mock data, or services without canonical source match.
- It is older than the current Night Supervisor/Morning Digest cycle and affects active status.
- It lacks exact file/action scope.
- It says `pending_review` but the underlying packet is old, broad, missing validators, or superseded.

## Superseded Approval Rules

Classify approval evidence as superseded when:

- A newer canonical approval gate exists for the same packet/action.
- The approval was archived.
- The approval was consumed and marked completed.
- The approval was replaced by a narrower packet or newer proof.
- The source moved from active inbox to archive, historical, approved/resumed sample, done, or completed evidence.
- A projection output references an older approval count than current Approval Intelligence.

## Blocked Approval Rules

Classify approval evidence as blocked when:

- It requests or implies live trading, broker/API use, real orders, real webhooks, secrets, credentials, scheduler creation, worker launch, commit, push, merge, PR creation, reset, clean, or protected file mutation without exact current approval.
- It lacks exact scope for APPLY.
- It lacks validator proof where validation is required.
- It conflicts with current branch/worktree state.
- It is malformed or cannot be parsed.
- It attempts to treat projection output as authority.

## Approval Path Classification

| Path | Classification | Reason |
|---|---|---|
| `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json` | `CANONICAL` | Declares `active_authority` for `automation/orchestration/approval_inbox/`. |
| `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json` | `CANONICAL` | Active gate item; currently `pending_review` and `approved_by_human=false`, so it does not authorize APPLY. |
| `automation/orchestration/approval_inbox/APPROVAL_STATUS_RULES_001.md` | `CANONICAL` | Defines status meanings and commit/push boundary. |
| `automation/orchestration/approval_inbox/AIOS_APPROVAL_QUEUE.example.json` | `HISTORICAL` | Example queue under canonical folder, not authority. |
| `automation/orchestration/approval_inbox/archive/APPROVAL_INBOX_001.json` | `SUPERSEDED` | Archived prior authority record, includes expired state. |
| `automation/orchestration/approval_inbox/archive/APPLY_APPROVAL_GATE_001.json` | `SUPERSEDED` | Archived/expired gate state. |
| `automation/orchestration/approval_inbox/*.DRY_RUN.ps1` | `PROJECTION` | Preview/generator/summary scripts; not approval decisions. |
| `automation/orchestration/approvals/APPROVE_PR_TEMPLATE.json` | `HISTORICAL` | Template for PR approval, not current decision. |
| `automation/orchestration/approvals/APPROVE_PR_73.json` | `HISTORICAL` | Specific old PR approval evidence; not current protected action authority. |
| `automation/orchestration/approvals/APPROVE_PR_245.json` | `HISTORICAL` | Specific old PR approval evidence; must not transfer to current work. |
| `automation/orchestration/approvals/APPROVE_PR_246.json` | `HISTORICAL` | Specific old PR approval evidence; must not transfer to current work. |
| `automation/orchestration/approvals/APPROVE_PR_247.json` | `HISTORICAL` | Specific old PR approval evidence; must not transfer to current work. |
| `automation/orchestration/approvals/APPROVE_PR_248.json` | `HISTORICAL` | Specific old PR approval evidence; must not transfer to current work. |
| `relay/approvals/20260530-165822-danger.approval.md` | `HISTORICAL` and `BLOCKED` if treated as active | Old Relay approval for dangerous/live-order wording. |
| `relay/approvals/20260530-165828-dirty-repo.approval.md` | `HISTORICAL` | Old dirty repo approval on a prior branch/state. |
| `relay/approvals/20260530-172704-dirty-repo.approval.md` | `HISTORICAL` | Old dirty repo approval on a prior branch/state. |
| `relay/approvals/enable-sos-notifier.approval.md` | `HISTORICAL` and `BLOCKED` if treated as executable | Requires credential/notifier approval; old Relay evidence only. |
| `relay/approvals/enable-telegram-bridge.approval.md` | `HISTORICAL` and `BLOCKED` if treated as executable | Requires bot token/credential boundary; old Relay evidence only. |
| `relay/approvals/register-night-scheduler.approval.md` | `HISTORICAL` and `BLOCKED` if treated as executable | Scheduler/background behavior requires separate current approval. |
| `relay/approvals/example.approval.json` | `HISTORICAL` | Example Relay approval, not active authority. |
| `relay/approvals/g-commit-the-relay-scaffold-and.approval.json` | `HISTORICAL` | Old Relay commit request, not current commit approval. |
| `relay/approvals/g-push-the-validator-to-main.approval.json` | `HISTORICAL` | Old Relay push request, not current push approval. |
| `relay/approvals/approved/resumed/AIOS_SAMPLE_RESUME_PROOF.approval.md` | `HISTORICAL` | Sample/resume proof, explicitly not real authority. |
| `relay/approvals/historical/commit-relay-prototype.approval.md` | `HISTORICAL` | Historical/manual commit guidance, not active approval authority. |
| `Relay/approvals/*` | `SUPERSEDED` or `HISTORICAL` | Duplicate-casing Relay path; must not become second approval head. |
| `control/operation_glue/APPROVAL_INBOX.json` | `SUPERSEDED` | Operation Glue v0.1 projection; canonical owner is orchestration approval inbox. |
| `services/python_supervisor/approval_projector.py` | `PROJECTION` | Projection-only unifier; planned output is telemetry. |
| `services/python_supervisor/approval_queue.py` | `PROJECTION` | Projection-only Night Supervisor approval queue from Relay evidence. |
| `services/approvals/approvalInbox.ts` | `BLOCKED` as canonical authority, `PROJECTION` as service model | In-memory store; not canonical persisted approval authority. |
| `services/approvals/approvalDecision.ts` | `BLOCKED` as canonical authority, `PROJECTION` as service decision model | Mutates in-memory approval and writes telemetry; not Human Owner approval. |
| `automation/orchestration/night_supervisor/Invoke-AiOsApprovalQueue.DRY_RUN.ps1` | `PROJECTION` | DRY_RUN wrapper; blocks non-main and dirty source unless inspection-only. |
| `automation/orchestration/approval_runner/` | `PROJECTION` | Read-only decision runner for safety review; does not mutate approvals. |
| `telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.json` | `PROJECTION` | Recommendation-only, `approval_authority=false`, one active card. |
| `telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.md` | `PROJECTION` | Markdown display version of approval intelligence. |
| `telemetry/morning_digest/MORNING_BRIEF_V2_LATEST.json` | `PROJECTION` | Recommendation-only brief; known approval summary noise remains. |
| `telemetry/morning_digest/MORNING_BRIEF_V2_LATEST.md` | `PROJECTION` | Display summary; says classification fix is needed. |
| `telemetry/morning_digest/MORNING_DIGEST_STATE.json` | `HISTORICAL` | Old digest state inflated approval count to 45. |
| `telemetry/morning_digest/MORNING_DIGEST_LATEST.md` | `HISTORICAL` | Old digest markdown with stale approval counts. |
| `telemetry/morning_digest/PROTECTED_ACTION_READINESS_LATEST.json` | `PROJECTION` | Recommendation-only protected action classification, no authority. |
| `telemetry/morning_digest/OPENAI_API_APPROVAL_BOUNDARY_LATEST.*` | `PROJECTION` | Recommendation-only API approval boundary; no external-call authority. |
| `telemetry/morning_digest/OPENAI_RECOMMENDATION_LATEST.*` | `PROJECTION` | Recommendation-only, no approval authority. |
| `telemetry/morning_digest/OPENAI_SANITIZED_SUMMARY_LATEST.*` | `PROJECTION` | Sanitized summary, no approval authority. |
| `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json` | `PROJECTION` | Bridge projection of active approval count, not authority. |
| `apps/dashboard/mock-data/aios-approval-inbox-v1.example.json` | `HISTORICAL` | Display-only mock fixture from 2026-05-13. |
| `apps/dashboard/mock-data/night_supervisor_approval_queue.sample.json` | `HISTORICAL` | Sample Night Supervisor approval queue, not active state. |
| `apps/dashboard/mock-data/autonomy_bridge_state.sample.json` | `HISTORICAL` | Sample bridge state with approval count. |
| `apps/dashboard/mock-data/build-progress-sos-alerts.example.json` | `HISTORICAL` | Mock SOS/build prep approval statuses. |
| `apps/dashboard/mock-data/night-supervisor-12h.example.json` | `HISTORICAL` | Mock 12h supervisor approval statuses. |
| `apps/dashboard/mock-data/protected_action_gate.sample.json` | `HISTORICAL` | Mock protected-action gate data. |

## Root Causes Of Approval Confusion

1. Approval authority and approval visibility are spread across many paths.
2. Legacy Relay approvals still contain active-looking instructions.
3. Dashboard fixtures contain approval statuses without active-source labels.
4. Morning Digest old state inflated active approvals to 45.
5. Approval Intelligence reduced active approvals to 1 but is only a projection.
6. Some service code can mutate in-memory approval objects, which can look like approval execution even though it is not canonical Human Owner approval.
7. Archived or completed approval evidence can be counted as pending if classification is shallow.
8. `Relay/` and `relay/` casing duplicates can make one historical approval appear twice.
9. Protected-action examples can be mistaken for current approval cards.
10. Approval freshness is not yet tied to branch/worktree, exact files, validator proof, and consumption state in one resolver.

## Top Approval Projection Defects

| Rank | Defect | Impact | Fastest fix |
|---:|---|---|---|
| 1 | Projection outputs can look like approval authority | Weekend/overnight unsafe execution risk | Require `approval_authority=false` on all projections. |
| 2 | Stale Relay approvals remain active-looking | False pending approval burden | Default Relay approvals to `HISTORICAL`. |
| 3 | Old Morning Digest approval count conflicts with Approval Intelligence | Operator confusion | Use canonical owner plus filtered projection count. |
| 4 | Active gate is pending but old/broad | Current APPLY ambiguity | Defer and require narrower current APPLY packet. |
| 5 | Dashboard mock approvals can look current | False command-center state | Label all dashboard mock approval data historical/display-only. |
| 6 | Operation Glue approval inbox appears parallel | Duplicate approval head | Mark as superseded projection. |
| 7 | Service approval model is in-memory and telemetry-writing | Authority drift risk | Keep service approval state non-canonical until explicitly promoted. |
| 8 | Archived canonical files can look active | Replay risk | Classify archive as superseded by default. |
| 9 | Approval expiry/consumption not enforced consistently | Approval replay risk | Require freshness resolver to check exact scope and consumed/completed state. |
| 10 | Credential/scheduler approvals remain visible from Relay | SOS and safety risk | Classify as blocked if treated as executable; historical otherwise. |

## Fastest Fix Sequence

1. Create approval projection acceptance tests as report-only evidence.
2. Define exact projection output fields: source path, source owner, canonical match, freshness, authority flag, mutation flag, status, and next safe action.
3. Require all non-canonical approval outputs to emit `approval_authority=false`.
4. Treat Relay, dashboard mock data, Operation Glue, and telemetry approvals as projections or historical evidence by default.
5. Filter completed, sample, example, archive, and historical records out of active approval counts.
6. Mark `APPLY_APPROVAL_GATE_001.json` as current pending-review evidence but not execution approval.
7. Require branch/worktree and exact-file validation before any current approval can be used.
8. Add superseded and consumed approval checks.
9. Prove Night Supervisor, Morning Digest, Dashboard, and SOS all display the same active approval count.
10. Only after proof, build a preview-only approval projection adapter that writes no approval state.

## Vacation-Readiness Impact

| Absence window | Approval projection impact |
|---|---|
| 4 hours | Manageable if all projections are treated as display-only and protected actions stop. |
| 12 hours | Blocking until current active approval count is trusted and stale Relay approvals are filtered. |
| Overnight | Blocking until Night Supervisor and Morning Digest agree on active approval blockers and SOS rules. |
| Weekend | Hard blocking until approval freshness, expiry, superseded state, and failover behavior are proven across cycles. |

Approval projection is a weekend blocker because AI_OS must know whether it is waiting for Anthony or merely displaying old evidence. False approval-needed status creates noise; false approval-granted status is unsafe.

## Exact Next APPLY Packet Recommendation

Packet ID: APPROVAL_PROJECTION_ACCEPTANCE_TESTS_001
Mode: APPLY report-only
Allowed path: `Reports/vacation_candidate/`
Create only: `Reports/vacation_candidate/APPROVAL_PROJECTION_ACCEPTANCE_TESTS.md`

Required report contents:

- PASS cases for canonical pending approval, canonical completed approval, projection-only approval intelligence, and dashboard display-only approvals.
- FAIL cases for Relay approval as authority, Operation Glue inbox as authority, dashboard mock approval as active approval, archived approval replay, stale branch/worktree approval, broad old APPLY gate, credential/scheduler approvals, and service in-memory approval decision as canonical authority.
- Classification matrix for `CANONICAL`, `PROJECTION`, `HISTORICAL`, `SUPERSEDED`, and `BLOCKED`.
- Minimum acceptance threshold for overnight and weekend absence trials.
- Exact future preview-only scaffold boundary for approval projection evidence.

## Recommendation

Recommendation: VALIDATE, then CONSOLIDATE.

Do not build a new approval system. Do not promote Relay, dashboard, telemetry, or service approval models. First prove an approval projection contract that keeps `automation/orchestration/approval_inbox/` canonical and forces all other approval surfaces to remain display-only or historical unless a current canonical source match exists.

Status: DRY_RUN discovery complete. No source code, scripts, schemas, queues, approvals, bridges, commits, pushes, or telemetry writes were created.
