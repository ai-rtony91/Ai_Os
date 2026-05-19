# AI_OS Repo Structure Cleanup Current Assessment

Date: 2026-05-19

Mode: APPLY documentation and ignore-rule update only. No push. No merge. No main edit.

## Current Git State

- Current branch: `phase-82-copy-paste-reduction-runner`
- Remote: `origin https://github.com/ai-rtony91/Ai_Os.git`
- Working tree before this assessment: not clean because five untracked Phase 82 runner files were present from earlier work.
- Git warning observed: `Permission denied` reading `C:\Users\mylab/.config/git/ignore`.

Latest commits observed:

- `2d686e9 chore: archive legacy reports and trading lab docs`
- `8441946 docs: add initial repo structure triage`
- `c48298f Merge pull request #179 from ai-rtony91/codex-queue-core`
- `5309e61 Merge branch 'main' into codex-queue-core`
- `5fb7b08 Implement canonical packet queue core`
- `291a111 Merge pull request #178 from ai-rtony91/codex-operations-docs`
- `423a101 Merge pull request #177 from ai-rtony91/codex-runtime-api`
- `30c4b00 docs: add AIOS operations runbooks`

## Diff Versus `origin/main`

`origin/main...HEAD` shows the cleanup branch is primarily the archive move plus ignore/report cleanup:

- `.gitignore` updated.
- `docs/AI_OS/trading_laboratory/` moved to `archive/docs_aios_trading_laboratory_legacy/`.
- `Reports/` moved to `archive/reports_legacy/`.
- `automation/orchestration/workers/logs/validator_worker.log` removed from tracking.
- `docs/audits/repo-structure-triage-initial.md` added.

Diff stat observed:

- 840 files changed
- 65 insertions
- 50 deletions
- most path changes are rename-only archive moves

## Tracked Top-Level Counts

Observed with `git ls-files`:

| Count | Name |
| ---: | --- |
| 837 | archive |
| 790 | docs |
| 597 | automation |
| 237 | apps |
| 39 | services |
| 27 | scripts |
| 19 | aios |
| 10 | work_packets |
| 8 | schemas |
| 7 | internal |
| 3 | agent |
| 3 | inputs |
| 2 | .github |
| 2 | checkpoints |
| 2 | approvals |
| 2 | tests |

Single-file tracked root or small entries include root governance docs, `aios.ps1`, `telemetry/work_ledger.jsonl`, `task_log.json`, `validation_result.json`, and `completion_report.json`.

## Largest Active Folders Excluding Archive

Observed with `git ls-files`, excluding `archive/`:

| Count | Name |
| ---: | --- |
| 770 | docs/AI_OS |
| 250 | automation/orchestration |
| 149 | apps/dashboard |
| 87 | apps/trading_lab |
| 68 | automation/operator |
| 52 | automation/status |
| 48 | automation/trading_lab |
| 24 | automation/dispatcher |
| 19 | aios/modules |
| 11 | services/runtime |
| 11 | automation/mission_control |
| 11 | services/dispatcher |
| 10 | automation/window_identity |
| 9 | automation/windows_workstation |
| 9 | automation/telemetry |
| 8 | schemas/aios |

## Classification

### KEEP ACTIVE

- `apps/dashboard`
- `apps/trading_lab`
- `aios`
- `services`
- `scripts`
- `schemas`
- `tests`
- `.github`
- `docs/audits`
- small intentional docs folders under `docs/`
- root governance docs: `README.md`, `AGENTS.md`, `SECURITY.md`, `RISK_POLICY.md`, `COMPLIANCE_BASELINE.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, `LICENSE`

### CONSOLIDATE NEXT

- `automation/orchestration`
- duplicate worker registries:
  - `automation/orchestration/worker_registry.example.json`
  - `automation/orchestration/worker_registry.v1.example.json`
  - `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
  - `automation/orchestration/workers/WORKER_REGISTRY.json`
  - `automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json`
- duplicate queue concepts:
  - `automation/orchestration/packet_queue.example.json`
  - `automation/orchestration/queue/DISPATCHER_QUEUE.json`
  - `automation/orchestration/queue/WORKER_PACKET_QUEUE_001.json`
  - `work_packets/queues/`
  - root `scripts/*queue*.ps1`
- duplicate approval concepts:
  - root orchestration approval examples
  - `automation/orchestration/approval_inbox/`
  - `automation/orchestration/approval_runner/`
  - `work_packets/approvals/`
- duplicate supervisor/runtime/control-loop concepts:
  - `automation/orchestration/supervisor/`
  - `automation/orchestration/runtime/`
  - `automation/orchestration/control/`
  - `automation/orchestration/daemon/`
- duplicate `show-*` scripts and terminal UI helpers.
- overlap between `scripts/` and `automation/orchestration/`.

### ARCHIVE / DELETE CANDIDATE

- `archive/reports_legacy` after human review and summary extraction.
- `archive/docs_aios_trading_laboratory_legacy` after human review and summary extraction.
- tracked runtime logs if any reappear outside archive.
- generated reports/checkpoints under active paths.
- local heartbeat JSON files if untracked.
- stale or generated orchestration example state files after references are mapped.
- earlier untracked Phase 82 separate-runner files if MAIN CONTROL rejects that direction.

### DO NOT TOUCH

- `.git`
- active app source and package files.
- active app tests.
- `apps/dashboard/assets` unless explicitly scoped.
- `apps/trading_lab/src`, `apps/trading_lab/tests`, and requirements files.
- `aios`, `services`, and `scripts` until references are checked.
- current branch history.
- `.github` workflows unless inspected.
- root governance docs unless explicitly approved.

## Current Risks

- `automation/orchestration` still has multiple overlapping control systems and should not be scaled until consolidated.
- Several example JSON files look like state snapshots, but many are referenced by scripts or docs, so blind archiving is unsafe.
- `scripts/` and `automation/orchestration/` overlap around queue, worker, heartbeat, lock, and status operations.
- The five untracked Phase 82 files from the previous runner direction are active-path clutter unless accepted or removed by explicit human decision.
- Git emits a user-level ignore permission warning, which should be fixed outside this repo if it becomes disruptive.

## Recommended Next Actions

1. Human review the current cleanup branch and decide whether to keep or discard the untracked Phase 82 runner files.
2. Treat `automation/orchestration` as the next controlled cleanup target.
3. Do not move orchestration files yet; first approve a canonical source-of-truth map for worker registry, queue, approval inbox, validator chain, and commit package flow.
4. Keep `archive/reports_legacy` and `archive/docs_aios_trading_laboratory_legacy` intact tonight.
5. Run a focused follow-up pass to identify which root `scripts/` remain canonical versus which should become wrappers over `automation/orchestration`.

## Review Status

Ready for human review after validation.
