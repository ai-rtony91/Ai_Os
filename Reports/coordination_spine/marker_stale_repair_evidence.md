# Marker Stale Repair Evidence

## Summary
This report records the bounded marker-only repair that refreshed `control/cycle/last_marker.json` without running the full night cycle.

## Baseline
- Baseline commit: `18858e2a2e8f78a2128ba1dfcafcfa25b07bc7df`
- Known stale marker timestamp before repair: `2026-06-02T16:45:38Z`
- Marker stale threshold: `RestartMarkerMaxAgeSeconds = 172800`

## Marker Refresh Action
- Helper created: `automation/orchestration/coordination_spine/Update-AiOsCycleMarker.DRY_RUN.ps1`
- Helper mode: DRY_RUN default, `-Apply` required to write
- Applied helper once to refresh only `control/cycle/last_marker.json`
- No full night cycle was run

## Marker Status After
- Old `updated_at_utc`: `2026-06-02T16:45:38Z`
- New `updated_at_utc`: `2026-06-09T23:18:43Z`
- `marker_stale` cleared from recovery telemetry: yes
- `marker_stale` cleared from cockpit telemetry: yes

## Recovery Status After
- `marker_freshness_status`: `FRESH`
- `recovery_readiness`: `REVIEW_REQUIRED`
- Remaining recovery warning: `heartbeat_degraded`

## Cockpit Status After
- `approval_gate_status`: `BLOCKED`
- `live_dispatch_status`: `BLOCKED`
- `t2b_status`: `prerequisite_only`

## Remaining Blockers
- `packet_factory_approval_required`
- `packet_factory_blocked`
- `queue_blocked`
- `queue_blocked, lock_review_required_or_collision, recovery_blocked`

## Warnings
- `heartbeat_degraded`
- `live_dispatch_blocked_by_design`
- `module5b_design_only`
- `packet_factory_missing_required_fields`
- `t2b_prerequisite_only`

## Mutation Check
- Only the allowed files changed during repair:
  - `control/cycle/last_marker.json`
  - `telemetry/coordination_spine/RECOVERY_BOOTSTRAP_VIEW.json`
  - `telemetry/coordination_spine/COORDINATION_SPINE_VIEW.json`
  - this evidence report
- No queue, lock, approval inbox, dispatcher, scheduler, SOS/ADB, dashboard, broker, webhook, secrets, or authority mutation occurred

## Validation Summary
- Helper parser check passed
- Recovery parser check passed
- Cockpit parser check passed
- `python -m pytest tests/orchestration/test_cycle_marker_refresh.py` passed
- JSON parse validation passed for:
  - `control/cycle/last_marker.json`
  - `telemetry/coordination_spine/RECOVERY_BOOTSTRAP_VIEW.json`
  - `telemetry/coordination_spine/COORDINATION_SPINE_VIEW.json`
- Governance validator passed for `automation/orchestration/work_packets/proposed/AIOS-COORDINATION-SPINE-V1.md`
- `git diff --check` passed

## Safe Next Action
If a longer proof is desired, rerun the cockpit lane now that the marker is fresh. Otherwise keep the lane read-only.
