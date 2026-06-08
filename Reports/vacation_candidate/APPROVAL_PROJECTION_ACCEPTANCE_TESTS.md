# Approval Projection Acceptance Tests

Packet ID: APPROVAL_PROJECTION_ACCEPTANCE_TESTS_001
Lane: APPROVAL_PROJECTION_PROOF
Mode: APPLY report-only
Branch observed: feature/full-operator-relief-closed-loop-v1
Worktree observed: C:\Dev\Ai.Os
Report date: 2026-06-07

## Purpose

This report defines the acceptance-test suite required before AI_OS can trust approval projection for vacation-readiness decisions.

It defines tests only. It creates no code, scripts, schemas, queues, approvals, telemetry, adapters, bridge, approval system, automation, commits, or pushes.

Approval Projection passes only when it proves that `automation/orchestration/approval_inbox/` remains canonical and every other approval surface is projection-only, historical, superseded, blocked, or display-only.

## Trust Boundary

Approval Projection answers:

```text
What approval state should be shown, and how fresh is that evidence?
```

Approval Projection must not answer:

```text
Is this action approved to execute?
```

Execution authority remains with Anthony / AI_OS Owner, exact current approval scope, and the protected-action gates. Projection evidence must never approve APPLY, commit, push, merge, PR creation, worker launch, scheduler creation, queue mutation, approval mutation, telemetry mutation, broker/API use, secrets, live trading, reset, clean, or protected file mutation.

## Required Evidence Sources

Primary report evidence:

- `Reports/vacation_candidate/APPROVAL_PROJECTION_DISCOVERY.md`
- `Reports/vacation_candidate/VACATION_READINESS_PROOF_LADDER.md`
- `Reports/vacation_candidate/MORNING_DIGEST_ACCEPTANCE_TESTS.md`
- `Reports/vacation_candidate/EVIDENCE_FRESHNESS_ACCEPTANCE_TESTS.md`

Approval source paths referenced by the acceptance suite:

