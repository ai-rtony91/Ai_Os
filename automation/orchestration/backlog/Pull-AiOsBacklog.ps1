<#
.SYNOPSIS
Pulls one approved GREEN self-continuation backlog item into relay goals.

.DESCRIPTION
Reads control/self_continuation/BACKLOG.json and selects at most one item where
status is READY, risk_tier is GREEN, and gate is APPROVED. Default mode prints
the selected goal only. With -Apply, writes one relay/goals/{id}.goal.txt and
marks the source backlog item PULLED using a temp-file replace.
#>

[CmdletBinding()]
param(
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$backlogPath = Join-Path $repoRoot "control\self_continuation\BACKLOG.json"
$relayGoalsDir = Join-Path $repoRoot "relay\goals"

function Get-AiOsUtc {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Write-AiOsBacklogLine {
    param([Parameter(Mandatory = $true)][string]$Message)
    Write-Host ("{0} {1}" -f (Get-AiOsUtc), $Message)
}

function Get-AiOsBacklogItems {
    param([Parameter(Mandatory = $true)]$Backlog)

    if ($Backlog.PSObject.Properties.Name -contains "items") {
        return @($Backlog.items)
    }

    if ($Backlog.PSObject.Properties.Name -contains "candidates") {
        return @($Backlog.candidates)
    }

    return @()
}

function Get-AiOsPropertyText {
    param(
        [AllowNull()][object]$Object,
        [Parameter(Mandatory = $true)][string]$Name
    )

    if ($null -eq $Object) { return "" }
    if ($Object.PSObject.Properties.Name -contains $Name) {
        return [string]$Object.$Name
    }

    return ""
}

if (-not (Test-Path -LiteralPath $backlogPath -PathType Leaf)) {
    Write-AiOsBacklogLine "NO_BACKLOG_FILE path=$backlogPath"
    exit 0
}

$backlog = Get-Content -LiteralPath $backlogPath -Raw | ConvertFrom-Json
$items = @(Get-AiOsBacklogItems -Backlog $backlog)
$eligible = @(
    $items |
    Where-Object {
        (Get-AiOsPropertyText -Object $_ -Name "status") -eq "READY" -and
        (Get-AiOsPropertyText -Object $_ -Name "risk_tier") -eq "GREEN" -and
        (Get-AiOsPropertyText -Object $_ -Name "gate") -eq "APPROVED"
    } |
    Select-Object -First 1
)

if ($eligible.Count -eq 0) {
    Write-AiOsBacklogLine "NO_GREEN_APPROVED_BACKLOG"
    exit 0
}

$item = $eligible[0]
$id = [string]$item.id
if ([string]::IsNullOrWhiteSpace($id)) {
    throw "Eligible backlog item is missing id."
}

$safeId = ($id -replace "[^A-Za-z0-9._-]", "-").Trim("-")
if ([string]::IsNullOrWhiteSpace($safeId)) {
    throw "Eligible backlog item id cannot be made filesystem-safe."
}

$goalText = [string]$item.goal
if ([string]::IsNullOrWhiteSpace($goalText)) {
    throw "Eligible backlog item $id is missing goal text."
}

$goalPath = Join-Path $relayGoalsDir ("{0}.goal.txt" -f $safeId)
$pulledAt = Get-AiOsUtc

if (-not $Apply) {
    Write-AiOsBacklogLine "WOULD_PULL_BACKLOG id=$id target=$goalPath"
    Write-Host $goalText
    exit 0
}

if (-not (Test-Path -LiteralPath $relayGoalsDir -PathType Container)) {
    New-Item -ItemType Directory -Path $relayGoalsDir -Force | Out-Null
}

@(
    "source=BACKLOG"
    "item_id=$id"
    "pulled_at_utc=$pulledAt"
    ""
    $goalText
) | Set-Content -LiteralPath $goalPath -Encoding UTF8

$item.status = "PULLED"
$item | Add-Member -NotePropertyName "pulled_at_utc" -NotePropertyValue $pulledAt -Force
$tempPath = "{0}.tmp" -f $backlogPath
$backlog | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $tempPath -Encoding UTF8
Move-Item -LiteralPath $tempPath -Destination $backlogPath -Force

Write-AiOsBacklogLine "PULLED_GREEN_APPROVED_BACKLOG id=$id target=$goalPath"
