# Morning Digest Acceptance Tests

Packet ID: MORNING_DIGEST_ACCEPTANCE_TESTS_001
Lane: MORNING_DIGEST_PROOF
Mode: APPLY report-only
Branch observed: feature/full-operator-relief-closed-loop-v1
Worktree observed: C:\Dev\Ai.Os
Report date: 2026-06-07

## Purpose

This report defines the acceptance-test suite required before Morning Digest can be trusted for AI_OS vacation-readiness decisions.

It defines tests only. It creates no code, scripts, schemas, queues, approvals, telemetry, source edits, commits, or pushes.

Morning Digest passes only when it proves that it consumes current source-owner evidence, rejects stale evidence, labels historical evidence, handles superseded evidence, reports accurate approval and blocker counts, agrees with Night Supervisor and Dashboard projections, and labels freshness and source ownership clearly.

## Trust Boundary

Morning Digest is a consumer-facing summary. It is not the canonical owner of:

- work packet state
- approval state
- worker state
- validator state
- runtime state
- dashboard state
- SOS state
- protected-action authority

Morning Digest may report source state only after the underlying source owner is classified by the Evidence Freshness rules as CURRENT for the decision being made.

## Required Evidence Inputs

| Evidence input | Requirement |
|---|---|
| Digest artifact path | The digest markdown or digest state artifact being evaluated. |
| Digest generated timestamp | Structured `generated_at` or equivalent timestamp; file modified time is fallback only. |
| Digest cycle ID | Digest date or cycle identifier used to compare with bridge and dashboard projections. |
| Source owner list | Every status-impacting source and its canonical or projection owner. |
| Source freshness classification | CURRENT, STALE, HISTORICAL, SUPERSEDED, or BLOCKED for each source. |
| Source timestamp | Source timestamp used to classify each input. |
| Current git preflight | Branch, worktree, and dirty state when repo state appears in digest. |
| Approval count source | Canonical approval owner or filtered projection with approval-authority false. |
| Blocker count source | Canonical blocker owner or filtered projection with source classifications. |
| Night Supervisor projection | Current bridge or supervisor output with cycle ID and source classifications. |
| Dashboard projection | Dashboard source labels and display references when digest data is shown in UI. |
| SOS evidence | `display_alert`, `sos_wake_required`, blocker hash, and stale or duplicate suppression evidence. |

## Required Digest Outputs

| Output | Requirement |
|---|---|
| Digest classification | CURRENT, STALE, HISTORICAL, SUPERSEDED, or BLOCKED. |
| Source freshness table | Every status-impacting source with owner, timestamp, and classification. |
| Projection freshness | Digest artifact freshness separate from source freshness. |
| Current repo state | Current branch/worktree/dirty state or explicit not-applicable label. |
| Approval count | Active approval count with source owner and filtering basis. |
| Blocker count | Active blocker count with source owner and filtering basis. |
| Night Supervisor agreement | Match, mismatch, stale, blocked, or not-applicable. |
| Dashboard agreement | Match, mismatch, stale, blocked, mock-only, or not-applicable. |
| SOS dependency state | Whether digest can inform display alert, SOS wake, or neither. |
| executable | Must always be false. |
| next_safe_action | Refresh source evidence, rerun digest proof, inspect approval owner, inspect blocker owner, block trial, or proceed to next proof. |

## Acceptance Threshold

Morning Digest trust passes only when all critical tests pass:

1. Digest artifact freshness and source freshness are separated.
2. `*_LATEST.*` files do not automatically classify as current.
3. Stale source evidence prevents CURRENT digest classification.
4. Historical Relay, report, sample, mock, and prior-cycle evidence remains detail-only.
5. Superseded evidence cannot drive current counts or current status.
6. Approval count is sourced from canonical approval ownership or a current filtered projection.
7. Blocker count is sourced from current blocker evidence and excludes historical or superseded records.
8. Night Supervisor and Morning Digest agree or the mismatch is explicit and blocking.
9. Dashboard displays Morning Digest only with source freshness labels.
10. `executable=false` remains invariant.

Any failure involving approval authority, protected actions, source freshness, branch/worktree mismatch, SOS suppression, live trading, broker/API, secrets, commits, pushes, queue writes, approval writes, or telemetry writes blocks 12-hour and overnight readiness.

## Acceptance Tests

