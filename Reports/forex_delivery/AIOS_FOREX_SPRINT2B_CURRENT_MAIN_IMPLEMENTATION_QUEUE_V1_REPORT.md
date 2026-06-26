# AIOS Forex Sprint 2B Current Main Implementation Queue V1 Report

## Packet Identity

- Packet ID: AIOS-FOREX-SPRINT2B-CURRENT-MAIN-IMPLEMENTATION-QUEUE-V1
- Mode: APPLY
- Zone: Reports Only
- Lane: Forex Sprint 2B Current Main Implementation Queue
- Worktree: C:\Dev\Ai.Os
- Branch: main
- Report path: Reports/forex_delivery/AIOS_FOREX_SPRINT2B_CURRENT_MAIN_IMPLEMENTATION_QUEUE_V1_REPORT.md

## Boundary

This report creates an implementation queue only. It creates no runtime authority, broker authority, credential authority, account authority, order authority, trade authority, live-trading authority, protected-action authority, staging authority, commit authority, push authority, PR authority, merge authority, branch authority, scheduler authority, daemon authority, webhook authority, or dashboard mutation authority.

No branch switch, branch creation, staging, commit, push, PR creation, merge, reset, clean, stash, runtime edit, test edit, script edit, app edit, schema edit, broker call, secret read, environment read, dashboard mutation, trade placement, or production mutation was authorized or performed by this packet.

## Preflight

Required command:

```powershell
git status --short --branch
```

Observed before creating this report:

```text
## main...origin/main
```

Result:

- Current branch: main
- Dirty worktree before report creation: no
- Target report existed before this packet: no
- Current clean-main baseline: accepted for report creation

After this report is created, future implementation packets must treat the worktree as dirty until this report is intentionally preserved, committed through a separately approved protected-action gate, or the implementation work starts in an isolated clean worktree.

## 1. Why Sprint 1 Worked

Sprint 1 worked because it used bounded parallel reporting, not parallel runtime mutation.

The successful pattern was:

1. Every worker observed the branch/worktree state before writing.
2. Each worker had one exact report output path.
3. Workers could read overlapping evidence but did not write the same file tree.
4. Runtime code, tests, scripts, apps, schemas, protected actions, broker access, secrets, and live trading were blocked.
5. A synthesis worker collapsed specialized reports into one queue before protected actions or implementation.
6. Commit/push remained separate protected actions after report generation.

The useful throughput came from narrowing each worker's question and output, not from loosening governance.

## 2. Why The Failed Sprint 2 Attempt Blocked

The failed Sprint 2 attempt blocked because it tried to move from report-first parallelism into implementation without preserving the same safety shape.

Blocking conditions:

- Implementation work touches shared runtime, script, test, app, or schema surfaces, so same-branch simultaneous implementation workers can collide.
- A dirty shared worktree makes branch assumptions unsafe.
- New implementation branches from a dirty worktree risk carrying unrelated report or authority state.
- Dashboard, risk, candidate, broker-health, profitability, demo-intent, and stop-control work share downstream contracts, so out-of-order implementation can create mismatched truth.
- Validator output is evidence only; it does not approve staging, commit, push, PR creation, merge, broker access, or live execution.

Sprint 2B must therefore keep parallelism in report-first planning and serialize actual code PRs from a clean observed baseline.

## 3. Current Clean-Main Baseline

Current baseline for this queue:

- Branch: main
- Pre-report status: clean
- Remote tracking marker: main...origin/main
- Shared baseline intent: all Sprint 2B implementation PRs start from current clean main, not from the old dirty feature branch.
- Current packet output: one new report file only.

Baseline rule:

Do not start an implementation packet from this same worktree after this report unless `git status --short --branch` is clean again. If this report remains uncommitted, use a separate clean worktree or run the protected commit gate first.

## 4. Worker Lane Model For Same-Branch Report-First Execution

Safe same-branch report-first lane model:

