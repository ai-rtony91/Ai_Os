# Approval Flow Map

Date: 2026-06-01
Packet: AIOS-P23

## 1. Approval Chain

Canonical caller: `automation/orchestration/approval_inbox/Invoke-AiOsApprovalChain.DRY_RUN.ps1`

The DRY_RUN chain calls the existing approval scripts in order:

1. `approval_detection/Find-AiOsApprovalMatch.DRY_RUN.ps1`
2. `approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1`
3. `approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1`
4. `approval_runner/Invoke-AiOsApprovalExecutorPreview.DRY_RUN.ps1`

The caller captures step output and returns one gate verdict. It does not execute APPLY, advance packet state, commit, or push.

## 2. Apply Gate File

Canonical gate: `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`

The gate must include `packet_id`, `approval_status`, `approved_by_human`, requested/approved mode fields, path boundaries, validator requirements, and blocked paths. The `packet_id` must be bound before approval can flow to a specific packet.

## 3. Human Approval

Binding a gate to a packet is not approval. Human Owner approval requires both fields in the gate:

- `approved_by_human`: `true`
- `approval_status`: `approved_for_apply`

Until both fields are set by Anthony Meza, the chain verdict remains pending or blocked and no APPLY authority is granted.

## 4. Current P23 Binding

AIOS-P23 binds `APPLY_APPROVAL_GATE_001.json` to packet `phase-17-work-packet-router-state-machine` only. It keeps `approval_status` as `pending_review` and `approved_by_human` as `false`.
