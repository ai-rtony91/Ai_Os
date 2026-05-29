# AI_OS Terminal Workstations

Phase 16.21-25 defines a practical three-lane terminal setup.

Use the workstation and deck scripts directly. The older `Start-AiOsOneCommandLauncher.ps1` reference is not active in this folder.

Preview first:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsWorkstation.ps1
```

Static UI shell preview:

```text
automation/orchestration/terminal_workstations/AIOS_TERMINAL_CONTROL_SURFACE_PREVIEW.html
```

This HTML file is a static preview only. It does not replace Windows Terminal, does not launch workers, and does not change runtime behavior. It is the design target for future terminal workstation UI: translucent panels, side rails, worker cards, status badges, progress bars, command input strip, and customization controls.

Real worker runtime remains PowerShell/terminal-based for now.

## Terminal Control Surface v3

The v3 preview is static only. It does not change Windows Terminal settings, edit PowerShell profiles, launch workers, or replace the existing terminal runtime.

It shows the desired app-like terminal direction: a dark AI_OS shell with translucent code cards, operation deck rail, OCC worker rail, validation and risk panels, lifecycle rows, progress badges, command input strip, visible operator status, and a right-side customization studio.

Future versions may connect to worker status JSON after approval. The customization target includes panel color, blur, radius, size, placement, badges, and layout density.

Open persistent deck windows manually as needed:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsCommandDeck.ps1
powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsBuildEngine.ps1
powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsValidationDeck.ps1
```

`Start-AiOsWorkstation.ps1` remains a single-window status display.

## Lanes

- `Ai_Os COMMAND DECK`: Magenta label. Git, GitHub CLI, issues, PRs, commits, merges.
- `Ai_Os BUILD ENGINE`: Green label. Codex work lane. Codex launch is manual only.
- `Ai_Os VALIDATION DECK`: Cyan label. PowerShell status checks, validators, queue checks, repo checks.

## Visible Persistent Windows

Persistent deck scripts print their banner, show a final visible state, and wait for the operator to press Enter before closing. This prevents visible worker/deck windows from flashing open and disappearing.

Default persistent deck state is `IDLE`.

Persistent decks stay open all day. Temporary OCC workers close after completed APPLY/commit workflow or park on BLOCKED.

Temporary OCC workers remain packet-scoped and should stay open for one assigned task or project phase. The same visible OCC worker window should cover APPLY, validation, commit, push, PR/merge if used, and the final sync/status report for that task.

Temporary OCC windows may stay visible while `WORKING`. They should show `COMPLETE` only after the final APPLY/commit/push or merge/sync report is done, then close once or allow the operator to close. Failed or blocked workers should park on `BLOCKED` for operator review.

Do not open and close the same worker every 5, 10, or 20 minutes for the same active task. Prefer reusing the same worker window and lane until that task reaches final `COMPLETE` or `BLOCKED`.

Anti-pileup rule: future launcher logic should cap the maximum visible temporary workers. Do not spawn unlimited new windows. Completed temporary worker windows should be closed or explicitly dismissed after the final report is captured.

Allowed visible states:

- `IDLE`
- `WORKING`
- `COMPLETE`
- `BLOCKED`
- `CLOSED`

Codex is not launched automatically. Manual Codex launch prevents the wrong branch, packet, or prompt from starting work too early.

PowerToys/FancyZones window placement remains manual.

Branch changes, commits, pushes, merges, issue creation, and PR creation remain operator-approved.

The exact next safe action is printed before the operator starts work.

## Launcher Rules

Each launcher:

- sets repo path to `C:\Dev\Ai.Os`
- sets a clean window title
- prints a clear banner
- prints copy/paste markers:

```text
=== COPY START ===
Paste terminal output between COPY START and COPY END when sending to ChatGPT.
=== COPY END ===
```

- shows its role
- shows allowed actions
- shows blocked actions

## Color Rules

- COMMAND DECK: one long Magenta top border, two long Magenta bottom borders, and printed title `Ai_Os COMMAND DECK` with an emoji.
- BUILD ENGINE: one long Green top border, two long Green bottom borders, and printed title `Ai_Os BUILD ENGINE` with an emoji.
- VALIDATION DECK: one long Cyan top border, two long Cyan bottom borders, and printed title `Ai_Os VALIDATION DECK` with an emoji.
- WORKSTATION MASTER: mixed Magenta, Green, Cyan, Yellow, and Red sections.
- COPY START / COPY END: one Yellow line above, one Yellow line below, and Yellow marker text.
- Blocked actions: Red
- Allowed actions: Green
- Repo, branch, and status: Cyan or Gray
- Each deck prints: `LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW.`

## Blocked Actions

- no WScript.Shell
- no SendKeys
- no ALT+SPACE
- no Num Lock changes
- no Windows Terminal settings edits
- no Codex auto-launch
- no extra windows
- no startup tasks
- no scheduled tasks
- no dashboard edits
- no broker, OANDA, API keys, webhooks, real orders, or live trading
- no install
- no commit
- no push
