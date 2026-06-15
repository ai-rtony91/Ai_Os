# AIOS Operator Checkpoint Dashboard

## Purpose

The operator checkpoint dashboard exists to make AIOS readable at the stop points that matter. The runtime self-route can still produce full evidence, but the default human output should start with a compact status panel instead of a large raw JSON report or a long diagnostic transcript.

This layer supports the current monthly mission: self-building AIOS -> forex-builder proof -> daily earned repo work -> gated trade readiness.

AIOS is the factory. Forex is the first proof product. Daily GitHub work is the compounding output. Live trade readiness is a protected downstream gate, not an automatic background action.

## Default View

The default dashboard is compact. It shows the active mission, selected packet, state, progress flags, next action, bored queue state, safety boundary, and detail hint in 7 to 10 lines.

Full JSON remains available through `-OutputJson`. Detail mode may print additional diagnostic lines, but the default operator view must stay short and action-oriented.

Example:

```text
AIOS STATUS
Mission: self-building AIOS -> forex-builder proof -> daily earned repo work -> gated trade readiness
Packet: PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS
State: WAITING_FOR_APPROVAL
Progress: selected=yes | prompt=yes | tests=not_run | PR=none | SOS=no
Next: approve APPLY / skip packet / inspect details
Bored queue: inactive because a packet is selected
Safety: no broker/live/secrets/orders/webhooks
Details: run with -OutputJson for full report
```

## Checkpoints

- Mission Check: confirms `self-building AIOS -> forex-builder proof -> daily earned repo work -> gated trade readiness`.
- Packet Check: shows the selected packet ID or `none`.
- Approval Check: shows whether AIOS is waiting for Anthony, approved locally, blocked, or complete.
- Workbench Check: shows whether work was written, not written, or preview-only.
- Validation Check: shows tests as `pass`, `fail`, `not_run`, or `unknown`.
- PR Check: shows PR state as `none`, `open`, `checking`, `green`, `merged`, or `blocked`.
- SOS Check: shows whether Anthony must be woken.
- Bored Queue Check: shows one safe fallback task when no higher-priority active packet exists.

## States

- `WAITING_FOR_APPROVAL`: a packet is selected and Codex-ready, but execution approval is missing.
- `APPROVED_TO_WORK`: a selected packet has explicit local execution approval.
- `PR_IN_PROGRESS`: a selected packet has an open or checking PR state.
- `READY_FOR_MERGE_APPROVAL`: checks are green/pass and merge approval is the next protected decision.
- `SOS_REQUIRED`: a blocker requires Anthony.
- `IDLE_SAFE`: no selected packet and no active candidate packets exist.
- `BLOCKED`: a blocker exists and no earlier state applies.
- `REPORT_ONLY`: evidence was produced without a higher-priority action state.

## Bored Queue Policy

AIOS may use bored queue tasks only when no higher-priority active packet exists and only inside approved safety boundaries.

Bored queue tasks are data only. They are not executed by the checkpoint dashboard. They must be small legitimate repo-improvement tasks such as doc polish, test hardening, dashboard simplification, roadmap acceptance cleanup, paper-only forex evidence expansion, risk gate docs/tests, daily contribution loop prep, validator guard cleanup, or compact report contract improvements.

Forbidden bored queue behavior:

- No fake commits.
- No meaningless whitespace commits.
- No generated noise commits.
- No `Reports/` commits unless explicitly approved.
- No `control/review_bridge/` commits unless explicitly approved.
- No scheduler or daemon work.
- No broker or live trading work.
- No secrets, credentials, orders, or webhooks.
- No protected mutation.
- No cleanup or delete without explicit approval.

## Earned Green Box Policy

Green boxes are a byproduct of legitimate validated repo work, not the goal by themselves.

The daily contribution loop should earn activity through scoped docs, tests, contracts, or implementation packets that pass validation and preserve AIOS governance. It must not manufacture commits for heatmap activity.

## Protected Boundaries

The checkpoint dashboard is a control-plane usability layer. It does not authorize:

- broker integration
- OANDA/live exchange integration
- live trading
- paper order execution
- credentials, secrets, or env reads/writes
- webhooks
- scheduler or daemon execution
- worker dispatch
- queue mutation
- approval mutation
- report writes
- git staging, commit, push, or merge

## Forex-Builder Relationship

The current proof line is the forex-builder roadmap. The checkpoint panel should make that proof readable by showing which packet is selected, whether the Codex prompt is ready, whether Anthony approval is missing, and what the next safe action is.

The dashboard does not move the forex roadmap forward by itself. It only exposes the stop point clearly.

## Future Daily Contribution Loop

The future daily loop can use this panel to decide whether AIOS is working, waiting, blocked, complete, or idle-safe. When idle-safe, AIOS may propose one bored queue task as a safe fallback candidate. That proposal still requires the normal packet, validation, approval, commit, and push gates before any protected action.
