# AI_OS Repo Memory

## Purpose

This file records the latest operator-confirmed repo state that future AI_OS workers should consult before asking the operator to repeat known push-state, dirty-state, or queue-state checks.

This memory is a starting context, not command authority. If the branch changes, a new commit or push occurs, or local evidence contradicts this file, workers must mark the mismatch and refresh the state through the normal governed workflow.

## Last Updated

- Timestamp: 2026-06-05
- Updated by: Codex worker, lane `MEMORY_LOOP_APPLY`

## Last Known Push State

main is synced with origin/main after the latest push.

## Last Pushed Commits

- ee2129a chore: establish archive structure for OneDrive snapshots
- 3a88c6c docs(governance): clarify AI_OS naming and repo path authority
- d333cd6 Add hard duplicate-prevention rule for Codex workers

## Current Local Dirty State

- README.md is modified and unstaged.
- Multiple untracked automation/ and docs/ files remain local.
- AGENTS.md duplicate-prevention rule is committed and pushed.

## Pending Local Work

- Classify remaining untracked automation/ and docs/ files before assigning fixed parallel worker lanes.
- Decide whether the local README.md modification should be kept, reverted, or moved into a scoped lane.
- Keep untracked local material out of authority until it is classified.

## Next Safe Queue

1. Classify remaining untracked automation/ and docs/ files.
2. Decide whether README.md should be kept, reverted, or moved into a lane.
3. Do not create fixed parallel worktrees until the dirty local state is classified.
4. Do not repeatedly ask the operator to re-check the already-known push state unless the branch changes or a new commit/push occurs.

## Worker Rule

Before asking for another git status or push-state confirmation, workers must read this memory file and use it as the starting context.

Workers should re-check git state only when one of these applies:

- The branch changed.
- A new commit or push occurred.
- The worker needs current file-level evidence before editing.
- The recorded memory conflicts with visible repo evidence.
- The operator explicitly requests a fresh status check.

## Assessment Memory Loop

Purpose:

Future AI_OS assessments and reassessments must check this memory before producing conclusions. This section is a recurrence-prevention control, not new approval authority. It records prior fixes, accepted risks, expected outcomes, regression checks, and reopen conditions so future workers do not repeat known mistakes or create duplicate governance.

Assessment loop:

1. Run the current-state assessment from repo evidence.
2. Review the latest relevant memory entry below.
3. Compare the current issue against prior problems, root causes, fixes, and accepted risks.
4. Decide whether the issue is new, an old regression, or a duplicate-authority risk.
5. Reopen a prior decision only when current evidence matches a listed reopen condition.

Future-assessment checklist:

- What did the last assessment conclude?
- What changed since?
- Did the expected improvement happen?
- Did the old issue return?
- Did the fix create a new bottleneck?
- Is this a new issue or an old regression?
- Are we creating duplicate authority?
- Should this decision be reopened?

### Tracked Reassessment Themes - 2026-06-05

#### Blast Radius Governance

- Problem discovered: Governance burden was being applied too broadly, causing low-risk inspection and planning work to inherit packet burdens meant for higher-risk mutation or production work.
- Root cause: Governance rules did not clearly scale required process to actual blast radius before packet validation began.
- Fix applied: Added a tiered blast-radius model in `AGENTS.md` through commit `8de08e3 docs(governance): align governance burden with blast radius`.
- Expected outcome: Low-risk read-only and planning work can proceed with lighter governance, while local apply, authority changes, production, secrets, trading, broker/API, and protected actions remain strict.
- Accepted risk: Tier classification can be misread if future packets omit scope or hide mutation behind analysis wording.
- Regression checks: Confirm future packets classify READ_ONLY, DRY_RUN PLAN, SANDBOX_OUTPUT, LOCAL_APPLY, PROMOTION, or PRODUCTION_OR_LIVE before validation; confirm protected actions still require explicit approval.
- Reopen conditions: Reopen if low-risk work is blocked by excessive packet burden again, or if the tier model is used to weaken commit, push, merge, secrets, live trading, broker/API, or authority gates.

