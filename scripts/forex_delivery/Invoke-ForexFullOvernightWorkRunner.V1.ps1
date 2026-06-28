param(
    [int] $MaxCycles = 12,
    [int] $MaxMinutes = 480,
    [switch] $DryRun,
    [switch] $NoPublish
)

Set-Location -LiteralPath "C:/Dev/Ai.Os"
$ErrorActionPreference = "Stop"

$AllowedPaths = @(
  "automation/forex_engine/forex_full_overnight_work_runner_v1.py"
  "scripts/forex_delivery/run_forex_full_overnight_work_runner_v1.py"
  "scripts/forex_delivery/validate_forex_full_overnight_work_runner_v1.ps1"
  "scripts/forex_delivery/publish_forex_full_overnight_work_runner_v1.ps1"
  "scripts/forex_delivery/Invoke-ForexFullOvernightWorkRunner.V1.ps1"
  "docs/governance/programs/contracts/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.json"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1_REPORT.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_NEXT_ACTION_QUEUE_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_CHECKPOINT_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_ACTIVE_PACKET_QUEUE_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_EXTERNAL_GATE_STOP_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_OWNER_HANDOFF_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_NEXT_CODEX_PROMPT_V1.md"
  "tests/forex_engine/test_forex_full_overnight_work_runner_v1.py"
)

$RunnerScript = "scripts/forex_delivery/run_forex_full_overnight_work_runner_v1.py"
$ValidatorScript = "scripts/forex_delivery/validate_forex_full_overnight_work_runner_v1.ps1"
$PublishScript = "scripts/forex_delivery/publish_forex_full_overnight_work_runner_v1.ps1"
$JsonReportPath = "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.json"
$CheckpointPath = "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_CHECKPOINT_V1.md"
$NextPromptPath = "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_NEXT_CODEX_PROMPT_V1.md"
$RequiredPaths = @(
  "Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_CONTINUATION_LEDGER_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_EXTERNAL_GATE_BRIDGE_REGISTRY_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1.md"
)

$CycleClassifyScript = @'
import json
import sys
from automation.forex_engine.forex_full_overnight_work_runner_v1 import evaluate_forex_full_overnight_work_runner

payload = json.loads(sys.stdin.read() or "{}")
result = evaluate_forex_full_overnight_work_runner(payload)
print(json.dumps(result, sort_keys=True))
'@

Write-Output "FULL_OVERNIGHT_RUNNER_STARTED"