- `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
- `automation/orchestration/approval_inbox/APPROVAL_STATUS_RULES_001.md`
- `automation/orchestration/approval_inbox/archive/`
- `automation/orchestration/approvals/`
- `telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.json`
- `telemetry/morning_digest/MORNING_DIGEST_STATE.json`
- `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json`
- `apps/dashboard/mock-data/`
- `control/operation_glue/APPROVAL_INBOX.json`
- `relay/approvals/`
- `Relay/approvals/`
- `services/approvals/`
- `services/python_supervisor/approval_projector.py`
- `services/python_supervisor/approval_queue.py`

These are evidence sources for future tests. This report does not edit or write any of them.

## Required Evidence Inputs

| Input | Requirement |
|---|---|
| Approval source path | Path that provided approval evidence. |
| Source owner | CANONICAL, PROJECTION, HISTORICAL, SUPERSEDED, or BLOCKED owner classification. |
| Approval status | Pending, approved, rejected, completed, expired, blocked, historical, superseded, malformed, or unknown. |
| Approval authority flag | True only for canonical owner evidence; false for projections. |
| Approval mutation flag | Must be false for every projection. |
| Recommendation-only flag | Must be true for every projection. |
| Approval scope | Packet ID, action type, files, allowed paths, branch, worktree, validator chain, stop point, and expiry/consumption state when present. |
| Source timestamp | Timestamp from the canonical source or source artifact. |
| Projection timestamp | Timestamp from the displaying projection if different from source timestamp. |
| Current branch/worktree | Required when approval affects repo actions. |
| Validator evidence | Required when approval depends on validation state. |
| Protected-action type | APPLY, commit, push, merge, PR, branch switch, reset, clean, worker launch, scheduler, queue write, approval write, telemetry write, external/API, broker, live trading, or secret access. |

## Required Outputs

| Output | Requirement |
|---|---|
| Approval classification | CANONICAL, PROJECTION, HISTORICAL, SUPERSEDED, or BLOCKED. |
| Approval freshness | CURRENT, STALE, HISTORICAL, SUPERSEDED, or BLOCKED. |
| Active approval count | Count after filtering historical, superseded, completed, sample, example, and blocked records. |
| Projection authority flag | Must be false for all projections. |
| Projection mutation flag | Must be false for all projections. |
| Canonical source match | True only when projection references current canonical source evidence. |
| Scope match | Exact, mismatch, missing, expired, consumed, superseded, or not-applicable. |
| Display alert | Whether the approval state should be shown. |
| SOS wake required | Whether approval state blocks safe unattended continuation. |
| Blocked reason | Required when classification is BLOCKED. |
| Next safe action | Inspect canonical owner, refresh projection, reconcile count, block trial, request exact approval, or continue to next proof. |
| executable | Must always be false. |

## Acceptance Threshold

Approval Projection Trust passes only when all critical tests pass:

1. Canonical ownership is limited to `automation/orchestration/approval_inbox/`.
2. All projections emit approval-authority false and approval-mutation false.
3. Relay, Dashboard mock, Operation Glue, telemetry, service-local, archived, sample, and historical approval evidence cannot become active authority.
4. Active approval count excludes completed, archived, historical, sample, example, superseded, malformed, blocked, and stale records.
5. Exact scope is required for any current approval display tied to a protected action.
6. Morning Digest, Night Supervisor, and Dashboard agreement is explicit.
7. Stale and superseded approvals cannot be replayed.
8. Approval blockers and SOS dependency behavior are classified without sending notifications or creating approvals.
9. Live trading, broker/API, secrets, scheduler, worker launch, commit, push, merge, reset, clean, queue write, approval write, telemetry write, or protected file mutation risks classify as BLOCKED unless separately and exactly approved in a future protected-action workflow.
10. `executable=false` remains invariant.

Any failure in canonical ownership, projection-only behavior, exact scope, protected-action risk, SOS dependency, or executable invariance blocks overnight and weekend readiness.

## Acceptance Tests

### Canonical Approval Ownership

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-CANON-001 | Evidence comes from `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`. | CANONICAL source owner. | Output identifies canonical owner and preserves authority path. | Any other path is treated as equal authority. | Canonical inbox path, authority status, source timestamp. |
| AP-CANON-002 | Evidence comes from `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json` with `approved_by_human=false` or pending review. | CANONICAL evidence, not execution approval. | Active card may display, but executable remains false. | Pending gate authorizes APPLY. | Gate status, approval flag, packet scope. |
| AP-CANON-003 | Evidence comes from `APPROVAL_STATUS_RULES_001.md`. | CANONICAL status vocabulary. | Status meanings are used without mutating approval state. | Status rules are treated as approval decision. | Rules path, referenced status. |
| AP-CANON-004 | A non-canonical path claims approval authority. | BLOCKED as authority, PROJECTION or HISTORICAL as evidence. | Authority drift is surfaced. | Non-canonical path becomes approval owner. | Source path, claimed authority, canonical comparison. |

### Projection-Only Behavior

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-PROJ-001 | `APPROVAL_INTELLIGENCE_V2_LATEST.json` reports an active approval card. | PROJECTION only. | `approval_authority=false`, `approval_mutation=false`, and recommendation-only behavior are present. | Projection grants approval or mutates approval state. | Projection path, authority flag, mutation flag, count. |
| AP-PROJ-002 | Night Supervisor bridge reports active approval count. | PROJECTION only. | Count is display evidence and must reference source freshness. | Bridge count becomes approval authority. | Bridge path, count, source reference. |
| AP-PROJ-003 | Morning Digest summarizes approvals. | PROJECTION/summary only. | Digest count is reconciled with current source or blocked. | Digest count becomes canonical approval state. | Digest path, count, source owner. |
| AP-PROJ-004 | Dashboard displays approval queue or approval card. | Display-only projection. | Dashboard cannot approve, mutate, or widen scope. | Dashboard mock or display becomes active authority. | Dashboard source label, card data. |
| AP-PROJ-005 | Service-local approval model or in-memory decision appears. | PROJECTION as model, BLOCKED as canonical authority. | Service state cannot replace Human Owner approval. | Service state becomes canonical authority. | Service path, decision state, persistence behavior. |

### Stale Approval Detection

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-STALE-001 | Approval evidence refers to a prior branch, worktree, or dirty state. | STALE or BLOCKED. | Current branch/worktree mismatch is explicit. | Old approval applies to current work. | Approval branch/worktree, current preflight. |
| AP-STALE-002 | Approval predates relevant file mutation or validator rerun. | STALE or BLOCKED. | Approval cannot support current protected action. | Old approval remains current. | Approval timestamp, mutation or validator timestamp. |
| AP-STALE-003 | Relay approval is old and active-looking. | HISTORICAL, or BLOCKED if treated as executable. | Relay evidence is detail-only. | Relay approval becomes active. | Relay approval path, timestamp. |
| AP-STALE-004 | Approval lacks exact files, action type, validators, branch, or stop point. | BLOCKED. | Missing scope is named. | Broad approval is treated as current. | Approval scope fields. |
| AP-STALE-005 | Projection is fresh but underlying approval source is stale. | Projection freshness separate; source freshness STALE. | Projection does not upgrade source. | Fresh projection makes stale approval current. | Projection timestamp, source timestamp. |

### Superseded Approval Detection

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-SUPER-001 | Newer canonical approval gate exists for same packet/action. | Older approval SUPERSEDED. | Older evidence is detail-only. | Older evidence drives active status. | Old and new gate paths, timestamps, packet ID. |
| AP-SUPER-002 | Approval was archived. | SUPERSEDED or HISTORICAL. | Archived approval is excluded from active count. | Archived approval remains active. | Archive path, active path comparison. |
| AP-SUPER-003 | Approval was consumed by completed action. | SUPERSEDED or completed. | Cannot be replayed. | Consumed approval authorizes new action. | Completion marker, action history. |
| AP-SUPER-004 | Projection references older count than current approval intelligence. | SUPERSEDED projection. | Count mismatch blocks or downgrades display. | Old count remains active. | Old projection, current projection, timestamps. |
| AP-SUPER-005 | Approval was replaced by narrower packet or newer proof. | SUPERSEDED. | Narrower/current packet governs display. | Broad old approval continues. | Packet IDs, scope comparison. |

### Approval Count Accuracy

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-COUNT-001 | Canonical owner reports one current pending gate and projection reports one active card. | Active count 1 with projection-only flag. | Count matches and authority remains canonical. | Projection count becomes authority. | Canonical gate, approval intelligence count. |
| AP-COUNT-002 | Morning Digest old state reports 45 approvals while current filtered projection reports 1. | MISMATCH and stale digest count excluded. | Count mismatch blocks readiness until reconciled. | Old count inflates active approval burden. | Digest count, projection count, timestamps. |
| AP-COUNT-003 | Relay historical approvals are present. | Excluded from active count. | Relay records are historical by default. | Relay approvals inflate count. | Relay approval list, classifications. |
| AP-COUNT-004 | Dashboard mock approvals are present. | Excluded from active count. | Mock label prevents active status. | Mock approvals counted as active. | Dashboard fixture path, mock label. |
| AP-COUNT-005 | Archived, completed, rejected, expired, sample, or example approvals are present. | Excluded from active count. | Count filter states exclusion reason. | Non-active records counted as active. | Status, path, timestamp. |

### Approval Source Ownership Accuracy

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-OWNER-001 | Approval source path is canonical inbox. | Source owner CANONICAL. | Path maps to active authority. | Canonical path is downgraded without reason. | Source path, authority status. |
| AP-OWNER-002 | Approval source path is telemetry. | Source owner PROJECTION. | Telemetry cannot approve or mutate. | Telemetry becomes authority. | Telemetry path, projection flags. |
| AP-OWNER-003 | Approval source path is Relay or duplicate-casing Relay. | Source owner HISTORICAL by default. | Casing duplicate is surfaced. | Relay becomes second approval head. | `relay/` and `Relay/` paths. |
| AP-OWNER-004 | Approval source path is Operation Glue inbox. | Source owner SUPERSEDED. | Canonical owner remains orchestration inbox. | Operation Glue becomes parallel authority. | Operation Glue path, canonical comparison. |
| AP-OWNER-005 | Approval source path is service in-memory model. | PROJECTION as model, BLOCKED as authority. | Service state does not grant protected actions. | Service state becomes canonical approval. | Service path, state behavior. |

### Night Supervisor Approval Agreement

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-NIGHT-001 | Night Supervisor active approval count matches current filtered approval projection. | MATCH. | Both show same active count and source freshness. | Match claimed without source reference. | Bridge state, projection count, source path. |
| AP-NIGHT-002 | Night Supervisor says NEEDS_APPROVAL. | Display and approval-required only. | No execution permission is implied. | NEEDS_APPROVAL is treated as approval. | Supervisor status, output boundary. |
| AP-NIGHT-003 | Night Supervisor reads stale Relay approval. | HISTORICAL or BLOCKED, not active. | Relay approval excluded from active count. | Relay approval drives supervisor status. | Bridge source list, Relay path. |
| AP-NIGHT-004 | Night Supervisor cycle is older than approval source. | STALE projection or MISMATCH. | Requires refreshed projection. | Old cycle count remains trusted. | Cycle timestamp, approval source timestamp. |

### Morning Digest Approval Agreement

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-DIGEST-001 | Morning Digest approval count matches current filtered projection and source owner. | MATCH. | Count is display-only and source-labeled. | Digest count becomes authority. | Digest count, source owner, projection flags. |
| AP-DIGEST-002 | Morning Digest old state reports stale inflated approval count. | STALE count excluded. | Digest blocks readiness until refreshed. | Old count remains active. | Digest state timestamp, approval count. |
| AP-DIGEST-003 | Morning Digest includes Relay approvals as active. | FAIL or BLOCKED. | Relay approvals must be historical detail-only. | Relay approvals inflate digest count. | Digest evidence list, Relay paths. |
| AP-DIGEST-004 | Morning Digest lacks approval source owner label. | BLOCKED for approval trust. | Missing label is explicit. | Digest approval state is accepted. | Digest source table. |

### Dashboard Approval Agreement

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-DASH-001 | Dashboard mock approval fixture is displayed. | HISTORICAL or mock-only. | Dashboard cannot change active approval count. | Mock approval becomes active. | Dashboard fixture path, source label. |
| AP-DASH-002 | Dashboard live bridge count matches current projection. | MATCH as display only. | Display labels projection and authority false. | Dashboard display becomes authority. | Dashboard projection, bridge count. |
| AP-DASH-003 | Dashboard approval card lacks source label or freshness label. | BLOCKED for vacation dashboard trust. | Missing label blocks readiness display. | Card is treated as current. | Dashboard card data, source label. |
| AP-DASH-004 | Dashboard shows approve action without current protected-action approval workflow. | BLOCKED. | Display-only boundary is preserved. | Dashboard grants approval. | Dashboard card/action metadata. |

### Approval Freshness Labeling

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-FRESH-001 | Canonical approval source is current but projection is old. | Source CURRENT, projection STALE. | Consumer requires refresh for display. | Old projection shown as current. | Source timestamp, projection timestamp. |
| AP-FRESH-002 | Projection is current but source approval is stale. | Projection CURRENT, source STALE. | Source stale prevents active approval trust. | Projection freshness upgrades source. | Projection timestamp, source timestamp. |
| AP-FRESH-003 | Approval timestamp is missing. | BLOCKED for current decision. | Missing timestamp is named. | Missing timestamp becomes current. | Source path, missing timestamp proof. |
| AP-FRESH-004 | Approval status is malformed or unknown. | BLOCKED. | Status cannot be guessed. | Unknown status treated as pending. | Raw status, parser result. |
| AP-FRESH-005 | Approval is current only for exact scope. | CURRENT only when exact scope matches. | Files, action, branch, validators, and stop point match. | Approval scope is widened. | Scope fields, requested action. |

### Approval Blocker Classification

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-BLOCKER-001 | Approval is required before protected action can continue. | BLOCKED or NEEDS_APPROVAL display. | Safe next action requests exact approval. | System continues without approval. | Protected-action type, approval status. |
| AP-BLOCKER-002 | Approval evidence requests live trading, broker/API, secrets, credentials, or real webhook behavior. | BLOCKED. | Risk is preserved and surfaced. | Risk is reduced to routine approval. | Approval path, risk flag. |
| AP-BLOCKER-003 | Approval evidence requests commit, push, merge, reset, clean, PR action, worker launch, or scheduler creation without explicit current approval. | BLOCKED. | Protected-action gate boundary is preserved. | Projection authorizes action. | Requested action, approval scope. |
| AP-BLOCKER-004 | Approval evidence conflicts with branch/worktree state. | BLOCKED. | State mismatch is named. | Approval applies across branches. | Approval branch/worktree, current state. |
| AP-BLOCKER-005 | Approval evidence lacks validator proof where validator is required. | BLOCKED. | Validator gap is named. | Approval proceeds without validator proof. | Validator chain, validator status. |

### Approval SOS Dependency Behavior

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| AP-SOS-001 | Routine approval-needed state exists but does not block safe unattended continuation. | `display_alert=true`, `sos_wake_required=false`. | Display-only wake class is used. | Every approval-needed state wakes Anthony. | Approval status, blocker severity. |
| AP-SOS-002 | Approval blocks safe continuation for vacation trial. | `display_alert=true`, `sos_wake_required=true` or BLOCKED_REVIEW based on severity. | Current unsuperseded blocker is surfaced. | Approval blocker is hidden. | Approval blocker, source freshness, severity. |
| AP-SOS-003 | Historical Relay approval asks for credentials, scheduler, or notifier behavior. | HISTORICAL and BLOCKED if treated as executable; no wake by itself. | Historical risk is visible without false wake. | Historical item wakes or authorizes action. | Relay approval path, risk class. |
| AP-SOS-004 | Stale approval blocker was already notified. | Stale notification cannot suppress current blocker. | Current blocker hash controls suppression. | Old `last_notified` suppresses current approval blocker. | Notification key, approval blocker hash. |
| AP-SOS-005 | Duplicate current approval blocker appears in multiple projections. | One display/wake decision after dedupe. | Dedupe uses source owner, scope, status, and blocker hash. | Duplicate projections create repeated wakes. | Projection paths, canonical source ref, blocker hash. |

## Pass Criteria

Approval Projection trust passes when:

1. Canonical ownership remains limited to `automation/orchestration/approval_inbox/`.
2. Every projection is labeled projection-only, recommendation-only, approval-authority false, and approval-mutation false.
3. Active approval count is reconciled across canonical source, Approval Intelligence, Night Supervisor, Morning Digest, and Dashboard display.
4. Relay, Operation Glue, telemetry, dashboard mock, services, archives, samples, and historical records cannot become authority.
5. Stale, superseded, expired, consumed, rejected, malformed, broad, or scope-mismatched approval evidence is excluded or blocked.
6. Approval freshness labels separate source freshness from projection freshness.
7. Approval blockers classify safe next action and SOS dependency without writing approvals or sending notifications.
8. `executable=false` remains invariant.

## Fail Criteria

Approval Projection trust fails if:

1. A projection grants approval authority.
2. A projection can mutate approval state.
3. Relay, Dashboard, Operation Glue, telemetry, service-local, archive, sample, or historical approval evidence becomes active authority.
4. Approval count differs across consumers without a blocking mismatch.
5. Stale or superseded approval evidence remains active.
6. A broad old approval applies to a new packet, branch, file set, validator chain, or protected action.
7. Night Supervisor, Morning Digest, or Dashboard implies execution approval.
8. SOS wakes for historical approvals or suppresses a current approval blocker with stale notification state.
9. Any live trading, broker/API, secret, credential, scheduler, worker launch, commit, push, merge, reset, clean, queue write, approval write, telemetry write, or protected file mutation risk is not blocked.
10. Any output is executable.

## Evidence Required To Execute The Suite Later

Minimum evidence needed:

- current branch and worktree
- current `git status --short --branch`
- canonical approval inbox status and timestamp
- active approval gate status and scope
- approval status rules
- approval intelligence projection count and timestamp
- Night Supervisor approval count and timestamp
- Morning Digest approval count and timestamp
- Dashboard approval source label or projection reference
- Relay approval paths and classifications
- archive/completed/expired/superseded approval markers
- source freshness and projection freshness classifications
- protected-action type and requested scope when approval affects actionability
- SOS display and wake fields when approval blocks safe continuation

## Acceptance Threshold By Absence Window

| Absence window | Minimum approval projection threshold |
|---|---|
| 4 hours | Projection may remain display-only if all protected actions stop and no projection grants authority. |
| 12 hours | Active approval count must be reconciled across canonical source, Morning Digest, and Night Supervisor. |
| Overnight | Approval blocker classification and SOS dependency behavior must pass. |
| Weekend | Stale, superseded, archived, duplicate, and multi-cycle approval projections must pass. |

## Readiness Impact

| State | 4-hour readiness | 12-hour readiness | Overnight readiness | Weekend readiness |
|---|---:|---:|---:|---:|
| Before approval projection acceptance suite | 67% | 56% | 44% | 33% |
| Suite defined | 68% | 59% | 47% | 36% |
| Suite executed and passed later | 74% | 66% | 52% | 43% |

This report defines the suite. It does not execute it.

## Exact Next APPLY Packet Recommendation

Recommended next packet:

```text
CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER:
AI_OS_EXECUTABLE_PACKET

