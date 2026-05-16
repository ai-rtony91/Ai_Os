# AI_OS Terminal Workstations

Phase 16.21-25 defines a practical three-lane terminal setup.

Use `Start-AiOsWorkstation.ps1` first. It prints the startup banner, repo path, branch, git status, latest commits, open issues, open PRs, lane map, and next safe action.

## Lanes

- `Ai_Os COMMAND DECK`: Magenta label. Git, GitHub CLI, issues, PRs, commits, merges.
- `Ai_Os BUILD ENGINE`: Green label. Codex work lane. Codex launch is manual only.
- `Ai_Os VALIDATION DECK`: Cyan label. PowerShell status checks, validators, queue checks, repo checks.

## Launcher Rules

Each launcher:

- sets repo path to `C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN`
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
