# Vacation Readiness Proof Ladder

Packet ID: `VACATION_READINESS_PROOF_LADDER_APPLY_001`
Lane: `VACATION_PROOF_LADDER`
Mode: `APPLY` report-only
Branch observed: `feature/full-operator-relief-closed-loop-v1`
Worktree observed: `C:\Dev\Ai.Os`
Report date: 2026-06-07

## Purpose

This report defines the master proof ladder for moving AI_OS from current vacation-readiness assessment to evidence-backed vacation candidate.

It does not create code, scripts, queues, approvals, telemetry, automation, commits, pushes, bridges, or schemas. It defines the exact pass/fail sequence for:

- 4-hour candidate
- 12-hour candidate
- overnight candidate
- weekend candidate

Current baseline from `VACATION_READINESS_MAX_PUSH.md`:

| Absence window | Current readiness | Candidate threshold |
|---|---:|---:|
| 4 hours | 64% | 70% |
| 12 hours | 50% | 65% |
| Overnight | 39% | 60% |
| Weekend | 28% | 70% |

## Gate Principles

1. Proof must use current source-owner evidence, not stale report confidence.
2. Evidence is never approval.
3. Projection is never authority.
4. Validator pass is never protected-action permission.
5. No vacation trial begins with unknown dirty state.
6. No SOS rule is trusted until stale suppression and duplicate suppression are proven.
7. No weekend simulation begins until 4-hour, 12-hour, and overnight gates have passed in order.

## Full Proof Ladder

### Proof Gate 0: Dirty Baseline Trust

| Field | Definition |
|---|---|
| Purpose | Prove the repo state is known, classified, and safe to use as the starting point for vacation-readiness proof. |
| Pass criteria | Current branch equals `feature/full-operator-relief-closed-loop-v1`; worktree equals `C:\Dev\Ai.Os`; every dirty or untracked path is classified; modified backup script is inspected, parked, or assigned to a dedicated package; no unknown dirty source remains in the trial baseline. |
| Fail criteria | Branch mismatch; worktree mismatch; unclassified dirty path; protected script/source patch affects trial confidence; untracked executable source is treated as stable runtime; any secret, broker, live-trading, queue-write, approval-write, commit, push, merge, reset, or clean request appears. |
| Evidence required | `git status --short --branch`; `git diff --stat`; `Reports/vacation_candidate/VACATION_BASELINE_CLASSIFICATION.md`; backup patch review or explicit park decision; current no-commit/no-push boundary. |
| Dependencies | AGENTS authority; README repo identity; WHITEPAPER trading boundary; current branch/worktree preflight. |
| Blockers | `scripts/backup/Start-AiOsT9SnapshotBackup.ps1` remains a modified protected script; report and adapter trees remain untracked until packaged or parked. |
| Readiness increase | 4h: +6; 12h: +2; overnight: +1; weekend: +1. |
| Next gate unlocked | Proof Gate 1: Evidence Freshness Trust. |

### Proof Gate 1: Evidence Freshness Trust

| Field | Definition |
|---|---|
| Purpose | Prove AI_OS can classify evidence consistently as `CURRENT`, `STALE`, `HISTORICAL`, `BLOCKED`, or `SUPERSEDED`. |
| Pass criteria | Acceptance report defines pass/fail cases for current source-owner evidence, stale digest, historical Relay, dashboard mock data, branch mismatch, validator outdated, approval expired/consumed, projection-fresh/source-stale, and SOS current blocker. |
| Fail criteria | `*_LATEST.*` is treated as automatically current; Relay or dashboard mock evidence drives active state; projection timestamp hides stale source evidence; missing source timestamp is accepted for current vacation decisions. |
| Evidence required | `Reports/vacation_candidate/EVIDENCE_FRESHNESS_RESOLVER_DISCOVERY.md`; acceptance matrix; current source-owner list; expiration windows; stale/superseded rules. |
| Dependencies | Gate 0; canonical source-owner rules for work packets, approvals, workers, validators, commit packages, runtime projection, reports, and Relay fallback. |
| Blockers | Resolver not yet acceptance-tested; no single consumer currently enforces source freshness across Morning Digest, Night Supervisor, Dashboard, Relay, SOS, and telemetry. |
| Readiness increase | 4h: +2; 12h: +5; overnight: +4; weekend: +5. |
| Next gate unlocked | Proof Gate 2: Morning Digest Trust. |