| Lane type | Parallel-safe on same branch | Write boundary | Stop point |
| --- | --- | --- | --- |
| Report-only planning | Yes, when each worker has one unique report path and the worktree is clean at preflight | Reports/forex_delivery single-file output | Stop after report and validators |
| Evidence classification | Yes, when report-only and no file moves/deletes | Reports/forex_delivery single-file output | Stop after report and validators |
| Queue synthesis | No, should run after planning reports exist | One synthesis report | Stop after queue report |
| Runtime implementation | No on one shared worktree | Exact code, script, test, report files for one PR | Stop after validation, no commit/push unless separately approved |
| Dashboard/app implementation | No on one shared worktree | Exact app and test files for one PR | Stop after validation, no commit/push unless separately approved |
| Protected action | Never parallel | Exact approved files/action only | Stop after requested protected action |

Same-branch report-first execution remains useful only when all workers are bounded to unique reports and no worker changes implementation files.

## 5. Implementation Packets That Must Be Serialized

These packets must be serialized for actual code APPLY work:

1. Risk Budget Ledger V1
2. Broker Health Read-Only Summary V1
3. Profitability Evidence Scorecard V1
4. Stop/Pause/Resume Matrix V1
5. Supervised Demo Intent Card V1
6. Dashboard Truth Summary V1

Reason:

Each implementation creates or changes executable surfaces and their tests. Even when modules are separate, they share evidence vocabulary, readiness states, safety flags, and dashboard truth semantics. One implementation PR should land and be validated before the next depends on it.

## 6. Implementation Packets That Can Be Planned In Parallel

The following can be planned in parallel as report-only packets if each has one unique report output and no runtime writes:

- Risk Budget Ledger implementation design
- Broker Health Read-Only implementation design
- Profitability Evidence implementation design
- Stop/Pause/Resume Matrix implementation design
- Supervised Demo Intent Card implementation design
- Dashboard Truth Summary implementation design

Safe planning conditions:

- Preflight confirms the worker is on the expected branch.
- Preflight confirms the worktree is clean or the packet explicitly uses an isolated worktree.
- Allowed path is one exact report file.
- Forbidden paths include runtime code, tests, scripts, apps, schemas, docs, secrets, credentials, tokens, broker/API calls, trades, protected actions, and branch operations.
- Each planning worker stops after report creation and validators.

## 7. Candidate Scoring V1 Landed Status

Status: landed as a current dependency, not a Sprint 2B reimplementation target.

Current report evidence shows:

- Review-Ready Candidate Selector V1 exists as a deterministic local selector.
- It selects only review-ready candidates from local dictionaries.
- It uses evidence depth, statistical profit score, profit factor, expectancy, sample size, risk score, recency score, drawdown score, and max drawdown for deterministic ranking.
- It explicitly keeps execution, broker access, credential access, account access, trade action, live trade, demo trade, paper trade, order placement, order closure, and production activation false.
- Candidate Evidence Intake V1 and Candidate To Gate Bridge V1 are also reported as landed in the review chain.

Important distinction:

The 22H/6D Candidate Scoring Rubric remains a planning item in the demo-readiness spine. Sprint 2B should not reimplement the landed local selector. If a rubric adapter is needed later, it should be a separate small PR after Risk Budget Ledger V1 clarifies the risk vocabulary.

## 8. Risk Budget Implementation Plan

Goal:

Create a pure local Risk Budget Ledger V1 that determines whether a candidate can proceed to review under explicit risk caps.

Required behavior:

- Accept sanitized local dictionaries only.
- Track per-candidate risk cap, per-window risk cap, aggregate open risk cap, daily loss cap, and manual halt state.
- Return deterministic statuses such as `RISK_BUDGET_ACCEPTED`, `RISK_BUDGET_BLOCKED`, and `RISK_BUDGET_INCOMPLETE`.
- Include blockers for missing candidate ID, missing risk cap, exceeded per-candidate cap, exceeded aggregate cap, daily stop active, halt active, invalid numeric input, or unsafe permission flags.
- Keep all broker, credential, account, order, trade, live, demo, paper, and production permissions false.
- Include tests for pass, incomplete, blocked, unsafe flag, invalid numeric, and deterministic output cases.

