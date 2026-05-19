# AI_OS Compliance Checkers

This folder contains DRY_RUN/read-only compliance checkers for AI_OS approval, commit, and push safety review.

These checkers are read-only. They do not approve work, apply changes, stage files, commit, push, release locks, execute webhooks, or modify dispatcher runtime.

## General Compliance Checker

`Test-AiOsCompliance.DRY_RUN.ps1` checks the current repository state before APPLY, commit, or push.

It reports:

- `PASS`, `REVIEW`, or `BLOCKED`
- changed files
- staged files
- untracked files
- blocked files
- warning files
- missing worker report or validation evidence
- next safe action
- `Commit performed: NO`
- `Push performed: NO`

Example command:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/compliance/Test-AiOsCompliance.DRY_RUN.ps1 -Mode DRY_RUN -OutputJson
```

Use `AIOS_COMPLIANCE_CHECK.example.json` as the expected output shape.

## Agent Evidence Checker

`Test-AiOsAgentCompliance.DRY_RUN.ps1` checks whether worker evidence follows `AGENTS.md` rules.

Checks included:

- `git add .` detection
- unauthorized `git push` detection
- missing DRY_RUN/APPLY report structure
- protected path violation visibility
- broker, live trading, API key, secret, webhook, or real order boundary visibility
- missing validation output
- missing next-safe-action output

Example command:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/compliance/Test-AiOsAgentCompliance.DRY_RUN.ps1 -EvidencePath Reports/operator
```

Expected result:

- beginner-readable console summary
- validator-friendly JSON printed to stdout
- `PASS`, `WARN`, or `FAIL` scoring for the agent evidence checker
- `PASS`, `REVIEW`, or `BLOCKED` scoring for the general compliance checker

Safety notes:

- Scan specific worker report folders or files. Do not scan the entire repo unless you are intentionally reviewing historical docs.
- A `WARN` means human review is needed.
- A `FAIL` means approval, commit, and push should stay blocked until corrected.
- A `BLOCKED` result means stop before APPLY, commit, or push.

Next safe action: run the general checker before approval gates, then run the agent evidence checker against worker report paths when worker output is part of the packet.
