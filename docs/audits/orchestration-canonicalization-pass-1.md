# AI_OS Orchestration Canonicalization Pass 1

Date: 2026-05-19

Mode: practical safe canonicalization. No files moved. No files deleted. No APPLY scripts run. No push. No merge.

## Files Inspected

- `automation/orchestration/orchestration_status_snapshot.example.json`
- `automation/orchestration/orchestration_spine_v1.example.json`
- `automation/orchestration/show-orchestration-status.ps1`
- `automation/orchestration/show-worker-status.ps1`
- `automation/orchestration/show-dispatcher-queue.ps1`
- `automation/orchestration/show-approval-inbox.ps1`
- `automation/orchestration/show-validator-chain.ps1`
- `automation/orchestration/show-commit-package.ps1`
- `automation/orchestration/sync-worker-registry.ps1`
- `automation/orchestration/mission_control/Export-AiOsMissionState.ps1`
- `automation/orchestration/mission_control/aios_mission_state.example.json`
- `automation/orchestration/supervisor/aios_supervisor_state.example.json`
- `automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1`
- `automation/orchestration/terminal_workstations/Start-AiOsTelemetryDeck.ps1`

## Files Changed

- `automation/orchestration/README.md`
- `automation/orchestration/mission_control/Export-AiOsMissionState.ps1`
- `automation/orchestration/mission_control/aios_mission_state.example.json`
- `automation/orchestration/orchestration_spine_v1.example.json`
- `automation/orchestration/orchestration_status_snapshot.example.json`
- `automation/orchestration/show-approval-inbox.ps1`
- `automation/orchestration/show-commit-package.ps1`
- `automation/orchestration/show-dispatcher-queue.ps1`
- `automation/orchestration/show-orchestration-status.ps1`
- `automation/orchestration/show-validator-chain.ps1`
- `automation/orchestration/show-worker-status.ps1`
- `automation/orchestration/supervisor/aios_supervisor_state.example.json`
- `automation/orchestration/sync-worker-registry.ps1`
- `automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1`
- `automation/orchestration/terminal_workstations/Start-AiOsTelemetryDeck.ps1`
- `docs/audits/orchestration-canonicalization-pass-1.md`

## Canonical References Updated

- Worker registry now prefers `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`.
- Queue/work packets now prefer `automation/orchestration/work_packets/`.
- Command queue references now include `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`.
- Approval inbox now prefers `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`.
- Validator chain now prefers `automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json`.
- Validator chain map also preserves `automation/orchestration/validators/VALIDATOR_CHAIN_001.json`.
- Commit package displays now prefer `automation/orchestration/commit_packages/COMMIT_PACKAGE_RECOMMENDATION.example.json`.
- Mission and supervisor state examples now watch canonical queue, approval, and validator paths.
- Operator menu and telemetry deck now point operators to `automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1`.
- `automation/orchestration/README.md` now documents canonical paths and compatibility fallback rules.

## Compatibility Fallbacks Kept

- `packet_queue.example.json` remains a fallback for scripts that need old packet detail fields.
- `worker_registry.example.json` remains a fallback for old registry displays.
- `approval_inbox.example.json` remains a fallback for old packet-list approval displays.
- `validator_chain.example.json` remains a fallback for old validator display shape.
- `commit_package.example.json` remains a fallback for old commit package display shape.
- Root `show-*` scripts remain in place for compatibility.
- No archive move was made.

## Queue Limitation

The canonical queue path is a folder: `automation/orchestration/work_packets/`.

Old queue displays expected one JSON file with a `packets` array. This pass does not fake that data. The display scripts now show folder-state counts for `active`, `blocked`, and `complete`, and keep `packet_queue.example.json` as a legacy detail fallback.

## Old Files Still Referenced

Reference scan still finds old paths in:

- `automation/orchestration/daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1`
- `automation/orchestration/clean_state_gate.ps1`
- `automation/orchestration/orchestration_spine_v1.example.json` as `legacy_source_example`
- `automation/orchestration/orchestration_status_snapshot.example.json` as legacy fallback fields
- `automation/orchestration/show-approval-inbox.ps1` as fallback text/path
- `automation/orchestration/show-commit-package.ps1` as fallback path
- `automation/orchestration/show-dispatcher-queue.ps1` as fallback text/path
- `automation/orchestration/show-validator-chain.ps1` as fallback path/text
- `automation/orchestration/show-worker-status.ps1` as fallback text/path
- `automation/orchestration/sync-worker-registry.ps1` as queue detail fallback and legacy warning text

## Files Safe To Archive In A Later Pass

Only after the remaining references above are updated:

- `automation/orchestration/packet_queue.example.json`
- `automation/orchestration/worker_registry.example.json`
- `automation/orchestration/approval_inbox.example.json`
- `automation/orchestration/validator_chain.example.json`
- `automation/orchestration/commit_package.example.json`
- redundant root `show-*` scripts replaced by the canonical control/status command

## Validation Commands Run

Required:

```powershell
git status --short
git diff --stat
git diff --name-status
git diff --check
rg -n "packet_queue\.example\.json|worker_registry\.example\.json|approval_inbox\.example\.json|validator_chain\.example\.json|commit_package\.example\.json" automation/orchestration
git ls-files | Select-String "\.log$"
git ls-files | Select-String "heartbeat"
```

PowerShell parser check:

```powershell
$files = @(
  "automation/orchestration/show-orchestration-status.ps1",
  "automation/orchestration/show-worker-status.ps1",
  "automation/orchestration/show-dispatcher-queue.ps1",
  "automation/orchestration/show-approval-inbox.ps1",
  "automation/orchestration/show-validator-chain.ps1",
  "automation/orchestration/show-commit-package.ps1"
)
foreach ($file in $files) {
  if (Test-Path $file) {
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($file, [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors.Count -gt 0) {
      Write-Host "PARSER ERRORS: $file"
      $errors
    } else {
      Write-Host "OK: $file"
    }
  }
}
```

## Risks

- Old root examples remain referenced by compatibility fallbacks.
- Some display scripts still rely on legacy packet detail fields because the canonical queue is folder-based.
- This pass improves path preference but does not fully consolidate root `show-*` scripts.
- Runtime execution was not performed; validation was limited to parser and repository checks.

## Next Safe Action

Review this pass. If accepted, run a second pass to update `daily_snapshot`, `clean_state_gate`, and remaining fallback text after deciding whether folder-state queue counts are enough for operator displays.