Implementation posture:

- No broker/API call.
- No environment read.
- No secret read.
- No account identifier handling.
- No order or trade action.
- No dashboard mutation.
- No commit or push.

## 9. Broker Health Read-Only Implementation Plan

Goal:

Create a read-only Broker Health Summary V1 that can classify sanitized broker-readiness evidence without connecting to a broker.

Required behavior:

- Accept injected sanitized snapshots only.
- Reject any snapshot that contains credential, account identifier, endpoint value, raw payload, order ID, position ID, or private value signals.
- Classify health as `BROKER_HEALTH_READY_FOR_REVIEW`, `BROKER_HEALTH_BLOCKED`, or `BROKER_HEALTH_UNKNOWN`.
- Track demo/practice mode proof, live-mode denial, stale timestamp, market-data route denial, order-route denial, read-only confirmation, and recovery-drill status.
- Produce owner-visible blockers and next safe action.

Implementation posture:

- Read-only local logic.
- No network.
- No broker API.
- No credential, account, endpoint, or environment access.
- No order route.
- No live or demo trade.

## 10. Dashboard Truth Summary Implementation Plan

Goal:

Create a display-only Dashboard Truth Summary V1 that aggregates Sprint 2B evidence into one operator-safe read model.

Required behavior:

- Consume local result dictionaries from candidate scoring, risk budget, broker health, profitability evidence, stop/pause/resume, and demo intent.
- Return compact truth fields for mode, status, blockers, next safe action, selected candidate, risk budget state, broker health state, profitability evidence state, stop-control state, demo intent state, dashboard freshness, and execution permission flags.
- Never infer readiness from missing inputs.
- Treat conflicting inputs as blocked.
- Keep all action permissions false.
- Remain usable by a future UI without requiring UI mutation in this PR.

Implementation posture:

- Implement after the upstream evidence producers land.
- No app/dashboard file changes until the read model is stable.
- No network, broker, credential, account, order, trade, live, demo, paper, scheduler, daemon, webhook, or production mutation.

## 11. Profitability Evidence Implementation Plan

Goal:

Create a Persistent Profitability Evidence Scorecard V1 that evaluates whether candidate evidence is deep enough for supervised demo review.

Required behavior:

- Accept sanitized local campaign/result dictionaries only.
- Evaluate sample count, session count, expectancy, profit factor, max drawdown, evidence depth, regime coverage, recency, and blocker list.
- Return deterministic statuses such as `PROFITABILITY_EVIDENCE_ACCEPTED`, `PROFITABILITY_EVIDENCE_MORE_DATA_REQUIRED`, and `PROFITABILITY_EVIDENCE_REJECTED`.
- Reject shallow sample depth, negative expectancy, low profit factor, excessive drawdown, missing regime coverage, stale evidence, and unsafe permission flags.
- Make no profit claim without evidence.

Implementation posture:

- No candidate generation.
- No trade recommendation.
- No broker or account action.
- No compounding approval.
- No live-readiness claim.

## 12. Supervised Demo Intent Card Implementation Plan

Goal:

Create a supervised demo intent card builder that prepares an owner-visible review card after candidate, risk, broker health, profitability, and stop-control evidence exists.

Required behavior:

- Accept local evidence dictionaries from candidate selection, risk budget, broker health, profitability evidence, and stop/pause/resume.
- Return `DEMO_INTENT_REVIEW_READY`, `DEMO_INTENT_BLOCKED`, or `DEMO_INTENT_INCOMPLETE`.
- Include candidate ID, instrument, side, risk budget state, broker health state, profitability state, stop controls, evidence freshness, blockers, and next safe action.
- Keep action permissions false and state that Human Owner approval is required before any broker-facing or protected action.
- Block if any upstream component is missing, stale, unsafe, rejected, or contradictory.