SUPERVISOR IDENTITY:
Anthony / AI_OS Owner

PACKET ID:
SOS_NO_SEND_ACCEPTANCE_TESTS_APPLY_001

LANE:
SOS_NO_SEND_PROOF

ZONE:
AI_OS Vacation Candidate / SOS No-Send

WORKER IDENTITY:
Codex CLI Worker

MODE:
APPLY

BRANCH:
feature/full-operator-relief-closed-loop-v1

WORKTREE:
C:\Dev\Ai.Os

APPROVAL AUTHORITY:
Anthony / AI_OS Owner

READ-FIRST AUTHORITY FILES:
AGENTS.md
README.md
WHITEPAPER.md

ALLOWED PATHS:
Reports/vacation_candidate/

PROTECTED PATHS:
AGENTS.md
README.md
WHITEPAPER.md
automation/
tools/
scripts/
src/
config/
control/
Relay/
.github/
schemas/
telemetry/

VALIDATOR CHAIN:
1. Read AGENTS.md.
2. Read README.md.
3. Read WHITEPAPER.md.
4. Read Reports/vacation_candidate/EVIDENCE_FRESHNESS_ACCEPTANCE_TESTS.md.
5. Read Reports/vacation_candidate/MORNING_DIGEST_ACCEPTANCE_TESTS.md.
6. Read Reports/vacation_candidate/APPROVAL_PROJECTION_ACCEPTANCE_TESTS.md.
7. Read Reports/vacation_candidate/VACATION_READINESS_PROOF_LADDER.md.
8. Confirm branch/worktree state.
9. Create only Reports/vacation_candidate/SOS_NO_SEND_ACCEPTANCE_TESTS.md.
10. Run git diff --check.
11. Run git status --short --branch.

MISSION:
Create the acceptance-test suite for SOS no-send trust.

TASK:
Define pass/fail tests for display_alert, sos_wake_required, stale suppression, duplicate suppression, current blocker wake, historical alert no-wake, approval-blocker behavior, failover classification, no-secret/no-send boundary, and executable=false invariance.

STRICT RULES:
- Report only.
- No code.
- No scripts.
- No source edits.
- No queue writes.
- No approval writes.
- No telemetry writes.
- No commits.
- No pushes.
- No branch switching.
- No live trading paths.
- No broker paths.
- No secrets.
- Do not create a new bridge, queue, approval system, notifier, adapter, or automation.

STOP POINT:
Stop after report creation and validation.

FINAL RESPONSE FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS:
```

## Stop Point

Report created only under `Reports/vacation_candidate/`. No source code, scripts, schemas, queues, approvals, telemetry, automation, commits, pushes, branch switching, live trading paths, broker paths, secrets, new bridge, new queue, new adapter, or new approval system were created.
