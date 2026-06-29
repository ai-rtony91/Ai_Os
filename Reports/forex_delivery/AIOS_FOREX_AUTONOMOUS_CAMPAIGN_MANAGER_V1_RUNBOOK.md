# AIOS Forex Autonomous Campaign Manager V1 Runbook

## 1) Run in DryRun
Run from repo root:
```powershell
pwsh -File scripts/forex_delivery/Invoke-ForexAutonomousCampaignManager.V1.ps1 -DryRun -NoPublish -MaxCycles 3 -MaxMinutes 30
```

Expected output:
- `FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_STARTED`
- `SELECTED_STAGE:<stage>`
- `NEXT_ACTION:<action>`
- `CHECKPOINT_PATH:Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md`
- `NEXT_CODEX_PROMPT_PATH:Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_NEXT_CODEX_PROMPT_V1.md`
- `FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_STOP_REASON:<reason>`

## 2) Run normal repo-safe mode
```powershell
pwsh -File scripts/forex_delivery/Invoke-ForexAutonomousCampaignManager.V1.ps1 -MaxCycles 12 -MaxMinutes 480
```
The run should not perform branch writes, commits, pushes, PR creation, or merges.
It only updates:
- `AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_STATE.json`
- `AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md`
- `AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_NEXT_CODEX_PROMPT_V1.md`

## 3) Read checkpoint
Open `Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md` and verify:
- Campaign id and selected stage
- Status and next action
- Blockers and allowed paths
- Validators and safety boundary

## 4) Read next prompt
Open `Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_NEXT_CODEX_PROMPT_V1.md` and verify:
- `CODEX-ONLY PROMPT`
- `AI_OS EXECUTION TOKEN`
- `AI_OS BOOTSTRAP REQUIRED`
- identity markers
- `ALLOWED PATHS`, `FORBIDDEN PATHS`, `APPROVAL AUTHORITY`, `VALIDATOR CHAIN`, `STOP POINT`, `FINAL REPORT FORMAT`

## 5) Recover from Git permission blocker
If `git add` or metadata writes fail with `Permission denied`:
- stop
- retry command as an owned-shell with write access to `.git`
- do not retry blind
- continue only after `git status --short --branch` is successful

## 6) Recover from PR check failure
If checks fail:
- keep the branch local
- preserve all new files
- update `AIOS_FOREX_AUTONOMY_FINISHER_V4_REPORT.md` with failure evidence
- fix blockers
- rerun manager after fix

## 7) Continue after reboot
- confirm current branch with `git branch --show-current`
- confirm campaign state with `Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_STATE.json`
- rerun the dry-run command and continue with the next output stage
- never touch files outside allowed paths

## 8) Human-gated items
- Any PR merge decision
- final owner review approval
- any live-broker proof-of-capability transition
