# AIOS Parallel Execution Doctrine V1 Report

## Packet Identity

- Packet ID: AIOS-PARALLEL-EXECUTION-DOCTRINE-V1
- Mode: APPLY
- Zone: Reports Only
- Lane: AIOS Parallel Execution Doctrine
- Worktree: C:\Dev\Ai.Os
- Branch: feature/forex-epc004-22h6d-augmentation-v1
- Report path: Reports/forex_delivery/AIOS_PARALLEL_EXECUTION_DOCTRINE_V1_REPORT.md

## Boundary

This report is doctrine and synthesis evidence only.

It creates no runtime authority, no governance authority, no broker authority, no credential authority, no account authority, no order authority, no trade authority, no live-trading authority, no protected-action authority, no staging authority, no commit authority, no push authority, no PR authority, and no merge authority.

No branch switch, branch creation, staging, commit, push, PR creation, runtime edit, broker call, secret read, environment read, dashboard mutation, trade placement, or production mutation was authorized or performed by this packet.

## Preflight

Command:

```powershell
git status --short --branch
```

Observed before this report was created:

```text
## feature/forex-epc004-22h6d-augmentation-v1
 M docs/governance/programs/epics/EPC-FOREX-004-PRODUCTION-TRANSITION-V1.md
?? Reports/forex_delivery/AIOS_FOREX_BRANCH_PRESERVATION_MERGE_PREP_V1_REPORT.md
?? Reports/forex_delivery/AIOS_FOREX_CURRENT_BRANCH_ARCHITECTURE_NOTE_V1_REPORT.md
?? Reports/forex_delivery/AIOS_FOREX_DEMO_READINESS_SPINE_V1_REPORT.md
?? Reports/forex_delivery/AIOS_FOREX_EPC004_22H6D_AUGMENTATION_V1_REPORT.md
?? Reports/forex_delivery/AIOS_FOREX_FINAL_GAP_ANALYSIS_V1_REPORT.md
?? Reports/forex_delivery/AIOS_FOREX_GOVERNANCE_CONSOLIDATION_V1_REPORT.md
?? Reports/forex_delivery/AIOS_FOREX_PARALLEL_WORKER_SYNTHESIS_INTAKE_V1_REPORT.md
?? Reports/forex_delivery/AIOS_FOREX_REPORT_INDEX_CLASSIFIER_V1_REPORT.md
```

The observed branch matched the required packet branch.

## Source Reports Reviewed

- Reports/forex_delivery/AIOS_FOREX_EPC004_22H6D_AUGMENTATION_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_GOVERNANCE_CONSOLIDATION_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_CURRENT_BRANCH_ARCHITECTURE_NOTE_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_REPORT_INDEX_CLASSIFIER_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_FINAL_GAP_ANALYSIS_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_DEMO_READINESS_SPINE_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_BRANCH_PRESERVATION_MERGE_PREP_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_PARALLEL_WORKER_SYNTHESIS_INTAKE_V1_REPORT.md

## Executive Doctrine

Parallel Codex windows are useful for AIOS when they are used as independent read-heavy workers with one exact report output each. They become unsafe when they share write targets, mutate authority files at the same time, switch branches over dirty work, stage broad file sets, or treat validator output as approval.

The successful current-branch pattern was:

1. Keep all workers on the same observed branch.
2. Use report-only APPLY packets with one allowed output path.
3. Forbid branch switching, protected actions, broker access, secrets, runtime mutation, and live trading.
4. Let workers read overlapping evidence but write only their own report file.
5. Add a synthesis worker after specialized reports exist.
6. Preserve the branch before adding implementation workers or starting new branches.

The doctrine is not "more workers always improves throughput." The doctrine is "parallelize bounded inspection and report production, then collapse findings into one queue before any protected action or implementation work."

## 1. Why Parallel Codex Windows Increased Throughput

Parallel windows increased throughput because AIOS had multiple independent questions that could be answered from mostly read-only evidence:

