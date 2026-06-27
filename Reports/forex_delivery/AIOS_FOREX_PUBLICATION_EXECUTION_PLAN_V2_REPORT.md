# AIOS Forex Publication Execution Plan V2 Report

## Packet Identity

- Mission ID: MISSION-AIOS-FOREX
- Mission Name: AIOS Forex Publication Strategy
- Program ID: PRG-FOREX-001
- Program Name: AIOS Forex Supervised Operational Validation
- Epic ID: EPC-FOREX-PUBLICATION-EXECUTION-V2
- Epic Name: Publication Execution Planning
- Bucket ID: BKT-FOREX-PUBLICATION-PLAN
- Bucket Name: Publication Planning
- Packet ID: AIOS-FOREX-PUBLICATION-EXECUTION-PLAN-V2
- Packet Name: Publication Execution Plan V2
- Mode: LOCAL_APPLY
- Zone: Report Only
- Lane: Publication Planning
- Worker identity: Codex Publication Planner
- Worktree: C:\Dev\Ai.Os
- Observed branch: main

## Authority And Evidence Read

Read and used:

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `RISK_POLICY.md`
- `docs/governance/AI_OS_REPO_MEMORY.md`
- `docs/governance/aios-identity-and-lane-governance.md`
- `docs/governance/source-of-truth-map.md`
- `docs/audits/active-system-map.md`
- `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`
- `docs/workflows/AI_OS_PR_LANE_RUNNER.md`
- `Reports/forex_delivery/AIOS_FOREX_MASTER_CONVERGENCE_LONG_RUN_V2_REPORT.md`

This report is planning evidence only. It does not approve staging, commit, push, PR creation, merge, reset, clean, stash, broker/API use, credential handling, trading, scheduler, daemon, webhook, or production activation.

## Current Publication State

Observed pre-report state:

```text
cwd: C:\Dev\Ai.Os
branch: main
remote: https://github.com/ai-rtony91/Ai_Os.git
origin/main...HEAD: 0 behind, 1 ahead
ahead commit: 10ed5808 feat: add forex completion review engines
```

Dirty-state classification:

- The dirty state is same-mission Forex work.
- It includes one existing local commit, modified tracked Forex files, broad untracked Forex reports, untracked Forex engine modules, untracked runner scripts, and untracked tests.
- `Reports/forex_delivery/AIOS_FOREX_CANDIDATE_INTAKE_DEMO_REVIEW_BRIDGE_V1_REPORT.md` appears modified in status but has no content diff in the observed check.
- `Reports/forex_delivery/readiness_state_recalculation_v1_report.json` has a newline-only diff.

No branch switch, branch creation, stash, reset, clean, stage, commit, push, PR, merge, broker/API action, credential action, trading action, scheduler, daemon, webhook, or production action was performed in this packet.

## Optimal Strategy

Use two primary PRs plus one optional hygiene PR.

Best path:

1. Preserve and publish the already committed local work as PR 1.
2. Preserve the remaining dirty Forex backlog as PR 2 with exact commit groups inside the PR.
3. Keep line-ending or newline-only noise out of functional PRs unless Anthony separately approves a hygiene PR.
4. Use exact-file staging only after a protected-action gate and Human Owner approval.
5. Never use `git add .`.
6. Never push directly to `main`.
7. Do not reset or sync local `main` until all wanted dirty work is committed and remotely preserved.

Worst path:

- Broad stage the backlog.
- Push `main` directly.
- Reset or clean before preserving untracked reports, modules, scripts, and tests.
- Mix newline-only noise into a functional review.
- Merge reports that imply execution authority or weaken `RISK_POLICY.md`.

## Estimated PR Count

Primary PR count: 2.

Optional PR count: 1 hygiene PR only if Anthony wants to normalize newline or line-ending residue.

Total expected PR count: 2 required, 3 maximum.

## Exact PR Groups

### PR 1 - Existing Completion Review Engines

Purpose: publish current local ahead commit `10ed5808`.

Recommended branch name:

```text
lane/forex-completion-review-engines
```

Contents:

- Commit `10ed5808 feat: add forex completion review engines`
- No dirty work.
- No additional files staged.

Review focus:

- Completion review engine behavior.
- Read-only broker health boundary.
- Dashboard truth summary display-only boundary.
- Risk budget and stop/pause/resume gates.
- Owner decision brief remains review-only.
- Tests prove no broker execution, credentials, live trading, money movement, scheduler, daemon, webhook, or production activation.

