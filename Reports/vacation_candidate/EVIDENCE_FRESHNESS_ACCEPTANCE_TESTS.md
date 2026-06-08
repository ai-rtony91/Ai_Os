# Evidence Freshness Acceptance Tests

Packet ID: EVIDENCE_FRESHNESS_ACCEPTANCE_TESTS_002
Lane: EVIDENCE_FRESHNESS_PROOF
Mode: APPLY report-only
Branch observed: feature/full-operator-relief-closed-loop-v1
Worktree observed: C:\Dev\Ai.Os
Report date: 2026-06-07

## Purpose

This report defines the acceptance-test suite required before AI_OS can trust evidence freshness for vacation-readiness decisions.

It defines tests only. It creates no code, scripts, schemas, queues, approvals, telemetry, adapters, bridge, automation, commits, or pushes.

The tests prove that Morning Digest, Night Supervisor, Dashboard, Approval Projection, Relay, Runtime, and SOS can use the same freshness vocabulary:

- CURRENT
- STALE
- HISTORICAL
- SUPERSEDED
- BLOCKED

## Acceptance Scope

The suite must prove three boundaries:

1. Source-owner freshness is separate from projection freshness.
2. A fresh display or latest pointer cannot make stale source evidence current.
3. Unknown, unsafe, mismatched, or unprovable evidence blocks vacation-readiness decisions.

The suite is required before any 12-hour readiness trial. It is also the Proof Gate 1 acceptance suite from `Reports/vacation_candidate/VACATION_READINESS_PROOF_LADDER.md`.

## Required Evidence Inputs

Every tested evidence item must provide or explicitly fail on these inputs:

| Input | Requirement |
|---|---|
| Source path | Path to the source evidence record or projection artifact. |
| Source owner | Canonical owner or projection owner, such as work packets, approval inbox, validators, runtime telemetry, digest, dashboard, Relay, or report evidence. |
| Source type | Queue, approval, validator, worker, digest, supervisor, dashboard, Relay, runtime, SOS, report, fixture, or mock. |
| Source timestamp | Structured timestamp when present, with file modified time allowed only as a fallback. |
| Projection timestamp | Timestamp for consumer-facing output when different from the source timestamp. |
| Decision purpose | Current-state display, vacation proof, approval visibility, SOS classification, digest summary, dashboard display, or historical detail. |
| Packet, lane, or cycle ID | Required when evidence is packet, worker, validator, digest, supervisor, or approval scoped. |
| Branch and worktree | Required when repo state affects the decision. |
| Validation timestamp | Required when the decision depends on validator evidence. |
| Approval scope | Required when the evidence concerns approval or protected action state. |
| Dedupe key | Source owner, source path, event type, source timestamp, and source hash or stable event ID. |

## Required Outputs

Each acceptance test must produce these outputs:

| Output | Requirement |
|---|---|
| Classification | One of CURRENT, STALE, HISTORICAL, SUPERSEDED, or BLOCKED. |
| Classification basis | Human-readable reason tied to timestamp, owner, state, source, or safety boundary. |
| Source freshness | Freshness of the underlying owner evidence. |
| Projection freshness | Freshness of the consumer-facing artifact. |
| Source timestamp UTC | Timestamp used for source freshness. |
| Projection timestamp UTC | Timestamp used for display or generated output freshness. |
| Expiration rule | Rule or window used to classify stale evidence. |
| Superseded by | Newer evidence path, event, cycle, or pointer when applicable. |
| Blocked reasons | Exact missing, unsafe, mismatched, failed, or unknown reasons. |
| Risk flags | Protected action, secret, broker, live trading, branch mismatch, approval mismatch, validator mismatch, or source owner mismatch. |
| display_alert | Boolean display indicator. |
| sos_wake_required | Boolean wake indicator. |
| wake_class | NONE, DISPLAY_ONLY, SOS_REQUIRED, or BLOCKED_REVIEW. |
| executable | Must always be false. |
| next_safe_action | Review, rerun current evidence read, refresh digest, run no-send SOS proof, inspect approval owner, or block vacation trial. |

## Evidence Sources

Primary evidence for this acceptance suite:

