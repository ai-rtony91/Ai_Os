<#
.SYNOPSIS
Pulls bounded GREEN self-continuation backlog items into relay goals.

.DESCRIPTION
Reads control/self_continuation/BACKLOG.json and selects at most
max_auto_goals_per_cycle items where status is READY and risk_level is GREEN.
Default mode prints goal and approval previews only. With -Apply, writes
relay/goals/{id}.goal.txt for GREEN items and relay/approvals/{id}.approval.md
for non-GREEN READY items. Recurring GREEN items remain READY.
#>

[CmdletBinding()]
param(
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$backlogPath = Join-Path $repoRoot "control\self_continuation\BACKLOG.json"
$stopPath = Join-Path $repoRoot "control\self_continuation\STOP"
$relayGoalsDir = Join-Path $repoRoot "relay\goals"
$relayApprovalsDir = Join-Path $repoRoot "relay\approvals"

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

function Get-AiOsPropertyBool {
    param(
        [AllowNull()][object]$Object,
        [Parameter(Mandatory = $true)][string]$Name
    )

    if ($null -eq $Object) { return $false }
    if ($Object.PSObject.Properties.Name -contains $Name) {
        return [bool]$Object.$Name
    }

    return $false
}

function Get-AiOsPropertyArray {
    param(
        [AllowNull()][object]$Object,
        [Parameter(Mandatory = $true)][string]$Name
    )

    if ($null -eq $Object) { return @() }
    if ($Object.PSObject.Properties.Name -contains $Name -and $null -ne $Object.$Name) {
        return @($Object.$Name)
    }

    return @()
}

function Get-AiOsBacklogCap {
    param([Parameter(Mandatory = $true)]$Backlog)

    if ($Backlog.PSObject.Properties.Name -contains "max_auto_goals_per_cycle") {
        $cap = [int]$Backlog.max_auto_goals_per_cycle
        if ($cap -gt 0) { return $cap }
    }

    return 1
}

function ConvertTo-AiOsSafeId {
    param([Parameter(Mandatory = $true)][string]$Id)

    $safeId = ($Id -replace "[^A-Za-z0-9._-]", "-").Trim("-")
    if ([string]::IsNullOrWhiteSpace($safeId)) {
        throw "Backlog item id cannot be made filesystem-safe."
    }
    return $safeId
}

function New-AiOsGoalText {
    param(
        [Parameter(Mandatory = $true)]$Item,
        [Parameter(Mandatory = $true)][string]$PulledAt
    )

    return @(
        "source=BACKLOG"
        "item_id=$($Item.id)"
        "pulled_at_utc=$PulledAt"
        ""
        [string]$Item.goal
    ) -join [Environment]::NewLine
}

function New-AiOsApprovalText {
    param(
        [Parameter(Mandatory = $true)]$Item,
        [Parameter(Mandatory = $true)][string]$GeneratedAt
    )

    return @(
        "# Self-Continuation Approval Required"
        ""
        "id: $($Item.id)"
        "title: $($Item.title)"
        "risk_level: $($Item.risk_level)"
        "created_at_utc: $GeneratedAt"
        "reason: NON_GREEN_SELF_CONTINUATION_CANDIDATE"
        ""
        "## Gate Flags"
        (Get-AiOsPropertyArray -Object $Item -Name "gate_flags" | ForEach-Object { "- $_" }) -join [Environment]::NewLine
        ""
        "## Proposed Goal"
        [string]$Item.goal
        ""
        "## Boundary"
        "This candidate is not auto-emitted as a relay goal. Human approval is required before execution."
    ) -join [Environment]::NewLine
}

if (Test-Path -LiteralPath $stopPath -PathType Leaf) {
    Write-AiOsBacklogLine "STOP_FLAG_PRESENT selected=0"
    exit 0
}

if (-not (Test-Path -LiteralPath $backlogPath -PathType Leaf)) {
    Write-AiOsBacklogLine "NO_BACKLOG_FILE path=$backlogPath"
    exit 0
}

$backlog = Get-Content -LiteralPath $backlogPath -Raw | ConvertFrom-Json
$items = @(Get-AiOsBacklogItems -Backlog $backlog)
$cap = Get-AiOsBacklogCap -Backlog $backlog
$eligible = @(
    $items |
    Where-Object {
        (Get-AiOsPropertyText -Object $_ -Name "status").ToUpperInvariant() -eq "READY" -and
        (Get-AiOsPropertyText -Object $_ -Name "risk_level").ToUpperInvariant() -eq "GREEN"
    } |
    Sort-Object @{ Expression = { [int]$_.priority }; Descending = $true }, @{ Expression = { [string]$_.id }; Ascending = $true } |
    Select-Object -First $cap
)
$needsApproval = @(
    $items |
    Where-Object {
        (Get-AiOsPropertyText -Object $_ -Name "status").ToUpperInvariant() -eq "READY" -and
        (Get-AiOsPropertyText -Object $_ -Name "risk_level").ToUpperInvariant() -ne "GREEN"
    } |
    Sort-Object @{ Expression = { [int]$_.priority }; Descending = $true }, @{ Expression = { [string]$_.id }; Ascending = $true }
)

if ($eligible.Count -eq 0 -and $needsApproval.Count -eq 0) {
    Write-AiOsBacklogLine "NO_GREEN_READY_BACKLOG"
    exit 0
}

if ($eligible.Count -eq 0) {
    Write-AiOsBacklogLine "NO_GREEN_READY_BACKLOG approvals=$($needsApproval.Count)"
}

$generatedAt = Get-AiOsUtc
$emittedGoals = 0
$approvalCount = 0

foreach ($item in $eligible) {
    $id = [string]$item.id
    if ([string]::IsNullOrWhiteSpace($id)) {
        throw "Eligible backlog item is missing id."
    }

    $goalText = [string]$item.goal
    if ([string]::IsNullOrWhiteSpace($goalText)) {
        throw "Eligible backlog item $id is missing goal text."
    }

    $safeId = ConvertTo-AiOsSafeId -Id $id
    $goalPath = Join-Path $relayGoalsDir ("{0}.goal.txt" -f $safeId)
    $pulledAt = Get-AiOsUtc
    $goalOutput = New-AiOsGoalText -Item $item -PulledAt $pulledAt

    if (-not $Apply) {
        Write-AiOsBacklogLine "GOAL_PREVIEW id=$id target=$goalPath"
        Write-Host $goalOutput
    } else {
        if (-not (Test-Path -LiteralPath $relayGoalsDir -PathType Container)) {
            New-Item -ItemType Directory -Path $relayGoalsDir -Force | Out-Null
        }

        $goalOutput | Set-Content -LiteralPath $goalPath -Encoding UTF8
        $item | Add-Member -NotePropertyName "last_pulled_at_utc" -NotePropertyValue $pulledAt -Force
        if (-not (Get-AiOsPropertyBool -Object $item -Name "recurring")) {
            $item.status = "PULLED"
            $item | Add-Member -NotePropertyName "pulled_at_utc" -NotePropertyValue $pulledAt -Force
        }
        Write-AiOsBacklogLine "PULLED_GREEN_READY_BACKLOG id=$id target=$goalPath recurring=$(Get-AiOsPropertyBool -Object $item -Name "recurring")"
    }
    $emittedGoals++
}

foreach ($item in $needsApproval) {
    $id = [string]$item.id
    if ([string]::IsNullOrWhiteSpace($id)) {
        throw "Approval backlog item is missing id."
    }

    $safeId = ConvertTo-AiOsSafeId -Id $id
    $approvalPath = Join-Path $relayApprovalsDir ("{0}.approval.md" -f $safeId)
    $approvalText = New-AiOsApprovalText -Item $item -GeneratedAt $generatedAt

    if (-not $Apply) {
        Write-AiOsBacklogLine "APPROVAL_PREVIEW id=$id target=$approvalPath"
        Write-Host $approvalText
    } else {
        if (-not (Test-Path -LiteralPath $relayApprovalsDir -PathType Container)) {
            New-Item -ItemType Directory -Path $relayApprovalsDir -Force | Out-Null
        }
        $approvalText | Set-Content -LiteralPath $approvalPath -Encoding UTF8
        Write-AiOsBacklogLine "WROTE_APPROVAL_PREVIEW id=$id target=$approvalPath"
    }
    $approvalCount++
}

if ($Apply) {
    $tempPath = "{0}.tmp" -f $backlogPath
    $backlog | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $tempPath -Encoding UTF8
    Move-Item -LiteralPath $tempPath -Destination $backlogPath -Force
}

Write-AiOsBacklogLine "BACKLOG_PULL_SUMMARY goals=$emittedGoals approvals=$approvalCount cap=$cap"
