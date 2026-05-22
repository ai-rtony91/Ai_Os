[CmdletBinding()]
param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-AiOsChangedPath {
    param([string]$StatusLine)

    if ([string]::IsNullOrWhiteSpace($StatusLine) -or $StatusLine.Length -lt 4) {
        return $null
    }

    $path = $StatusLine.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }

    return ($path -replace "\\", "/")
}

function Get-AiOsActivePacket {
    $activePacketRoot = "automation/orchestration/work_packets/active"
    if (-not (Test-Path -LiteralPath $activePacketRoot -PathType Container)) {
        return [pscustomobject]@{
            packet_id = "none"
            status = "none"
            file = "none"
            summary = "No active packet folder found."
        }
    }

    $packetFiles = @(Get-ChildItem -LiteralPath $activePacketRoot -File -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)
    if ($packetFiles.Count -eq 0) {
        return [pscustomobject]@{
            packet_id = "none"
            status = "none"
            file = "none"
            summary = "No active packet found."
        }
    }

    $packetFile = $packetFiles[0]
    try {
        $packet = Get-Content -LiteralPath $packetFile.FullName -Raw | ConvertFrom-Json
        $goal = if ($packet.goal) { [string]$packet.goal } elseif ($packet.intent) { [string]$packet.intent } elseif ($packet.title) { [string]$packet.title } else { "" }
        return [pscustomobject]@{
            packet_id = if ($packet.packet_id) { [string]$packet.packet_id } else { $packetFile.BaseName }
            status = if ($packet.status) { [string]$packet.status } else { "UNKNOWN" }
            file = ($packetFile.FullName.Replace((Get-Location).Path + [IO.Path]::DirectorySeparatorChar, "") -replace "\\", "/")
            summary = $goal
        }
    }
    catch {
        return [pscustomobject]@{
            packet_id = $packetFile.BaseName
            status = "JSON_PARSE_REVIEW_REQUIRED"
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

$branch = git branch --show-current
$statusLines = @(git status --short --untracked-files=all)
$dirtyFiles = @(
    foreach ($line in $statusLines) {
        $path = Get-AiOsChangedPath -StatusLine $line
        if ($null -ne $path) { $path }
    }
)

$activePacket = Get-AiOsActivePacket

$nextRecommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
if (Test-Path -LiteralPath "automation/runtime/recommendation/Get-AiOsNextCommand.ps1" -PathType Leaf) {
    try {
        $next = powershell -ExecutionPolicy Bypass -File automation/runtime/recommendation/Get-AiOsNextCommand.ps1 -QuietJson | ConvertFrom-Json
        if ($next.next_best_step) { $nextRecommendedCommand = [string]$next.next_best_step }
    }
    catch {
        $nextRecommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
    }
}

$validatorRecommendation = powershell -ExecutionPolicy Bypass -File automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$commitRecommendation = powershell -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$approvedSourceFiles = @($commitRecommendation.approved_source_files)
foreach ($file in $dirtyFiles) {
    if ($file -like "automation/orchestration/handoff/*.ps1" -or $file -like "automation/orchestration/handoff/*.md") {
        if ($approvedSourceFiles -notcontains $file) {
            $approvedSourceFiles += $file
        }
    }
}
$approvedSourceFiles = @($approvedSourceFiles | Sort-Object -Unique)
$suggestedGitAddCommands = @($approvedSourceFiles | ForEach-Object { "git add -- `"$_`"" })
$suggestedCommitMessage = if ($approvedSourceFiles | Where-Object { $_ -like "automation/orchestration/handoff/*" }) { "Add AIOS Codex handoff generator" } elseif ($commitRecommendation.suggested_commit_message) { [string]$commitRecommendation.suggested_commit_message } else { "Update AIOS operator loop tooling" }
$commitPackageSummary = [ordered]@{
    approved_source_files = $approvedSourceFiles
    ignored_runtime_files = @($commitRecommendation.ignored_runtime_files)
    risky_files = @($commitRecommendation.risky_files)
    suggested_git_add_commands = $suggestedGitAddCommands
    suggested_commit_message = $suggestedCommitMessage
    push_reminder = if ($commitRecommendation.push_reminder) { [string]$commitRecommendation.push_reminder } else { "Do not push until the operator explicitly approves push." }
}

$codexPrompt = @"
PHASE NEXT - APPLY OR DRY_RUN PER OPERATOR APPROVAL
AIOS Operator Handoff

Current branch: $branch
Active packet: $($activePacket.packet_id) [$($activePacket.status)]
Active packet file: $($activePacket.file)

Objective:
Continue AIOS operator-loop work using read-only guidance first. Do not touch dashboard, broker/trading execution, scheduled tasks, startup tasks, secrets, deletes, commits, or pushes unless explicitly approved.

Current dirty files:
$(ConvertTo-AiOsListText -Items $dirtyFiles)

Next recommended command:
$nextRecommendedCommand

Validator recommendation:
$($validatorRecommendation.recommended_validator_command)
Reason: $($validatorRecommendation.reason)
Approval required: $($validatorRecommendation.approval_required)

Commit package recommendation:
Approved source files:
$(ConvertTo-AiOsListText -Items $commitPackageSummary.approved_source_files)

Ignored runtime files:
$(ConvertTo-AiOsListText -Items $commitPackageSummary.ignored_runtime_files)

Risky files:
$(ConvertTo-AiOsListText -Items $commitPackageSummary.risky_files)

Rules:
- no git add unless operator gives exact file list
- no commit unless operator gives exact commit command
- no push unless operator gives exact push command
- report files created, files updated, validation result, git status, commit status, and push status
"@

$powerShellBlock = @"
git status --short --branch
powershell -ExecutionPolicy Bypass -File automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1
powershell -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1
$nextRecommendedCommand
"@

$safetyReminders = @(
    "Read-only handoff generation only.",
    "No git add, commit, or push is performed.",
    "No delete, dashboard, broker/trading execution, scheduled task, startup task, or secret action is performed.",
    "Runtime packet files should not be committed unless explicitly approved."
)

$result = [ordered]@{
    schema = "aios_codex_handoff.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    current_branch = $branch
    current_dirty_files = $dirtyFiles
    active_packet = $activePacket
    next_recommended_command = $nextRecommendedCommand
    validator_recommendation = $validatorRecommendation
    commit_package_recommendation = $commitPackageSummary
    ready_to_paste_codex_prompt = $codexPrompt
    ready_to_paste_powershell_command_block = $powerShellBlock
    safety_reminders = $safetyReminders
    commit_performed = "NO"
    push_performed = "NO"
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AIOS Codex Handoff"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host ""
Write-Host "current_branch:"
Write-Host $branch
Write-Host ""
Write-Host "current_dirty_files:"
Write-Host (ConvertTo-AiOsListText -Items $dirtyFiles)
Write-Host ""
Write-Host "active_packet:"
Write-Host "$($activePacket.packet_id) [$($activePacket.status)]"
Write-Host $activePacket.file
Write-Host ""
Write-Host "next_recommended_command:"
Write-Host $nextRecommendedCommand
Write-Host ""
Write-Host "validator_recommendation:"
Write-Host $validatorRecommendation.recommended_validator_command
Write-Host "reason: $($validatorRecommendation.reason)"
Write-Host "approval_required: $($validatorRecommendation.approval_required)"
Write-Host ""
Write-Host "commit_package_recommendation:"
Write-Host "approved_source_files:"
Write-Host (ConvertTo-AiOsListText -Items $commitPackageSummary.approved_source_files)
Write-Host "ignored_runtime_files:"
Write-Host (ConvertTo-AiOsListText -Items $commitPackageSummary.ignored_runtime_files)
Write-Host "risky_files:"
Write-Host (ConvertTo-AiOsListText -Items $commitPackageSummary.risky_files)
Write-Host ""
Write-Host "ready_to_paste_codex_prompt:"
Write-Host $codexPrompt
Write-Host ""
Write-Host "ready_to_paste_powershell_command_block:"
Write-Host $powerShellBlock
Write-Host ""
Write-Host "safety_reminders:"
$safetyReminders | ForEach-Object { Write-Host "- $_" }
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
