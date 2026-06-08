# Night Supervisor Controlled-Cycle Proof

Packet ID: NIGHT_SUPERVISOR_CONTROLLED_CYCLE_PROOF_001
Lane: NIGHT_SUPERVISOR_CONTROLLED_CYCLE_PROOF
Mode: APPLY report-only
Branch observed: feature/full-operator-relief-closed-loop-v1
Worktree observed: C:\Dev\Ai.Os
Report date: 2026-06-07

## Purpose

This report defines controlled-cycle proof cases showing that Night Supervisor can process evidence safely without becoming execution authority.

It defines proof only. It creates no code, scripts, schemas, queues, approvals, telemetry, adapters, bridge, automation, commits, or pushes.

Night Supervisor proof passes only when it can classify current, stale, historical, superseded, blocked, approval-needed, SOS-required, and display-alert evidence while preserving the evidence-only boundary.

## Evidence-Only Boundary

Night Supervisor output is evidence and operator guidance only. It must not:

- mutate queues
- mutate approvals
- launch workers
- stage, commit, or push
- create PRs
- merge
- reset or clean
- create schedulers, daemons, or automation
- call OpenAI
- call MCP
- call external providers
- write telemetry
- touch broker, live-trading, real order, webhook, or secret paths

All controlled-cycle proof outputs must preserve:

```text
executable=false
queue_written=false
approval_written=false
telemetry_written=false
worker_launched=false
scheduler_created=false
provider_called=false
broker_called=false
commit_performed=false
push_performed=false
```

## Evidence Sources

Primary report evidence:

- `Reports/vacation_candidate/VACATION_READINESS_PROOF_LADDER.md`
- `Reports/vacation_candidate/EVIDENCE_FRESHNESS_ACCEPTANCE_TESTS.md`
- `Reports/vacation_candidate/MORNING_DIGEST_ACCEPTANCE_TESTS.md`
- `Reports/vacation_candidate/APPROVAL_PROJECTION_ACCEPTANCE_TESTS.md`
- `Reports/vacation_candidate/SOS_NO_SEND_PROOF.md`

Referenced future evidence sources:

- `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json`
- `telemetry/night_supervisor/last_notified.json`
- `telemetry/morning_digest/MORNING_DIGEST_STATE.json`
- `telemetry/morning_digest/MORNING_DIGEST_LATEST.md`
- `telemetry/runtime/runtime_state.json`
- `automation/orchestration/work_packets/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/workers/`
- `automation/orchestration/validators/`
- `automation/orchestration/commit_packages/`
- `relay/`
- `Relay/`
- dashboard projection sources

These are evidence references only. This report does not edit, execute, or write any referenced source.

## Required Evidence Inputs

| Input | Requirement |
|---|---|
| Cycle ID | Stable Night Supervisor cycle identifier. |
| Cycle timestamp | Generation or observation timestamp for the cycle. |
| Source list | Every evidence source consumed by the cycle. |
| Source owner | Canonical, projection, historical, or blocked owner for each source. |
| Source freshness | CURRENT, STALE, HISTORICAL, SUPERSEDED, or BLOCKED for each source. |
| Approval state | Active approval count, source owner, projection flag, and freshness. |
| Blocker state | Active blocker count, severity, source owner, and freshness. |
| SOS state | display_alert, sos_wake_required, wake_class, dedupe basis, and no-send status. |
| Branch/worktree state | Required when repo state affects the cycle. |
| Validator state | Required when cycle claims readiness or trial proof. |
| Safety boundary flags | No-write, no-launch, no-provider, no-broker, no-commit, and no-push flags. |

## Required Proof Outputs

| Output | Requirement |
|---|---|
| Cycle classification | CURRENT, STALE, HISTORICAL, SUPERSEDED, BLOCKED, NEEDS_APPROVAL, SOS_REQUIRED, or DISPLAY_ALERT. |
| Source classifications | Table of all major source inputs and freshness states. |
| Continuation decision | DISPLAY_ONLY, BLOCKED_REVIEW, SOS_REQUIRED, or READY_FOR_NEXT_PROOF. |
| Approval projection status | Current, stale, historical, superseded, blocked, or not applicable. |
| SOS status | display-only, wake required, stale suppressed, duplicate suppressed, or blocked. |
| Mutation flags | All queue, approval, telemetry, worker, scheduler, provider, broker, commit, and push flags false. |
| executable | Must always be false. |
| next_safe_action | Refresh source evidence, block trial, run SOS proof, run Gate 0 closeout, run 4-hour plan, or continue to next proof. |