### Proof Gate 2: Morning Digest Trust

| Field | Definition |
|---|---|
| Purpose | Prove Morning Digest and Morning Brief can distinguish current status from stale, historical, superseded, or blocked evidence. |
| Pass criteria | Digest artifact freshness and source freshness are reported separately; stale `MORNING_DIGEST_LATEST.md` from 2026-06-02 is classified stale/historical for current decisions; digest cannot claim current branch `main` clean while current branch is dirty feature branch; approval count mismatch is surfaced; fresh projection from stale source is downgraded. |
| Fail criteria | Digest file age alone is accepted as current; stale Relay approvals inflate active approval count; dashboard cards link to stale digest detail without classification; stale `last_notified` suppresses SOS; missing canonical queue/approval/validator source reads are treated as safe. |
| Evidence required | `Reports/vacation_candidate/MORNING_DIGEST_FRESHNESS_AUDIT.md`; current git preflight; digest state timestamp; bridge state timestamp; approval count comparison; source-owner freshness classification. |
| Dependencies | Gate 1; Morning Digest source list; Night Supervisor bridge projection; canonical approval owner classification. |
| Blockers | Current audit says Morning Digest is blocking for 12-hour, overnight, and weekend readiness until source freshness is enforced. |
| Readiness increase | 4h: +1; 12h: +5; overnight: +4; weekend: +4. |
| Next gate unlocked | Proof Gate 3: Approval Projection Trust. |

### Proof Gate 3: Approval Projection Trust

| Field | Definition |
|---|---|
| Purpose | Prove AI_OS can show approval state without creating a second approval authority. |
| Pass criteria | `automation/orchestration/approval_inbox/` remains the sole canonical owner; all telemetry, dashboard, Relay, Operation Glue, service-local, and historical approval surfaces classify as projection, historical, superseded, or blocked; every projection emits approval-authority false and approval-mutation false; active count agrees across proof outputs. |
| Fail criteria | Relay approval becomes current authority; dashboard mock approval is counted as active; archived approval replays; broad old APPLY gate is treated as executable; service in-memory approval is treated as canonical; projection output mutates approval state. |
| Evidence required | `Reports/vacation_candidate/APPROVAL_PROJECTION_DISCOVERY.md`; canonical approval source list; active approval count; projection classification matrix; exact status rules for pending, completed, expired, rejected, historical, superseded, and blocked. |
| Dependencies | Gates 0-2; canonical approval owner; freshness resolver acceptance rules. |
| Blockers | Approval projection acceptance tests do not yet exist; active `APPLY_APPROVAL_GATE_001.json` is pending review and broad, so it does not authorize execution. |
| Readiness increase | 4h: +1; 12h: +4; overnight: +4; weekend: +5. |
| Next gate unlocked | Proof Gate 4: SOS No-Send Trust. |

### Proof Gate 4: SOS No-Send Trust

| Field | Definition |
|---|---|
| Purpose | Prove SOS wake logic without sending notifications, using current unsuperseded blocker evidence only. |
| Pass criteria | `display_alert=true` is separated from `sos_wake_required=true`; routine review stays display-only; current safety blocker wakes; stale blocker does not wake; historical Relay SOS does not wake; duplicate blocker suppresses repeat wake; stale `last_notified` cannot suppress current blocker; simulated delivery failure becomes blocked evidence. |
| Fail criteria | Historical SOS file wakes; stale `last_notified` suppresses active blocker; every `NEEDS_APPROVAL` wakes; duplicate wake fires repeatedly for same blocker; notifier proof requires credentials or real send; failover is unclassified. |
| Evidence required | SOS no-send proof report; blocker identity rule; source owner and hash rule; duplicate suppression rule; stale suppression rule; delivery failure classification; no-secret/no-send validation. |
| Dependencies | Gates 1-3; Morning Digest stale rules; Approval Projection display versus wake boundary; Night Supervisor evidence-only boundary. |
| Blockers | Existing evidence has SOS fields, but no proof of delivery, dedupe, stale suppression, or failover behavior. |
| Readiness increase | 4h: +1; 12h: +2; overnight: +6; weekend: +6. |
| Next gate unlocked | Proof Gate 5: Night Supervisor Trust. |

