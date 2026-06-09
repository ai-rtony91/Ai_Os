# AI_OS PR Lane Runner

## Purpose

Define the PR Lane Runner as the standard way to move approved AI_OS work into protected main.

This is a design and workflow specification. It does not create executable automation, does not stage files, does not commit, does not push, does not create pull requests, and does not merge pull requests.

## Operator Goal

Reduce operator burden by replacing manual direct pushes and browser PR creation with a governed CLI PR lane.

The runner is intended to reduce repeated command approvals, manual branch thinking, manual push decisions, manual PR creation steps, manual check watching, and manual merge/sync steps while preserving operator authority and protected-main safety.

For this PR lane, confirmed-safe DRY_RUN/report commands can continue by default with `Option 2` (the next safe governed step). Protected actions (`merge`, `commit`, `push`, worker launch, scheduler, Night Supervisor, SOS/ADB, notifications, broker/OANDA/webhook, or live trading) remain explicit approval gates.

## Scope

This workflow applies globally across AI_OS lanes, branches, worktrees, Codex sessions, and future Claude review lanes when they are operating inside AI_OS governance.

## Non-Goals

The PR Lane Runner must not:

- bypass protected main
- force push
- disable rulesets
- skip CI/validate
- stage unapproved backlog
- run unreviewed scripts
- merge failing checks
- silently resolve conflicts
- create broad or duplicate files
- mutate outside approved lane scope

## Required Authority Stack

Every PR lane must load:

1. `AGENTS.md`
2. `docs/governance/AI_OS_REPO_MEMORY.md`
3. `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`
4. `docs/workflows/AI_OS_PR_LANE_RUNNER.md`
5. assigned lane prompt
6. operator instruction

## Standard PR Lane Flow

### 1. Preflight

- Confirm correct repo path: `C:\Dev\Ai.Os`.
- Confirm remote: `https://github.com/ai-rtony91/Ai_Os.git`.
- Confirm base branch: `main`.
- Confirm GitHub CLI is authenticated.
- Confirm `main` is synced before branch creation.
- For worktree lanes, confirm the exact worktree with `git -C <absolute-worktree-path>` checks for status, branch, and remote.
- Do not use `Get-Location` alone as proof of the active repo or worktree.
- Do not re-check known state unnecessarily if `docs/governance/AI_OS_REPO_MEMORY.md` already covers it.

### 2. Branch

- Create a lane branch using naming pattern: `lane/<short-purpose>`.
- Never work directly on `main` for protected changes.
- Worker lanes must use a non-main branch. `main` is reserved for Main Control/manual control only.
- Before assigning a worker lane, reject duplicate lane IDs, branches, worktree paths, and window/tab titles.
- If a target folder exists but is not listed by `git worktree list --porcelain`, treat it as a stale leftover folder and stop; do not delete it from the PR lane.

### 3. Stage

- Stage only explicitly approved files.
- Never use `git add .`.
- Never stage untracked backlog unless explicitly assigned.

### 4. Commit

- Use `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`.
- Commit only if the gate returns `SAFE_TO_COMMIT`.
- Require a commit message.
- Require cached diff file list check.
- Require cached diff review.
- Commit only approved scope.

### 5. Push Lane Branch

- Push only the lane branch.
- Do not push directly to `main`.
- Use:

```powershell
git push -u origin <lane-branch>
```

### 6. Create PR

- Use GitHub CLI:

```powershell
gh pr create --base main --head <lane-branch> --title "<title>" --body "<body>"
```

- PR title must match the lane purpose.
- PR body must include:
  - mission
  - files changed
  - validation expected
  - risk notes
  - operator intent

### 7. Watch Checks

- Use:

```powershell
gh pr checks --watch
```

- Treat CI/validate as the inspection gate.
- Do not merge while checks are pending, failing, or missing.

### 8. Merge

- Merge only if checks pass.
- Use:

```powershell
gh pr merge --squash --delete-branch
```

- Do not merge if validate fails.
- Do not override rulesets.
- Do not bypass GitHub protection.

### 9. Sync Local Main

- After merge:

```powershell
git fetch origin
git switch main
git reset --hard origin/main
git status --short --branch
```

- Untracked backlog may remain and must be reported as known local backlog, not as a new emergency.

## No-Editor Git Safety Rule

- No Vim.
- No Nano.
- No Notepad.
- No plain `git pull`.
- No plain `git merge` if it can open an editor.
- Use `gh pr merge --squash --delete-branch` for approved PRs.
- After each PR merge, sync local main with:

```powershell
git fetch origin
git switch main
git reset --hard origin/main
git status --short --branch
```

- If an editor opens unexpectedly, exit with:

```text
Esc
:q!
Enter
```

- Then stop and report the command that opened the editor, repo path, branch, and next safe non-editor command.

### 10. Final Report

The final report must include:

- PR number / URL
- branch used
- commit hash before PR
- merge result
- CI/validate result
- local main sync result
- known untracked backlog status
- next safe action

## Command Classification

### `AUTO_PROCEED_READ_ONLY`

Future tooling may auto-proceed with these commands when they are inside the approved scope and needed for the current lane:

- `git diff -- <approved file>`
- `git diff --check -- <approved file>`
- `git diff --cached --name-only`
- `git diff --cached`
- `git status --short --branch` only when state is needed
- `git log -1` only when commit hash is not already known
- `gh pr checks --watch` after PR exists
- `Get-Content`, `rg`, and `Test-Path` inside approved scope

### `HUMAN_APPROVAL_REQUIRED`

These commands require human authorization:

- `git add <approved files>`
- `git commit -m "<message>"`
- `git push -u origin <lane-branch>`
- `gh pr create`
- `gh pr merge --squash --delete-branch`
- `git reset --hard origin/main` after PR merge
- any write, move, copy, delete, branch deletion, script run, or automation launcher

### `BLOCKED`

These commands are blocked:

- `git add .`
- `git push origin main` for protected work
- `git clean`
- `git reset` before merge/sync authorization
- force push
- running unreviewed `.ps1` files
- staging broad untracked backlog
- merging failed checks
- bypassing validate
- creating duplicate workflow files
- continuing placeholder tasks

## Safety Gates

The runner must stop when:

- cached diff includes unapproved files
- branch is wrong
- remote is wrong
- validate fails
- PR cannot be created
- merge conflicts appear
- GitHub blocks the action
- email privacy blocks commit or push
- ruleset violations appear
- Codex is uncertain

## Conflict Policy

If conflicts occur:

- stop
- report exact conflict
- do not auto-resolve unless separately authorized
- do not continue to the next lane

## Email Identity Policy

Git commits should use GitHub no-reply email if GitHub privacy blocks business or personal email.

Business email may remain business identity, but commit author email must be GitHub-accepted.

If `GH007` appears, stop and repair author email before retrying.

## Integration With Roles

- ChatGPT: orchestrator / mission commander support
- Codex: implementation and PR lane runner
- Claude: isolated instructor-inspector / reviewer / CTO-style advisor
- Operator: final authority

One AI role, one purpose, one output, one stop point.

## Future Implementation Path

The next APPLY lane should create a local helper only after this spec is committed:

```text
automation/orchestration/Invoke-AIOSPrLaneRunner.ps1
```

The helper must start as DRY_RUN/report-only before APPLY behavior.

Do not create that script in this lane.
