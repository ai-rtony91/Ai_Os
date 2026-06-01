<#
.SYNOPSIS
Writes a compact AI_OS morning brief from local night-cycle evidence.
#>

[CmdletBinding()]
param(
    [switch]$Apply = $true,
    [string]$Date = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$relayRoot = Join-Path $repoRoot "relay"
$reportDir = Join-Path $relayRoot "reports"
$briefPath = Join-Path $reportDir ("MORNING_BRIEF_{0}.md" -f $Date)

function Get-AiOsTaskJson {
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Get-AiOsGroupedCount {
    param(
        [AllowEmptyCollection()]
        [object[]]$Objects,
        [Parameter(Mandatory = $true)][string]$Property
    )

    $values = @(
        foreach ($object in $Objects) {
            if ($null -ne $object -and $object.PSObject.Properties.Name -contains $Property -and -not [string]::IsNullOrWhiteSpace([string]$object.$Property)) {
                [string]$object.$Property
            } else {
                "UNKNOWN"
            }
        }
    )

    if ($values.Count -eq 0) { return "none" }
    return (($values | Group-Object | Sort-Object Name | ForEach-Object { "{0}={1}" -f $_.Name, $_.Count }) -join ", ")
}

function Get-AiOsGitStatus {
    Push-Location -LiteralPath $repoRoot
    try {
        $lines = @(git status --short 2>$null | ForEach-Object { [string]$_ })
        return [pscustomobject]@{
            clean = ($lines.Count -eq 0)
            count = $lines.Count
            lines = $lines
        }
    }
    finally {
        Pop-Location
    }
}

$doneFiles = @(Get-ChildItem -LiteralPath (Join-Path $relayRoot "done") -File -Filter "*.task.json" -ErrorAction SilentlyContinue)
$errorFiles = @(Get-ChildItem -LiteralPath (Join-Path $relayRoot "error") -File -Filter "*.task.json" -ErrorAction SilentlyContinue)
$doneTasks = @($doneFiles | ForEach-Object { Get-AiOsTaskJson -Path $_.FullName })
$errorTasks = @($errorFiles | ForEach-Object { Get-AiOsTaskJson -Path $_.FullName })

$approvalFiles = @(Get-ChildItem -LiteralPath (Join-Path $relayRoot "approvals") -File -Filter "*" -ErrorAction SilentlyContinue)
$now = Get-Date
$approvalLines = @(
    foreach ($file in $approvalFiles | Sort-Object Name) {
        $age = [int]($now.ToUniversalTime() - $file.LastWriteTimeUtc).TotalHours
        "- $($file.Name) age_hours=$age"
    }
)
if ($approvalLines.Count -eq 0) { $approvalLines = @("- none") }

$telemetryDir = Join-Path $repoRoot ("telemetry\night_supervisor\{0}" -f $Date)
$telemetryFiles = @(Get-ChildItem -LiteralPath $telemetryDir -File -ErrorAction SilentlyContinue)
$telemetryText = if ($telemetryFiles.Count -eq 0) { "not found" } else { "{0} file(s)" -f $telemetryFiles.Count }
$blockedCount = 0
$validatorText = "none"
foreach ($file in $telemetryFiles) {
    try {
        $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
        if ($json.PSObject.Properties.Name -contains "blocked_count") { $blockedCount += [int]$json.blocked_count }
        if ($json.PSObject.Properties.Name -contains "validator_results") { $validatorText = "present" }
    }
    catch {
        # Ignore non-JSON telemetry in the compact morning brief.
    }
}

$backlogPath = Join-Path $repoRoot "control\self_continuation\BACKLOG.json"
$readyByTier = "not found"
if (Test-Path -LiteralPath $backlogPath -PathType Leaf) {
    $backlog = Get-Content -LiteralPath $backlogPath -Raw | ConvertFrom-Json
    $items = if ($backlog.PSObject.Properties.Name -contains "items") { @($backlog.items) } else { @($backlog.candidates) }
    $ready = @($items | Where-Object { [string]$_.status -eq "READY" })
    $readyByTier = if ($ready.Count -eq 0) {
        "none"
    } else {
        (($ready | Group-Object { if ($_.PSObject.Properties.Name -contains "risk_tier") { $_.risk_tier } else { $_.risk_level } } | Sort-Object Name | ForEach-Object { "{0}={1}" -f $_.Name, $_.Count }) -join ", ")
    }
}

$git = Get-AiOsGitStatus
$repoState = if ($git.clean) { "clean" } else { "dirty count=$($git.count)" }
$nextCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File automation\orchestration\Invoke-AiOsNightCycle.ps1"

$lines = @(
    "# AI_OS Morning Brief - $Date"
    ""
    "## WHAT THE NIGHT DID"
    "- done_count=$($doneFiles.Count)"
    "- done_by_worker=$(Get-AiOsGroupedCount -Objects $doneTasks -Property worker)"
    "- done_by_tier=$(Get-AiOsGroupedCount -Objects $doneTasks -Property tier)"
    "- error_count=$($errorFiles.Count)"
    ""
    "## WHAT NEEDS YOUR EYES"
    "- pending_approvals=$($approvalFiles.Count)"
) + $approvalLines + @(
    ""
    "## WHAT IS QUEUED"
    "- backlog_ready_by_tier=$readyByTier"
    "- night_supervisor=$telemetryText blocked_count=$blockedCount validators=$validatorText"
    ""
    "## REPO STATE"
    "- $repoState"
    ""
    "## NEXT SAFE ACTION"
    "- $nextCommand"
)

if ($lines.Count -ge 100) {
    throw "Morning brief line count must stay below 100; got $($lines.Count)."
}

if ($Apply) {
    if (-not (Test-Path -LiteralPath $reportDir -PathType Container)) {
        New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
    }
    $lines | Set-Content -LiteralPath $briefPath -Encoding UTF8
    Write-Host "MORNING_BRIEF_WRITTEN path=$briefPath lines=$($lines.Count)"
} else {
    $lines | Write-Output
}
