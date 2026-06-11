CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

identity marker: Codex East local executor
supervisor identity: ChatGPT Personal
packet ID: AIOS-OPEN-PR-BACKLOG-CLEANUP-REVIEW-AFTER-570
mode: DRY_RUN
zone: GitHub PR backlog cleanup review
worker identity: Codex East
lane: pr-backlog-cleanup-review
worktree: C:\Dev\Ai.Os
branch: resolve after preflight; expected main

approval authority: Anthony remains Human Owner. This packet does not approve closing PRs, merging PRs, deleting branches, force-pushing, rebasing, committing, pushing, runtime launch, runtime execution, queue mutation, scheduler registration, SOS send, live trading, broker action, credential access, or secret storage.

allowed paths:
- Reports/pr_backlog_reconciliation/

forbidden paths:
- AGENTS.md
- README.md
- docs/governance/
- docs/workflows/
- docs/security/
- scripts/backup/
- automation/orchestration/work_packets/active/
- automation/orchestration/work_packets/blocked/
- automation/orchestration/work_packets/complete/
- automation/orchestration/workers/inbox/
- automation/orchestration/command_queue/
- automation/orchestration/approval_inbox/
- telemetry/runtime/
- services/
- apps/trading_lab/
- aios/modules/trader/
- .github/
- .git/
- secrets
- credentials
- .env

validator chain:
- git status --short --branch

stop point:
Stop after producing a human-readable cleanup recommendation. Do not close PRs. Do not merge PRs. Do not delete branches. Do not push. Do not commit.

mission:
Review the PR backlog reconciliation after PR #570 and prepare the next human-approved cleanup lane. The recommended strategy is to close obvious superseded PRs in a separate mutation pass, keep only selected autonomy candidates for focused review, handle Dependabot separately, handle non-main-base PR #301 separately, and avoid blind merges.

preflight:
1. Run:
   cd C:\Dev\Ai.Os
   pwd
   git status --short --branch
   git branch --show-current
   git remote -v

2. Confirm current branch is main or a clean review branch created for this dry-run review. If the repo has unrelated dirty files, stop and report.

3. Read:
   AGENTS.md
   Reports/pr_backlog_reconciliation/open_pr_backlog_after_570_reconciliation.md
   Reports/pr_backlog_reconciliation/open_pr_backlog_after_570_reconciliation.json

cleanup review:
1. Prepare an exact close-review list from the reconciliation report:
   - #554
   - #550
   - #521
   - #511
   - #504
   - #502
   - #469
   - #468
   - #466
   - #451
   - #449
   - #295
   - #294
   - #274
   - #267
   - #243
   - #236

2. Prepare an exact keep/review list:
   - #533
   - #528

3. Prepare an exact Dependabot list for a separate dependency lane:
   - #445
   - #444
   - #359
   - #358
   - #357
   - #251
   - #249

4. Prepare a separate non-main-base note for #301. Do not include #301 in a main-base close or merge batch.

5. Mark high-risk PRs for human review before any mutation:
   - #550
   - #437
   - #436
   - #300
   - #301
   - #462
   - #451
   - #449
   - #295
   - #267

6. Do not recommend any blind merge. Any merge target must be separately reviewed against current main with file-level diff evidence and explicit Human Owner approval.

report output:
Create or refresh only this report:
- Reports/pr_backlog_reconciliation/open_pr_backlog_cleanup_review_after_570.md

The report must include:
- close-review list with reason.
- keep/review list with reason.
- Dependabot lane list.
- non-main-base #301 note.
- high-risk warning.
- explicit statement that no PR was closed, merged, edited, or deleted.
- exact next packet recommendation for a future human-approved mutation pass, if Anthony chooses to close the close-review list.

validation:
Run the validator chain exactly. Report skipped steps with reason.

final report format:
SUMMARY:
WHAT WAS REVIEWED:
CLOSE-REVIEW LIST:
KEEP / REVIEW LIST:
DEPENDABOT LANE:
NON-MAIN-BASE:
HIGH-RISK WARNING:
VALIDATION:
SAFE NEXT COMMAND:
STATUS: DRY_RUN COMPLETE, NO FILES CHANGED