## Controlled-Cycle Proof Cases

### CURRENT Evidence Cycle

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| NS-CURRENT-001 | Cycle has current source-owner evidence for queue, approval, validator, worker, digest, runtime, and SOS inputs. | Cycle classification CURRENT. | All source inputs are CURRENT and projection/source freshness is separated. | Cycle timestamp alone makes stale sources current. | Cycle ID, source table, freshness classifications. |
| NS-CURRENT-002 | Current cycle includes approval-needed display item that does not block continuation. | DISPLAY_ALERT or NEEDS_APPROVAL display-only. | Approval remains projection-only and executable=false. | Approval-needed becomes execution approval. | Approval projection, authority flag, source owner. |
| NS-CURRENT-003 | Current cycle includes current repo preflight matching branch/worktree. | Repo evidence CURRENT. | Branch/worktree match packet and dirty baseline is classified. | Old main/clean repo state is accepted. | Current branch, worktree, git status. |

### STALE Evidence Cycle

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| NS-STALE-001 | Cycle was generated before current repo mutation or current proof report creation. | STALE for current decision. | Cycle cannot support vacation trial without refresh. | Old cycle is accepted as current. | Cycle timestamp, mutation or newer evidence timestamp. |
| NS-STALE-002 | Cycle includes stale Morning Digest or stale digest state. | STALE_SOURCE and BLOCKED_REVIEW if status-impacting. | Stale digest does not become current through bridge. | Bridge timestamp hides stale digest input. | Bridge source list, digest timestamp. |
| NS-STALE-003 | Cycle includes stale approval projection. | STALE approval source. | Approval count must be refreshed or blocked. | Stale approval count remains active. | Approval projection timestamp, source timestamp. |
| NS-STALE-004 | Cycle includes stale runtime heartbeat or stale embedded packet evidence. | Projection/source split. | Runtime freshness does not override stale packet evidence. | Runtime heartbeat makes packet evidence current. | Runtime timestamp, packet evidence timestamp. |

### HISTORICAL Evidence Cycle

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| NS-HIST-001 | Cycle consumes Relay done, processed, outbox, report, or prior SOS record. | HISTORICAL detail-only. | Relay evidence cannot drive active state without current owner promotion. | Relay history drives current blockers or approvals. | Relay path, timestamp, source owner. |
| NS-HIST-002 | Cycle consumes bridge audit or vacation report as runtime proof. | HISTORICAL for runtime decisions. | Report is supporting evidence only. | Report becomes queue or approval source. | Report path, report date. |
| NS-HIST-003 | Cycle consumes dashboard mock fixture. | HISTORICAL or mock-only display. | Mock cannot affect active status. | Mock fixture drives cycle state. | Dashboard source label, fixture path. |

### SUPERSEDED Evidence Cycle

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| NS-SUPER-001 | Newer Night Supervisor cycle exists for same purpose. | Older cycle SUPERSEDED. | Older cycle becomes detail-only. | Older cycle drives latest status. | Old and new cycle IDs, timestamps. |
| NS-SUPER-002 | Newer digest, approval, blocker, validator, or SOS transition supersedes cycle input. | Cycle becomes STALE or SUPERSEDED for that source. | Newer source transition controls display. | Superseded cycle input remains active. | Source timestamps, transition IDs. |
| NS-SUPER-003 | Approval consumed or replaced after cycle generation. | Approval source SUPERSEDED. | Cycle cannot use old approval count. | Consumed approval stays active. | Approval history, cycle timestamp. |
| NS-SUPER-004 | SOS alert superseded by newer blocker transition or resolution. | Old SOS state SUPERSEDED. | Old alert does not wake or suppress. | Old SOS state drives current wake. | Alert key, blocker hash, newer transition. |

