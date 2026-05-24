# AIOS Worktree Agent Packet Template

Use this template to assign one Codex worker to one existing AI_OS worktree. Replace bracketed values before use.

````text
🧩 CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: [TOKEN]

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. docs/governance/AI_OS_REPO_MEMORY.md
3. assigned lane instructions
4. operator instruction

If unavailable, stop and report missing AI_OS context.

Worker:
[agent1 | agent2 | agent3 | agent4]

Lane:
[lane name]

Repo:
[exact absolute repo path]

Worktree:
[exact absolute worktree path]

Branch:
[expected branch name]

Valid active worktrees:
- C:\Dev\Ai.Os-agent1-registry-dryrun
- C:\Dev\Ai.Os-agent2-registry-blocked
- C:\Dev\Ai.Os-agent3-registry-approval
- C:\Dev\Ai.Os-agent4-registry-cleanup-report

Allowed write boundary:
[absolute allowed path or read-only]

Blocked paths:
[absolute or repo-relative blocked paths]

Mission:
[one scoped mission]

Rules:
- Use the assigned active worktree path only.
- Do not use C:\Dev\.workers paths.
- Do not trust Get-Location inside Codex as proof of the active worktree.
- Use git -C <exact absolute worktree path> for branch, status, remote, and diff checks.
- Use absolute file paths for reads and writes.
- Use PowerShell Select-String for text search; do not use Bash grep.
- Promotion is PR-based only.
- Do not merge directly to main.
- Do not push directly to main.
- Do not open Vim, Nano, Notepad, or any editor.
- Do not auto-launch Codex, worker loops, daemons, startup tasks, terminals, or launchers unless separately approved.
- If the target folder exists but is not listed by git worktree list --porcelain, report a stale leftover folder and stop.
- If a folder is locked after worktree cleanup, close processes holding it, run git worktree prune once, and request explicit cleanup approval before deletion.
- If pre-flight fails, stop and report.
- Do not self-repair failed pre-flight state.

Required pre-flight:
```powershell
git -C "[absolute worktree path]" status --short --branch
git -C "[absolute worktree path]" branch --show-current
git -C "[absolute worktree path]" remote -v
git -C "[repo path]" worktree list --porcelain
Test-Path "[absolute allowed path]"
Select-String -Path "[absolute file path]" -Pattern "[pattern]" -SimpleMatch
```

Validation:
[validation commands, using git -C and absolute paths]

Final report:
1. Worktree used
2. Branch confirmed
3. Files created
4. Files updated
5. Validation result
6. Git status
7. Commit status
8. Push status
9. Stop point

Stop condition:
[exact stop point]
````