$endTime = (Get-Date).AddMinutes([Math]::Max(1, $MaxMinutes))
for ($cycle = 1; $cycle -le $MaxCycles; $cycle++) {
    Write-Output "CYCLE_$cycle"

    if ((Get-Date) -gt $endTime) {
        Write-Output "FULL_OVERNIGHT_RUNNER_STOP_REASON:MAX_RUNTIME_REACHED"
        break
    }

    $branch = git branch --show-current
    if ($branch -ne "main") {
        throw "RUNNER_REQUIRES_MAIN_BRANCH: $branch"
    }

    git fetch origin

    foreach ($requiredPath in $RequiredPaths) {
        if (-not (Test-Path $requiredPath)) {
            throw "REQUIRED_REPORT_MISSING: $requiredPath"
        }
        Get-Content -Path $requiredPath -Raw | Out-Null
    }

    $statusLines = @()
    foreach ($line in (git status --short)) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        $statusLines += [string]$line
    }

    python $RunnerScript
    if ($LASTEXITCODE -ne 0) {
        throw "RUNNER_EXECUTION_FAILED"
    }

    if (-not (Test-Path $JsonReportPath)) {
        throw "RUNNER_REPORT_MISSING"
    }

    $payload = Get-Content -Path $JsonReportPath -Raw | ConvertFrom-Json
    Write-Output "SELECTED_PACKET:$($payload.next_packet_id)"
    Write-Output "RUNNER_STATUS:$($payload.runner_status)"
    Write-Output "RUNNER_MODE:$($payload.runner_mode)"
    Write-Output "OVERNIGHT_LOOP_STATUS:$($payload.overnight_loop_status)"
    Write-Output "VALIDATION_RESULT:GENERATED"
    Write-Output "CHECKPOINT_PATH:$CheckpointPath"

    if ($payload.external_gate_stop) {
        Write-Output "NEXT_ACTION:EXTERNAL_GATE_STOP"
        Write-Output "PUBLISH_RESULT:NOT_ATTEMPTED"
        Write-Output "FULL_OVERNIGHT_RUNNER_STOP_REASON:EXTERNAL_GATE_STOP"
        break
    }

    if ($statusLines.Count -eq 0) {
        $localHead = (git rev-parse HEAD).Trim()
        $remoteHead = (git rev-parse origin/main).Trim()
        if ($localHead -ne $remoteHead) {
            throw "MAIN_NOT_SYNCED_WITH_ORIGIN_MAIN"
        }

        if (Test-Path $NextPromptPath) {
            $selectedPacketPath = $payload.selected_next_packet.packet_source_path
            $nextPrompt = @"
# AIOS Forex Full Overnight Work Runner Next Codex Prompt V1

## Next Packet
$($payload.next_packet_id)

## Packet Source
$selectedPacketPath

## Run Instruction
Copy this packet in full and execute through owner host loop handoff.
The runner is owner-hosted and remains interactive, so owner confirmation is required.
"@
            Set-Content -Path $NextPromptPath -Value $nextPrompt -Encoding UTF8
        }

        Write-Output "PUBLISH_RESULT:NOT_APPLICABLE"
        Write-Output "NEXT_ACTION:NEXT_CODEX_PROMPT_READY"
        Write-Output "FULL_OVERNIGHT_RUNNER_STOP_REASON:NEXT_CODEX_PROMPT_READY"
        break
    }

    $classifyPayload = @{
        runner_action = "CLASSIFY"
        git_status_lines = $statusLines
        active_allowed_paths = $AllowedPaths
    } | ConvertTo-Json -Depth 10

    $classificationRaw = $classifyPayload | python -c $CycleClassifyScript
    if ($LASTEXITCODE -ne 0) {
        throw "CLASSIFICATION_FAILED"
    }
    $classification = $classificationRaw | ConvertFrom-Json
    if (-not $classification.path_classification.can_continue) {
        Write-Output "VALIDATION_RESULT:BLOCKED_DIRTY_SCOPE"
        Write-Output "PUBLISH_RESULT:NOT_ATTEMPTED"
        Write-Output "NEXT_ACTION:DIRTY_SCOPE_VIOLATION"
        Write-Output "FULL_OVERNIGHT_RUNNER_STOP_REASON:DIRTY_SCOPE_VIOLATION"
        if ($classification.path_classification.blocked_paths) {
            Write-Output "BLOCKED_PATHS:$($classification.path_classification.blocked_paths -join ', ')"
        }
        if ($classification.path_classification.blocked_secret_like_paths) {
            Write-Output "BLOCKED_SECRET_PATHS:$($classification.path_classification.blocked_secret_like_paths -join ', ')"
        }
        break
    }

    Write-Output "VALIDATION_RESULT:RUNNING"
    pwsh -File $ValidatorScript
    if ($LASTEXITCODE -ne 0) {
        Write-Output "PUBLISH_RESULT:NOT_ATTEMPTED"
        Write-Output "NEXT_ACTION:REPAIR_VALIDATION_FAIL"
        Write-Output "FULL_OVERNIGHT_RUNNER_STOP_REASON:VALIDATION_FAILED"
        break
    }

    Write-Output "VALIDATION_RESULT:VALIDATION_PASSED"

    if ($DryRun -or $NoPublish) {
        Write-Output "PUBLISH_RESULT:NOT_ATTEMPTED"
        Write-Output "NEXT_ACTION:VALIDATION_ONLY"
        if ($DryRun) {
            Write-Output "FULL_OVERNIGHT_RUNNER_STOP_REASON:DRYRUN_COMPLETE"
            break
        }
        continue
    }

    Write-Output "NEXT_ACTION:PUBLISHING"
    pwsh -File $PublishScript
    if ($LASTEXITCODE -ne 0) {
        Write-Output "PUBLISH_RESULT:FAILED"
        Write-Output "NEXT_ACTION:REPAIR_PUBLISH_FAIL"
        Write-Output "FULL_OVERNIGHT_RUNNER_STOP_REASON:PUBLISH_FAILED"
        break
    }

    Write-Output "PUBLISH_RESULT:PUBLISHED"
    Write-Output "FULL_OVERNIGHT_RUNNER_STOP_REASON:CONTINUE_CYCLE"
}