### Current Evidence Consumption

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| MD-CURRENT-001 | Digest artifact is inside its freshness window and all status-impacting source inputs are CURRENT. | Digest classification CURRENT. | Source table shows every input owner, timestamp, and CURRENT classification. | Digest uses artifact age only. | Digest timestamp, source classifications, cycle ID. |
| MD-CURRENT-002 | Digest includes current repo state for the active branch and worktree. | Repo state is accepted as CURRENT. | Branch equals `feature/full-operator-relief-closed-loop-v1`; worktree equals `C:\Dev\Ai.Os`; dirty state is classified. | Digest reports old branch or clean state as current. | Current git status, branch, worktree, dirty baseline classification. |
| MD-CURRENT-003 | Digest consumes current Night Supervisor bridge projection with current source inputs. | Night Supervisor agreement MATCH. | Cycle IDs align and stale source inputs are absent. | Bridge timestamp hides stale source inputs. | Bridge generated timestamp, source list, cycle ID. |
| MD-CURRENT-004 | Digest consumes current approval projection with approval-authority false. | Approval count accepted as projection only. | Count matches filtered active approval evidence; authority remains false. | Projection becomes approval authority. | Approval source path, count, scope, authority flag. |

### Stale Evidence Rejection

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| MD-STALE-001 | `MORNING_DIGEST_LATEST.md` is dated 2026-06-02 for a 2026-06-07 decision. | Digest classification STALE or HISTORICAL. | Digest cannot support current vacation readiness. | Latest filename is treated as current. | Digest path, digest date, current decision date. |
| MD-STALE-002 | `MORNING_DIGEST_STATE.json` says branch `main` clean while current branch is dirty feature branch. | BLOCKED for repo-state proof. | Branch/worktree mismatch is explicit. | Old clean state is accepted. | Digest repo state, current git status. |
| MD-STALE-003 | Digest is freshly generated from stale Relay, stale bridge, or stale runtime input. | Projection freshness may be fresh; source freshness is STALE. | Digest downgrades overall trust. | Fresh generation timestamp makes stale sources current. | Digest timestamp, source timestamps, source classifications. |
| MD-STALE-004 | Validator evidence used by digest predates changed files. | BLOCKED or STALE. | Digest refuses validation confidence. | Old validator pass supports current state. | Validator timestamp, changed file list. |
| MD-STALE-005 | `last_notified` is old and source blocker state is unknown. | Digest cannot suppress SOS. | SOS dependency is BLOCKED or display-only. | Old notification suppresses current wake decision. | Notification timestamp, blocker state, blocker hash if present. |

### Historical Evidence Labeling

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| MD-HIST-001 | Prior Morning Digest or Morning Brief from earlier cycle is retained. | HISTORICAL. | Prior artifact remains detail-only. | Prior artifact drives current status. | Artifact path, cycle date. |
| MD-HIST-002 | Relay done, processed, outbox, report, alert, or prior SOS record appears in digest evidence. | HISTORICAL by default. | Digest labels Relay record detail-only. | Relay record contributes to active count. | Relay path, category, timestamp. |
| MD-HIST-003 | Dashboard mock or fixture data appears in digest/dashboard comparison. | HISTORICAL or mock-only display. | Mock label prevents active status. | Mock data changes digest status. | Dashboard source label, fixture path. |
| MD-HIST-004 | Bridge audit or vacation report is summarized by digest. | HISTORICAL for runtime decisions. | Report is evidence record only. | Report becomes queue, approval, or blocker authority. | Report path, report date, decision purpose. |

### Superseded Evidence Handling

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| MD-SUPER-001 | Newer digest exists for the same purpose. | Older digest is SUPERSEDED or HISTORICAL. | Older digest cannot drive latest status. | Older digest remains current. | Old and new digest paths, timestamps. |
| MD-SUPER-002 | Newer Night Supervisor cycle exists. | Older bridge-derived digest state is SUPERSEDED or STALE. | Digest requires current cycle alignment. | Old bridge cycle drives current digest. | Supervisor cycle IDs, timestamps. |
| MD-SUPER-003 | Approval was consumed, expired, rejected, or replaced after digest captured it. | Approval item excluded from active count. | Digest flags count mismatch or superseded approval. | Old approval remains active. | Approval event history, digest timestamp. |
| MD-SUPER-004 | Blocker was resolved or replaced after digest captured it. | Old blocker excluded from active blocker count. | Digest updates blocker status or blocks until refreshed. | Resolved blocker remains active. | Blocker event history, digest timestamp. |
| MD-SUPER-005 | SOS alert was superseded by newer blocker transition. | Old alert cannot wake or suppress. | Digest marks stale/superseded SOS state. | Old SOS state drives current wake decision. | Alert key, blocker hash, newer transition. |