Implementation posture:

- Review card only.
- No order ticket.
- No broker call.
- No demo trade.
- No live trade.
- No approval capture.

## 13. Stop/Pause/Resume Matrix Implementation Plan

Goal:

Create a Stop/Pause/Resume Matrix V1 that standardizes owner-visible stop controls before supervised demo review.

Required behavior:

- Accept local control state dictionaries only.
- Map triggers to `STOP`, `PAUSE`, `RESUME_BLOCKED`, `RESUME_REVIEW_READY`, or `ESCALATE_TO_OWNER`.
- Include triggers for daily loss cap, max drawdown, stale evidence, broker health blocked, risk budget blocked, missing stop controls, conflicting dashboard truth, manual halt, incident flag, and unsafe permission flags.
- Require explicit owner review before resume when any stop, incident, broker, risk, or evidence-blocker state was active.
- Return blockers and next safe action.

Implementation posture:

- No scheduler.
- No daemon.
- No webhook.
- No autonomous restart.
- No broker/API call.
- No trade action.

## 14. Exact Recommended Order For Implementation PRs

Recommended code PR order:

1. Risk Budget Ledger V1
2. Broker Health Read-Only Summary V1
3. Profitability Evidence Scorecard V1
4. Stop/Pause/Resume Matrix V1
5. Supervised Demo Intent Card V1
6. Dashboard Truth Summary V1

Rationale:

- Risk budget establishes the safety vocabulary used by all later work.
- Broker health is independent enough to follow immediately, but it should not be shown as dashboard truth until its sanitized read-only contract is stable.
- Profitability evidence should use candidate scoring as an input and stay separate from risk acceptance.
- Stop/pause/resume should land before demo intent so the card can show clear owner controls.
- Demo intent should aggregate candidate, risk, broker, profitability, and stop-control evidence.
- Dashboard truth should land last because it is the display summary of all prior Sprint 2B states.

Candidate scoring is not listed as a new PR because Candidate Scoring V1 is already landed as a dependency.

## 15. Exact Next 6 Codex Worker Prompts To Generate After This Report

These prompts are future packets. They are not active in this report packet. Do not paste any future packet until the worktree is clean or an isolated clean worktree is used.

### Prompt 1: Risk Budget Ledger V1

```text
CODEX-ONLY PROMPT
AI_OS BOOTSTRAP REQUIRED
AI_OS EXECUTION TOKEN

Identity: AI_OS Upstream Supervisor
Supervisor Identity: ChatGPT
Worker Identity: Codex

Packet ID:
AIOS-FOREX-SPRINT2B-RISK-BUDGET-LEDGER-V1

Mode:
APPLY

Zone:
Local Implementation

Lane:
Forex Sprint 2B Risk Budget Ledger

Worktree:
C:\Dev\Ai.Os

Branch:
main

Approval Authority:
Human Owner approval by explicit execution of this complete packet.

Allowed Paths:
automation/forex_engine/sprint2b_risk_budget_ledger_v1.py
scripts/forex_delivery/run_sprint2b_risk_budget_ledger_v1.py
tests/forex_engine/test_sprint2b_risk_budget_ledger_v1.py
Reports/forex_delivery/AIOS_FOREX_SPRINT2B_RISK_BUDGET_LEDGER_V1_REPORT.md

Forbidden Paths:
.env
**/.env
**/*secret*
**/*credential*
**/*token*
apps/**
schemas/**
.github/**
docs/**

Protected Action Rules:
Do not switch branches.
Do not create branches.
Do not read secrets or environment variables.
Do not call broker APIs.
Do not place trades.
Do not stage, commit, push, open PR, merge, reset, clean, or stash.

Preflight:
Run:
git status --short --branch

If current branch is not main, stop and report BLOCKED_NOT_ON_MAIN.
If worktree is dirty, stop and report BLOCKED_DIRTY_WORKTREE.
If any allowed output file already exists, stop and report BLOCKED_FILE_EXISTS.

Task:
Implement pure local Sprint 2B Risk Budget Ledger V1.
It must accept sanitized local dictionaries only, classify accepted, blocked, and incomplete risk-budget states, preserve all execution permission flags as false, and include focused tests and a report.

Validator Chain:
python -m py_compile automation/forex_engine/sprint2b_risk_budget_ledger_v1.py scripts/forex_delivery/run_sprint2b_risk_budget_ledger_v1.py tests/forex_engine/test_sprint2b_risk_budget_ledger_v1.py
python -m pytest tests/forex_engine/test_sprint2b_risk_budget_ledger_v1.py -q
git diff --check
git status --short --branch

STOP POINT:
Create only the allowed files. No commit. No push.

Final Report:
Return files changed, validation output, remaining dirty files, and next recommended packet.
```

