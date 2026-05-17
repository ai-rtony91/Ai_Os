[CmdletBinding()]
param(
    [switch]$QuietJson,
    [switch]$SkipStartDisplay
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-AiOsActivePacket {
    $activePacketRoot = "automation/orchestration/work_packets/active"
    if (-not (Test-Path -LiteralPath $activePacketRoot -PathType Container)) {
        return [pscustomobject]@{
            packet_id = "none"
            packet_status = "none"
            file = "none"
            summary = "No active packet folder found."
        }
    }

    $packetFiles = @(Get-ChildItem -LiteralPath $activePacketRoot -File -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)
    if ($packetFiles.Count -eq 0) {
        return [pscustomobject]@{
            packet_id = "none"
            packet_status = "none"
            file = "none"
            summary = "No active packet found."
        }
    }

    $packetFile = $packetFiles[0]
    try {
        $packet = Get-Content -LiteralPath $packetFile.FullName -Raw | ConvertFrom-Json
        $summary = if ($packet.goal) { [string]$packet.goal } elseif ($packet.intent) { [string]$packet.intent } elseif ($packet.title) { [string]$packet.title } else { "" }
        return [pscustomobject]@{
            packet_id = if ($packet.packet_id) { [string]$packet.packet_id } else { $packetFile.BaseName }
            packet_status = if ($packet.status) { [string]$packet.status } else { "UNKNOWN" }
            file = ($packetFile.FullName.Replace((Get-Location).Path + [IO.Path]::DirectorySeparatorChar, "") -replace "\\", "/")
            summary = $summary
        }
    }
    catch {
        return [pscustomobject]@{
            packet_id = $packetFile.BaseName
            packet_status = "JSON_PARSE_REVIEW_REQUIRED"
            file = ($packetFile.FullName.Replace((Get-Location).Path + [IO.Path]::DirectorySeparatorChar, "") -replace "\\", "/")
            summary = $_.Exception.Message
        }
    }
}

function Invoke-AiOsQuietJson {
    param([string]$ScriptPath)

    if (-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
        return $null
    }

    return powershell -ExecutionPolicy Bypass -File $ScriptPath -QuietJson | ConvertFrom-Json
}

function ConvertTo-AiOsListText {
    param($Items)

    $values = @($Items)
    if ($values.Count -eq 0) { return "- none" }
    return (($values | ForEach-Object { "- $_" }) -join [Environment]::NewLine)
}

$branch = git branch --show-current
$activePacket = Get-AiOsActivePacket

$queueRunnerCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/queue_runner/Invoke-AiOsOperatorQueueRunner.DRY_RUN.ps1"
$codexHandoffCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1"
$validatorCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1"
$commitPackageCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1"

if (-not $SkipStartDisplay -and -not $QuietJson) {
    Write-Host "SESSION STEP 1 - .\aios.ps1 start" -ForegroundColor Yellow
    powershell -ExecutionPolicy Bypass -File .\aios.ps1 start
    Write-Host ""
}

$queueRunnerSummary = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/queue_runner/Invoke-AiOsOperatorQueueRunner.DRY_RUN.ps1"
$codexHandoff = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1"
$validatorRecommendation = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1"
$commitPackageSummary = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1"

$nextCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
if ($queueRunnerSummary -and $queueRunnerSummary.next_recommended_command) {
    $nextCommand = [string]$queueRunnerSummary.next_recommended_command
}

$stopConditions = @(
    "Stop if any output asks for APPLY without explicit operator approval.",
    "Stop if dashboard, broker/trading execution, scheduled task, startup task, secret, delete, commit, or push paths appear.",
    "Stop if validator recommendation says approval_required YES.",
    "Stop if approval status includes blocked actions.",
    "Stop if worker lock status reports stale lock warning other than NO.",
    "Stop before git add, commit, or push unless the operator provides exact commands."
)

$exactNextSafeAction = $queueRunnerCommand

$result = [ordered]@{
    schema = "aios_operator_session_bootstrap.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    branch = $branch
    active_packet = $activePacket
    next_command = $nextCommand
    queue_runner_summary = $queueRunnerSummary
    codex_handoff_command = $codexHandoffCommand
    codex_handoff_summary = $codexHandoff
    validator_command = $validatorCommand
    validator_recommendation = $validatorRecommendation
    commit_package_command = $commitPackageCommand
    commit_package_summary = $commitPackageSummary
    stop_conditions = $stopConditions
    exact_next_safe_action = $exactNextSafeAction
    commit_performed = "NO"
    push_performed = "NO"
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 16
    exit 0
}

Write-Host "AIOS Operator Session Bootstrap"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host ""
Write-Host "branch:"
Write-Host $branch
Write-Host ""
Write-Host "active_packet:"
Write-Host "$($activePacket.packet_id) [$($activePacket.packet_status)]"
Write-Host $activePacket.file
Write-Host ""
Write-Host "next_command:"
Write-Host $nextCommand
Write-Host ""
Write-Host "queue_runner_summary:"
if ($queueRunnerSummary) {
    Write-Host "packet_status: $($queueRunnerSummary.packet_status)"
    Write-Host "next_recommended_command: $($queueRunnerSummary.next_recommended_command)"
    Write-Host "codex_handoff_command: $($queueRunnerSummary.codex_handoff_command)"
} else {
    Write-Host "unavailable"
}
Write-Host ""
Write-Host "Codex handoff command:"
Write-Host $codexHandoffCommand
Write-Host ""
Write-Host "validator command:"
if ($validatorRecommendation) {
    Write-Host $validatorRecommendation.recommended_validator_command
    Write-Host "reason: $($validatorRecommendation.reason)"
    Write-Host "approval_required: $($validatorRecommendation.approval_required)"
} else {
    Write-Host $validatorCommand
}
Write-Host ""
Write-Host "commit package summary:"
if ($commitPackageSummary) {
    Write-Host "approved_source_files:"
    Write-Host (ConvertTo-AiOsListText -Items $commitPackageSummary.approved_source_files)
    Write-Host "ignored_runtime_files:"
    Write-Host (ConvertTo-AiOsListText -Items $commitPackageSummary.ignored_runtime_files)
    Write-Host "risky_files:"
    Write-Host (ConvertTo-AiOsListText -Items $commitPackageSummary.risky_files)
} else {
    Write-Host "unavailable"
}
Write-Host ""
Write-Host "stop_conditions:"
$stopConditions | ForEach-Object { Write-Host "- $_" }
Write-Host ""
Write-Host "exact_next_safe_action:"
Write-Host $exactNextSafeAction
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
