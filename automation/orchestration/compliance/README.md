# AI_OS Agent Compliance Checker

This folder contains a DRY_RUN scaffold for checking whether worker evidence follows `AGENTS.md` rules.

The checker is read-only. It does not approve work, apply changes, stage files, commit, push, release locks, or modify dispatcher runtime.

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
- `PASS`, `WARN`, or `FAIL` scoring

Safety notes:

- Scan specific worker report folders or files. Do not scan the entire repo unless you are intentionally reviewing historical docs.
- A `WARN` means human review is needed.
- A `FAIL` means approval, commit, and push should stay blocked until corrected.

Next safe action: run this checker against one worker report path before using it in any larger validator chain.