### Prompt 2: Broker Health Read-Only Summary V1

```text
CODEX-ONLY PROMPT
AI_OS BOOTSTRAP REQUIRED
AI_OS EXECUTION TOKEN

Identity: AI_OS Upstream Supervisor
Supervisor Identity: ChatGPT
Worker Identity: Codex

Packet ID:
AIOS-FOREX-SPRINT2B-BROKER-HEALTH-READONLY-V1

Mode:
APPLY

Zone:
Local Implementation

Lane:
Forex Sprint 2B Broker Health Read-Only Summary

Worktree:
C:\Dev\Ai.Os

Branch:
main

Approval Authority:
Human Owner approval by explicit execution of this complete packet.

Allowed Paths:
automation/forex_engine/sprint2b_broker_health_readonly_v1.py
scripts/forex_delivery/run_sprint2b_broker_health_readonly_v1.py
tests/forex_engine/test_sprint2b_broker_health_readonly_v1.py
Reports/forex_delivery/AIOS_FOREX_SPRINT2B_BROKER_HEALTH_READONLY_V1_REPORT.md

Forbidden Paths:
.env
**/.env
**/*secret*
**/*credential*
**/*token*
apps/**
schemas/**
.github/**
docs/**

Protected Action Rules:
Do not switch branches.
Do not create branches.
Do not read secrets or environment variables.
Do not call broker APIs.
Do not place trades.
Do not stage, commit, push, open PR, merge, reset, clean, or stash.

Preflight:
Run:
git status --short --branch

If current branch is not main, stop and report BLOCKED_NOT_ON_MAIN.
If worktree is dirty, stop and report BLOCKED_DIRTY_WORKTREE.
If any allowed output file already exists, stop and report BLOCKED_FILE_EXISTS.

Task:
Implement pure local Sprint 2B Broker Health Read-Only Summary V1.
It must accept injected sanitized snapshots only, reject private broker material signals, classify ready, blocked, and unknown states, keep all action permissions false, and include focused tests and a report.

Validator Chain:
python -m py_compile automation/forex_engine/sprint2b_broker_health_readonly_v1.py scripts/forex_delivery/run_sprint2b_broker_health_readonly_v1.py tests/forex_engine/test_sprint2b_broker_health_readonly_v1.py
python -m pytest tests/forex_engine/test_sprint2b_broker_health_readonly_v1.py -q
git diff --check
git status --short --branch

STOP POINT:
Create only the allowed files. No commit. No push.

Final Report:
Return files changed, validation output, remaining dirty files, and next recommended packet.
```

### Prompt 3: Profitability Evidence Scorecard V1