- Architecture worker mapped the current branch pipeline and dependency risks.
- Report index worker classified a large flat report directory by filename signals.
- Gap analysis worker ranked remaining engineering gaps and blockers.
- Demo readiness worker organized paper, demo, OANDA, supervised demo, and live-readiness artifacts into one lifecycle spine.
- Preservation worker classified dirty files and commit grouping risk.
- Synthesis worker defined how to merge parallel outputs into one final queue.
- Evidence worker surfaced the EPC-004 22H/6D doctrine, evidence canonicalization need, and no-live safety boundary.
- Doctrine worker converted the observed workflow into repeatable operating doctrine.

The work was parallel-safe because each worker produced a separate report and did not need to edit another worker's output. The throughput came from narrowing each worker's question, not from relaxing governance.

## 2. Safe Lane Separation Model

Safe parallel execution requires separation by write target, role, and stop point.

| Separation layer | Safe rule | Unsafe pattern |
| --- | --- | --- |
| Write target | One worker writes one explicitly allowed file | Two workers edit the same report, authority file, runtime file, or index |
| Branch state | Every worker verifies the same current branch before writing | A worker assumes `main`, switches branches, or writes after state drift |
| Work type | Parallelize read-heavy reports, indexes, evidence maps, and gap reviews | Parallelize runtime edits, schema edits, commits, branch operations, or broker work |
| Authority | Generated reports remain evidence unless promoted by an approved authority packet | A report creates new governance law or overrides AGENTS.md/RISK_POLICY.md |
| Protected actions | Staging, commit, push, PR, merge, reset, clean, and branch deletion remain serial and approval-gated | One worker stages or commits while others are still writing |
| Evidence | Workers cite source files and observed branch state | Workers invent branch state, readiness state, or blocker closure |
| Final synthesis | One synthesis worker deduplicates recommendations and ranks next packets | Every worker emits separate "final" next actions without reconciliation |

## 3. Allowed Current-Branch Report-Only Workflow

The current branch can support additional reports-only work only when all of these are true:

1. The packet has an execution token or an explicit operator execution request.
2. The required branch is the observed current branch.
3. The worktree is not switched, stashed, reset, cleaned, staged, committed, pushed, merged, or used to open a PR.
4. The allowed write path is a single exact report file under Reports/forex_delivery.
5. The target report does not already exist unless the packet explicitly authorizes updating that exact file.
6. The worker may read non-secret repo evidence needed for the report.
7. The worker must not read secrets, environment variables, credentials, tokens, account IDs, broker payloads, or vault material.
8. The worker must not run broker code, place trades, mutate runtime state, or call external broker/API surfaces.
9. The worker runs the validator chain after the report is created.
10. The final return includes the created file, doctrine/report sections, validator output, dirty files, and the next safe packet.

This workflow is useful only while the output remains evidence/report material. It is not a substitute for branch preservation.

## 4. Collision Risks Discovered Today

The current workflow exposed real collision risks:

1. Dirty-state snapshots can become stale while other report workers are still writing.
2. New untracked reports can appear between a worker's preflight and validator step.
3. Some packets recorded requested branches that differed from the observed branch.
4. Multiple reports recommended similar next packets, creating duplicate recommendation pressure.
5. Report filenames can sound like executable packets even when the files are evidence only.
6. A dirty governance authority file remained present while many reports depended on its content.
7. A shared worktree makes branch switch, stash, commit, and PR actions high risk until all outputs are preserved.
8. `git diff --check` can pass while still emitting a line-ending warning on a pre-existing modified file.
9. Workers can overproduce "final" reports unless a synthesis lane collapses outputs into one action queue.
10. Report-only success can hide preservation debt if no one stops the lane and commits or intentionally defers the dirty set.

## 5. Branch And Worktree Safety Rules