### Proof Gate 5: Night Supervisor Trust

| Field | Definition |
|---|---|
| Purpose | Prove Night Supervisor can classify current, stale, blocked, approval-needed, and superseded cycles without executing work or mutating authority. |
| Pass criteria | Controlled cycle classifies current evidence as current; old digest and runtime projection as stale/historical; blocked evidence as blocker; approval-needed evidence as display/approval-required only; superseded evidence as detail-only; supervisor output remains evidence-only and cannot launch workers, mutate packets, mutate approvals, stage, commit, push, schedule, call APIs, or touch broker/live paths. |
| Fail criteria | Night Supervisor treats stale digest as current; old Relay approval drives active state; validator pass becomes approval; `NEEDS_APPROVAL` is treated as execution permission; supervisor writes queue, approval, telemetry, or source paths outside a scoped future packet. |
| Evidence required | Night Supervisor proof report; current cycle fixture or frozen evidence set; stale cycle evidence; blocked cycle evidence; approval-needed cycle evidence; superseded cycle evidence; safety-boundary readback. |
| Dependencies | Gates 1-4; Morning Digest trust; Approval Projection trust; SOS no-send trust. |
| Blockers | Current bridge state is evidence-only and useful, but not yet proven as current for 2026-06-07 dirty feature branch state. |
| Readiness increase | 4h: +0; 12h: +2; overnight: +5; weekend: +5. |
| Next gate unlocked | Proof Gate 6: 4-Hour Trial. |

### Proof Gate 6: 4-Hour Trial

| Field | Definition |
|---|---|
| Purpose | Prove AI_OS can sit unattended for four hours without false safety, silent blocker, or unauthorized action. |
| Pass criteria | Gates 0-5 pass or have explicit non-blocking exceptions; current branch/worktree snapshot captured; no protected actions run; no source mutation occurs; no queue/approval/telemetry writes occur; SOS no-send classifier would wake for true blocker; final readout shows current status, stale items, blockers, approvals, and safe next action. |
| Fail criteria | Dirty baseline changes during trial without classification; protected action requested or attempted; stale digest displayed as current; SOS classifier misses current blocker; routine display alert becomes wake; live/broker/secret path appears. |
| Evidence required | 4-hour trial plan; start snapshot; end snapshot; no-mutation validation; SOS no-send result; Morning Digest source classification; approval projection result. |
| Dependencies | Gates 0-5. |
| Blockers | Current backup script patch remains the strongest 4-hour blocker until inspected or parked. |
| Readiness increase | 4h reaches 72%; 12h +1; overnight +1; weekend +1. |
| Next gate unlocked | Proof Gate 7: 12-Hour Trial. |

### Proof Gate 7: 12-Hour Trial

| Field | Definition |
|---|---|
| Purpose | Prove AI_OS can cover a half-day operator absence with trustworthy current-state reporting. |
| Pass criteria | 4-hour trial passed; Codex final evidence normalizes; Evidence Freshness, Morning Digest, Approval Projection, SOS, and Night Supervisor reports agree on active blocker and approval state; stale evidence is downgraded; end-of-trial readout is actionable without raw tree inspection. |
| Fail criteria | Morning Digest and Night Supervisor disagree; active approval count mismatch remains unexplained; stale Relay or dashboard mock data drives active state; source freshness is unknown for queue, approval, validator, or worker state; no current safe next action exists. |
| Evidence required | 12-hour trial report; normalized Codex evidence; current/stale classification output; digest/bridge alignment proof; approval projection proof; no-send SOS proof. |
| Dependencies | Gate 6 plus evidence normalization proof. |
| Blockers | Freshness and approval projection are current 12-hour blockers until acceptance-tested. |
| Readiness increase | 12h reaches 68%; overnight +2; weekend +2. |
| Next gate unlocked | Proof Gate 8: Overnight Trial. |