#### Morning Brief v2

- Problem discovered: Morning decision surfaces mixed active approval decisions with examples, completed records, and stale digest state.
- Root cause: Presentation logic counted raw pending-human-review items without enough filtering for example records, completed approvals, and stale projection mismatches.
- Fix applied: Added repeatable Morning Brief v2 output in commit `3489f61 feat(night-supervisor): add repeatable morning brief v2 output`, then refined consumption during Bridge Intelligence v1 work.
- Expected outcome: Morning Brief v2 presents current active decision cards separately from noise and stale-state warnings.
- Accepted risk: Digest state and markdown can still be stale if only the bridge state is refreshed or if old generated outputs are read as current.
- Regression checks: Confirm `MORNING_BRIEF_V2_LATEST.json` exposes active decision cards, noise cards, stale-state warnings, `recommendation_only`, and current status fields; confirm examples and completed records are not counted as active approvals.
- Reopen conditions: Reopen if Morning Brief v2 again shows completed records, examples, or stale relay/digest artifacts as active approval work.

#### Bridge Intelligence v1

- Problem discovered: Autonomy Bridge reported `BLOCKED` while the latest Night Supervisor report was `READY`.
- Root cause: Bridge status scanned broad historical/source artifacts and allowed any classified blocked item to dominate top-level status.
- Fix applied: Committed Bridge Intelligence v1 in `5ef27a8 feat(night-supervisor): anchor bridge status to active evidence`.
- Expected outcome: Latest Night Supervisor report anchors bridge status; active blockers drive `BLOCKED`; active approvals drive `NEEDS_APPROVAL`; historical relay artifacts remain detail-only evidence.
- Accepted risk: Broad raw evidence still contains blocked-looking text and old artifacts, so future consumers must honor `status_impact` and active/current buckets instead of raw item status alone.
- Regression checks: Confirm `AUTONOMY_BRIDGE_STATE.json` includes `bridge_status`, `active_current`, `active_decision_cards`, `current_blockers`, `raw_evidence`, and `status_impact`; confirm old relay errors, examples, samples, completed records, and stale projections do not force `BLOCKED`.
- Reopen conditions: Reopen if bridge top-level status is again driven by historical relay artifacts, examples, completed records, stale projections, or old test blockers instead of current active operational evidence.

#### Operator Guidance Layer

- Source: ChatGPT export full-shard aggregate tally. No raw transcript was imported, no private content was stored, and no attachment content was inspected.
- Problem discovered: Repeated human-AI productivity friction concentrated in Git/GitHub/PR/branch handling, repo/path selection, terminal/CLI and PowerShell use, Codex approval prompts, manual repair burden, stale-state confusion, and unclear next actions.
- Root cause: AI guidance often assumed operational vocabulary, current UI shape, repo state, or approval-risk context that the operator needed translated into immediate action.
- Process fix: Added an Operator Guidance Layer rule in `AGENTS.md` requiring action-first, beginner-readable, scope-aware guidance for Git, repo paths, terminal commands, validation, UI/web steps, and Codex approval prompts.
- Expected outcome: Fewer manual repair loops, clearer next actions, safer approval choices, and less repeated confusion around repo path, PR flow, branch state, command purpose, success condition, and stop condition.
- Accepted risk: Over-explaining can become new noise if assistants turn the guidance layer into long tutorials instead of short action-first translation.
- Regression checks: Confirm future prompts explain the immediate action clearly; confirm Codex approval prompts get plain-language risk translation; confirm Git/GitHub/branch/path instructions include success condition and stop condition; confirm UI guidance avoids stale button assumptions and uses current official documentation or visible-state fallback when exact UI matters.
- Reopen conditions: Reopen if repeated frustration from unclear commands, repo paths, PR flow, approval prompts, missing vocabulary, or stale UI assumptions returns.