### Approval Count Accuracy

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| MD-APPROVAL-001 | Digest approval count differs from Night Supervisor or filtered approval projection. | BLOCKED until reconciled. | Mismatch is explicit with both counts shown. | Digest hides count mismatch. | Digest count, bridge count, projection count. |
| MD-APPROVAL-002 | Digest includes historical Relay approvals. | Historical Relay approvals excluded from active count. | Count source is canonical owner or current filtered projection. | Relay approvals inflate count. | Relay approval paths, canonical/projection count. |
| MD-APPROVAL-003 | Approval projection reports active item but approval owner is unread or unknown. | BLOCKED for vacation proof. | Digest marks source unknown. | Projection count is treated as canonical. | Projection path, owner-read status. |
| MD-APPROVAL-004 | Approval item has broad, expired, consumed, or mismatched scope. | Excluded or BLOCKED. | Digest states scope reason. | Item is counted as actionable. | Approval scope, status, expiry or consumption. |

### Blocker Count Accuracy

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| MD-BLOCKER-001 | Digest blocker count includes stale or historical records. | Count is rejected or downgraded. | Active count includes only current unsuperseded blockers. | Historical blockers inflate active count. | Blocker list, source classification. |
| MD-BLOCKER-002 | Night Supervisor reports zero active blockers but digest reports active blockers. | MISMATCH and BLOCKED until reconciled. | Both counts and source timestamps are shown. | Mismatch is ignored. | Digest blocker count, supervisor blocker count. |
| MD-BLOCKER-003 | A blocker source lacks timestamp or owner. | BLOCKED. | Digest refuses to count as current. | Unknown blocker counted as current. | Blocker path, missing field proof. |
| MD-BLOCKER-004 | Blocker has live trading, broker/API, secret, protected-action, or queue/approval mutation risk. | BLOCKED and display alert true. | Risk class is preserved. | Risk is downgraded silently. | Risk flag, source path, decision purpose. |

### Night Supervisor Agreement

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| MD-NIGHT-001 | Digest and Night Supervisor share current cycle and matching counts. | MATCH. | Approval, blocker, and freshness counts agree. | Agreement claimed without source classification. | Digest state, bridge state, cycle ID. |
| MD-NIGHT-002 | Bridge is newer than digest but includes stale digest input. | STALE_SOURCE mismatch. | Digest cannot claim current based on bridge timestamp. | Bridge timestamp makes digest current. | Bridge source list, digest timestamp. |
| MD-NIGHT-003 | Night Supervisor says NEEDS_APPROVAL. | Approval-needed display only. | Digest does not treat it as execution permission. | Digest implies approval or action authority. | Supervisor status, approval projection. |
| MD-NIGHT-004 | Night Supervisor cycle is older than current repo state. | STALE or BLOCKED. | Digest requires refreshed supervisor proof. | Old cycle is accepted. | Cycle timestamp, current git preflight. |

### Dashboard Agreement

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| MD-DASH-001 | Dashboard card references stale digest detail path. | Dashboard agreement STALE. | Card includes or requires freshness label. | Card appears current without classification. | Dashboard details reference, digest classification. |
| MD-DASH-002 | Dashboard shows mock approval, worker, runtime, queue, or SOS data. | Mock-only or HISTORICAL. | Digest does not use mock as active state. | Mock data affects digest status. | Dashboard source label, fixture path. |
| MD-DASH-003 | Dashboard live bridge projection conflicts with digest count. | MISMATCH and BLOCKED until reconciled. | Difference is surfaced with source timestamps. | Dashboard and digest disagreement is hidden. | Dashboard projection, digest count, bridge count. |
| MD-DASH-004 | Dashboard lacks resolver classification for digest card. | BLOCKED for vacation dashboard trust. | Digest requires display classification before dashboard use. | Dashboard is trusted by display path alone. | Dashboard source label, digest source table. |

### Freshness Labeling

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| MD-FRESH-001 | Digest artifact is current but source input is stale. | Digest shows projection CURRENT and source STALE. | Overall readiness is downgraded. | Single current label hides stale input. | Artifact timestamp, source timestamp. |
| MD-FRESH-002 | Digest artifact is stale but source input was current at generation time. | Digest is STALE for current decision. | Digest does not overstate currentness. | Source at generation time makes old digest current. | Digest timestamp, source timestamp, current time. |
| MD-FRESH-003 | Source timestamp is missing. | BLOCKED for current vacation decision. | Digest names missing timestamp. | Missing timestamp becomes current. | Source path, missing timestamp proof. |
| MD-FRESH-004 | File modified time fallback is used. | Fallback is labeled. | Digest does not present fallback as source-authored time. | Fallback is treated as authoritative source timestamp. | File path, fallback time, classification basis. |

