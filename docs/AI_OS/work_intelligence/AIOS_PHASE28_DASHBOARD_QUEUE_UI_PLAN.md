# AI_OS Phase 28 Dashboard Queue UI Plan

## 1. Purpose

Phase 28 plans a simple dashboard view for Work Intelligence queue items.

This pack creates plan and mock data only. It does not edit dashboard HTML, CSS, or JavaScript.

## 2. Placement Recommendation

Recommended placement:

- inside the operator/workbench area
- near the future DevOps Control Window
- separate from Trading Lab execution surfaces
- below the next safe action area or beside Work Intelligence summary

The view should not become the main page.

## 3. UI Shape

Use a compact panel.

Preferred desktop shape:

- one simple table/list
- one row per queue item
- clear priority and status chips
- recommended action in plain language

Preferred mobile shape:

- stacked compact rows
- no nested cards inside cards
- no horizontal overflow if avoidable

## 4. Required Fields

Visible fields:

- `queue_rank`
- `title`
- `priority`
- `status`
- `suggested_worker_lane`
- `recommended_action`

Optional fields for later:

- `task_id`
- `source`
- `evidence_strength`
- `route_reason`

## 5. Status Display Rules

Rules:

- If priority is HIGH, show it clearly.
- If status is BLOCKED, show the blocked reason/action clearly.
- If evidence is weak, show `UNKNOWN`.
- Use beginner-readable labels.
- Avoid dense diagnostics in the first panel.

## 6. Lane Display Rules

Lane labels should be visible but not dominant.

Suggested lanes:

- Work Intelligence
- Operator Orchestration
- Dashboard UI
- Trading Lab
- UNKNOWN

## 7. No Execution Controls

The queue UI must not include:

- execution buttons
- worker launch buttons
- APPLY buttons
- commit buttons
- push buttons
- hidden command triggers
- broker/OANDA/API/live execution controls

Display state only.

## 8. Mobile Behavior

Mobile behavior:

- stack rows vertically
- keep rank, priority, and status visible
- wrap long recommended actions
- avoid oversized cards
- avoid nested rabbit holes

## 9. Mock Data Contract

Mock JSON file:

```text
apps/dashboard/mock-data/work-intelligence-queue-v1.example.json
```

Required fields:

- `schema`
- `generated_at`
- `mode`
- `source`
- `queue_count`
- `queue_items`
- `next_safe_action`

Each queue item includes:

- `queue_rank`
- `title`
- `priority`
- `status`
- `suggested_worker_lane`
- `recommended_action`

## 10. Future APPLY Boundaries

Future dashboard APPLY must be separately approved.

Boundaries:

- no scanner edits
- no worker ingestion edits
- no command execution
- no dashboard route changes unless separately approved
- no JavaScript command runners
- no broker/OANDA/API/live execution logic

## 11. Validation

Validation for this plan and mock data:

```powershell
Get-Content -Raw apps/dashboard/mock-data/work-intelligence-queue-v1.example.json | ConvertFrom-Json | Out-Null
git diff --check
git status --short --branch
```