- Do not switch branches while dirty files exist unless a separate approved preservation plan says exactly how to protect them.
- Do not create new branches from a dirty shared worktree during a parallel report run.
- Do not assume `main` is active. Current observed branch state wins over ideal packet assumptions.
- Do not stage or commit while parallel workers are still producing files.
- Do not stage every dirty file. Stage only exact Human Owner-approved files after cached diff review.
- Do not mix governance-authority edits with unrelated report outputs unless the Human Owner approves that exact grouping.
- Do not treat untracked report files as disposable; they may be evidence from a separate worker.
- Do not use one shared worktree for simultaneous runtime edits or simultaneous authority edits.
- Preserve or intentionally abandon the current branch before starting implementation branches.
- Use isolated Git worktrees for future multi-branch or multi-implementation parallelism.

## 6. Worker Role Model

Parallel workers should be assigned by question type, not by enthusiasm or general availability. Each worker needs one lane, one output, one stop point, and one collision rule.

## Worker Lane Table

| Worker lane | Primary question | Expected output | Write scope | Collision control | Status from current run |
| --- | --- | --- | --- | --- | --- |
| Doctrine worker | What reusable doctrine should AIOS keep from the multi-window workflow? | AIOS_PARALLEL_EXECUTION_DOCTRINE_V1_REPORT.md | One doctrine report | Runs after source reports exist; does not edit source reports | This report |
| Architecture worker | What is the current Forex branch architecture, dependency map, and fastest safe packet path? | AIOS_FOREX_CURRENT_BRANCH_ARCHITECTURE_NOTE_V1_REPORT.md | One architecture report | Reads authority/report context; no runtime or governance edits | Completed as report-only evidence |
| Evidence worker | What evidence contract and proof chain must become canonical before expansion? | Evidence canonicalization findings or EPC-004 evidence basis | One evidence report or existing EPC augmentation report | Must not read secrets or broker/account material | Evidence need identified; dedicated canonicalization packet still recommended |
| Report index worker | Which Reports/forex_delivery files are current-state, evidence-only, superseded, archive-candidate, broker/OANDA, profit, demo, live, governance, or dashboard truth? | AIOS_FOREX_REPORT_INDEX_CLASSIFIER_V1_REPORT.md | One index/classifier report | Filename/content scope must be explicit; no moves/deletes | Completed as filename-only classifier |
| Gap analysis worker | What blocks execution, validation, operator confidence, 22H/6D operation, persistent profitability, and supervised autonomy? | AIOS_FOREX_FINAL_GAP_ANALYSIS_V1_REPORT.md | One gap report | Must label branch mismatch if observed branch differs from assumed branch | Completed as report-only evidence |
| Demo readiness worker | What is the current paper-to-demo-to-OANDA-to-supervised-demo readiness spine? | AIOS_FOREX_DEMO_READINESS_SPINE_V1_REPORT.md | One readiness spine report | Separates demo evidence from live exception authority | Completed as report-only evidence |
| Preservation/merge-prep worker | What dirty files exist, which outputs belong together, and what must be reviewed before staging? | AIOS_FOREX_BRANCH_PRESERVATION_MERGE_PREP_V1_REPORT.md | One preservation report | Does not stage, commit, push, PR, merge, or switch branches | Completed as report-only evidence |
| Synthesis worker | How should all worker outputs be ingested, deduplicated, conflict-checked, and ranked? | AIOS_FOREX_PARALLEL_WORKER_SYNTHESIS_INTAKE_V1_REPORT.md | One synthesis intake report | Must not execute the action queue; it only defines intake rules | Completed as report-only evidence |

## 7. Maximum Safe Worker Count

For one dirty shared worktree on one branch:

- Safe upper bound: 8 report-only workers, matching the current lane set, when every worker has a unique exact output file and no worker performs protected actions.
- Preferred operating range: 4 to 6 report-only workers when the branch already has dirty governance or many untracked reports.
- Protected-action worker count: 1, only after all report workers stop and exact Human Owner approval is present.
- Runtime implementation worker count in a shared dirty worktree: 0.
- Broker/API/secret/live-trading worker count by default: 0.