```text
CODEX-ONLY PROMPT
AI_OS BOOTSTRAP REQUIRED
AI_OS EXECUTION TOKEN

Identity: AI_OS Upstream Supervisor
Supervisor Identity: ChatGPT
Worker Identity: Codex

Packet ID:
AIOS-FOREX-SPRINT2B-PROFITABILITY-EVIDENCE-V1

Mode:
APPLY

Zone:
Local Implementation

Lane:
Forex Sprint 2B Profitability Evidence Scorecard

Worktree:
C:\Dev\Ai.Os

Branch:
main

Approval Authority:
Human Owner approval by explicit execution of this complete packet.

Allowed Paths:
automation/forex_engine/sprint2b_profitability_evidence_v1.py
scripts/forex_delivery/run_sprint2b_profitability_evidence_v1.py
tests/forex_engine/test_sprint2b_profitability_evidence_v1.py
Reports/forex_delivery/AIOS_FOREX_SPRINT2B_PROFITABILITY_EVIDENCE_V1_REPORT.md

Forbidden Paths:
.env
**/.env
**/*secret*
**/*credential*
**/*token*
apps/**
schemas/**
.github/**
docs/**

Protected Action Rules:
Do not switch branches.
Do not create branches.
Do not read secrets or environment variables.
Do not call broker APIs.
Do not place trades.
Do not stage, commit, push, open PR, merge, reset, clean, or stash.

Preflight:
Run:
git status --short --branch

If current branch is not main, stop and report BLOCKED_NOT_ON_MAIN.
If worktree is dirty, stop and report BLOCKED_DIRTY_WORKTREE.
If any allowed output file already exists, stop and report BLOCKED_FILE_EXISTS.

Task:
Implement pure local Sprint 2B Profitability Evidence Scorecard V1.
It must accept sanitized local campaign/result dictionaries only, classify accepted, more-data-required, and rejected evidence states, make no profit claim without evidence, preserve all action permissions as false, and include focused tests and a report.

Validator Chain:
python -m py_compile automation/forex_engine/sprint2b_profitability_evidence_v1.py scripts/forex_delivery/run_sprint2b_profitability_evidence_v1.py tests/forex_engine/test_sprint2b_profitability_evidence_v1.py
python -m pytest tests/forex_engine/test_sprint2b_profitability_evidence_v1.py -q
git diff --check
git status --short --branch

STOP POINT:
Create only the allowed files. No commit. No push.

Final Report:
Return files changed, validation output, remaining dirty files, and next recommended packet.
```

### Prompt 4: Stop/Pause/Resume Matrix V1

```text
CODEX-ONLY PROMPT
AI_OS BOOTSTRAP REQUIRED
AI_OS EXECUTION TOKEN

Identity: AI_OS Upstream Supervisor
Supervisor Identity: ChatGPT
Worker Identity: Codex

Packet ID:
AIOS-FOREX-SPRINT2B-STOP-PAUSE-RESUME-MATRIX-V1

Mode:
APPLY

Zone:
Local Implementation

Lane:
Forex Sprint 2B Stop Pause Resume Matrix

Worktree:
C:\Dev\Ai.Os

Branch:
main

Approval Authority:
Human Owner approval by explicit execution of this complete packet.

Allowed Paths:
automation/forex_engine/sprint2b_stop_pause_resume_matrix_v1.py
scripts/forex_delivery/run_sprint2b_stop_pause_resume_matrix_v1.py
tests/forex_engine/test_sprint2b_stop_pause_resume_matrix_v1.py
Reports/forex_delivery/AIOS_FOREX_SPRINT2B_STOP_PAUSE_RESUME_MATRIX_V1_REPORT.md

Forbidden Paths:
.env
**/.env
**/*secret*
**/*credential*
**/*token*
apps/**
schemas/**
.github/**
docs/**

Protected Action Rules:
Do not switch branches.
Do not create branches.
Do not read secrets or environment variables.
Do not call broker APIs.
Do not place trades.
Do not stage, commit, push, open PR, merge, reset, clean, or stash.

Preflight:
Run:
git status --short --branch

If current branch is not main, stop and report BLOCKED_NOT_ON_MAIN.
If worktree is dirty, stop and report BLOCKED_DIRTY_WORKTREE.
If any allowed output file already exists, stop and report BLOCKED_FILE_EXISTS.

Task:
Implement pure local Sprint 2B Stop/Pause/Resume Matrix V1.
It must map local control states into stop, pause, resume-blocked, resume-review-ready, and owner-escalation statuses, require owner review after blocker states, preserve all action permissions as false, and include focused tests and a report.

Validator Chain:
python -m py_compile automation/forex_engine/sprint2b_stop_pause_resume_matrix_v1.py scripts/forex_delivery/run_sprint2b_stop_pause_resume_matrix_v1.py tests/forex_engine/test_sprint2b_stop_pause_resume_matrix_v1.py
python -m pytest tests/forex_engine/test_sprint2b_stop_pause_resume_matrix_v1.py -q
git diff --check
git status --short --branch

STOP POINT:
Create only the allowed files. No commit. No push.

Final Report:
Return files changed, validation output, remaining dirty files, and next recommended packet.
```