### PR 2 - Forex Evidence Closure And Publication Backlog

Purpose: preserve and review the remaining same-mission dirty Forex backlog after PR 1 is protected.

Recommended branch name:

```text
lane/forex-publication-v2-dirty-backlog
```

Contents:

- Commit Group 2: report-only evidence and publication reports.
- Commit Group 3: evidence intake, proof, and milestone adapters.
- Commit Group 4: final closure, final bundle, and supervised compounding policy.
- Commit Group 5: integration hardening and regression tests.

Review focus:

- No report creates new governance authority.
- Evidence adapters remain deterministic, local, sanitized, and fail-closed.
- Final closure remains review-only.
- Supervised compounding remains blocked from execution.
- Integration updates do not turn any protected permission flag true.

### Optional PR 3 - Newline Or Line-Ending Hygiene

Purpose: resolve non-functional dirty status only if it remains after PR 2 and Anthony approves a narrow hygiene lane.

Recommended branch name:

```text
lane/forex-publication-hygiene
```

Candidate contents:

- `Reports/forex_delivery/readiness_state_recalculation_v1_report.json`, only if the final-newline normalization is wanted.
- `Reports/forex_delivery/AIOS_FOREX_CANDIDATE_INTAKE_DEMO_REVIEW_BRIDGE_V1_REPORT.md`, only if a future content diff appears. Current observed state has no content diff.

Do not merge this optional PR if it only adds review noise and the dirty state can instead be handled by an approved exact restore or status-refresh lane.

## Exact Commit Groups

### Commit Group 1 - Already Committed Local Ahead Work

Status: already committed as `10ed5808 feat: add forex completion review engines`.

Route: PR 1.

Exact contents:

- `Reports/forex_delivery/AIOS_FOREX_COMPLETION_CLEANUP_VALIDATION_UNBLOCK_V2_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_COMPLETION_FULL_RERUN_VALIDATION_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_COMPLETION_REPAIR_PROMPT_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_MASTER_COMPLETION_LONG_RUN_APPLY_V1_REPORT.md`
- `automation/forex_engine/broker_health_readonly_v1.py`
- `automation/forex_engine/dashboard_truth_summary_v1.py`
- `automation/forex_engine/forex_closure_integration_bridge_v1.py`
- `automation/forex_engine/forex_final_readiness_checker_v1.py`
- `automation/forex_engine/forex_owner_decision_brief_v1.py`
- `automation/forex_engine/profitability_evidence_v1.py`
- `automation/forex_engine/risk_budget_engine_v1.py`
- `automation/forex_engine/stop_pause_resume_engine_v1.py`
- `automation/forex_engine/supervised_demo_intent_card_v1.py`
- `scripts/forex_delivery/run_broker_health_readonly_v1.py`
- `scripts/forex_delivery/run_dashboard_truth_summary_v1.py`
- `scripts/forex_delivery/run_forex_closure_integration_bridge_v1.py`
- `scripts/forex_delivery/run_forex_final_readiness_checker_v1.py`
- `scripts/forex_delivery/run_forex_owner_decision_brief_v1.py`
- `scripts/forex_delivery/run_profitability_evidence_v1.py`
- `scripts/forex_delivery/run_risk_budget_engine_v1.py`
- `scripts/forex_delivery/run_stop_pause_resume_engine_v1.py`
- `scripts/forex_delivery/run_supervised_demo_intent_card_v1.py`
- `tests/forex_engine/test_broker_health_readonly_v1.py`
- `tests/forex_engine/test_dashboard_truth_summary_v1.py`
- `tests/forex_engine/test_forex_closure_integration_bridge_v1.py`
- `tests/forex_engine/test_forex_final_readiness_checker_v1.py`
- `tests/forex_engine/test_forex_owner_decision_brief_v1.py`
- `tests/forex_engine/test_profitability_evidence_v1.py`
- `tests/forex_engine/test_risk_budget_engine_v1.py`
- `tests/forex_engine/test_stop_pause_resume_engine_v1.py`
- `tests/forex_engine/test_supervised_demo_intent_card_v1.py`

### Commit Group 2 - Report-Only Evidence And Publication Reports

Status: first new commit recommended for the remaining dirty backlog.

Route: PR 2.

Recommended commit message:

```text
docs(forex): preserve publication evidence reports
```

Exact contents:

