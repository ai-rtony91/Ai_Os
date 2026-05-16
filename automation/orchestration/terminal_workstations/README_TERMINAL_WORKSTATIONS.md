# AI_OS Terminal Workstations

Phase 16.21-25 defines a practical three-lane terminal setup.

Use `Start-AiOsWorkstation.ps1` first. It prints the startup banner, repo path, branch, git status, latest commits, open issues, open PRs, lane map, and next safe action.

## Lanes

- `AI_OS COMMAND DECK`: Magenta label. Git, GitHub CLI, issues, PRs, commits, merges.
- `AI_OS BUILD ENGINE`: Green label. Codex work lane. Codex launch is manual only.
- `AI_OS VALIDATION DECK`: Cyan label. PowerShell status checks, validators, queue checks, repo checks.

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

- COMMAND DECK: Magenta border and title
- BUILD ENGINE: Green border and title
- VALIDATION DECK: Cyan border and title
- COPY START / COPY END: Yellow border and marker text
- Blocked actions: Red
- Allowed actions: Green
- Repo, branch, and status: Cyan or Gray

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
