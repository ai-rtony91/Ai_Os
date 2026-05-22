# AI_OS Repo Structure Triage - Initial Findings

## Current Control Repo
C:\Dev\Ai.Os

## Current Branch
phase-82-copy-paste-reduction-runner

## Main Findings

### Confirmed Cleanup Candidates
- docs/AI_OS/trading_laboratory
  - 501 tracked files
  - Exists on origin/main
  - Looks like generated planning / paper trading documentation maze

- Reports
  - 336 tracked files
  - Mostly checkpoints, daily reports, health reports, dispatcher outputs
  - Looks like committed runtime/report history

- automation/orchestration
  - 251 tracked files
  - Many overlapping control concepts: workers, queues, approvals, supervisor, validators, reports

- automation/orchestration/workers/logs/validator_worker.log
  - Tracked runtime log
  - Should likely be removed from Git tracking later and ignored

### Lower Concern
- apps/dashboard
  - Real frontend app
  - node_modules ignored and untracked
  - Review AIOS_STATIC_PREVIEW.html, AIOS_MUSIC_COMPANION.html, private-media, skeleton, mock-data later

- apps/trading_lab
  - 87 tracked files
  - Looks like real lab/app area, not first deletion target

- .codex_worktrees
  - Only two visible local worktrees
  - Not first cleanup target

### Main Diagnosis
AI_OS has a small real core buried under a large paper/report/orchestration sprawl.

## Do Not Delete Yet
No deletions until a cleanup branch and explicit delete/archive list exist.
