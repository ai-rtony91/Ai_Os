# AI_OS PR Handoff Reporter

## Purpose

Define the PR Handoff Reporter as the standard AI_OS method for transferring PR lane results without screenshots.

The reporter produces structured handoff packets that can be pasted into ChatGPT, Codex, Claude, daily reports, logs, or future dashboards.

## Problem Statement

Screenshots are operator-friendly but poor worker handoff artifacts. AI_OS needs structured text that can be copied, parsed, logged, reviewed, handed off, and reused.

Terminal transcripts are also noisy. They often mix useful state, old output, command prompts, warnings, and local backlog details. A PR handoff packet reduces that noise to a stable record.

## Scope

This workflow applies after PR creation, check watching, merge, branch cleanup, and local main sync.

It is a documentation and reporting standard. It does not create executable automation in this lane.

## Non-Goals

The PR Handoff Reporter must not:

- bypass protected main
- replace CI/validate
- merge PRs
- push branches
- stage files
- commit files
- delete branches by itself in this design lane
- touch known untracked backlog
- rely on screenshots as the primary record
- create executable automation in this lane

## Required Data Fields

The handoff packet must include:

- PR number
- PR URL
- PR title
- base branch
- head branch
- merge state
- mergeable state if available
- PR state
- check names
- check conclusions
- check status
- workflow name
- merge result
- local branch cleanup result
- remote branch cleanup result
- local current branch
- local main sync status
- known untracked backlog status
- next safe action
- timestamp if available

## Required CLI Sources

Use:

```powershell
gh pr view <number> --json number,title,state,mergeStateStatus,mergeable,statusCheckRollup,headRefName,baseRefName,url
git status --short --branch
git branch --show-current
```

Optional future source:

```powershell
git log -1 --oneline
```

The reporter should not run mutation commands. It should only collect state and format the result.

## Output Format 1: Markdown Handoff

Use this human-readable format for ChatGPT, Claude, Codex, daily reports, or operator review:

```markdown
# AI_OS PR Handoff

## PR
- Number:
- URL:
- Title:
- Base branch:
- Head branch:
- PR state:
- Merge state:
- Mergeable:

## Checks
- Workflow:
- Check name:
- Status:
- Conclusion:

## Merge And Cleanup
- Merge result:
- Local branch cleanup:
- Remote branch cleanup:
- Local current branch:
- Local main sync:
- Known untracked backlog:

## Next Safe Action
-

## Timestamp
-
```

## Output Format 2: JSON Handoff

Use this machine-readable format for future dashboards, logs, automation, or structured worker handoff:

```json
{
  "pr": {
    "number": null,
    "url": "",
    "title": "",
    "base_branch": "",
    "head_branch": "",
    "state": "",
    "merge_state": "",
    "mergeable": ""
  },
  "checks": [
    {
      "workflow": "",
      "name": "",
      "status": "",
      "conclusion": ""
    }
  ],
  "merge_and_cleanup": {
    "merge_result": "",
    "local_branch_cleanup": "",
    "remote_branch_cleanup": "",
    "local_current_branch": "",
    "local_main_sync_status": "",
    "known_untracked_backlog_status": ""
  },
  "next_safe_action": "",
  "timestamp": ""
}
```

## Example Markdown Handoff

```markdown
# AI_OS PR Handoff

## PR
- Number: 193
- URL: https://github.com/ai-rtony91/Ai_Os/pull/193
- Title: Add AI_OS execution token rule
- Base branch: main
- Head branch: lane/execution-token-rule
- PR state: merged
- Merge state: clean
- Mergeable: mergeable

## Checks
- Workflow: validate
- Check name: validate
- Status: completed
- Conclusion: success

## Merge And Cleanup
- Merge result: squashed and merged
- Local branch cleanup: completed
- Remote branch cleanup: completed
- Local current branch: main
- Local main sync: synced to origin/main at fc026a3
- Known untracked backlog: remains local; do not stage or treat as a new emergency

## Next Safe Action
- Continue with the next assigned AI_OS lane.

## Timestamp
- 2026-05-23
```

## Example JSON Handoff

```json
{
  "pr": {
    "number": 193,
    "url": "https://github.com/ai-rtony91/Ai_Os/pull/193",
    "title": "Add AI_OS execution token rule",
    "base_branch": "main",
    "head_branch": "lane/execution-token-rule",
    "state": "merged",
    "merge_state": "clean",
    "mergeable": "mergeable"
  },
  "checks": [
    {
      "workflow": "validate",
      "name": "validate",
      "status": "completed",
      "conclusion": "success"
    }
  ],
  "merge_and_cleanup": {
    "merge_result": "squashed and merged",
    "local_branch_cleanup": "completed",
    "remote_branch_cleanup": "completed",
    "local_current_branch": "main",
    "local_main_sync_status": "synced to origin/main at fc026a3",
    "known_untracked_backlog_status": "remains local; do not stage or treat as a new emergency"
  },
  "next_safe_action": "Continue with the next assigned AI_OS lane.",
  "timestamp": "2026-05-23"
}
```

## Screenshot Rule

Screenshots are optional operator evidence only.

Screenshots are not the primary AI_OS worker handoff format.

AI_OS workers should prefer structured PR handoff packets over screenshots for workflow state transfer.

Use screenshots only when UI state matters, text is unavailable, or the operator explicitly wants human visual evidence.

## Integration

### `docs/workflows/AI_OS_PR_LANE_RUNNER.md`

The PR Lane Runner defines how approved AI_OS work moves through lane branch, PR, validate, merge, and local sync. The PR Handoff Reporter records the result of that flow after the runner completes.

### `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`

The Commit/Push Gate controls whether staging, committing, or pushing is safe. The PR Handoff Reporter does not bypass the gate and does not authorize mutation. It reports completed PR lane state.

### Claude Isolated Instructor-Inspector Role

Claude may review PR handoff packets as structured evidence, critique risk, identify missing state, and recommend safer next actions without taking over execution.

### Codex Implementation Role

Codex may generate PR handoff packets when assigned a reporting or PR lane workflow. Codex must not mutate repo state while producing a handoff unless separately assigned an APPLY lane with an approved write boundary.

### ChatGPT Orchestration Role

ChatGPT may use PR handoff packets to maintain continuity, guide the operator, create the next Codex prompt, or summarize workflow state without relying on screenshots.

### AI_OS Execution Token Rule

A PR handoff packet is evidence, not an executable task. Codex must not execute a handoff packet unless it is wrapped in a complete tokenized AI_OS work packet or the operator explicitly says to execute it.

## Future Implementation Path

Recommend a later APPLY lane:

```text
automation/orchestration/Export-AIOSPrHandoff.ps1
```

The future script must start as DRY_RUN/report-only.

It must not mutate repo state.

It must only collect state and emit markdown/JSON handoff output.

Do not create that script in this lane.