- `Reports/vacation_candidate/EVIDENCE_FRESHNESS_RESOLVER_DISCOVERY.md`
- `Reports/vacation_candidate/MORNING_DIGEST_FRESHNESS_AUDIT.md`
- `Reports/vacation_candidate/VACATION_READINESS_PROOF_LADDER.md`
- `Reports/vacation_candidate/APPROVAL_PROJECTION_DISCOVERY.md`
- `Reports/vacation_candidate/VACATION_READINESS_MAX_PUSH.md`

Referenced source-owner paths for future tests:

- `automation/orchestration/work_packets/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/workers/`
- `automation/orchestration/validators/`
- `automation/orchestration/commit_packages/`
- `telemetry/morning_digest/`
- `telemetry/night_supervisor/`
- `telemetry/runtime/`
- `apps/dashboard/`
- `services/telemetry/`
- `relay/`
- `Relay/`
- `Reports/`

These referenced paths are evidence sources only for this report. This packet does not edit them.

## Acceptance Threshold

Evidence Freshness Trust passes only when all critical tests pass:

1. CURRENT, STALE, HISTORICAL, SUPERSEDED, and BLOCKED classifications are proven.
2. Source-owner freshness and projection freshness are never collapsed into one field.
3. Missing required timestamps fail for current vacation decisions.
4. Branch or worktree mismatch blocks repo-state evidence.
5. Latest pointers do not automatically classify as current.
6. Relay records and dashboard mocks cannot drive active state.
7. Approval projections cannot become approval authority.
8. Validator evidence predating file changes is stale or blocked.
9. Current unsuperseded blockers set display or SOS fields correctly.
10. `executable=false` remains invariant.

Any failure in tests touching SOS, approval, protected action, live trading, broker/API, secrets, branch/worktree alignment, or validator freshness blocks 12-hour readiness.

## Test Matrix

### CURRENT Tests

| Test ID | Input condition | Expected classification | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| FR-CURRENT-001 | Source-owner evidence has current timestamp, current branch/worktree where required, valid owner, valid source path, and no newer superseding event. | CURRENT | Source freshness and projection freshness both pass for the decision purpose. | Evidence uses projection timestamp only or lacks owner proof. | Source path, owner, source timestamp, decision purpose, branch/worktree when applicable. |
| FR-CURRENT-002 | Runtime heartbeat is current while packet evidence inside runtime projection is stale. | CURRENT for runtime projection, STALE for packet source | Output separates projection freshness from source freshness. | Runtime fresh timestamp makes stale packet evidence current. | `telemetry/runtime/` projection timestamp and packet evidence timestamp. |
| FR-CURRENT-003 | Current approval projection reads canonical approval owner and reports display-only status. | CURRENT as projection only | Approval source is current and projection emits approval-authority false. | Projection claims authority or executable permission. | Canonical approval path, approval scope, projection timestamp, `executable=false`. |
| FR-CURRENT-004 | Current Night Supervisor cycle references only current source evidence for its cycle. | CURRENT | Cycle ID, source timestamps, and source owner classifications align. | Current cycle output includes stale digest or historical Relay as active state. | Supervisor cycle ID, source list, source classifications. |

### STALE Tests

| Test ID | Input condition | Expected classification | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| FR-STALE-001 | Morning Digest artifact is older than 18 hours for vacation decision. | STALE | Digest remains readable but cannot support current readiness. | Digest latest filename is treated as current. | Digest path, generated timestamp, current decision time. |
| FR-STALE-002 | Digest state records branch `main` clean while current branch is `feature/full-operator-relief-closed-loop-v1` with dirty paths. | STALE or BLOCKED | Repo-state mismatch is surfaced. | Old clean state is accepted. | Digest repo state, current git status, current branch. |
| FR-STALE-003 | Validator evidence timestamp predates a relevant file mutation. | STALE or BLOCKED | Validator cannot support current decision. | Validator pass remains accepted after file changes. | Validator timestamp, changed file list, mutation timestamp or current diff. |
| FR-STALE-004 | Bridge projection is newer than digest but consumes stale digest source. | STALE source, CURRENT or STALE projection based on age | Output shows fresh projection from stale source. | Bridge generated timestamp hides stale digest input. | Bridge generated timestamp, digest source timestamp, source classifications. |
| FR-STALE-005 | Git status evidence is older than 15 minutes or predates mutation. | STALE | Repo decision requires fresh preflight. | Old git state is used for current readiness. | Git status timestamp, mutation evidence or age window. |