### Proof Gate 8: Overnight Trial

| Field | Definition |
|---|---|
| Purpose | Prove AI_OS can run an overnight evidence cycle and only interrupt Anthony for true SOS or unsafe continuation. |
| Pass criteria | 12-hour trial passed; Night Supervisor controlled cycle passes; Morning Digest cannot report stale inputs as current; SOS stale suppression and duplicate suppression pass; protected action, live/broker, secret, scheduler, queue-write, approval-write, commit, push, merge, reset, and clean requests stop safely. |
| Fail criteria | Any stale source suppresses SOS; historical alert wakes; routine approval review wakes unnecessarily; Night Supervisor cycle cannot produce a final handoff; dashboard/display surfaces active-looking mock data; protected action path proceeds without Anthony. |
| Evidence required | Overnight trial report; Night Supervisor proof; SOS no-send proof; Morning Digest final handoff; approval projection consistency proof; protected-action stop proof. |
| Dependencies | Gate 7. |
| Blockers | SOS and Night Supervisor proof gaps are current overnight blockers. |
| Readiness increase | Overnight reaches 63%; weekend +4. |
| Next gate unlocked | Proof Gate 9: Weekend Simulation. |

### Proof Gate 9: Weekend Simulation

| Field | Definition |
|---|---|
| Purpose | Prove AI_OS can survive multiple unattended cycles with evidence expiration, failover, and consolidation behavior. |
| Pass criteria | Overnight trial passed; multi-cycle freshness expiration works; superseded evidence cannot drive latest status; queue and approval projections are canonical-owner aligned; Relay casing/historical evidence is classified; failover cases for missed cycle, stale telemetry, notifier failure, queue reader failure, approval reader failure, and dashboard stale display pass; all work remains no-commit/no-push unless separately approved. |
| Fail criteria | Missed cycle is invisible; stale telemetry appears healthy; notifier failure is silent; approval/queue reader failure is not blocked; Relay or Operation Glue becomes authority; dashboard mock data is shown as live; branch state changes without classification. |
| Evidence required | Weekend simulation report; multi-cycle state table; failover case matrix; queue projection mapping; approval projection mapping; Relay consolidation classification; final morning handoff. |
| Dependencies | Gate 8; queue projection mapping; Relay consolidation classification; package or parking plan for dirty branch. |
| Blockers | Multi-cycle proof, failover proof, queue/approval consolidation, and Relay classification remain incomplete. |
| Readiness increase | Weekend reaches 72% if all prior gates remain current. |
| Next gate unlocked | Vacation candidate review and selective commit/package closeout. |

## Gate Dependency Graph

```text
Gate 0 Dirty Baseline Trust
  -> Gate 1 Evidence Freshness Trust
    -> Gate 2 Morning Digest Trust
      -> Gate 3 Approval Projection Trust
        -> Gate 4 SOS No-Send Trust
          -> Gate 5 Night Supervisor Trust
            -> Gate 6 4-Hour Trial
              -> Gate 7 12-Hour Trial
                -> Gate 8 Overnight Trial
                  -> Gate 9 Weekend Simulation
```

Parallel support work allowed after Gate 1:

```text
Codex result evidence hardening
Approval projection acceptance tests
Morning Digest freshness acceptance tests
SOS no-send discovery
Night Supervisor proof discovery
Relay consolidation discovery
Queue projection mapping
```

Parallel support work must remain report-only or preview-only until its upstream gate is complete.

## Fastest Path

Fastest route to a vacation candidate:

1. Finish Gate 0 by inspecting or parking the backup patch and packaging the dirty baseline.
2. Define acceptance tests for Gate 1 rather than building resolver code first.
3. Use Gate 1 classifications to prove Morning Digest freshness.
4. Prove approval projection before any approval UI or service changes.
5. Prove SOS in no-send mode.
6. Prove Night Supervisor with frozen current/stale/blocked/approval/superseded evidence.
7. Run 4-hour trial.
8. Run 12-hour trial.
9. Run overnight trial.
10. Only then run weekend simulation.