For isolated Git worktrees:

- Safe scale increases because each worker can own a separate branch and working directory.
- The limit becomes one writer per authority file, one writer per runtime module cluster, and one protected-action lane at a time.
- Synthesis must still be serial before preservation, PR creation, merge, or production-impacting decisions.

## 8. When To Stop Adding Workers

Stop adding workers when any of these occur:

1. More than one worker needs the same write target.
2. A worker asks to switch branches, stash, reset, clean, stage, commit, push, open a PR, or merge.
3. New reports are repeating the same next-packet recommendation without closing a blocker.
4. The action queue is unclear or has more than ten high-priority items.
5. Branch mismatch labels appear in more than one report.
6. Current dirty files include a governance authority edit that future workers depend on.
7. A report-only lane starts proposing runtime, schema, dashboard, broker, secret, or live-trading work.
8. Validator output changes unexpectedly between workers.
9. The Human Owner would need to manually reconcile competing "final" statuses.
10. A preservation/merge-prep worker has enough information to prepare exact-file staging recommendations.

For the current branch, the safest doctrine is: stop adding new report workers after this doctrine report and move to preservation or final conflict-matrix review.

## 9. When To Preserve Or Commit Before Continuing

Preserve before continuing when:

- A canonical authority file has been edited.
- Multiple reports depend on that edited authority file.
- New workers are starting to reference each other's reports as source evidence.
- The next work would involve implementation, tests, schemas, scripts, apps, automation, dashboards, broker surfaces, or live-readiness action.
- A branch switch, new branch, PR, or merge is being considered.
- The current report set is useful enough that losing it would force manual reconstruction.

For this branch, preservation should happen before any more implementation or branch work. The modified EPC-FOREX-004 authority file and current report set are now a coherent branch-output bundle, but staging and commit still require a separate protected-action gate and exact Human Owner approval.

## 10. How To Synthesize Outputs Into One Final Action Queue

Use this synthesis method:

1. Inventory all worker outputs and record path, branch assumption, dirty-state snapshot, and stop point.
2. Extract every recommendation into a flat list.
3. Tag each action by lane, risk tier, mode, allowed path, forbidden path, validator chain, evidence source, and stop condition.
4. Merge duplicate recommendations by keeping the narrowest safe scope and clearest validator.
5. Split recommendations that combine protected actions with report-only work.
6. Block recommendations that touch live trading, broker execution, secrets, account values, production mutation, or protected Git actions without explicit approval.
7. Rank the remaining actions by blocker removal, safety value, evidence value, operator value, and effort control.
8. Promote no more than ten next packet candidates.
9. Keep evidence-only findings separate from executable actions.
10. Stop before staging, commit, push, PR creation, merge, broker/API use, secrets, or live trading.

## Final Action Queue