### HISTORICAL Tests

| Test ID | Input condition | Expected classification | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| FR-HIST-001 | Bridge audit or vacation report is used as runtime proof after newer source state exists. | HISTORICAL | Report remains evidence only, not runtime authority. | Report is used as current queue, approval, or worker state. | Report path, report date, decision purpose. |
| FR-HIST-002 | Relay done, processed, outbox, alert, or prior SOS record is discovered. | HISTORICAL | Relay item is detail-only unless promoted by current source owner evidence. | Relay item drives active state. | Relay path, classification reason, source owner. |
| FR-HIST-003 | Dashboard mock fixture displays queue, approval, SOS, or runtime examples. | HISTORICAL or BLOCKED if used as active state | Mock label prevents active classification. | Mock data is displayed as current operational state. | Dashboard source label, fixture path, display context. |
| FR-HIST-004 | Prior Morning Digest or Morning Brief from earlier cycle is retained for reference. | HISTORICAL | Prior artifact does not affect latest readiness. | Prior digest suppresses current blocker or approval. | Digest path, cycle date, current cycle ID. |

### SUPERSEDED Tests

| Test ID | Input condition | Expected classification | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| FR-SUPER-001 | Newer evidence exists for the same packet, lane, source owner, and event type. | SUPERSEDED | Older evidence points to newer record. | Older evidence still appears in latest status. | Older and newer source paths, timestamps, packet or lane ID. |
| FR-SUPER-002 | Approval was consumed, rejected, expired, or replaced after prior approved evidence. | SUPERSEDED | Prior approval cannot authorize action. | Old approval is replayed. | Approval event history, status, scope, expiry or consumption marker. |
| FR-SUPER-003 | Validator rerun exists for the same changed file set. | SUPERSEDED | Older validator result is detail-only. | Older passing result overrides newer failure or newer run. | Validator run IDs, timestamps, changed file set. |
| FR-SUPER-004 | Latest pointer changed after evidence was captured. | SUPERSEDED | Prior latest target no longer drives display. | Old latest target remains current. | Pointer timestamp, old target, new target. |
| FR-SUPER-005 | SOS alert is replaced by a newer blocker transition or resolution. | SUPERSEDED | Old alert does not wake and does not suppress new blocker. | Old alert wakes or suppresses current blocker incorrectly. | Alert key, blocker hash, last notified state, current blocker state. |

### BLOCKED Tests

| Test ID | Input condition | Expected classification | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| FR-BLOCK-001 | Required current evidence lacks timestamp and no safe fallback exists. | BLOCKED | Vacation decision stops. | Missing timestamp is treated as current. | Source path, missing timestamp proof, decision purpose. |
| FR-BLOCK-002 | Branch or worktree mismatch exists for repo-state decision. | BLOCKED | Mismatch is named and safe next action is fresh preflight. | Evidence from wrong branch/worktree is accepted. | Expected branch/worktree, observed branch/worktree. |
| FR-BLOCK-003 | Evidence is malformed, contradictory, or missing required owner. | BLOCKED | Output names missing field or contradiction. | Parser guesses owner or state. | Raw evidence path, parse result, missing fields. |
| FR-BLOCK-004 | Evidence includes secret, broker/API, live trading, real order, webhook, or credential risk. | BLOCKED | Risk flag blocks continuation and wake/display logic escalates by severity. | Risk is hidden as stale or historical. | Source path, risk flag, decision purpose. |
| FR-BLOCK-005 | Required validator status is failed, not run, partial, or unknown. | BLOCKED | Protected or vacation decision cannot proceed. | Validator gap is ignored. | Validator status, required validation list, changed files. |
| FR-BLOCK-006 | Approval scope mismatches protected action, files, branch, command, or session. | BLOCKED | Approval cannot be projected as executable. | Mismatched approval enables action. | Approval scope, requested action, files, branch, command, expiry. |

## Timestamp Validation Tests