- `Reports/forex_delivery/AIOS_FOREX_22H6D_OBSERVATION_CLOSURE_V2_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_BROKER_DEMO_READINESS_LANE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_CAPITAL_COMPOUNDING_SAFETY_LANE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_COLLECT_MISSING_REAL_EVIDENCE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_CONTINUOUS_CLOSURE_LONG_RUN_V2_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_CONTINUOUS_CLOSURE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_CONTINUOUS_EVIDENCE_ADVANCEMENT_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_CONTINUOUS_LONG_RUN_V3_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_DASHBOARD_VALIDATOR_SCOPE_REPAIR_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_DEMO_TRADE_DECISION_DRY_RUN_LANE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_DIRTY_MAIN_PRESERVATION_REVIEW_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_EVIDENCE_GAP_CLOSURE_LANDING_REVIEW_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_EVIDENCE_LANDING_RECONCILE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_EVIDENCE_MILESTONE_CONTINUATION_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_FINAL_BUNDLE_REPAIR_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_FINAL_CLOSURE_AUDIT_LANE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_FINAL_SYSTEM_VALIDATION_CLOSURE_LANE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_LOCAL_COMMIT_10ED5808_CONVERGENCE_VALIDATION_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_LOCAL_COMMIT_10ED5808_PRESERVATION_VALIDATION_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_MASTER_CONVERGENCE_LONG_RUN_V2_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_OPERATIONAL_READINESS_CERTIFICATION_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_PRESERVATION_PR_HYGIENE_LANE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_PUBLICATION_EXECUTION_PLAN_V2_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_PUBLICATION_PR_LANDING_LANE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_REAL_EVIDENCE_GAP_CLOSURE_LONG_RUN_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_REAL_EVIDENCE_INTAKE_REVALIDATION_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_REAL_EVIDENCE_INTAKE_REVALIDATION_V2_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_REAL_EVIDENCE_INTAKE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_REAL_PROFIT_EVIDENCE_CONTINUATION_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_REPLAY_WALKFORWARD_PROFITABILITY_EVIDENCE_VALIDATION_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_SHUTDOWN_RECOVERY_LANDING_REVIEW_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_WALKFORWARD_OOS_CLOSURE_V2_REPORT.md`

Excluded from this commit:

- `Reports/forex_delivery/AIOS_FOREX_CANDIDATE_INTAKE_DEMO_REVIEW_BRIDGE_V1_REPORT.md`, because no content diff was observed.
- `Reports/forex_delivery/readiness_state_recalculation_v1_report.json`, because the observed diff is final-newline-only.

### Commit Group 3 - Evidence Intake, Proof, And Milestone Adapters

Status: second new commit recommended for the remaining dirty backlog.

Route: PR 2.

Recommended commit message:

```text
feat(forex): add evidence intake and milestone adapters
```

Exact contents:

- `automation/forex_engine/evidence_milestone_selector_v1.py`
- `automation/forex_engine/observation_evidence_intake_v1.py`
- `automation/forex_engine/persistent_profitability_evidence_v1.py`
- `automation/forex_engine/profitability_evidence_intake_v1.py`
- `automation/forex_engine/replay_evidence_intake_v1.py`
- `automation/forex_engine/replay_proof_evidence_v1.py`
- `automation/forex_engine/supervised_observation_22h6d_evidence_v1.py`
- `automation/forex_engine/walk_forward_evidence_intake_v1.py`
- `automation/forex_engine/walk_forward_oos_evidence_v1.py`
- `scripts/forex_delivery/run_evidence_milestone_selector_v1.py`
- `scripts/forex_delivery/run_observation_evidence_intake_v1.py`
- `scripts/forex_delivery/run_persistent_profitability_evidence_v1.py`
- `scripts/forex_delivery/run_profitability_evidence_intake_v1.py`
- `scripts/forex_delivery/run_replay_evidence_intake_v1.py`
- `scripts/forex_delivery/run_replay_proof_evidence_v1.py`
- `scripts/forex_delivery/run_supervised_observation_22h6d_evidence_v1.py`
- `scripts/forex_delivery/run_walk_forward_evidence_intake_v1.py`
- `scripts/forex_delivery/run_walk_forward_oos_evidence_v1.py`
- `tests/forex_engine/test_evidence_milestone_selector_v1.py`
- `tests/forex_engine/test_observation_evidence_intake_v1.py`
- `tests/forex_engine/test_persistent_profitability_evidence_v1.py`
- `tests/forex_engine/test_profitability_evidence_intake_v1.py`
- `tests/forex_engine/test_replay_evidence_intake_v1.py`
- `tests/forex_engine/test_replay_proof_evidence_v1.py`
- `tests/forex_engine/test_supervised_observation_22h6d_evidence_v1.py`
- `tests/forex_engine/test_walk_forward_evidence_intake_v1.py`
- `tests/forex_engine/test_walk_forward_oos_evidence_v1.py`