| Rank | Proposed next action | Source basis | Mode | Risk posture | Recommended outcome |
| ---: | --- | --- | --- | --- | --- |
| 1 | AIOS-FOREX-CURRENT-BRANCH-PRESERVATION-PROTECTED-ACTION-GATE-V1 | Preservation report, architecture note, dirty EPC-004 edit | DRY_RUN first, protected APPLY only if approved | Protected Git action if it proceeds past review | Prepare exact file list, cached diff review plan, and commit grouping; do not stage yet |
| 2 | AIOS-FOREX-PARALLEL-WORKER-FINAL-INVENTORY-AND-CONFLICT-MATRIX-V1 | Synthesis intake and this doctrine | DRY_RUN | Low if read-only | Verify all worker outputs, branch assumptions, duplicate recommendations, and conflicts |
| 3 | AIOS-FOREX-EVIDENCE-CANONICALIZATION-PLAN-V1 | EPC004 report, architecture note, demo readiness, gap analysis | APPLY, reports-only | Low if report-only | Define canonical evidence fields for market, candidate, risk, demo intent, management, result, and dashboard truth |
| 4 | AIOS-FOREX-REPORT-IDENTITY-HEADER-NORMALIZATION-PLAN-V1 | Governance consolidation and report index classifier | APPLY, reports-only | Low if report-only | Define future report header rules without editing existing authority |
| 5 | AIOS-FOREX-OANDA-EVIDENCE-SPINE-INDEX-V1 | Demo readiness, gap analysis, report index classifier | APPLY, reports-only | Medium because broker-adjacent evidence must stay sanitized | Index OANDA demo, read-only, owner-run, P/L, and result artifacts without reading secrets |
| 6 | AIOS-FOREX-BROKER-DEMO-PROOF-ARC-INDEX-V1 | Governance consolidation, demo readiness, report index classifier | APPLY, reports-only | Medium because broker concepts must remain non-executable | Collapse broker-demo V2-V9, first proof attempts, and protected connection reports into one index |
| 7 | AIOS-FOREX-FINAL-SCOPE-NO-SECRET-NO-ACCOUNT-SCAN-EVIDENCE-V1 | Gap analysis | DRY_RUN or tightly scoped APPLY evidence | Medium; must avoid env/secret reads and raw account disclosure | Produce a no-secret/no-account evidence bundle only from approved paths and sanitized outputs |
| 8 | AIOS-FOREX-CANDIDATE-RISK-INTENT-CONTRACT-PLAN-V1 | Architecture note and EPC004 22H/6D doctrine | APPLY, reports-only | Low if report-only | Connect candidate intake, risk sizing, and demo intent before any execution discussion |
| 9 | AIOS-FOREX-22H6D-STOP-PAUSE-RESUME-ESCALATION-MATRIX-V1 | EPC004 doctrine, demo readiness, gap analysis | APPLY, reports-only | Low if report-only | Define owner-visible stop controls for supervised windows |
| 10 | AIOS-FOREX-OWNER-DECISION-BRIEF-AFTER-EVIDENCE-CLOSURE-V1 | Gap analysis and synthesis intake | DRY_RUN first | Low until it asks for approval | Create one operator decision packet only after evidence canonicalization and branch preservation are complete |

## Collision Prevention Checklist

Use this checklist before launching parallel workers:

- Current branch was verified with `git status --short --branch`.
- Dirty files were classified before any worker writes.
- Each worker has one exact output path.
- No two workers share a write target.
- No worker can edit AGENTS.md, RISK_POLICY.md, governance authority, runtime code, tests, schemas, apps, scripts, automation, dashboard files, environment files, secret-adjacent files, or broker surfaces unless explicitly approved for that lane.
- Every target file is checked for prior existence before creation.
- Workers are report-only unless a packet explicitly names a different allowed path and validator chain.
- No worker is allowed to stage, commit, push, open a PR, merge, switch branches, reset, clean, or delete branches.
- No worker reads secrets, environment variables, credentials, tokens, account IDs, vault material, or raw broker payloads.
- No worker places trades or runs broker code.
- Every worker returns git status and validation output.
- A synthesis worker runs before protected actions.
- A preservation worker runs before implementation branches or commit prep.
- The Human Owner is not asked to manually repair malformed packets.

## Safe Packet Template

This is a reference-only skeleton for future packet authors. It is not executable until every field is concrete, the allowed path is exact, the forbidden paths are exact, the current branch is verified or marked for preflight resolution, and the routing marker is added as the first line by the packet generator after validation.