| Test ID | Requirement | Pass criteria | Fail criteria |
|---|---|---|---|
| FR-TIME-001 | Structured timestamps are preferred over file modified time. | Uses structured timestamp when present. | Uses file modified time over structured generated time. |
| FR-TIME-002 | File modified time fallback is marked as fallback. | Classification basis states fallback. | Fallback is presented as source-authored time. |
| FR-TIME-003 | Future timestamps are blocked. | Future source time becomes BLOCKED. | Future timestamp becomes CURRENT. |
| FR-TIME-004 | Clock skew is surfaced. | Skew beyond configured tolerance becomes BLOCKED or STALE. | Skew is ignored. |
| FR-TIME-005 | Expiration window is source-type specific. | Digest, runtime, git, validator, approval, and SOS use separate windows. | One generic window controls every source. |

## Freshness Ownership Tests

| Test ID | Requirement | Pass criteria | Fail criteria |
|---|---|---|---|
| FR-OWNER-001 | Queue freshness belongs to work packet owner. | Digest and dashboard consume queue freshness without owning it. | Digest or dashboard becomes queue authority. |
| FR-OWNER-002 | Approval freshness belongs to approval inbox and protected-action gate. | Projection emits approval-authority false. | Projection grants approval. |
| FR-OWNER-003 | Validator freshness belongs to validator evidence owner. | Validator result is checked against changed files. | Any old validator pass remains valid. |
| FR-OWNER-004 | Runtime freshness belongs to runtime telemetry only for runtime heartbeat. | Runtime freshness does not overwrite source evidence freshness. | Fresh heartbeat makes stale packet current. |
| FR-OWNER-005 | Relay is historical fallback by default. | Relay currentness requires current owner promotion. | Relay file path alone becomes current. |

## Stale Detection Tests

| Test ID | Requirement | Pass criteria | Fail criteria |
|---|---|---|---|
| FR-STALE-DETECT-001 | Git state expires after mutation or 15 minutes for repo decisions. | Fresh preflight required. | Old preflight supports vacation trial. |
| FR-STALE-DETECT-002 | Digest expires after 18 hours or source change. | Digest downgraded. | Latest pointer remains current. |
| FR-STALE-DETECT-003 | Approval expires after scope mismatch, consumption, rejection, or expiry. | Approval downgraded. | Old approval remains actionable. |
| FR-STALE-DETECT-004 | Validator expires after covered file changes. | Validator downgraded. | Old validation still supports changed file set. |
| FR-STALE-DETECT-005 | SOS notification expires after blocker transition. | Old dedupe cannot suppress new blocker. | Old `last_notified` suppresses current blocker. |

## Superseded Detection Tests

| Test ID | Requirement | Pass criteria | Fail criteria |
|---|---|---|---|
| FR-SUPER-DETECT-001 | Newer cycle supersedes older digest and supervisor outputs. | Older cycle becomes detail-only. | Older cycle drives status. |
| FR-SUPER-DETECT-002 | Newer approval event supersedes old approval status. | Old status cannot be replayed. | Old approval remains active. |
| FR-SUPER-DETECT-003 | Newer validator rerun supersedes older validator output. | Latest run controls validation state. | Older pass hides latest fail. |
| FR-SUPER-DETECT-004 | Newer alert or resolution supersedes old SOS alert. | Old alert does not wake. | Old alert wakes or suppresses incorrectly. |

## Morning Digest Freshness Validation

| Test ID | Input condition | Expected result |
|---|---|---|
| FR-DIGEST-001 | `MORNING_DIGEST_LATEST.md` dated 2026-06-02 is used for current 2026-06-07 vacation decision. | STALE for current decision and HISTORICAL as prior artifact. |
| FR-DIGEST-002 | `MORNING_DIGEST_STATE.json` says branch `main` clean while observed branch is dirty feature branch. | BLOCKED for repo-state vacation proof. |
| FR-DIGEST-003 | Digest is freshly generated from stale Relay or stale bridge inputs. | Digest projection may be fresh, but source freshness is STALE. |
| FR-DIGEST-004 | Digest reports approval count different from canonical or filtered projection count. | BLOCKED until approval owner read reconciles count. |
| FR-DIGEST-005 | Digest source freshness is unknown for queue, approval, validator, or worker state. | BLOCKED for 12-hour and overnight readiness. |

Pass condition: Morning Digest cannot classify as CURRENT unless artifact freshness and all status-impacting source inputs are CURRENT.

