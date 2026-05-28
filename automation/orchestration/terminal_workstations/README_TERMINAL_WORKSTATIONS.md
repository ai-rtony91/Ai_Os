# AI_OS Terminal Workstations

Phase 16.21-25 defines a practical three-lane terminal setup.

Use the workstation and deck scripts directly. The older `Start-AiOsOneCommandLauncher.ps1` reference is not active in this folder.

Preview first:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsWorkstation.ps1
```

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

Persistent decks stay open. Temporary OCC workers close after completed APPLY/commit workflow or park on BLOCKED.

Temporary OCC workers remain packet-scoped. Temporary OCC windows may stay visible while `WORKING`, should show `COMPLETE` after APPLY plus commit/push reporting, then close or allow operator close. Failed or blocked workers should park on `BLOCKED`.

Anti-pileup rule: do not allow unlimited stacked worker windows. Completed temporary worker windows should be closed or explicitly dismissed after the report is captured.

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
