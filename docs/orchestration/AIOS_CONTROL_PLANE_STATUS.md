# AIOS Control-Plane Status

`aios_control_plane_status.py` aggregates the local autonomy control-plane
contracts into dashboard-readable `AIOS_CONTROL_PLANE_STATUS.v1`.

The status includes milestone, current goal, loop status, resume readiness, next
component, next action, proof net, approvals required, blockers, safety flags,
and `dashboard_ready`.

`dashboard_ready` is true only when resume state is ready, bounded executor
readiness is present, the local runner bridge is preview-ready, and there are no
safety blockers for live trading, broker activity, scheduler/daemon activation,
worker dispatch, queue/approval mutation, credentials, real orders, or real
webhooks.

Persistence is explicit only and bounded to
`Reports/aios_control_plane/AIOS_CONTROL_PLANE_STATUS_latest.json`. This module
does not change visible dashboard UI.