### Commit Group 4 - Final Closure, Final Bundle, And Supervised Compounding

Status: third new commit recommended for the remaining dirty backlog.

Route: PR 2.

Recommended commit message:

```text
feat(forex): add final closure evidence bundle
```

Exact contents:

- `automation/forex_engine/final_closure_evidence_v1.py`
- `automation/forex_engine/final_evidence_bundle_v1.py`
- `automation/forex_engine/supervised_compounding_policy_v1.py`
- `scripts/forex_delivery/run_final_closure_evidence_v1.py`
- `scripts/forex_delivery/run_final_evidence_bundle_v1.py`
- `tests/forex_engine/test_final_closure_evidence_v1.py`
- `tests/forex_engine/test_final_evidence_bundle_v1.py`
- `tests/forex_engine/test_supervised_compounding_policy_v1.py`

### Commit Group 5 - Integration Hardening And Regression Tests

Status: fourth new commit recommended for the remaining dirty backlog.

Route: PR 2.

Recommended commit message:

```text
test(forex): harden final readiness integration gates
```

Exact contents:

- `automation/forex_engine/forex_closure_integration_bridge_v1.py`
- `automation/forex_engine/forex_final_readiness_checker_v1.py`
- `automation/forex_engine/forex_owner_decision_brief_v1.py`
- `tests/forex_delivery/test_live_micro_trade_arming_gate.py`
- `tests/forex_delivery/test_one_shot_live_micro_trade_execution_review.py`
- `tests/forex_delivery/test_paper_signal_execution_loop.py`
- `tests/forex_delivery/test_read_only_live_data_bridge.py`
- `tests/forex_engine/test_candidate_intake_demo_review_bridge.py`
- `tests/forex_engine/test_forex_closure_integration_bridge_v1.py`
- `tests/forex_engine/test_forex_owner_decision_brief_v1.py`
- `tests/forex_engine/test_profit_milestone_100_120_tracker_v1.py`
- `tests/forex_engine/test_readiness_state_recalculation_v1.py`

### Optional Commit Group 6 - Hygiene Only

Status: optional. Do not include in functional PRs unless separately approved.

Route: optional PR 3.

Recommended commit message:

```text
chore(forex): normalize publication report hygiene
```

Exact candidate contents:

- `Reports/forex_delivery/readiness_state_recalculation_v1_report.json`
- `Reports/forex_delivery/AIOS_FOREX_CANDIDATE_INTAKE_DEMO_REVIEW_BRIDGE_V1_REPORT.md`, only if a real content diff appears later.

## Exact First Commit Contents

The first publication commit is already present:

```text
10ed5808 feat: add forex completion review engines
```

Exact contents are the files listed in Commit Group 1.

Do not amend this commit in the publication lane unless Anthony separately approves a rewrite/rebase strategy. The safer path is to publish it as-is through PR 1.

## Exact Second Commit Contents

The second publication commit should be the first new commit in PR 2:

```text
docs(forex): preserve publication evidence reports
```

Exact contents are the files listed in Commit Group 2.

This commit should contain reports only. It must not include Python modules, runner scripts, tests, JSON newline-only cleanup, or no-content line-ending noise.

## File Routing

Route to PR 1:

- Existing local commit `10ed5808` only.

Route to PR 2, Commit Group 2:

- New report-only files under `Reports/forex_delivery/` listed in Commit Group 2.

Route to PR 2, Commit Group 3:

- New evidence intake, proof, milestone, walk-forward, profitability, and observation adapters.
- Matching runner scripts.
- Matching unit tests.

Route to PR 2, Commit Group 4:

- Final closure evidence.
- Final evidence bundle.
- Supervised compounding policy.
- Matching runner scripts and unit tests.

Route to PR 2, Commit Group 5:

- Existing integration/readiness/owner brief engine updates.
- Existing Forex delivery and Forex engine regression test updates.

Route to optional PR 3:

- Newline-only or no-content hygiene residue only.

Do not route anywhere without explicit future approval:

- Broker/API calls.
- Credentials.
- Account identifiers.
- Live trading.
- Money movement.
- Scheduler, daemon, webhook, or production activation.
- Direct push to `main`.
- Broad staging commands.
- Reset, clean, stash, or branch deletion.

## Safest Preservation Order

