# Orchestration Multiple-Heads Audit

## Summary

AI_OS has a confirmed multiple-heads risk in `automation/orchestration/`. The current layer is useful and active, but it contains many overlapping control concepts: packet queues, command queues, approval inboxes, approval runners, worker registries, validator chains, dispatcher previews, relay runners, session continuity records, supervisor loops, Night Supervisor previews, runtime loops, commit-package helpers, PR helpers, and root-level display scripts.

This audit is DRY_RUN only. It does not approve moving, deleting, renaming, runtime editing, Night Supervisor execution, Paper SOS resume, broker/OANDA/live trading, Pi GPIO/motor work, or protected Git actions.

## Canonical Orchestration Spine

AI_OS should converge on this authority chain:

```text
goal intake
-> OpenAI/ChatGPT planner
-> packet draft
-> dispatcher route scoring
-> worker assignment
-> validator chain
-> approval gate
-> execution worker
-> clean-state verifier
-> commit package
-> PR lane
-> human merge
-> trace/red-team/improvement loop
```

Night Supervisor remains preview/report-only until controlled-run gates pass.

Trading remains paper-only until trust gates pass.

## Duplicate Or Legacy Candidate Areas

These areas appear to overlap and require staged consolidation:

| Area | Candidate paths | Risk |
|---|---|---|
| Worker registry | `automation/orchestration/workers/`, root `worker_registry.v1.example.json`, `sync-worker-registry.ps1`, task cards, crew examples | Multiple worker sources can disagree. |
| Packet queues | `work_packets/`, `queue/`, root `packet_queue_ledger.v1.example.json`, command queue | Packet status can fragment across queues. |
| Approval authority | `approval_inbox/`, `approval_runner/`, `approval_processor/`, `approval_detection/`, root `approval_inbox.v1.example.json`, `approvals/` | Approval evidence can be mistaken for authority. |
| Validator authority | `validators/`, `validator_chain_runner/`, docs workflow standards, schema validators, health validators | Validator PASS can be over-read as APPLY approval. |
| Dispatch authority | `dispatch/`, `router/`, `execution_pipeline/`, `openai_api_bridge/`, `control/` | Route decision ownership can split. |
| Supervisor/runtime loops | `supervisor/`, `runtime/`, `night_supervisor/`, `auto_loop/`, `self_continuation/`, `daemon/` | Preview loops can drift toward runtime authority. |
| Relay/session continuity | `relay/`, `session/`, root `session_continuity.v1.example.json`, terminal workstation checkpoint files | Old continuity artifacts can become stale state. |
| Commit/PR helpers | `commit_packages/`, `pr_gates/`, root PR scripts, docs workflow standards | Protected action gates can be duplicated. |
| Root examples and show scripts | root `*.example.json`, root `show-*` scripts | Compatibility helpers can look canonical. |

## High-Risk Areas

- `automation/orchestration/night_supervisor/`: unsafe to modify until the Paper SOS working-directory boundary and controlled-run gates are stable.
- `automation/orchestration/runtime/`: runtime/self-route scripts can create autonomy confusion if consolidated before authority is mapped.
- `automation/orchestration/approval_inbox/`: contains active approval/gate records and archived examples; do not edit or move without an approval-state migration plan.
- `automation/orchestration/locks/`: contains path/worker lock evidence; do not edit during consolidation audit.
- `automation/orchestration/memory/`: runtime memory state is protected and not a consolidation target in this DRY_RUN.
- `automation/orchestration/relay/` and `session/`: may still serve continuity or handoff workflows; review references before retirement.

## No-Delete Warning

No file should be deleted, moved, renamed, or archived from this audit. The tracked orchestration tree is too interconnected to cut by filename alone. A future APPLY packet must prove:

- active references are known.
- replacement path is canonical.
- runtime and Night Supervisor paths are unaffected.
- Paper SOS resume boundary is unaffected.
- commit/PR gates remain intact.
- clean-state verifier still passes.

## Recommended Consolidation Order

1. Mark canonical authority docs and paths.
2. Add deprecation headers only to obvious examples and legacy docs after reference review.
3. Update docs/scripts to point to canonical paths.
4. Move/archive duplicate examples only after all readers are updated.
5. Remove only confirmed dead files with no active references.
6. Validate Night Supervisor and Paper SOS boundaries remain unaffected.
7. Run clean-state verifier and PR lane validation.

