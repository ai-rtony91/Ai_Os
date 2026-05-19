# AI_OS Orchestration Archive Pass 8

Date: 2026-05-19
Branch: phase-82-copy-paste-reduction-runner
Mode: APPLY, archive moves only

## Purpose

Pass 8 ran a final reference classification after Pass 7 and Pass 7B made legacy fallback files optional. The goal was to move only archive-safe legacy orchestration fallback files into `archive/orchestration_legacy/` without deleting files or moving canonical sources.

## Files Inspected

Reference scan covered active automation, docs, and scripts:

- `automation/`
- `docs/`
- `scripts/`

Candidate files inspected:

- `automation/orchestration/packet_queue.example.json`
- `automation/orchestration/packet_queue_ledger.v1.example.json`
- `automation/orchestration/worker_registry.example.json`
- `automation/orchestration/worker_registry.v1.example.json`
- `automation/orchestration/approval_inbox.example.json`
- `automation/orchestration/approval_inbox.v1.example.json`
- `automation/orchestration/validator_chain.example.json`
- `automation/orchestration/validator_routing_supervisor.v1.example.json`
- `automation/orchestration/commit_package.example.json`
- `automation/orchestration/persistent_worker_supervisor.v1.example.json`
- `automation/orchestration/launch_supervisor.v1.example.json`
- `automation/orchestration/queue_health_supervisor.v1.example.json`

## Files Moved

Moved to `archive/orchestration_legacy/root_examples/`:

- `automation/orchestration/packet_queue.example.json` -> `archive/orchestration_legacy/root_examples/packet_queue.example.json`
- `automation/orchestration/worker_registry.example.json` -> `archive/orchestration_legacy/root_examples/worker_registry.example.json`
- `automation/orchestration/approval_inbox.example.json` -> `archive/orchestration_legacy/root_examples/approval_inbox.example.json`
- `automation/orchestration/validator_chain.example.json` -> `archive/orchestration_legacy/root_examples/validator_chain.example.json`
- `automation/orchestration/commit_package.example.json` -> `archive/orchestration_legacy/root_examples/commit_package.example.json`

## Files Kept

Kept active:

- `automation/orchestration/packet_queue_ledger.v1.example.json`
- `automation/orchestration/worker_registry.v1.example.json`
- `automation/orchestration/approval_inbox.v1.example.json`
- `automation/orchestration/validator_routing_supervisor.v1.example.json`
- `automation/orchestration/persistent_worker_supervisor.v1.example.json`
- `automation/orchestration/launch_supervisor.v1.example.json`
- `automation/orchestration/queue_health_supervisor.v1.example.json`
- `automation/orchestration/orchestration_status_snapshot.example.json`
- `automation/orchestration/orchestration_spine_v1.example.json`

## Classification

| Candidate | Classification | Reason |
| --- | --- | --- |
| `packet_queue.example.json` | ARCHIVE SAFE | Primary queue display, worker status, sync, and clean-state paths now use canonical `work_packets/`; remaining active references are guarded fallback labels or historical docs. |
| `worker_registry.example.json` | ARCHIVE SAFE | Primary worker source is canonical `workers/AIOS_WORKER_REGISTRY.json`; remaining active references are guarded fallback labels or status/spine compatibility metadata. |
| `approval_inbox.example.json` | ARCHIVE SAFE | Primary approval source is canonical `approval_inbox/APPROVAL_INBOX_001.json`; remaining active references are guarded fallback labels or historical docs. |
| `validator_chain.example.json` | ARCHIVE SAFE | Primary validator source is canonical `validators/VALIDATOR_CHAIN_CONFIG_001.json`; remaining active references are guarded fallback labels or historical docs. |
| `commit_package.example.json` | ARCHIVE SAFE | Primary commit package source is canonical `commit_packages/COMMIT_PACKAGE_RECOMMENDATION.example.json`; Pass 7B cleared daily snapshot hard reference. |
| `packet_queue_ledger.v1.example.json` | KEEP ACTIVE | Still read directly by `show-packet-queue-ledger.ps1` and `show-worker-registry-v1.ps1`; docs include validation commands for it. |
| `worker_registry.v1.example.json` | KEEP ACTIVE | Still read directly by `show-worker-registry-v1.ps1`; docs include validation commands for it. |
| `approval_inbox.v1.example.json` | KEEP ACTIVE | Still read directly by `show-approval-inbox-v1.ps1`; docs include validation commands for it. |
| `validator_routing_supervisor.v1.example.json` | KEEP ACTIVE | Still read directly by `show-validator-routing-supervisor.ps1`; docs include validation commands for it. |
| `persistent_worker_supervisor.v1.example.json` | KEEP ACTIVE | Still read directly by `show-persistent-worker-supervisor.ps1`; docs include validation commands for it. |
| `launch_supervisor.v1.example.json` | KEEP ACTIVE | Still read directly by `show-launch-supervisor.ps1`; docs include validation commands for it. |
| `queue_health_supervisor.v1.example.json` | KEEP ACTIVE | Still read directly by `show-queue-health-supervisor.ps1` and referenced by mission/supervisor state examples. |

## Remaining Fallback References

Remaining references to the moved root example names are expected in:

- historical audit docs,
- older Phase 16 docs,
- status/spine compatibility metadata,
- optional guarded fallback paths in display/status scripts.

Remaining references to v1 example files are not archive-safe yet because active `show-*` scripts still read them directly.

## Validation Commands Run

```powershell
git status --short --branch
rg -n "packet_queue\.example\.json|packet_queue_ledger\.v1\.example\.json|worker_registry\.example\.json|worker_registry\.v1\.example\.json|approval_inbox\.example\.json|approval_inbox\.v1\.example\.json|validator_chain\.example\.json|validator_routing_supervisor\.v1\.example\.json|commit_package\.example\.json|persistent_worker_supervisor\.v1\.example\.json|launch_supervisor\.v1\.example\.json|queue_health_supervisor\.v1\.example\.json" automation docs scripts
git mv automation/orchestration/packet_queue.example.json archive/orchestration_legacy/root_examples/packet_queue.example.json
git mv automation/orchestration/worker_registry.example.json archive/orchestration_legacy/root_examples/worker_registry.example.json
git mv automation/orchestration/approval_inbox.example.json archive/orchestration_legacy/root_examples/approval_inbox.example.json
git mv automation/orchestration/validator_chain.example.json archive/orchestration_legacy/root_examples/validator_chain.example.json
git mv automation/orchestration/commit_package.example.json archive/orchestration_legacy/root_examples/commit_package.example.json
git status --short
git diff --stat
git diff --name-status
git diff --check
```

## Risks

- Optional fallback paths still point to the old root location. This is acceptable for Pass 8 because the scripts now continue from canonical sources if fallback files are missing.
- Older docs still reference old root locations and should be updated only if those docs are promoted back into active runbooks.
- The v1 supervisor and ledger examples remain a separate consolidation target because they still have direct display scripts.

## Next Cleanup Recommendation

Pass 9 should canonicalize or archive the v1 display lane separately:

- decide whether `show-*-v1.ps1` scripts are still needed,
- map v1 examples to canonical subfolders if kept,
- update Phase 16 docs only if they remain active runbooks,
- archive v1 examples only after their direct `show-*` dependencies are removed or made optional.