### Prompt 5: Supervised Demo Intent Card V1

```text
CODEX-ONLY PROMPT
AI_OS BOOTSTRAP REQUIRED
AI_OS EXECUTION TOKEN

Identity: AI_OS Upstream Supervisor
Supervisor Identity: ChatGPT
Worker Identity: Codex

Packet ID:
AIOS-FOREX-SPRINT2B-SUPERVISED-DEMO-INTENT-CARD-V1

Mode:
APPLY

Zone:
Local Implementation

Lane:
Forex Sprint 2B Supervised Demo Intent Card

Worktree:
C:\Dev\Ai.Os

Branch:
main

Approval Authority:
Human Owner approval by explicit execution of this complete packet.

Allowed Paths:
automation/forex_engine/sprint2b_supervised_demo_intent_card_v1.py
scripts/forex_delivery/run_sprint2b_supervised_demo_intent_card_v1.py
tests/forex_engine/test_sprint2b_supervised_demo_intent_card_v1.py
Reports/forex_delivery/AIOS_FOREX_SPRINT2B_SUPERVISED_DEMO_INTENT_CARD_V1_REPORT.md

Forbidden Paths:
.env
**/.env
**/*secret*
**/*credential*
**/*token*
apps/**
schemas/**
.github/**
docs/**

Protected Action Rules:
Do not switch branches.
Do not create branches.
Do not read secrets or environment variables.
Do not call broker APIs.
Do not place trades.
Do not stage, commit, push, open PR, merge, reset, clean, or stash.

Preflight:
Run:
git status --short --branch

If current branch is not main, stop and report BLOCKED_NOT_ON_MAIN.
If worktree is dirty, stop and report BLOCKED_DIRTY_WORKTREE.
If any allowed output file already exists, stop and report BLOCKED_FILE_EXISTS.

Task:
Implement pure local Sprint 2B Supervised Demo Intent Card V1.
It must aggregate candidate, risk budget, broker health, profitability evidence, and stop-control dictionaries into an owner-visible review card, block missing or unsafe inputs, preserve all action permissions as false, and include focused tests and a report.

Validator Chain:
python -m py_compile automation/forex_engine/sprint2b_supervised_demo_intent_card_v1.py scripts/forex_delivery/run_sprint2b_supervised_demo_intent_card_v1.py tests/forex_engine/test_sprint2b_supervised_demo_intent_card_v1.py
python -m pytest tests/forex_engine/test_sprint2b_supervised_demo_intent_card_v1.py -q
git diff --check
git status --short --branch

STOP POINT:
Create only the allowed files. No commit. No push.

Final Report:
Return files changed, validation output, remaining dirty files, and next recommended packet.
```

### Prompt 6: Dashboard Truth Summary V1

