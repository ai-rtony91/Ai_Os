# AIOS Standard Work Cycle

Status: CURRENT
Owner: AIOS Main Control
Purpose: define the official operator work cycle so AIOS connects, verifies, and resumes work instead of recreating or sprawling.

## Rule

AIOS work must follow this cycle unless a human operator explicitly approves an exception.

```text
validate environment
inspect repo state
define exact objective
prepare overwrite-safe commands
verify
commit
push
return to clean state
continue from recorded state
```

This is governance, not automation. It is the checklist every AIOS worker, Codex lane, Claude lane, and operator workflow should respect before changing the repo.

## 1. Validate environment

Confirm the working context before making changes.

Required checks:

- Confirm repo path.
- Confirm current branch.
- Confirm GitHub remote.
- Confirm local working tree state.
- Confirm required scripts/files exist.
- Confirm no protected paths are in scope unless explicitly approved.

Protected examples:

- secrets
- credentials
- broker paths
- live trading paths
- startup tasks
- scheduled tasks
- generated runtime state
- local scratch backups

## 2. Inspect repo state

Before planning edits, inspect the actual repo state.

Minimum state checks:

```powershell
git status --short --branch
git log -1 --oneline
```

Use targeted file inspection instead of guessing. Do not rely on memory when the repo can answer directly.

## 3. Define exact objective

Every task must have one objective.

Good objective:

```text
Connect existing workers mode to the existing Worker Address Book.
```

Bad objective:

```text
Improve workers and add useful features.
```

The objective must identify:

- intended outcome
- allowed files
- blocked files
- validation plan
- stop point

## 4. Prepare overwrite-safe commands

Commands must avoid broad or destructive behavior.

Allowed pattern:

```powershell
git add path/to/approved-file.ps1
```

Blocked pattern:

```powershell
git add .
```

No command should overwrite, delete, move, reset, clean, or replace files unless the operator explicitly approves that exact action.

## 5. Verify

Validation must happen before commit.

Common validation:

```powershell
git diff --check
```

Use targeted validation as appropriate:

- PowerShell parser checks
- JSON parse checks
- DRY_RUN script execution
- mode-specific checks such as `.\aios.ps1 -Mode workers`
- GitHub PR diff review

If validation fails, stop. Do not commit partial or unverified work.

## 6. Commit

Commit only after validation passes.

Rules:

- Commit only approved files.
- Use scoped commit messages.
- Do not include unrelated local files.
- Do not include generated state unless the task explicitly requires it.

Before commit:

```powershell
git diff --cached --name-only
```

The staged file list must match the approved scope.

## 7. Push

Push only the approved branch after the scoped commit is created.

Rules:

- Do not push dirty working trees without reporting them.
- Do not push unrelated changes.
- Open a small PR when appropriate.
- Prefer draft PRs when review is needed before merge.

## 8. Return to clean state

After merge or local cleanup, return Main Control to a clean state.

Required check:

```powershell
git status --short --branch
```

Expected clean main:

```text
## main...origin/main
```

If local prototype files remain, classify them before deleting:

- keep
- move to scratch backup
- delete later after backup
- leave untouched

## 9. Continue from recorded state

AIOS should not restart from memory alone.

Before continuing, inspect:

- current branch
- latest commit
- open work packets
- worker inbox
- Mission Control next action
- proof timestamp
- relevant reports

This is the resume rule: continue from evidence, not guesswork.

## Operating principles

### Connect before creating

Do not create a new mode, script, registry, launcher, or branch when an existing piece can be connected cleanly.

### Build only if value compounds

A change must improve reliability, safety, clarity, resume ability, or operator speed. If it only adds another thing, do not build it.

### DRY_RUN first

Default behavior should be read-only or preview-only. APPLY must be explicit.

### One branch, one purpose

A branch should represent one scoped connection, cleanup, or governance improvement.

### aios.ps1 is Main Control

`aios.ps1` is the official repo operator front door. Other scripts may be helpers, but operator flow should respect Main Control unless a specialist path is explicitly approved.

## Stop condition

Stop and ask for operator review when:

- scope expands
- protected paths are encountered
- validation fails
- unrelated local files appear
- a command would delete, reset, clean, overwrite, or stage broad changes
- a worker proposes a new feature instead of connecting or cleaning existing pieces

## Summary

AIOS should move through work in this order:

```text
safe context -> exact objective -> scoped change -> proof -> clean state -> recorded continuation
```

This cycle is the baseline for future AIOS work.