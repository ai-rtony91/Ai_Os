param(
    [switch]$QuietJson,
    [string]$OutputPath = ""
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            parse_error = $_.Exception.Message
            path = $Path
        }
    }
}

$runtimeStatePath = "automation/runtime/state/AIOS_RUNTIME_STATE.json"
$activePacketRoot = "automation/orchestration/work_packets/active"
$validatorRoots = @(
    "automation/validators",
    "automation/orchestration/validators",
    "scripts/validation"
)

$branch = git branch --show-current
$gitStatus = @(git status --short)
$runtimeState = Read-JsonFile -Path $runtimeStatePath

$activePackets = @()
if (Test-Path -LiteralPath $activePacketRoot -PathType Container) {
    $packetFiles = @(Get-ChildItem -LiteralPath $activePacketRoot -File -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object Name)
    foreach ($packetFile in $packetFiles) {
        $packet = Read-JsonFile -Path $packetFile.FullName
        $goal = ""
        if ($packet.goal) { $goal = [string]$packet.goal }
        elseif ($packet.intent) { $goal = [string]$packet.intent }
        elseif ($packet.title) { $goal = [string]$packet.title }

        $activePackets += [pscustomobject]@{
            file = $packetFile.FullName.Replace((Get-Location).Path + [IO.Path]::DirectorySeparatorChar, "")
            packet_id = [string]$packet.packet_id
            status = [string]$packet.status
            goal = $goal
        }
    }
}

$validatorFolders = @()
foreach ($validatorRoot in $validatorRoots) {
    if (Test-Path -LiteralPath $validatorRoot -PathType Container) {
        $validatorFolders += $validatorRoot
    }
}

$blockers = @()
if ($gitStatus.Count -gt 0) {
    $blockers += "Working tree has changes."
}
if ($runtimeState -and $runtimeState.health -and $runtimeState.health -ne "HEALTHY") {
    $blockers += "Runtime health is $($runtimeState.health)."
}
if ($activePackets.Count -eq 0) {
    $blockers += "No active packet found."
}
if ($validatorFolders.Count -eq 0) {
    $blockers += "No validator folder found."
}
if ($blockers.Count -eq 0) {
    $blockers += "No blocker detected."
}

$automationCandidates = @()
if ($activePackets.Count -gt 0) {
    $automationCandidates += "Summarize active packet progress before each operator command."
}
if ($gitStatus.Count -gt 0) {
    $automationCandidates += "Generate a DRY_RUN repo change report before selective staging."
}
if ($validatorFolders.Count -gt 0) {
    $automationCandidates += "Recommend the nearest validator chain for the active packet."
}
if ($automationCandidates.Count -eq 0) {
    $automationCandidates += "Create a first job automation packet."
}

$nextCommand = "powershell -ExecutionPolicy Bypass -File automation/runtime/recommendation/Get-AiOsNextCommand.ps1"

$report = [ordered]@{
    schema = "aios_repo_status_report.v1"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    WHERE_WE_ARE = [ordered]@{
        branch = $branch
        repo_clean = ($gitStatus.Count -eq 0)
        runtime_health = $(if ($runtimeState -and $runtimeState.health) { [string]$runtimeState.health } else { "UNKNOWN" })
        runtime_state_path = $runtimeStatePath
        validator_folders = $validatorFolders
    }
    WHAT_CHANGED = $gitStatus
    ACTIVE_PACKETS = $activePackets
    BLOCKERS = $blockers
    NEXT_COMMAND = $nextCommand
    AUTOMATION_CANDIDATES = $automationCandidates
    commit_performed = "NO"
    push_performed = "NO"
}

if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $parent = Split-Path -Parent $OutputPath
    if (-not [string]::IsNullOrWhiteSpace($parent) -and -not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    $report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
}

if ($QuietJson) {
    $report | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AIOS Repo Status Report"
Write-Host "WHERE_WE_ARE: branch=$($report.WHERE_WE_ARE.branch) repo_clean=$($report.WHERE_WE_ARE.repo_clean) runtime_health=$($report.WHERE_WE_ARE.runtime_health)"
Write-Host "WHAT_CHANGED:"
if ($gitStatus.Count -eq 0) { Write-Host "  none" } else { $gitStatus | ForEach-Object { Write-Host "  $_" } }
Write-Host "ACTIVE_PACKETS:"
if ($activePackets.Count -eq 0) { Write-Host "  none" } else { $activePackets | ForEach-Object { Write-Host "  $($_.packet_id) [$($_.status)] $($_.goal)" } }
Write-Host "BLOCKERS:"
$blockers | ForEach-Object { Write-Host "  $_" }
Write-Host "NEXT_COMMAND:"
Write-Host $nextCommand
Write-Host "AUTOMATION_CANDIDATES:"
$automationCandidates | ForEach-Object { Write-Host "  $_" }
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
