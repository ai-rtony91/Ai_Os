[CmdletBinding()]
param(
    [switch]$QuietJson
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

function ConvertTo-AiOsListText {
    param($Items)

    $values = @($Items)
    if ($values.Count -eq 0) { return "- none" }
    return (($values | ForEach-Object { "- $_" }) -join [Environment]::NewLine)
}

function Invoke-AiOsQuietJson {
    param([string]$ScriptPath)

    if (-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
        return $null
    }

    return powershell -ExecutionPolicy Bypass -File $ScriptPath -QuietJson | ConvertFrom-Json
}

$currentBranch = git branch --show-current
$activePacket = Get-AiOsActivePacket

$nextRecommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
$nextCommandResult = Invoke-AiOsQuietJson -ScriptPath "automation/runtime/recommendation/Get-AiOsNextCommand.ps1"
if ($nextCommandResult -and $nextCommandResult.next_best_step) {
    $nextRecommendedCommand = [string]$nextCommandResult.next_best_step
}

$codexHandoffCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1"
$codexHandoff = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1"
$validatorRecommendation = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1"
$commitPackageRecommendation = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1"
$approvalStatus = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1"
$workerLockStatus = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1"

$statusLines = @(git status --short --untracked-files=all)
$dirtyFiles = @(
    foreach ($line in $statusLines) {
        if ([string]::IsNullOrWhiteSpace($line) -or $line.Length -lt 4) { continue }
        $path = $line.Substring(3).Trim()
        if ($path -match " -> ") { $path = ($path -split " -> ")[-1].Trim() }
        $path -replace "\\", "/"
    }
)

if ($commitPackageRecommendation) {
    $approvedSourceFiles = @($commitPackageRecommendation.approved_source_files)
    foreach ($file in $dirtyFiles) {
        if ($file -eq "aios.ps1" -or $file -like "automation/orchestration/queue_runner/*.ps1" -or $file -like "automation/orchestration/queue_runner/*.json") {
            if ($approvedSourceFiles -notcontains $file) {
                $approvedSourceFiles += $file
            }
        }
    }

    $approvedSourceFiles = @($approvedSourceFiles | Sort-Object -Unique)
    $commitPackageRecommendation = [pscustomobject]@{
        approved_source_files = $approvedSourceFiles
        ignored_runtime_files = @($commitPackageRecommendation.ignored_runtime_files)
        risky_files = @($commitPackageRecommendation.risky_files)
        suggested_git_add_commands = @($approvedSourceFiles | ForEach-Object { "git add -- `"$_`"" })
        suggested_commit_message = "Add AIOS operator queue runner"
        push_reminder = if ($commitPackageRecommendation.push_reminder) { [string]$commitPackageRecommendation.push_reminder } else { "Do not push until commit validation is clean and the operator explicitly approves push." }
    }
}

$readyToPasteCodexPrompt = if ($codexHandoff -and $codexHandoff.ready_to_paste_codex_prompt) { [string]$codexHandoff.ready_to_paste_codex_prompt } else { "Run the Codex handoff command to generate the ready-to-paste prompt." }

$powerShellCommandBlock = @"
git status --short --branch
$codexHandoffCommand
powershell -ExecutionPolicy Bypass -File automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1
powershell -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1
$nextRecommendedCommand
"@

$stopConditions = @(
    "Stop if any command requests APPLY without explicit operator approval.",
    "Stop if dashboard, broker/trading execution, scheduled task, startup task, secret, delete, commit, or push paths appear.",
    "Stop if validator recommendation says approval_required YES.",
    "Stop if approval status shows blocked actions.",
    "Stop if worker lock status shows stale lock warning other than NO.",
    "Stop before git add, commit, or push unless the operator provides exact commands."
)

$result = [ordered]@{
    schema = "aios_operator_queue_runner.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    current_branch = $currentBranch
    active_packet = $activePacket
    packet_status = $activePacket.packet_status
    next_recommended_command = $nextRecommendedCommand
    codex_handoff_command = $codexHandoffCommand
    ready_to_paste_codex_prompt = $readyToPasteCodexPrompt
    validator_recommendation = $validatorRecommendation
    commit_package_recommendation = $commitPackageRecommendation
    approval_status = $approvalStatus
    worker_lock_status = $workerLockStatus
    powershell_command_block = $powerShellCommandBlock
    stop_conditions = $stopConditions
    commit_performed = "NO"
    push_performed = "NO"
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 14
    exit 0
}

Write-Host "AIOS Operator Queue Runner"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host ""
Write-Host "current_branch:"
Write-Host $currentBranch
Write-Host ""
Write-Host "active_packet:"
Write-Host "$($activePacket.packet_id) [$($activePacket.packet_status)]"
Write-Host $activePacket.file
Write-Host ""
Write-Host "packet_status:"
Write-Host $activePacket.packet_status
Write-Host ""
Write-Host "next_recommended_command:"
Write-Host $nextRecommendedCommand
Write-Host ""
Write-Host "codex_handoff_command:"
Write-Host $codexHandoffCommand
Write-Host ""
Write-Host "ready_to_paste_codex_prompt:"
Write-Host $readyToPasteCodexPrompt
Write-Host ""
Write-Host "validator_recommendation:"
if ($validatorRecommendation) {
    Write-Host $validatorRecommendation.recommended_validator_command
    Write-Host "reason: $($validatorRecommendation.reason)"
    Write-Host "approval_required: $($validatorRecommendation.approval_required)"
} else {
    Write-Host "unavailable"
}
Write-Host ""
Write-Host "commit_package_recommendation:"
if ($commitPackageRecommendation) {
    Write-Host "approved_source_files:"
    Write-Host (ConvertTo-AiOsListText -Items $commitPackageRecommendation.approved_source_files)
    Write-Host "ignored_runtime_files:"
    Write-Host (ConvertTo-AiOsListText -Items $commitPackageRecommendation.ignored_runtime_files)
    Write-Host "risky_files:"
    Write-Host (ConvertTo-AiOsListText -Items $commitPackageRecommendation.risky_files)
} else {
    Write-Host "unavailable"
}
Write-Host ""
Write-Host "approval_status:"
if ($approvalStatus) {
    Write-Host "pending_approvals: $(@($approvalStatus.pending_approvals).Count)"
    Write-Host "approved_actions: $(@($approvalStatus.approved_actions).Count)"
    Write-Host "blocked_actions: $(@($approvalStatus.blocked_actions).Count)"
    Write-Host "next_safe_command: $($approvalStatus.next_safe_command)"
} else {
    Write-Host "unavailable"
}
Write-Host ""
Write-Host "worker_lock_status:"
if ($workerLockStatus) {
    foreach ($lock in @($workerLockStatus.locks)) {
        Write-Host "worker_id: $($lock.worker_id)"
        Write-Host "claimed_packet: $($lock.claimed_packet)"
        Write-Host "lock_status: $($lock.lock_status)"
        Write-Host "stale_lock_warning: $($lock.stale_lock_warning)"
    }
} else {
    Write-Host "unavailable"
}
Write-Host ""
Write-Host "powershell_command_block:"
Write-Host $powerShellCommandBlock
Write-Host ""
Write-Host "stop_conditions:"
$stopConditions | ForEach-Object { Write-Host "- $_" }
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