Do not add a bridge, queue, approval system, live notifier, scheduler, OpenAI loop, MCP loop, or dashboard command center to accelerate this sequence.

## Critical Path

```text
Dirty baseline trust
-> Evidence freshness acceptance
-> Morning Digest source freshness
-> Approval projection authority boundary
-> SOS no-send stale and duplicate suppression
-> Night Supervisor controlled-cycle proof
-> 4-hour trial
-> 12-hour trial
-> overnight trial
-> weekend failover simulation
```

Critical risk:

```text
If freshness is wrong, every later gate can produce false safety or false interruption.
```

## Estimated Readiness After Each Gate

Estimates assume the gate passes and no new dirty or stale evidence appears afterward.

| Gate | 4h readiness | 12h readiness | Overnight readiness | Weekend readiness |
|---|---:|---:|---:|---:|
| Current state | 64% | 50% | 39% | 28% |
| Gate 0 | 70% | 52% | 40% | 29% |
| Gate 1 | 72% | 57% | 44% | 34% |
| Gate 2 | 73% | 62% | 48% | 38% |
| Gate 3 | 74% | 66% | 52% | 43% |
| Gate 4 | 75% | 68% | 58% | 49% |
| Gate 5 | 75% | 70% | 63% | 54% |
| Gate 6 | 72% proven | 71% | 64% | 55% |
| Gate 7 | 72% proven | 68% proven | 66% | 57% |
| Gate 8 | 72% proven | 68% proven | 63% proven | 61% |
| Gate 9 | 72% proven | 68% proven | 63% proven | 72% proven |

## Estimated Remaining Time After Each Gate

Timeline estimates are checkpoint ranges, not deadline promises.

| Gate completed | Remaining path to 4h | Remaining path to 12h | Remaining path to overnight | Remaining path to weekend |
|---|---|---|---|---|
| Current state | same session to 1 work session | 1-2 work sessions | 2-4 work sessions | multi-checkpoint |
| Gate 0 | same session | 1-2 work sessions | 2-3 work sessions | multi-checkpoint |
| Gate 1 | same session | 1 work session | 2-3 work sessions | multi-checkpoint |
| Gate 2 | same session | same session to 1 work session | 1-2 work sessions | multi-checkpoint |
| Gate 3 | same session | same session | 1-2 work sessions | multi-checkpoint |
| Gate 4 | same session | same session | 1 work session | 2-4 work sessions |
| Gate 5 | same session | same session | same session to 1 work session | 2-3 work sessions |
| Gate 6 | complete | same session to 1 work session | 1 work session | 2-3 work sessions |
| Gate 7 | complete | complete | same session to 1 work session | 1-2 work sessions |
| Gate 8 | complete | complete | complete | 1-2 work sessions |
| Gate 9 | complete | complete | complete | complete |

## Exact Next Apply Packet

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
VACATION_GATE_0_BASELINE_CLOSEOUT_APPLY_001

LANE:
VACATION_GATE_0_BASELINE_CLOSEOUT

ZONE:
AI_OS Vacation Candidate / Gate 0 Baseline Trust

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
4. Read Reports/vacation_candidate/VACATION_BASELINE_CLASSIFICATION.md.
5. Read Reports/vacation_candidate/VACATION_READINESS_PROOF_LADDER.md.
6. Confirm branch/worktree state.
7. Run git status --short --branch.
8. Run git diff --stat.
9. Create only Reports/vacation_candidate/VACATION_GATE_0_BASELINE_CLOSEOUT.md.
10. Run git diff --check.
11. Run git status --short --branch.

MISSION:
Close Proof Gate 0 by determining whether the current dirty baseline is trusted, blocked, or requires parking before any 4-hour trial.

TASK:
Create a report-only Gate 0 closeout that classifies the backup script patch, untracked reports, adapter source, tests, fixtures, and branch-ahead state against the Gate 0 pass/fail criteria.

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
- Do not create a new bridge, queue, or approval system.

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

Report only. No source files edited. No scripts created. No queue files written. No approval files written. No telemetry written. No commit. No push.
