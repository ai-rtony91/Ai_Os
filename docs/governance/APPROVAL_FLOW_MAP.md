# Approval Flow Map

Date: 2026-06-02
Packet: AIOS-24H-LOOP-CODEX1-APPROVAL-INBOX-AUTHORITY-APPLY-001

## 1. Approval Chain

Canonical caller: `automation/orchestration/approval_inbox/Invoke-AiOsApprovalChain.DRY_RUN.ps1`

The DRY_RUN chain calls the existing approval scripts in order:

1. `approval_detection/Find-AiOsApprovalMatch.DRY_RUN.ps1`
2. `approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1`
3. `approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1`
4. `approval_runner/Invoke-AiOsApprovalExecutorPreview.DRY_RUN.ps1`

The caller captures step output and returns one gate verdict. It does not execute APPLY, advance packet state, commit, or push.

## 2. Apply Gate File

Canonical inbox: `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`

Canonical gate: `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`

The active approval authority is the `automation/orchestration/approval_inbox/` folder. The active inbox records authority scope, Human Owner approval authority, blocked paths, and evidence/projection boundaries. The active gate records whether a specific APPLY packet is bound and approved.

The gate must include `packet_id`, `approval_status`, `approved_by_human`, requested/approved mode fields, path boundaries, validator requirements, and blocked paths. The `packet_id` must be bound before approval can flow to a specific packet.

## 3. Human Approval

Binding a gate to a packet is not approval. Human Owner approval requires both fields in the gate:

- `approved_by_human`: `true`
- `approval_status`: `approved_for_apply`

Until both fields are set by Anthony Meza, the chain verdict remains pending or blocked and no APPLY authority is granted.

## 4. Evidence And Projection Boundaries

These surfaces may be read as evidence or projection input, but they are not active approval authority:

- `relay/approvals/`
- `control/operation_glue/APPROVAL_INBOX.json`
- telemetry approval projections
- Night Supervisor output
- Autonomy Bridge output
- dashboard output

Validator output is evidence only. It does not approve APPLY, commit, push, merge, PR creation, runtime mutation, scheduler changes, broker/OANDA/API-key work, secrets handling, or trading actions.

## 5. Current Gate Binding

AIOS-P23 binds `APPLY_APPROVAL_GATE_001.json` to packet `phase-17-work-packet-router-state-machine` only. It keeps `approval_status` as `pending_review` and `approved_by_human` as `false`.

That gate state remains pending review. This authority repair does not approve the P23 APPLY lane or any future APPLY, commit, push, merge, PR creation, runtime mutation, scheduler change, broker/OANDA/API-key work, secrets handling, or trading action.
