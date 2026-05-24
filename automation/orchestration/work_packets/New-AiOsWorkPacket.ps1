param(
    [Parameter(Mandatory = $true)][string]$Intent,
    [Parameter(Mandatory = $true)][string]$OwnerLane,
    [Parameter(Mandatory = $true)][string]$AssignedWorker,
    [Parameter(Mandatory = $true)][string]$Repo,
    [Parameter(Mandatory = $true)][string]$Branch,
    [Parameter(Mandatory = $true)][string]$Validator,
    [Parameter(Mandatory = $true)][string]$NextAction,
    [string]$Mission = "",
    [string]$StopCondition = "",
    [string[]]$AllowedWriteBoundary = @(),
    [string]$Mode = "DRY_RUN",
    [string]$Title = "",
    [string]$PacketId = "",
    [string]$TaskId = "",
    [string]$Worktree = "",
    [string]$RiskClass = "standard",
    [string]$Priority = "normal",
    [string[]]$BlockedPaths = @(),
    [string[]]$RequiredAuthorityFiles = @("AGENTS.md", "README.md"),
    [string[]]$ValidationCommands = @(),
    [string]$FinalReportFormat = "EXECUTIVE_SUMMARY,FILES_CREATED,FILES_UPDATED,VALIDATION_RUN,NEXT_SAFE_ACTION",
    [bool]$CommitAllowed = $false,
    [bool]$PushAllowed = $false,
    [string]$RootPath = "automation/orchestration/work_packets"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

if ($Mode -notin @("DRY_RUN", "APPLY")) {
    Write-Host "ERROR: -Mode must be DRY_RUN or APPLY. Got: $Mode" -ForegroundColor Red
    exit 1
}

# Safe defaults for backward-compatible callers that omit the new fields.
# Test-AiOsWorkPacket.ps1 remains strict and will reject executable packets
# where these fields are still empty after defaults.
if ([string]::IsNullOrWhiteSpace($Mission)) {
    $Mission = if (-not [string]::IsNullOrWhiteSpace($Title)) { $Title } else { $Intent }
}
if ([string]::IsNullOrWhiteSpace($StopCondition)) {
    $StopCondition = "Report completion and stop for operator review."
}
if ($null -eq $AllowedWriteBoundary) {
    $AllowedWriteBoundary = @()
}

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

function ConvertTo-AiOsSlug {
    param([Parameter(Mandatory = $true)][string]$Value)

    $slug = $Value.ToLowerInvariant() -replace "[^a-z0-9]+", "-"
    $slug = $slug.Trim("-")
    if ([string]::IsNullOrWhiteSpace($slug)) {
        return "work-packet"
    }
    return $slug
}

$scriptName = Split-Path -Leaf $PSCommandPath
$utcNow = (Get-Date).ToUniversalTime()
$createdUtc = $utcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
$safePacketId = if ([string]::IsNullOrWhiteSpace($PacketId)) { ConvertTo-AiOsSlug -Value $Intent } else { ConvertTo-AiOsSlug -Value $PacketId }
$safeTitle = if ([string]::IsNullOrWhiteSpace($Title)) { $Intent } else { $Title }
$rootFullPath = Resolve-AiOsPath -Path $RootPath
$activePath = Join-Path $rootFullPath "active"

if (-not (Test-Path -LiteralPath $activePath -PathType Container)) {
    New-Item -ItemType Directory -Path $activePath -Force | Out-Null
}

$fileName = "$($utcNow.ToString('yyyyMMdd-HHmmss'))-$safePacketId.json"
$packetPath = Join-Path $activePath $fileName

$safeTaskId = if ([string]::IsNullOrWhiteSpace($TaskId)) { $safePacketId } else { $TaskId }
$safeWorktree = if ([string]::IsNullOrWhiteSpace($Worktree)) { "" } else { $Worktree }

$packet = [ordered]@{
    packet_id               = $safePacketId
    task_id                 = $safeTaskId
    title                   = $safeTitle
    intent                  = $Intent
    mission                 = $Mission
    mode                    = $Mode
    owner_lane              = $OwnerLane
    assigned_worker         = $AssignedWorker
    repo                    = $Repo
    branch                  = $Branch
    worktree                = $safeWorktree
    status                  = if ($Mode -eq "DRY_RUN") { "proposed" } else { "active" }
    priority                = $Priority
    risk_class              = $RiskClass
    created_utc             = $createdUtc
    updated_utc             = $createdUtc
    allowed_write_boundary  = $AllowedWriteBoundary
    blocked_paths           = $BlockedPaths
    required_authority_files = $RequiredAuthorityFiles
    validation_commands     = $ValidationCommands
    final_report_format     = $FinalReportFormat
    stop_condition          = $StopCondition
    commit_allowed          = $CommitAllowed
    push_allowed            = $PushAllowed
    validator               = $Validator
    next_action             = $NextAction
    blocked_by              = @()
    related_files           = @()
    related_packets         = @()
    notes                   = @()
}

$packetJson = $packet | ConvertTo-Json -Depth 4

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Work Packet Builder" -ForegroundColor Cyan
Write-Host "Mode: $Mode"
Write-Host "packet_id: $safePacketId"
Write-Host "task_id: $safeTaskId"
Write-Host "mission: $Mission"
Write-Host "owner_lane: $OwnerLane"
Write-Host "assigned_worker: $AssignedWorker"
Write-Host "repo: $Repo"
Write-Host "branch: $Branch"
Write-Host "risk_class: $RiskClass"
Write-Host "commit_allowed: $CommitAllowed"
Write-Host "push_allowed: $PushAllowed"
Write-Host "stop_condition: $StopCondition"
Write-Host ""

if ($Mode -eq "DRY_RUN") {
    Write-Host "DRY_RUN: packet definition below. No file written." -ForegroundColor Yellow
    Write-Host $packetJson
    Write-Host ""
    Write-Host "To write the packet, re-run with -Mode APPLY"
} else {
    if (-not (Test-Path -LiteralPath $activePath -PathType Container)) {
        New-Item -ItemType Directory -Path $activePath -Force | Out-Null
    }
    $packetJson | Set-Content -LiteralPath $packetPath -Encoding UTF8
    Write-Host "APPLY: packet written to $packetPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