```text
REFERENCE-ONLY SAFE REPORT PACKET SKELETON - NOT EXECUTABLE

Required routing:
- Codex routing marker as first line only after validation.
- AI_OS BOOTSTRAP REQUIRED.
- AI_OS EXECUTION TOKEN.

Required identity:
- Identity.
- Supervisor Identity.
- Worker Identity.
- Packet ID.
- Mode: DRY_RUN or APPLY.
- Zone.
- Lane.
- Worktree: C:\Dev\Ai.Os.
- Branch: current observed branch or "resolve after preflight".

Required boundary:
- Approval Authority.
- Mission ID and Mission Name when governed work requires it.
- Program ID and Program Name when Forex hierarchy applies.
- Epic ID and Epic Name when Forex hierarchy applies.
- Bucket ID and Bucket Name when Forex hierarchy applies.
- Packet ID and Packet Name.
- Allowed Paths: one exact path for report-only APPLY.
- Forbidden Paths: exact protected roots and secret-adjacent patterns.
- Protected Action Rules.

Required preflight:
- git status --short --branch.
- Stop on branch mismatch unless the packet explicitly says branch resolves after preflight.
- Stop if target output already exists and update was not explicitly approved.

Required task:
- One lane.
- One output file.
- Source reports or source paths.
- No branch switch.
- No protected Git action.
- No broker/API/secret/live-trading action.

Required validator chain:
- git status --short --branch.
- git diff --check.

Required stop point:
- Create or inspect only the named output.
- Return file path, sections delivered, validator output, dirty files, and next safe packet.
```

## Stop Conditions

Stop immediately if:

- The observed branch does not match the packet-required branch.
- The packet lacks required identity, branch, worktree, allowed path, forbidden path, validator chain, approval authority, or stop point.
- The target file already exists and the packet only authorizes creation.
- A worker needs to edit an existing file without explicit approval.
- Another worker is editing the same file or same authority tree.
- The task would require branch switch, branch creation, staging, commit, push, PR creation, merge, reset, clean, deletion, or stash without separate approval.
- The task would touch docs, automation, tests, scripts, apps, schemas, GitHub workflow files, environment files, secrets, credentials, tokens, account IDs, broker APIs, order routing, live trading, or production surfaces outside exact approval.
- Validator output reports whitespace errors or unexpected dirty files that overlap the lane.
- A report claims live trading, broker execution, money movement, or production readiness is approved without RISK_POLICY-compliant Human Owner approval.
- The operator would need to reconcile more parallel reports before deciding the next action.

## Recommended Future Upgrade: Isolated Git Worktrees

The next structural upgrade for parallel AIOS execution is isolated Git worktrees.

Why worktrees are better:

- Each worker gets a separate working directory and branch.
- Dirty files from one lane cannot silently appear in another worker's status.
- Branch-specific reports can record cleaner state.
- Implementation workers can run without sharing the same untracked report pool.
- Preservation, PR, and merge prep become easier to reason about.

Minimum worktree doctrine:

1. One worktree per branch and lane.
2. One owner per worktree at a time.
3. No two worktrees edit the same authority file without explicit lane reassignment.
4. Report-only workers can still share source reads but must not share output paths.
5. A central synthesis worker runs from a chosen integration branch after worker outputs are preserved.
6. Protected actions remain serial and approval-gated even when worktrees are isolated.

Worktrees do not weaken AGENTS.md, RISK_POLICY.md, protected-action gates, commit gates, push gates, PR gates, broker/API restrictions, secret handling, or live-trading blocks. They reduce collision risk; they do not create permission.

## Validator Commands

Post-create validation for this packet:

```powershell
git status --short --branch
git diff --check
```

Validator output is reported in the final Codex return for this packet.

## Recommended Next Packet

Single best next packet:

```text
AIOS-FOREX-CURRENT-BRANCH-PRESERVATION-PROTECTED-ACTION-GATE-V1
```

Recommended mode:

```text
DRY_RUN first
```

Reason:

The current branch now contains one modified EPC-FOREX-004 authority file and multiple reports produced by parallel workers. Further report-only work will add diminishing value until the branch is preserved or intentionally deferred. The next packet should not stage or commit by itself; it should first produce an exact-file protected-action gate review, cached-diff review plan, and commit grouping recommendation for Human Owner approval.

## Status

This packet stops after creating this single doctrine report.

No staging, commit, push, PR creation, merge, branch switching, runtime work, broker work, credential work, account work, order work, trade work, dashboard work, or live execution is authorized or performed.
