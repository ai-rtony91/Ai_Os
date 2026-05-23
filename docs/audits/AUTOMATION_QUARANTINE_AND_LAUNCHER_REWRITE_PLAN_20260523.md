# Automation Quarantine and Launcher Rewrite Plan

Date: 2026-05-23
Lane: Automation Quarantine and Launcher Rewrite Planning
Scope: documentation-only quarantine and future rewrite plan

## Quarantine Decision

The reviewed untracked automation scripts are quarantined as untrusted local backlog until a future approved APPLY lane rewrites, archives, or deletes them.

No automation script was executed during the safety review or during this documentation lane.

These files must not be treated as active AI_OS authority:

- `automation/Ai_Os_Reorganize.ps1`
- `automation/Create-MainControlShortcut.ps1`
- `automation/RUN_SYSTEM_WIZARD_V0_1.ps1`
- `automation/start_ai_os.ps1`
- `automation/orchestration/AI_OS_MAIN_CONTROL.ps1`
- `automation/legacy/`

## Scripts That Must Not Run

### `automation/Ai_Os_Reorganize.ps1`

Decision: do not run.

Reason:
- Performs broad OneDrive reorganization.
- Uses filesystem mutation commands including move, rename, create, remove, and log writes.
- Contains stale OneDrive-era project assumptions.
- Recommends `git add .`, which conflicts with current AI_OS governance.

Recommended later action: archive or replace with a DRY_RUN-only inventory planner. Do not repair in place unless explicitly approved.

### `automation/Create-MainControlShortcut.ps1`

Decision: do not run.

Reason:
- Copies scripts into user-local locations.
- Removes and recreates a desktop shortcut.
- Uses stale OneDrive and `AIOS_CLAUDE_01` paths.
- Performs APPLY-mode workstation mutation without current AI_OS path validation.

Recommended later action: rewrite as a DRY_RUN-first shortcut installer only after the active launcher target is approved.

### `automation/RUN_SYSTEM_WIZARD_V0_1.ps1`

Decision: do not run.

Reason:
- Points to a stale OneDrive wizard path.
- Executes a Python file outside the current active repo authority.
- Does not establish current AI_OS governance context before launching.

Recommended later action: archive unless a current system wizard is separately validated and promoted.

### `automation/start_ai_os.ps1`

Decision: do not run.

Reason:
- Launches Explorer, PowerShell, and VS Code windows rooted in stale OneDrive paths.
- Can steer the operator into the wrong working location.
- Has no current repo path validation or stop rule.

Recommended later action: rewrite only if AI_OS still needs a workstation launcher.

## Legacy / Reference Classification

`automation/legacy/` is reference-only.

It contains historical stage scripts for inventory, migration, approval packets, Codex handoff, and cleanup planning. Pattern evidence from the safety review found repeated OneDrive project roots plus mutation-capable commands such as directory creation, content writes, copies, moves, and Explorer launches.

No script under `automation/legacy/` should be promoted, run, or used as active authority until it is individually reviewed.

Recommended later action:
- Keep as legacy/reference until cleanup classification is complete.
- Archive scripts that only preserve historical migration context.
- Promote only narrowly scoped scripts that are rewritten for `C:\Dev\Ai.Os`, DRY_RUN-first behavior, and current AI_OS governance.

## Future Launcher Candidate

`automation/orchestration/AI_OS_MAIN_CONTROL.ps1` is the best future launcher candidate, but the current file must not run as-is.

Reason:
- It has the right conceptual role: an operator-facing main control launcher.
- Its observed behavior is closer to launcher/status output than destructive automation.
- It still targets stale `AIOS_CLAUDE_01` path authority.

Future launcher work must be a rewrite, not a quick path patch.

## Required Launcher Rewrite Guardrails

Any future launcher rewrite must:

1. Treat `C:\Dev\Ai.Os` as the active local repo folder.
2. Stop if launched from a known legacy inactive path.
3. Read or point the operator to `AGENTS.md` and `docs/governance/AI_OS_REPO_MEMORY.md`.
4. Default to read-only behavior.
5. Avoid `git add`, `git commit`, `git push`, branch switching, merge, rebase, cleanup, delete, move, or rename actions.
6. Clearly separate launcher/status mode from any future APPLY-capable mode.
7. Require explicit operator approval before any workstation mutation.
8. Use `Test-Path` for required paths before launch actions.
9. Refuse stale OneDrive, `AIOS_CLAUDE_01`, `AI_OS_V2_OLD_DO_NOT_USE`, or `ai-rtony91_Ai_Os_CLEAN` active-work paths.
10. Produce concise operator-visible output with the current path, intended action, expected result, and stop condition.

## Missing Safety Controls

The reviewed scripts are missing one or more of these controls:

- DRY_RUN default behavior.
- `WhatIf` or `ShouldProcess` protections.
- Current repo path validation.
- Stale-path refusal.
- Explicit allowed write boundary.
- No-mutation defaults.
- No broad recursion without an reviewed manifest.
- No shortcut or profile edits without separate approval.
- No script chaining without an allowlist.
- No `git add .` guidance.

## Recommended Next APPLY Lane

Recommended lane: `Automation Launcher Rewrite - DRY_RUN First`

Allowed write boundary for that future lane should be limited to one selected launcher file and any existing directly related launcher documentation. The first rewrite target should be `automation/orchestration/AI_OS_MAIN_CONTROL.ps1` only if the operator approves making it an active launcher candidate.

Future APPLY stop condition:
- Stop after producing a read-only launcher that validates `C:\Dev\Ai.Os`, refuses stale paths, prints safe next actions, and performs no repo or filesystem mutation.

Do not combine launcher rewrite, legacy cleanup, shortcut creation, and script deletion in the same lane.