Fail condition: Any `*_LATEST.*` digest file becomes current without source-owner proof.

## Night Supervisor Freshness Validation

| Test ID | Input condition | Expected result |
|---|---|---|
| FR-NIGHT-001 | Current Night Supervisor cycle has current source inputs and active cycle ID. | CURRENT for cycle projection, evidence-only for authority. |
| FR-NIGHT-002 | Night Supervisor bridge generated after stale digest but includes stale digest as source. | Projection/source split; stale digest cannot become current. |
| FR-NIGHT-003 | Night Supervisor reports NEEDS_APPROVAL. | Display and approval-required status only; no execution authority. |
| FR-NIGHT-004 | Old Night Supervisor cycle is used after current repo mutation. | STALE or HISTORICAL for current decision. |
| FR-NIGHT-005 | Supervisor sees blocked source freshness for queue, approval, validator, worker, or SOS. | BLOCKED continuation. |

Pass condition: Night Supervisor output remains evidence-only and cannot launch workers, write queues, write approvals, stage, commit, push, schedule, or call external providers.

Fail condition: Current cycle timestamp hides stale source inputs.

## Dashboard Freshness Validation

| Test ID | Input condition | Expected result |
|---|---|---|
| FR-DASH-001 | Dashboard displays mock approval, queue, worker, SOS, or runtime fixtures. | HISTORICAL or display-only; not active state. |
| FR-DASH-002 | Dashboard serves live bridge projection with stale digest detail reference. | Dashboard card shows source stale classification. |
| FR-DASH-003 | Dashboard runtime visibility is fresh but packet evidence is stale. | Projection/source split is visible. |
| FR-DASH-004 | Dashboard lacks source label. | BLOCKED for vacation readiness display. |

Pass condition: Dashboard displays resolver classification and never infers authority from data source labels alone.

Fail condition: Mock or projection data is treated as canonical current state.

## Approval Freshness Validation

| Test ID | Input condition | Expected result |
|---|---|---|
| FR-APPROVAL-001 | Approval projection reads canonical approval inbox and exact scope matches pending display. | CURRENT projection with approval-authority false. |
| FR-APPROVAL-002 | Relay approval record appears active-looking. | HISTORICAL unless promoted by current canonical owner evidence. |
| FR-APPROVAL-003 | Approval is expired, consumed, rejected, or superseded. | SUPERSEDED or STALE, never actionable. |
| FR-APPROVAL-004 | Approval scope differs from requested protected action, branch, files, command, or session. | BLOCKED. |
| FR-APPROVAL-005 | Approval projection emits executable permission. | Fail test immediately. |

Pass condition: Approval visibility is trustworthy without creating a second approval authority.

Fail condition: Any projection, dashboard card, report, Relay item, or telemetry file becomes approval authority.

## Relay Freshness Validation

| Test ID | Input condition | Expected result |
|---|---|---|
| FR-RELAY-001 | Relay done, processed, report, alert, outbox, sample, or historical path is discovered. | HISTORICAL by default. |
| FR-RELAY-002 | Both `relay/` and `Relay/` paths reference same category on Windows. | Duplicate/casing risk surfaced; neither becomes active by path alone. |
| FR-RELAY-003 | Relay approval is used for active approval count. | BLOCKED unless canonical owner confirms current approval. |
| FR-RELAY-004 | Relay SOS outbox file is old but named like an alert. | HISTORICAL; no wake and no suppression. |

Pass condition: Relay remains legacy fallback and detail-only by default.

Fail condition: Relay records drive current operator absence state without current source-owner proof.

## Runtime Freshness Validation

| Test ID | Input condition | Expected result |
|---|---|---|
| FR-RUNTIME-001 | Runtime heartbeat freshness is current but embedded packet evidence is stale. | CURRENT runtime projection, STALE packet source. |
| FR-RUNTIME-002 | Runtime state lacks source paths or source timestamps for status-impacting evidence. | BLOCKED for vacation proof. |
| FR-RUNTIME-003 | Runtime state is older than configured runtime visibility threshold. | STALE. |
| FR-RUNTIME-004 | Runtime projection attempts to authorize action. | Fail test immediately. |

