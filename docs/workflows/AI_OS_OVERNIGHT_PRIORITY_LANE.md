# AI_OS Overnight Priority Lane

## Purpose

The Overnight Priority Lane lets Anthony provide one prioritized overnight goal without manually managing every intermediate step.

This lane is a queue-tray and classification model only. It does not create a scheduler, launch workers, call OpenAI, mutate approvals, write telemetry, commit, push, merge, touch production, or perform protected execution.

## Queue-Tray Model

1. Anthony drops one priority goal into the overnight queue tray.
2. AI_OS classifies the goal by risk, readiness, allowed paths, forbidden paths, stop condition, and approval needs.
3. Night Supervisor observes available repo and telemetry evidence, then summarizes current state and blockers.
4. The OpenAI-ready lane prepares sanitized recommendation context only when the input is bounded and approved for recommendation use.
5. Protected Action Readiness classifies whether any proposed action is protected, production-adjacent, or blocked.
6. Codex receives exact packet candidates only. Codex does not self-select overnight work.
7. Anthony receives only SOS or protected-action decisions; routine classification continues as evidence and morning summary.

## Intake Schema

```json
{
  "goal": "string",
  "priority": "LOW | MEDIUM | HIGH | CRITICAL",
  "deadline_window": "string",
  "allowed_paths": ["string"],
  "forbidden_paths": ["string"],
  "risk_tier": "READ_ONLY | DRY_RUN_PLAN | SANDBOX_OUTPUT | LOCAL_APPLY | PROMOTION | PRODUCTION_OR_LIVE",
  "desired_output": "string",
  "approval_needed": true,
  "stop_condition": "string",
  "sos_conditions": ["string"]
}
```

Required intake behavior:

- Missing `goal`, `allowed_paths`, `forbidden_paths`, or `stop_condition` blocks packet drafting.
- Placeholder paths, `TODO`, `TBD`, or invented branch state block packet drafting.
- Production, secrets, broker/API, live trading, GPIO, motor control, scheduler creation, worker launch, approval mutation, commit, push, and merge require explicit protected-action approval before execution.
- The lane may prepare recommendation context; it may not execute protected actions.

## Output Schema

```json
{
  "ranked_tasks": [
    {
      "task_id": "string",
      "title": "string",
      "task_class": "DO_NOW | DO_NEXT | WAIT | BLOCKED | REQUIRES_APPROVAL | SOS_ONLY",
      "reason": "string",
      "blocked_by": ["string"],
      "candidate_codex_packet": "string or null",
      "protected_action_classification": "NONE | REVIEW_REQUIRED | PROTECTED | BLOCKED",
      "openai_input_ready": true,
      "morning_brief_summary": "string",
      "pi5_display_summary": "string",
      "human_approval_points": ["string"]
    }
  ]
}
```

Output requirements:

- `ranked_tasks` must be ordered by priority, readiness, safety, and dependency order.
- Every task must have exactly one `task_class`.
- Candidate Codex packets must preserve allowed paths, forbidden paths, validator chain, and stop point.
- Candidate Codex packets must include completeness status, missing evidence, and any unresolved approval point.
- Morning Brief and Pi5 display summaries are display-only and must not imply execution authority.

## Quality Clause

The Overnight Priority Lane must rank and packetize work by professional-grade standards. `DO_NOW` work must be clear, small, validated, and non-protected unless a separate approval explicitly authorizes the protected step. Low-quality, vague, broad, stale, duplicate-authority, or missing-validator packets should be classified `WAIT` or `BLOCKED`, not executed.

## Task Classes

`DO_NOW`
: Safe, bounded, and ready within the approved mode. No protected action is required before the next step.

`DO_NEXT`
: Valuable and likely safe, but depends on another task, fresh evidence, or operator sequencing.

`WAIT`
: Not blocked by failure, but should not run yet because timing, dependency, or stale evidence makes immediate action low value.

`BLOCKED`
: Cannot proceed safely because required evidence, files, approval, branch state, or validator output is missing.

`REQUIRES_APPROVAL`
: The next meaningful step touches a protected action, approval boundary, write boundary, production-adjacent system, or escalation path.

`SOS_ONLY`
: Anthony should be interrupted only when safe continuation is impossible or a protected-action decision cannot wait.

## Roles

OpenAI:
: Recommendation and ranking only. It may receive sanitized bounded context after approval, but it has no approval, execution, scheduler, worker-launch, repo mutation, production, trading, GPIO, or motor authority.

Night Supervisor:
: Observes, summarizes, classifies, and prepares morning evidence. It does not launch workers, mutate approvals, call APIs, or execute protected actions.

Codex:
: Executes exact packets only. It does not self-select overnight work, invent allowed paths, create schedulers, launch workers, call OpenAI, or continue past the packet stop point.

AI_OS:
: Routes goals, preserves boundaries, checks risk tier, prepares candidate packets, and keeps routine work out of Anthony's path unless a protected-action or SOS condition is reached.

Anthony:
: Sets the priority goal and approves protected-action or SOS decisions. Anthony is not the validator for malformed AI-generated packets.

## Protected Boundaries

The Overnight Priority Lane must stop before:

- scheduler creation
- worker launch
- OpenAI or external API call
- approval mutation
- telemetry write
- commit, push, merge, branch deletion, reset, or clean
- secrets, `.env`, broker/API keys, OANDA, live trading, real orders, real webhooks
- GPIO, motor controls, Pi physical control, or production promotion

Validator PASS is evidence only. It is not approval to execute protected actions.

## SOS Rule

Anthony should be interrupted overnight only when:

- a protected action needs explicit approval and waiting would block the approved overnight goal,
- evidence indicates a safety, data-loss, production, secret, broker/API, GPIO, motor, or live-trading risk,
- workers cannot continue safely because state is contradictory or corrupted,
- a stop condition is met and human decision is required.

Routine stale warnings, recommendation-only defers, display alerts, and non-urgent blockers should go to the Morning Brief and Pi5 display summary instead of waking Anthony.

## Morning And Pi5 Outputs

Morning Brief target:
: concise ranked task summary, blockers, approval points, and next safe command or packet.

Pi5 display target:
: display-only summary of active priority, task class counts, blockers, and whether SOS is required.

Both outputs must preserve:

- `DISPLAY ONLY`
- `NOT APPROVAL AUTHORITY`
- `NO MOTOR / GPIO / TRADING CONTROL`

## Stop Condition

The lane stops after producing ranked tasks, candidate Codex packets, risk classification, Morning Brief summary target, Pi5 display summary target, and human approval points.

It does not execute the candidate packets unless a separate complete APPLY or DRY_RUN packet is approved.