```text
CODEX-ONLY PROMPT
AI_OS BOOTSTRAP REQUIRED
AI_OS EXECUTION TOKEN

Identity: AI_OS Upstream Supervisor
Supervisor Identity: ChatGPT
Worker Identity: Codex

Packet ID:
AIOS-FOREX-SPRINT2B-DASHBOARD-TRUTH-SUMMARY-V1

Mode:
APPLY

Zone:
Local Implementation

Lane:
Forex Sprint 2B Dashboard Truth Summary

Worktree:
C:\Dev\Ai.Os

Branch:
main

Approval Authority:
Human Owner approval by explicit execution of this complete packet.

Allowed Paths:
automation/forex_engine/sprint2b_dashboard_truth_summary_v1.py
scripts/forex_delivery/run_sprint2b_dashboard_truth_summary_v1.py
tests/forex_engine/test_sprint2b_dashboard_truth_summary_v1.py
Reports/forex_delivery/AIOS_FOREX_SPRINT2B_DASHBOARD_TRUTH_SUMMARY_V1_REPORT.md

Forbidden Paths:
.env
**/.env
**/*secret*
**/*credential*
**/*token*
apps/**
schemas/**
.github/**
docs/**

Protected Action Rules:
Do not switch branches.
Do not create branches.
Do not read secrets or environment variables.
Do not call broker APIs.
Do not place trades.
Do not stage, commit, push, open PR, merge, reset, clean, or stash.

Preflight:
Run:
git status --short --branch

If current branch is not main, stop and report BLOCKED_NOT_ON_MAIN.
If worktree is dirty, stop and report BLOCKED_DIRTY_WORKTREE.
If any allowed output file already exists, stop and report BLOCKED_FILE_EXISTS.

Task:
Implement pure local Sprint 2B Dashboard Truth Summary V1.
It must aggregate candidate scoring, risk budget, broker health, profitability evidence, stop/pause/resume, and supervised demo intent dictionaries into a display-only read model, treat missing or conflicting inputs as blocked, preserve all action permissions as false, and include focused tests and a report.

Validator Chain:
python -m py_compile automation/forex_engine/sprint2b_dashboard_truth_summary_v1.py scripts/forex_delivery/run_sprint2b_dashboard_truth_summary_v1.py tests/forex_engine/test_sprint2b_dashboard_truth_summary_v1.py
python -m pytest tests/forex_engine/test_sprint2b_dashboard_truth_summary_v1.py -q
git diff --check
git status --short --branch

STOP POINT:
Create only the allowed files. No commit. No push.

Final Report:
Return files changed, validation output, remaining dirty files, and next recommended packet.
```

## Safe Parallel Lanes

Safe now only as report-first planning lanes:

- Risk Budget Ledger design report
- Broker Health Read-Only design report
- Profitability Evidence design report
- Stop/Pause/Resume Matrix design report
- Supervised Demo Intent Card design report
- Dashboard Truth Summary design report

Safe only after this report is preserved or in isolated clean worktrees:

- One implementation worker per exact module/test/script/report bundle.

## Blocked Lanes

Blocked from same-worktree parallel execution:

- Any two workers editing runtime files.
- Any two workers editing tests.
- Any worker editing apps while another worker edits dashboard truth contracts.
- Any branch creation from a dirty worktree.
- Any protected action without exact current-session Human Owner approval and gate review.
- Any broker/API, credential, account, order, trade, live, scheduler, daemon, webhook, or production path.

## Next Recommended Packet

Next recommended packet:

```text
AIOS-FOREX-SPRINT2B-RISK-BUDGET-LEDGER-V1
```

Run it only after this report is preserved or from an isolated clean worktree. It should be the first implementation PR because it establishes the risk vocabulary required by demo intent, stop controls, and dashboard truth.

## Stop Point

This packet stops after creating this single report. It does not approve implementation, staging, commit, push, PR creation, merge, branch creation, branch switching, broker access, live trading, demo trading, paper trading, credential access, account access, dashboard mutation, or production mutation.
