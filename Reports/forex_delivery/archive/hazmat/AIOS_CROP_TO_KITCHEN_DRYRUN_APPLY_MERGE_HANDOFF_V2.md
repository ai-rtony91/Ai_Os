# AIOS Crop-to-Kitchen DryRun Apply Merge Handoff V2

## 1. STATUS

BLOCKED_BY_SCOPE_EXPANSION_REQUIRED

## 2. DRY_RUN SUMMARY

- Branch at start: `main`
- HEAD at start: `f9f5f3ca docs(product): add AIOS Forex Play Store-grade policy layer (#1291)`
- Dirty files at start: existing Forex report/state artifacts plus untracked Vacation Mode code, tests, and reports
- Planned edits: only the allowed Vacation Mode modules, tests, and report files, plus report formatting repair where needed
- Safety classification: no secrets, no `.env`, no broker calls, no demo/live execution, no destructive cleanup

## 3. APPLY SUMMARY

- `tests/forex_engine/test_forex_vacation_mode_control_plane_orchestrator_v1.py`
  - Added the required bool fields to the orchestrator exit fixture so the stricter exit gate can hold when inputs are actually complete.
- `Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_REPORT.md`
  - Removed a trailing whitespace blocker reported by `git diff --check`.
- `Reports/forex_delivery/AIOS_FOREX_COMPLETION_GAP_ASSESSMENT_V1.md`
  - Updated the completion-gap record to reflect the targeted fix, the full-suite blockers, and the scope-expansion stop.
- `Reports/forex_delivery/AIOS_CROP_TO_KITCHEN_DRYRUN_APPLY_MERGE_HANDOFF_V2.md`
  - Created this handoff report.

## 4. VALIDATION EVIDENCE

- `python -m py_compile automation/forex_engine/forex_vacation_mode_entry_authority_gate_v1.py` -> pass
- `python -m py_compile automation/forex_engine/forex_vacation_mode_exit_authority_gate_v1.py` -> pass
- `python -m py_compile automation/forex_engine/forex_vacation_mode_position_supervisor_v1.py` -> pass
- `python -m py_compile automation/forex_engine/forex_vacation_mode_control_plane_orchestrator_v1.py` -> pass
- `python -m py_compile automation/forex_engine/forex_vacation_mode_release_candidate_scorecard_v1.py` -> pass
- `python -m pytest tests/forex_engine/test_forex_vacation_mode_entry_authority_gate_v1.py -q` -> 28 passed
- `python -m pytest tests/forex_engine/test_forex_vacation_mode_exit_authority_gate_v1.py -q` -> 24 passed
- `python -m pytest tests/forex_engine/test_forex_vacation_mode_position_supervisor_v1.py -q` -> 20 passed
- `python -m pytest tests/forex_engine/test_forex_vacation_mode_control_plane_orchestrator_v1.py -q` -> 6 passed after fixture repair
- `python -m pytest tests/forex_engine/test_forex_vacation_mode_release_candidate_scorecard_v1.py -q` -> 6 passed
- `python -m pytest tests/forex_engine/ -q` -> 15 failed, 13,319 passed
- `git diff --check` -> pass after whitespace repair; only a CRLF normalization warning remained
- Forbidden-marker scan on changed code/tests/reports -> `INERT_MARKER_ONLY`
- `git status --short --branch --untracked-files=all` -> dirty branch with pre-existing Forex report/state files and untracked Vacation Mode artifacts

## 5. REVIEW EVIDENCE

- `/review` unavailable in this session
- Self-review performed on the changed files
- Defects found: missing required bools in the orchestrator exit fixture, and one report whitespace blocker
- Defects repaired: orchestrator fixture, report whitespace
- Defects remaining: full-suite failures outside the allowed Vacation Mode file list, plus branch-sensitive expectations on the feature branch

## 6. CLEANUP/POLISH STATUS

- Ready: no
- Remaining blockers:
  - 15 full-suite failures outside the allowed Vacation Mode edit list
  - feature-branch status drift against tests that still expect `main`
  - pre-existing dirty Forex artifacts in the worktree
- Next cleanup packet needed: scope-expansion or branch/state alignment packet

## 7. PRODUCTIZATION STATUS

- Source of truth: the canonical repo files and current report evidence, not generated readiness claims
- Operator UX: Vacation Mode targeted suite is green, but the broader Forex state is not yet kitchen-clean
- Dashboard/readiness state: evidence only, not command authority
- Forex lane: metadata-only, fail-closed, and still below launch evidence
- Future app lane: not involved in this packet
- Play Store-style anchor: policy and packaging evidence only, not compliance or release proof
- Deployability: no

## 8. LAUNCH/TRADING CLAIMS

- READY_FOR_LAUNCH: no unless production release evidence exists
- READY_FOR_LIVE_TRADING: no unless owner-approved broker/live packet with receipts exists
- READY_FOR_PROFIT_CLAIM: no unless broker-verified realized PnL and repeatability exist
- PLAY_STORE_COMPLIANCE_DONE: no; not in scope

## 9. GIT FINALIZATION PLAN

- Branch name: `feature/aios-crop-to-kitchen-dryrun-apply-merge-v2`
- Files to stage: none until the scope-expansion blocker is resolved
- Commit message: `fix(forex): reconcile vacation mode safety contract`
- PR title: `fix(forex): reconcile vacation mode safety contract`
- Merge method: squash only after a scoped follow-on packet passes validation and review
- Final sync command: `git switch main` followed by a clean sync after merge, if merge approval is later granted

## 10. SAFE NEXT COMMAND

Open a scope-expansion packet for the 15 non-vacation-mode Forex failures, or re-authorize a branch/state-aligned cleanup packet if the broader suite is meant to run on `main` only.