### Source Ownership Labeling

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| MD-OWNER-001 | Digest summarizes work packet state. | Owner is `automation/orchestration/work_packets/`. | Digest consumes only. | Digest becomes packet authority. | Source owner label, source path. |
| MD-OWNER-002 | Digest summarizes approval state. | Owner is `automation/orchestration/approval_inbox/` or current projection marked authority false. | Digest cannot approve or mutate. | Digest implies approval authority. | Approval source label, authority flag. |
| MD-OWNER-003 | Digest summarizes validator state. | Owner is validator evidence. | Changed files are checked against validator freshness. | Old validator evidence is accepted. | Validator owner label, changed files. |
| MD-OWNER-004 | Digest summarizes Relay records. | Owner is Relay legacy fallback, HISTORICAL by default. | Relay is detail-only. | Relay becomes active owner. | Relay path, label. |
| MD-OWNER-005 | Digest summarizes Dashboard projection. | Owner is dashboard display, not source authority. | Digest distinguishes display from source. | Dashboard becomes canonical owner. | Dashboard source label, digest source table. |

## Pass Criteria

Morning Digest trust passes when:

1. All critical tests in this report have expected results and evidence requirements.
2. Digest classification cannot be CURRENT unless the digest artifact and all status-impacting source inputs are current.
3. Approval count and blocker count are reconciled with canonical owners or current filtered projections.
4. Night Supervisor and Dashboard agreement tests pass or explicitly block readiness.
5. Historical and superseded evidence is detail-only.
6. Stale evidence cannot suppress SOS or support 12-hour, overnight, or weekend readiness.
7. Source ownership labels are present for every status-impacting item.
8. `executable=false` remains invariant.

## Fail Criteria

Morning Digest trust fails if:

1. Digest artifact age alone determines current readiness.
2. A latest pointer is treated as current without source-owner proof.
3. Stale, historical, superseded, mock, sample, Relay, or report evidence drives active status.
4. Approval counts differ and the mismatch is not blocking.
5. Blocker counts differ and the mismatch is not blocking.
6. Night Supervisor and Digest disagree without a blocking classification.
7. Dashboard displays digest status without freshness labels.
8. Source ownership is missing for status-impacting evidence.
9. Digest implies approval, protected-action, queue, telemetry, commit, push, or runtime mutation authority.
10. Any output is executable.

## Evidence Requirements

Minimum evidence required to execute this suite later:

- current `git status --short --branch`
- current branch and worktree
- digest markdown path and timestamp
- digest state JSON path and timestamp
- Night Supervisor bridge path and timestamp
- approval count source and filtering basis
- blocker count source and filtering basis
- dashboard source label or projection reference
- source freshness classifications from Evidence Freshness acceptance rules
- SOS display and wake fields when digest is used for wake/no-wake decisions

## Acceptance Threshold By Absence Window

| Absence window | Minimum Morning Digest threshold |
|---|---|
| 4 hours | Digest may be historical if current git and blocker proof are checked separately. |
| 12 hours | Digest must pass current/stale/historical/superseded/blocked classification, approval count, blocker count, and Night Supervisor agreement tests. |
| Overnight | Digest must also pass SOS dependency and stale suppression tests. |
| Weekend | Digest must pass multi-cycle superseded handling and Dashboard agreement tests. |

## Readiness Impact

| State | 4-hour readiness | 12-hour readiness | Overnight readiness | Weekend readiness |
|---|---:|---:|---:|---:|
| Before Morning Digest acceptance suite | 66% | 53% | 42% | 31% |
| Suite defined | 67% | 56% | 44% | 33% |
| Suite executed and passed later | 73% | 62% | 48% | 38% |

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
APPROVAL_PROJECTION_ACCEPTANCE_TESTS_APPLY_001

LANE:
APPROVAL_PROJECTION_PROOF

ZONE:
AI_OS Vacation Candidate / Approval Projection

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
4. Read Reports/vacation_candidate/APPROVAL_PROJECTION_DISCOVERY.md.
5. Read Reports/vacation_candidate/EVIDENCE_FRESHNESS_ACCEPTANCE_TESTS.md.
6. Read Reports/vacation_candidate/MORNING_DIGEST_ACCEPTANCE_TESTS.md.
7. Read Reports/vacation_candidate/VACATION_READINESS_PROOF_LADDER.md.
8. Confirm branch/worktree state.
9. Create only Reports/vacation_candidate/APPROVAL_PROJECTION_ACCEPTANCE_TESTS.md.
10. Run git diff --check.
11. Run git status --short --branch.

MISSION:
Create the acceptance-test suite for Approval Projection trust without creating a second approval authority.

TASK:
Define pass/fail tests for canonical approval ownership, projection labeling, stale approval rejection, superseded approval handling, exact-scope matching, approval count accuracy, Morning Digest agreement, Night Supervisor agreement, Dashboard agreement, SOS dependency, and executable=false invariance.

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
- Do not create a new bridge, queue, approval system, or adapter.

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

Report created only under `Reports/vacation_candidate/`. No source code, scripts, schemas, queues, approvals, telemetry, automation, commits, pushes, branch switching, live trading paths, broker paths, secrets, new bridge, new queue, or new approval system were created.