Pass condition: Runtime freshness reports visibility health without overriding source truth.

Fail condition: Runtime heartbeat is treated as proof of queue, approval, validator, worker, or SOS freshness.

## SOS Freshness Dependency Validation

| Test ID | Input condition | Expected result |
|---|---|---|
| FR-SOS-001 | Current unsuperseded blocker affects safe continuation. | `display_alert=true`, `sos_wake_required=true`, wake_class SOS_REQUIRED. |
| FR-SOS-002 | Routine approval-needed or review-needed item is current but not urgent. | `display_alert=true`, `sos_wake_required=false`, wake_class DISPLAY_ONLY. |
| FR-SOS-003 | Historical Relay SOS file exists. | `display_alert=false`, `sos_wake_required=false`, classification HISTORICAL. |
| FR-SOS-004 | Stale `last_notified` exists for old blocker. | Cannot suppress current blocker. |
| FR-SOS-005 | Duplicate current blocker has same source owner, blocker hash, and active transition. | Duplicate wake suppressed, display remains accurate. |
| FR-SOS-006 | Notifier proof lacks credentials because this is no-send mode. | No secret requested; proof remains no-send. |
| FR-SOS-007 | Missing freshness for a required vacation blocker. | BLOCKED and display alert true; SOS wake depends on severity classification. |

Pass condition: SOS wakes only on current unsuperseded blockers and never wakes from historical, stale, superseded, mock, or sample evidence.

Fail condition: Stale evidence suppresses SOS or historical evidence triggers SOS.

## Pass Criteria

The acceptance suite passes when:

1. Every critical test above has a defined expected classification.
2. Source-owner freshness, projection freshness, and decision purpose are present in each output.
3. Missing or unsafe required evidence becomes BLOCKED for vacation decisions.
4. Historical and superseded evidence remain detail-only.
5. Approval visibility never becomes approval authority.
6. SOS display and wake behavior are separated.
7. `executable=false` is present on every produced evidence object.
8. No test requires code creation, script creation, queue write, approval write, telemetry write, secret, broker/API, live trading, commit, push, or branch switching.

## Fail Criteria

The suite fails if any of these occur:

1. A latest pointer is treated as automatically current.
2. Projection timestamp is treated as proof that source evidence is current.
3. Relay or dashboard mock evidence drives active state.
4. Approval projection grants authority or executable action.
5. Stale validator, stale branch, stale digest, stale Night Supervisor, or stale runtime evidence supports a vacation trial.
6. Historical SOS wakes the operator.
7. Stale `last_notified` suppresses a current blocker.
8. Secret, broker/API, live trading, real order, credential, or webhook risk does not classify as BLOCKED.
9. Any output has `executable=true`.
10. Any test requires mutating protected paths or creating new architecture.

## Readiness Impact

| Proof state | 4-hour readiness | 12-hour readiness | Overnight readiness | Weekend readiness |
|---|---:|---:|---:|---:|
| Before suite | 64% | 50% | 39% | 28% |
| Suite defined | 66% | 53% | 42% | 31% |
| Suite executed and passed later | 72% | 57% | 44% | 34% |

This report defines the suite. It does not execute it. Execution requires a later preview-only resolver or proof runner under a separate approved packet.

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
MORNING_DIGEST_FRESHNESS_ACCEPTANCE_TESTS_APPLY_001

LANE:
MORNING_DIGEST_FRESHNESS_PROOF

ZONE:
AI_OS Vacation Candidate / Morning Digest Freshness

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
5. Read Reports/vacation_candidate/MORNING_DIGEST_FRESHNESS_AUDIT.md.
6. Read Reports/vacation_candidate/VACATION_READINESS_PROOF_LADDER.md.
7. Confirm branch/worktree state.
8. Run git status --short --branch.
9. Create only Reports/vacation_candidate/MORNING_DIGEST_FRESHNESS_ACCEPTANCE_TESTS.md.
10. Run git diff --check.
11. Run git status --short --branch.

MISSION:
Define the Morning Digest freshness acceptance-test suite required before any 12-hour vacation-readiness trial.

TASK:
Create a report-only test suite proving Morning Digest cannot report stale, historical, superseded, blocked, mock, Relay, approval, dashboard, runtime, or SOS evidence as current.

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