### BLOCKED Evidence Cycle

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| NS-BLOCKED-001 | Required source evidence is missing, malformed, contradictory, or owner-unknown. | BLOCKED. | Cycle stops safe continuation. | Missing source is treated safe. | Missing field proof, source path. |
| NS-BLOCKED-002 | Branch/worktree mismatch exists. | BLOCKED. | Mismatch is named and fresh preflight required. | Wrong branch evidence is accepted. | Expected and observed branch/worktree. |
| NS-BLOCKED-003 | Validator required but failed, stale, partial, or not run. | BLOCKED. | Cycle cannot claim readiness. | Validator gap is ignored. | Validator status, changed files. |
| NS-BLOCKED-004 | Evidence contains secret, broker/API, live-trading, real-order, webhook, or credential risk. | BLOCKED and SOS-required based on severity. | Risk is surfaced without exposing secret value. | Risk is downgraded or hidden. | Redacted risk marker, source path. |

### Approval-Needed Cycle

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| NS-APPROVAL-001 | Current routine approval-needed item exists. | NEEDS_APPROVAL display-only. | No approval mutation and no execution permission. | Needs approval becomes approved. | Approval status, source owner, projection flags. |
| NS-APPROVAL-002 | Approval needed for protected action before continuation. | BLOCKED_REVIEW or SOS_REQUIRED. | Protected action stops until exact approval. | Supervisor proceeds with protected action. | Protected action type, approval scope. |
| NS-APPROVAL-003 | Approval evidence is stale, historical, or projection-only. | STALE, HISTORICAL, or PROJECTION display only. | Projection cannot authorize. | Projection becomes approval authority. | Approval source, freshness, authority flag. |

### SOS-Required Cycle

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| NS-SOS-001 | Current unsuperseded safety blocker exists. | SOS_REQUIRED. | `sos_wake_required=true` in proof output and no real notification sent. | Current blocker hidden or sent directly. | Blocker ID, severity, no-send flag. |
| NS-SOS-002 | Current secret, broker/live-trading, protected-action, or unauthorized mutation risk exists. | SOS_REQUIRED or BLOCKED_REVIEW. | Risk blocks continuation and remains no-send. | Risk proceeds or sends notification. | Risk class, source path, no-send proof. |
| NS-SOS-003 | Stale or historical SOS evidence exists. | Suppressed from wake. | Historical/stale evidence cannot wake or suppress current blocker. | Old SOS state drives wake/no-wake. | SOS path, timestamp, freshness. |

### Display-Alert Cycle

| Test ID | Input condition | Expected result | Pass criteria | Fail criteria | Evidence required |
|---|---|---|---|---|---|
| NS-DISPLAY-001 | Routine review, stale digest, or non-urgent approval state should be visible but not wake. | DISPLAY_ALERT. | `display_alert=true`, `sos_wake_required=false`. | Routine display wakes Anthony. | Alert class, severity, source freshness. |
| NS-DISPLAY-002 | Dashboard or Morning Digest needs stale label. | DISPLAY_ALERT with freshness label. | Display output includes source owner and freshness. | Stale label omitted. | Dashboard/digest source classification. |
| NS-DISPLAY-003 | Historical evidence appears for operator context. | DISPLAY_ONLY or HISTORICAL detail. | Does not affect active continuation decision. | Historical context becomes active state. | Historical path, classification. |

## Safety Boundary Verification

| Test ID | Boundary | Expected result | Fail condition |
|---|---|---|---|
| NS-SAFE-001 | Queue mutation | `queue_written=false` | Any queue write occurs or is recommended as automatic. |
| NS-SAFE-002 | Approval mutation | `approval_written=false` | Any approval write occurs or is recommended as automatic. |
| NS-SAFE-003 | Worker launch | `worker_launched=false` | Worker launch occurs or is recommended without separate approval. |
| NS-SAFE-004 | Commit | `commit_performed=false` | Commit occurs or is authorized by supervisor output. |
| NS-SAFE-005 | Push | `push_performed=false` | Push occurs or is authorized by supervisor output. |
| NS-SAFE-006 | Scheduler creation | `scheduler_created=false` | Scheduler, daemon, or background loop is created. |
| NS-SAFE-007 | Broker/live trading | `broker_called=false` | Broker/API/live-trading path is touched. |
| NS-SAFE-008 | OpenAI execution | `provider_called=false` | OpenAI call is made or authorized. |
| NS-SAFE-009 | MCP execution | `provider_called=false` | MCP call is made or authorized. |
| NS-SAFE-010 | Telemetry write | `telemetry_written=false` | Telemetry is written under this report-only proof. |

## Pass Criteria

Night Supervisor controlled-cycle proof passes when:

