# AIOS ChatGPT Reviewed PR Lifecycle Bridge (V1)

## Purpose

This bridge connects three bounded steps:

1. Codex CLI produces a final packet report in DRY_RUN mode.
2. Anthony copies that report into ChatGPT for human-readable supervisor review.
3. ChatGPT reviews for safety and returns a constrained PowerShell block.
4. Anthony executes the reviewed block locally to perform only the approved PR lifecycle step.

This design keeps explicit human control in the loop and prevents Codex or ChatGPT from performing
GitHub actions directly.

## Why this bridge exists

The packet workflow already has multiple approval and handoff transitions. This bridge makes those transitions
repeatable by standardizing:

- what Codex shares with review,
- what ChatGPT must return,
- how PowerShell executes only reviewed steps,
- and where the merge gate remains explicit.

## Handoff contract

### 1) Codex report → ChatGPT review

Use:
`automation/orchestration/review_bridge/New-AiOsCodexReportForChatGptReview.DRY_RUN.ps1`

Expected output includes:

- `schema`
- `mode`
- `packet_id`
- `branch`
- `report_summary`
- `safety_claims`
- `validation_claims`
- `requested_chatgpt_review`
- `requested_powerShell_output`
- `must_not_execute_without_anthony: true`
- `can_continue_without_anthony: false`
- `writes_files: false`

## What Anthony copies into ChatGPT

Anthony sends the JSON payload and requests a constrained PowerShell block.

ChatGPT must return only a PowerShell block, not raw text, after checking:

- repository state,
- blocked actions,
- safety flags,
- and whether the next step is still approved.

Required instruction in every review request:

> `ChatGPT must review this report and return a PowerShell block only after checking safety and repo state.`

## What ChatGPT returns

ChatGPT must return one block that:

- targets `automation/orchestration/pr_lifecycle/Invoke-AiOsReviewedPrLifecycle.DRY_RUN.ps1`,
- includes `-AnthonyReviewed`,
- is limited to approved operations (push, PR create/reuse, optional checks watch, optional merge),
- and does not add force push or commit/merge commands outside an explicit approval gate.

## What Anthony pastes into PowerShell

Anthony executes only the reviewed block in local PowerShell. No unreviewed script output is executed directly
against repo state.

## Helper behavior

`automation/orchestration/pr_lifecycle/Invoke-AiOsReviewedPrLifecycle.DRY_RUN.ps1` enforces:

- `-AnthonyReviewed` required.
- Must not run on base branch.
- Clean working tree required.
- Branch must be ahead of base.
- Push without force.
- Create PR if missing, or reuse existing open PR if found.
- Optional checks watch with `-WatchChecks`.
- Merge only with explicit flag:
  - `-AnthonyApprovedMerge` or
  - `-MergeAfterChecks` (alias).
- Sync main after merge.
- Re-run status and continuation proof in read-only mode.

The output includes:

- `schema`, `mode`
- `anthony_reviewed`
- `branch`, `base_branch`, `head_branch`
- `working_tree_clean`, `ahead_of_base`
- `pushed`, `pr_created`, `pr_reused`, `pr_number`, `pr_url`
- `checks_status`
- `merge_requested`, `merge_allowed`, `merged`
- `deleted_branch`, `synced_main`
- `aios_status_ran`, `continuation_plan_ran`, `continuation_bridge_ran`
- `next_packet_candidate`
- `execution_allowed: false`
- `human_approval_required`
- `requires_anthony_for_merge`
- `blocked_actions`
- `exact_next_safe_action`
- `reason`

## Default stop policy

Default behavior is stop-before-merge:

- when `-AnthonyApprovedMerge` is absent, helper blocks at approval-required merge boundary,
- `merged` remains `false`,
- `human_approval_required` remains `true`.

## Safety boundaries

- no commit creation.
- no force push.
- no runtime/queue/lock/approval/worker/scheduler/telemetry mutation.
- no broker/OANDA/webhook/order/secrets actions.
- no background scheduler/daemon launch.

## Example flows

### Example 1: PR create/check only

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/review_bridge/New-AiOsCodexReportForChatGptReview.DRY_RUN.ps1 `
  -PacketId AIOS-FOREX-... `
  -Branch feature/...
```

Then in PowerShell after ChatGPT review:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/pr_lifecycle/Invoke-AiOsReviewedPrLifecycle.DRY_RUN.ps1 `
  -AnthonyReviewed `
  -Title "feat: ..."`
  -Body "..." `
  -WatchChecks `
```

### Example 2: Merge after review and Anthony approval

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/pr_lifecycle/Invoke-AiOsReviewedPrLifecycle.DRY_RUN.ps1 `
  -AnthonyReviewed `
  -Title "feat: ..."`
  -Body "..." `
  -WatchChecks `
  -AnthonyApprovedMerge `
  -MergeAfterChecks
```

### Example 3: Post-merge continuation proof

```powershell
# emitted when -AnthonyApprovedMerge was provided and merge succeeded
# results include:
# - aios_status_ran = true
# - continuation_plan_ran = true
# - continuation_bridge_ran = true
```

## Next safe action

If output shows:

- `checks_status = PASS` and `merge_requested = false`, request Anthony approval for one more merge-capable command.
- If merge is requested and succeeds, inspect `next_packet_candidate` and run the normal continuation gate checks.
