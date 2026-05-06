# AIOS Shared Rules

Future AI_OS helper scripts must default to DRY_RUN and must make their mode visible in console output.

Helpers must use exact path scoping. They should operate only on the repo root or paths named in the approved work-order.

Helpers must not perform destructive actions. Do not delete, move, rename, overwrite, clean, reset, or reformat files unless a separate approved APPLY work-order gives exact scope and backup/checkpoint instructions.

Protected root files must not be edited without separate approval and backup/checkpoint planning:

- `README.md`
- `AGENTS.md`
- `RISK_POLICY.md`
- `SOURCE_LOG.md`
- `ERROR_LOG.md`
- `HALLUCINATION_LOG.md`
- `AAR.md`
- `DAILY_REPORT.md`
- `WHITEPAPER.md`

Helpers must not place trades, enable live trading, call broker execution paths, edit broker tokens, or handle credentials, secrets, private keys, recovery keys, or API keys.

Helpers must not perform startup, launcher, browser-launch, app-launch, registry, firewall, VPN, BIOS/UEFI, BitLocker, browser policy, or Task Scheduler actions unless a later work-order explicitly approves the exact action.

Report first, apply later. DRY_RUN output should describe what would happen and what approval is required before anything writes to disk.

Every APPLY-capable workflow needs a human approval gate. The human must approve the exact files, paths, mode, and next safe action.

Git checkpoint rule: do not run `git add`, `git commit`, or `git push` unless the human gives a separate explicit git checkpoint instruction.