1. Preserve PR 1 first by creating or pushing a non-main lane branch that points at current `HEAD` commit `10ed5808`. Do not stage dirty files for PR 1.
2. Do not sync, reset, clean, or stash local `main` while dirty same-mission work remains unpreserved.
3. After PR 1 is safely represented by a remote branch or merged PR, create the PR 2 lane under protected-action approval.
4. In PR 2, stage only Commit Group 2 and commit report-only evidence first.
5. Stage only Commit Group 3 and commit evidence intake/proof adapters second.
6. Stage only Commit Group 4 and commit final closure/final bundle/compounding policy third.
7. Stage only Commit Group 5 and commit integration hardening/regression tests fourth.
8. Run targeted validators after each functional group and full Forex validation before PR 2 review.
9. Handle optional hygiene only after PR 2 is merged or explicitly held.

## Merge Dependency Graph

```text
origin/main at 6fa19b73
  -> PR 1: 10ed5808 completion review engines
      -> PR 2 Commit Group 2: report-only publication evidence
      -> PR 2 Commit Group 3: evidence intake/proof adapters
          -> PR 2 Commit Group 4: final closure/final bundle/compounding
              -> PR 2 Commit Group 5: integration hardening/regression tests
                  -> Optional PR 3: hygiene only
```

Dependency notes:

- PR 2 depends on PR 1 because Commit Group 5 modifies files introduced by `10ed5808`.
- Commit Group 4 depends on Commit Group 3 because final evidence bundle imports evidence milestone, intake, proof, profitability, observation, and walk-forward adapters.
- Commit Group 5 depends on Commit Groups 3 and 4 because the integration bridge imports persistent profitability and supervised compounding policy, and final readiness now requires final bundle and final closure evidence keys.
- Optional hygiene has no functional dependency and should merge last or not at all.

## Estimated Review Order

1. Review PR 1 first.
2. Review PR 2 by commit group:
   - Commit Group 2 for report-only safety, no duplicate authority, and no live/broker weakening.
   - Commit Group 3 for deterministic evidence parsing, sanitized outputs, and fail-closed behavior.
   - Commit Group 4 for final closure and supervised compounding staying review-only.
   - Commit Group 5 for integration gates and regression coverage.
3. Review optional PR 3 only if hygiene remains necessary.

## Exact Final Merge Order

Final merge order:

1. Merge PR 1: `lane/forex-completion-review-engines`.
2. Rebase or refresh PR 2 against updated `origin/main` if PR 1 is squash-merged.
3. Merge PR 2: `lane/forex-publication-v2-dirty-backlog`.
4. Merge optional PR 3: `lane/forex-publication-hygiene`, only if approved and still needed.
5. Sync local `main` only after all wanted dirty work is committed, pushed, reviewed, and merged. Sync requires separate explicit approval because reset/sync can destroy unpreserved local state.

## Validator Plan For Future Publication

PR 1 validators:

- Compile the files introduced in commit `10ed5808`.
- Run the tests introduced in commit `10ed5808`.
- Run `git diff --check`.

PR 2 validators:

- Compile all new and modified `automation/forex_engine/*.py` files listed in Commit Groups 3, 4, and 5.
- Compile all new `scripts/forex_delivery/*.py` files listed in Commit Groups 3 and 4.
- Run all tests listed in Commit Groups 3, 4, and 5.
- Run `python -m pytest tests/forex_engine tests/forex_delivery -q` before final PR 2 review when runtime cost is acceptable.
- Run `git diff --check`.
- Read back the report-only files in Commit Group 2 for no authority drift and no live execution authorization.

Optional PR 3 validators:

- `git diff --check -- <exact hygiene files>`
- Readback of the exact hygiene files.

## Protected Action Gates Required Later

Each future stage requires separate current-session Human Owner approval:

- Stage exact files.
- Commit exact files with exact commit message.
- Push exact lane branch.
- Create exact PR.
- Watch checks if requested.
- Merge exact PR.
- Sync local `main`.
- Delete branch if requested.
- Reset, clean, stash, or restore any local residue.

Validator PASS is evidence only. It does not approve any protected action.

## Final Recommendation

Publication should proceed through two primary PRs:

1. PR 1 preserves the already committed completion review engines.
2. PR 2 preserves the dirty same-mission Forex backlog as grouped commits with reports first, evidence adapters second, final closure third, and integration hardening fourth.

Keep optional newline or line-ending hygiene out of functional PRs unless Anthony separately approves it.

STATUS: PUBLICATION PLAN COMPLETE
