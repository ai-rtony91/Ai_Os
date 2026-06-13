# AIOS Continuation → Proposed Packet Bridge (V1)

## Purpose

`Convert-AiOsContinuationPlanToProposedPacket.DRY_RUN.ps1` converts the supervised continuation plan into an approval-ready proposed packet preview for the next Forex build step.

The bridge is a DRY_RUN-only transformer.

- Input: supervised continuation plan payload.
- Output: deterministic preview payload and target proposed packet path.
- No writes, no execution, and no queue/approval mutation.

## Why this is not unattended autonomy

The bridge does not claim a worker, start a runtime job, or run APPLY.

- It never writes files.
- It never touches runtime state.
- It never updates approval inbox records.
- It never touches packet queues.
- It never starts workers.
- It leaves all execution decisions to human approval.

## How it consumes the continuation plan

The bridge reads continuation output either from:

- `Get-AiOsSupervisedContinuationPlan.DRY_RUN.ps1 -OutputJson` (default)
- `-ContinuationPlanPath` for a saved plan artifact
- `-ContinuationPlanJson` for in-memory/embedded payloads

It validates the required safety gates in the plan:

- `continuation_status == READY_FOR_APPROVAL`
- `execution_allowed == false`
- `human_approval_required == true`
- `can_continue_without_anthony == false`
- non-empty `recommended_next_packet_id`
- non-empty `recommended_files`
- non-empty `required_validators`
- non-empty `blocked_actions`
- clean workspace (`dirty_or_untracked_count == 0`) before proposing

If any check fails, status is `BLOCKED` and no execution payload is emitted.

## How it prepares the Sprint 18 proposal

When the continuation is clean and approved for review, the bridge builds:

- `proposed_packet_id = AIOS-FOREX-PAPER-STUDY-JOURNAL-APPLY-V1`
- `proposed_packet_lane = PAPER_STUDY_JOURNAL`
- `proposed_packet_path = automation/orchestration/work_packets/proposed/AIOS-FOREX-PAPER-STUDY-JOURNAL-APPLY-V1.md`
- `proposed_packet_payload` with:
  - `mode: APPLY`
  - `mission`: build Sprint 18 paper study journal from Sprint 17 continuity review output
  - `recommended_files` and `required_validators` carried from continuation plan
  - `allowed_write_boundary` aligned to `recommended_files`
  - safety invariants: `execution_allowed = false`, `human_approval_required = true`, `can_continue_without_anthony = false`
  - stop condition: `Stop after local commit only; no push/PR/merge automation.`

## Why it does not write the proposed packet file yet

This packet is a **preview contract** only.

- It returns the serialized packet payload for human review.
- It does not write `.md` or `.json` packet files.
- It is designed to keep the next step explicit and auditable.

## What is required next

An APPLY packet generation step is required to persist this proposal and perform write-safe validation for real packet emission.

Blocked execution gates remain in force:

- No runtime mutation
- No worker launch
- No approval inbox mutation
- No queue mutation
- No push/PR/merge automation

## Contract fields

The preview schema is:

`AIOS_CONTINUATION_TO_PROPOSED_PACKET_PREVIEW.v1`

Key fields include:

- `proposed_packet_status`
- `proposed_packet_id`
- `proposed_packet_path`
- `execution_allowed`
- `human_approval_required`
- `can_continue_without_anthony`
- `writes_files`
- `mutates_runtime`
- `mutates_approval`
- `mutates_queue`
- `starts_worker`
- `packet_validation_status`