1. CURRENT, STALE, HISTORICAL, SUPERSEDED, BLOCKED, approval-needed, SOS-required, and display-alert cycles have explicit pass/fail cases.
2. Source-owner freshness and projection freshness remain separate.
3. Stale, historical, superseded, or missing required evidence cannot support unattended continuation.
4. Approval-needed cycles remain display or blocked-review only and never grant approval.
5. SOS-required cycles remain no-send and do not call providers.
6. Display-alert cycles do not wake the operator unless severity requires SOS.
7. All no-mutation, no-launch, no-provider, no-broker, no-commit, no-push, and no-telemetry flags remain false.
8. `executable=false` remains invariant.

## Fail Criteria

Night Supervisor controlled-cycle proof fails if:

1. Cycle timestamp alone makes stale source evidence current.
2. Relay, dashboard mock, report, or historical evidence drives active state.
3. Approval-needed is treated as execution approval.
4. Validator pass is treated as protected-action permission.
5. Stale or superseded SOS evidence wakes or suppresses current blocker.
6. Missing required source evidence is treated as safe.
7. Any queue, approval, telemetry, source, worker, scheduler, provider, broker, commit, push, merge, reset, clean, or branch-switch action occurs.
8. Any OpenAI, MCP, broker/API, webhook, notification provider, or external service call occurs.
9. Any output is executable.

## Evidence Required To Execute The Suite Later

Minimum evidence needed:

- current branch and worktree
- current `git status --short --branch`
- Night Supervisor cycle ID and timestamp
- source list with owner and freshness classification
- Morning Digest state and freshness classification
- Approval Projection state and freshness classification
- SOS no-send state and dedupe classification
- runtime projection/source freshness split
- validator status and timestamp where readiness is claimed
- blocker count and approval count with source owner
- explicit safety boundary flags

## Acceptance Threshold

Night Supervisor trust passes only when all critical cycle tests and all safety boundary tests pass.

Any failure in queue mutation, approval mutation, worker launch, scheduler creation, telemetry write, provider call, broker/live-trading path, secret handling, commit, push, protected action, SOS current blocker, or executable invariance blocks overnight readiness.

Weekend readiness additionally requires superseded and multi-cycle stale handling to pass.

## Readiness Impact

| State | 4-hour readiness | 12-hour readiness | Overnight readiness | Weekend readiness |
|---|---:|---:|---:|---:|
| Before Night Supervisor controlled-cycle proof | 69% | 61% | 51% | 39% |
| Proof defined | 70% | 63% | 55% | 42% |
| Proof executed and passed later | 75% | 70% | 63% | 54% |

This report defines the proof. It does not execute it.

## Exact Next APPLY Packet

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
FOUR_HOUR_TRIAL_ACCEPTANCE_PLAN_APPLY_001

LANE:
FOUR_HOUR_TRIAL_PROOF

ZONE:
AI_OS Vacation Candidate / Four-Hour Trial

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
4. Read Reports/vacation_candidate/VACATION_READINESS_PROOF_LADDER.md.
5. Read Reports/vacation_candidate/EVIDENCE_FRESHNESS_ACCEPTANCE_TESTS.md.
6. Read Reports/vacation_candidate/MORNING_DIGEST_ACCEPTANCE_TESTS.md.
7. Read Reports/vacation_candidate/APPROVAL_PROJECTION_ACCEPTANCE_TESTS.md.
8. Read Reports/vacation_candidate/SOS_NO_SEND_PROOF.md.
9. Read Reports/vacation_candidate/NIGHT_SUPERVISOR_CONTROLLED_CYCLE_PROOF.md.
10. Confirm branch/worktree state.
11. Create only Reports/vacation_candidate/FOUR_HOUR_TRIAL_ACCEPTANCE_PLAN.md.
12. Run git diff --check.
13. Run git status --short --branch.

MISSION:
Create the four-hour vacation trial acceptance plan.

TASK:
Define pass/fail gates for start snapshot, no-mutation interval, evidence freshness, Morning Digest display, Approval Projection display, SOS no-send behavior, Night Supervisor controlled-cycle behavior, final snapshot, blocker handling, and safe next action.

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
- Do not create a new bridge, queue, approval system, adapter, scheduler, worker, notifier, or automation.

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

Report created only under `Reports/vacation_candidate/`. No source code, scripts, schemas, queues, approvals, telemetry, automation, commits, pushes, branch switching, live trading paths, broker paths, secrets, new bridge, new queue, new adapter, scheduler, worker, or approval system were created.
