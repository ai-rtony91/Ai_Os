# AIOS Packet Queue Planner

Schema: `AIOS_PACKET_QUEUE_PLANNER.v1`

`automation/orchestration/aios_packet_queue_planner.py` ranks candidate packet evidence, blocks unsafe or colliding packets, selects one next safe packet, and returns a Codex-ready packet preview. It does not execute packets, launch Codex, dispatch workers, mutate queues, mutate approvals, write Reports, access the network, commit, push, merge, reset, or delete branches.

## Inputs

Each candidate packet may include:

- `packet_id`
- `title`
- `lane`
- `priority`
- `milestone_value`
- `risk_level`
- `status`
- `required_files`
- `blocked_files`
- `required_approvals`
- `validators`
- `dependencies`
- `conflicts`
- `safety_flags`

The planner accepts either a list of candidate packets or a dictionary containing `candidates`, `candidate_packets`, or `packets`.

## Selection Rules

The planner ranks candidates by priority and milestone value, then selects the highest ranked safe candidate. A candidate is blocked or rejected before selection when it has:

- blocked, rejected, completed, or unknown status
- missing required files
- high, critical, unsafe, production, live, or unbounded risk
- protected approval requirements
- missing dependencies
- declared conflicts
- required-file collisions with its own blocked files
- required-file collisions with a higher ranked eligible candidate
- unsafe safety flags

## Output

The output includes:

- `queue_status`
- `selected_packet`
- `ranked_packets`
- `blocked_packets`
- `collision_status`
- `required_approvals`
- `next_safe_action`
- `codex_ready_packet_preview`
- side-effect proof fields
- `safety`

When no safe packet can be selected, `codex_ready_packet_preview.packet_ready` is false.

## Safety Contract

The planner is evidence-only. It keeps:

- `commands_executed` as `[]`
- `workers_dispatched` as `false`
- `queues_mutated` as `false`
- `approvals_mutated` as `false`
- `files_written` as `[]`
- `safety.preview_only` as `true`

The Codex packet text is a preview artifact only. Queue movement, worker assignment, approval mutation, staging, commits, pushes, merges, scheduler activation, daemon activation, and branch deletion remain outside this planner.
