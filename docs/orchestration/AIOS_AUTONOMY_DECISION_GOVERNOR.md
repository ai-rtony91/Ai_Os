# AI_OS Autonomy Decision Governor

## Purpose

AI_OS is the factory. Workers are the machines. Validators are quality control.
Approval gates are safety locks. The Autonomy Decision Governor is the factory
manager.

The governor decides the next safest highest-value work item from local evidence.
It explains why the task matters, assigns a lane, declares risk, names validators,
sets stop conditions, and emits a machine-readable decision artifact.

## Boundary

The governor does not trade live. It does not add broker execution, real webhook
execution, credential handling, background mutation, scheduler registration, or
provider dispatch. It does not bypass Anthony Meza. It does not approve APPLY,
commit, push, merge, or protected actions.

The governor is a conservative coordination layer above workers and below Human
Owner approval. It exists to prevent random Codex prompt sprawl by turning local
evidence into one governed next-action recommendation.

## Relationship To Existing Owners

The governor does not replace existing AI_OS components:

- Runtime queue adapters own queue normalization.
- Validator evidence routers own validator/evidence surface classification.
- Approval adapters own approval evidence projection.
- Self-build consumers normalize self-build evidence.
- Autonomy status reports surface status for operators.

The governor composes those outputs when present. If it detects duplicate intent,
it recommends extending the canonical owner instead of creating a competing brain.

## Relationship To The Closed Autonomy Loop

`automation/orchestration/aios_closed_autonomy_loop.py` consumes the governor's
selected decision and turns it into a one-cycle control-plane recommendation:
observe, decide, plan, validate gate, recommend dispatch, report, and stop. The
closed loop does not rank candidates or dispatch workers. Ranking remains owned
by the governor; dispatch remains blocked until a later approved worker-dispatch
packet connects approval, locks, queue state, validators, and stop controls.

## Decision Contract

The canonical schema is:

`schemas/orchestration/aios_autonomy_decision_governor.schema.json`

The default latest report is:

`Reports/autonomy_decision_governor/AIOS_AUTONOMY_DECISION_GOVERNOR_LATEST.json`

Required decision fields include:

- `next_highest_value_task`
- `decision_category`
- `why_this_task`
- `risk_level`
- `allowed_lane`
- `required_validators`
- `stop_conditions`
- `blocked`
- `blocked_reason`
- `evidence_inputs`
- `confidence`
- `recommended_packet_scope`
- `ranked_candidates`
- `selected_candidate_id`
- `selection_reason`

## Decision Ranking Engine

The governor ranks candidate next actions before selecting one. Each candidate
has:

- `task_id`
- `title`
- `category`
- `value_score`
- `urgency_score`
- `risk_score`
- `blocker_score`
- `validation_score`
- `autonomy_leverage_score`
- `total_score`
- `reason`
- `required_validator`
- `allowed_lane`
- `stop_condition`
- `blocked`

`risk_score` is a risk-control priority score. A high score means the risk needs
attention; it does not grant permission to proceed.

## Conservative Decision Order

1. Safety-blocked live trading, broker, webhook, real order, credential, or secret
   scope outranks everything and returns a blocked decision.
2. Dirty or unknown repo state outranks APPLY work and routes to status recon.
3. Active blocker evidence outranks worker, queue, and feature work.
4. Missing approval blocks APPLY.
5. Validator failure or missing validator evidence outranks feature work.
6. Queue blocker or backlog outranks dashboard and Trading Lab polish.
7. Self-build loop wiring outranks dashboard surfacing.
8. Trading Lab work stays in default paper/simulation or approved demo-review stages unless separately governed.
9. Dashboard or reporting surfacing stays lower priority until closed-loop
   autonomy evidence exists.
10. If no safe next step is provable, the governor blocks and reports.

## Safety Posture

The governor outputs decisions, not commands. A decision is evidence for a future
packet. It is not approval to mutate files, launch workers, register schedulers,
start background loops, access credentials, commit, push, merge, or trade.
