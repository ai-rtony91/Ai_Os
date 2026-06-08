# AI_OS Worker Dispatcher Control Plane V1

## Purpose

AI_OS has worker definitions and preview scripts, but those pieces do not yet form a deployable control plane. ChatGPT cannot directly deploy local workers because there is no repo-local contract that proves who the workers are, what lanes they may own, which paths they protect, whether locks collide, and whether an assignment is safe.

Worker Dispatcher / Control Plane V1 creates that contract. It is read-only by default and exists to produce safe assignment previews before any future worker-launch or assignment-executor lane is approved.

## Worker Roles

The dispatcher model defines these worker types:

- ChatGPT supervisor/planner
- Codex CLI local executor
- Claude Code reviewer/branch worker
- OpenAI/Codex app review/remote worker
- GitHub PR/checks layer
- Anthony approval authority

Only Anthony is approval authority. GitHub is a PR and checks layer, not a local executor. ChatGPT may plan and draft non-executable packets, but it is not a local file executor. Codex may execute only scoped, approved local packets. Claude is not approval authority.

## Authority Model

Each worker record declares:

- `worker_id`
- `worker_type`
- `display_name`
- `authority_level`
- `allowed_lanes`
- `forbidden_lanes`
- `allowed_actions`
- `forbidden_actions`
- `can_apply`
- `can_merge`
- `can_launch_workers`
- `can_touch_scheduler`
- `can_touch_live_sos`
- `can_touch_broker_or_trading`
- `can_touch_cloud_provider`
- `default_status`
- `evidence_path`
- `next_safe_action`

The validator fails closed when any non-Anthony worker claims approval authority, worker launch authority, scheduler authority, live SOS authority, broker/trading authority, cloud/provider authority, merge authority, direct main push, force push, branch deletion, or stash mutation.

## Lane Assignment Model

Each assignment declares:

- `lane_id`
- `lane_name`
- `assigned_worker_id`
- `status`
- `priority`
- `protected_paths`
- `related_branch`
- `related_pr`
- `required_approval`
- `lock_id`
- `allowed_actions`
- `forbidden_actions`
- `validation_contract`
- `output_contract`
- `next_safe_action`

Assignments without a lane or protected paths are invalid. APPLY assignments require an approval reference. Active assignments cannot own the same lane or overlapping protected paths.

## Worker State Model

Workers are classified as:

- `available`
- `busy`
- `blocked`
- `stale`
- `unknown`

Stale workers cannot receive APPLY work. Unknown workers cannot receive APPLY work. Blocked workers cannot receive new active assignments. Busy workers cannot receive colliding protected paths.

## Dispatch Preview

The preview answers:

- whether a task can be assigned
- which worker is selected
- whether protected paths collide
- whether queue state is missing
- whether locks are missing or stale
- whether assignment should be blocked
- whether operator approval is needed
- whether SOS is needed
- whether the dispatch packet is non-executable

Generated dispatch packets are draft-only and non-executable by default. They do not contain an execution token, do not approve APPLY, and include a stop point.

## Generated Output

Dispatcher runtime evidence belongs under ignored generated-output roots such as:

```text
Reports/generated/dispatcher/worker_dispatcher_preview.json
```

Routine validator sample checks do not write runtime evidence and should not dirty tracked files.

## Safety Boundaries

This PR does not launch workers.

This PR does not start a scheduler.

This PR does not send SOS.

This PR does not run Night Supervisor.

This PR does not grant APPLY authority.

This PR does not touch broker/live trading/cloud/provider behavior.

This PR does not make AI_OS weekend-ready.

## Future Path

The next control-plane step is a DRY_RUN assignment executor that consumes this registry and assignment contract, reads queue and lock sources, and produces a dispatch preview without launching any worker. A later APPLY lane may connect that executor to real worker launch only after approval inbox, queue, lock, CI, SOS, and scheduler-readiness gates are proven.
