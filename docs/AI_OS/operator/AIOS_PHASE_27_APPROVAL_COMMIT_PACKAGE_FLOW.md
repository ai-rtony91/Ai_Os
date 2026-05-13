# AI_OS Phase 27 Approval Commit Package Flow

## 1. Purpose

Phase 27 defines the human approval and exact-file commit package flow for AI_OS.

The goal is to make approved package commits safer by listing exact files, exact validation commands, and exact operator checkpoints.

This document does not stage, commit, push, merge, reset, or clean anything.

## 2. Approval Chain

Required approval chain:

1. DRY_RUN report reviewed
2. APPLY approved for exact file list
3. APPLY completed
4. validators pass
5. git diff --check passes
6. operator reviews changed files
7. commit package generated
8. operator stages exact files only
9. operator reviews git diff --cached
10. operator commits
11. operator pushes
12. operator verifies clean status

Any missing step blocks commit or push.

## 3. Commit Package Rules

A commit package must include:

- exact approved files
- blocked files
- validation commands
- exact `git add -- "file"` commands
- forbidden commands
- commit message draft
- push command draft
- clean status command
- operator checklist
- next safe action

The package is evidence and guidance only.

## 4. Exact-File Staging

Only exact-file staging is allowed.

Example:

```powershell
git add -- "docs/AI_OS/operator/AIOS_PHASE_27_APPROVAL_COMMIT_PACKAGE_FLOW.md"
```

Each approved file gets its own exact command.

## 5. Forbidden Staging

Forbidden:

```powershell
git add .
git add -A
git add *
git add docs/AI_OS/operator/*
```

Do not stage unapproved files.

## 6. Validation Before Commit

Before commit review, run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
```

Validation failure blocks commit review.

## 7. Commit Message Draft

Commit message is a draft until the operator approves.

Recommended style:

```text
docs: add AI_OS operator automation foundation plans
```

## 8. Push Approval

Push requires separate approval after commit.

No push may occur just because commit succeeded.

## 9. Clean Status Verification

After commit or push, verify:

```powershell
git status --short --branch
```

The operator decides whether remaining changes are expected.

## 10. Failure Handling

If validation fails:

- stop
- report failure
- do not stage
- do not commit
- do not push
- ask for operator recovery decision

Destructive git commands require explicit operator approval.

## 11. Example Operator Flow

1. Review DRY_RUN.
2. Approve APPLY for exact files.
3. Run APPLY.
4. Run validation.
5. Review changed files.
6. Generate commit package.
7. Run exact `git add -- "file"` commands.
8. Run `git diff --cached`.
9. Commit only if approved.
10. Push only if approved.
11. Verify status.

## 12. What This Does Not Automate

This does not automate:

- `git add`
- commit
- push
- merge
- rollback
- reset
- clean
- dashboard edits
- worker launch
- APPLY approval

Forbidden commands include:

- `git add .`
- `git add -A`
- wildcard staging
- staging unapproved files
- automatic commit
- automatic push
- destructive git commands
- reset/clean without explicit operator approval
