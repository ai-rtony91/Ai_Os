[CmdletBinding()]
param(
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    $current = Split-Path -Parent $PSCommandPath
    while ($current) {
        if (Test-Path -LiteralPath (Join-Path $current ".git")) {
            return $current
        }
        $parent = Split-Path -Parent $current
        if ($parent -eq $current) { break }
        $current = $parent
    }
    throw "Unable to resolve repository root from $PSCommandPath"
}

function ConvertTo-RelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $pathFull = [System.IO.Path]::GetFullPath($Path)
    $rootUri = [System.Uri]::new($rootFull + [System.IO.Path]::DirectorySeparatorChar)
    $pathUri = [System.Uri]::new($pathFull)
    return [System.Uri]::UnescapeDataString($rootUri.MakeRelativeUri($pathUri).ToString()).Replace("/", [System.IO.Path]::DirectorySeparatorChar)
}

function Read-JsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing JSON file: $Path"
    }
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Get-StatusValue {
    param($BridgeState)

    foreach ($name in @("night_supervisor_status", "supervisor_status", "status")) {
        if ($BridgeState.PSObject.Properties.Name -contains $name) {
            $value = [string]$BridgeState.$name
            if (-not [string]::IsNullOrWhiteSpace($value)) {
                return $value.ToUpperInvariant()
            }
        }
    }
    return "UNKNOWN"
}

function Get-CountValue {
    param(
        $Object,
        [string[]]$Names
    )

    foreach ($name in $Names) {
        if ($Object.PSObject.Properties.Name -contains $name) {
            $value = $Object.$name
            if ($null -ne $value) {
                return [int]$value
            }
        }
    }
    return 0
}

function Get-MustSeeCount {
    param($BridgeState)

    if ($BridgeState.PSObject.Properties.Name -notcontains "must_see" -or $null -eq $BridgeState.must_see) {
        return 0
    }
    if ($BridgeState.must_see -is [System.Array]) {
        return $BridgeState.must_see.Count
    }
    return 1
}

function Test-CycleClean {
    param($BridgeState)

    $status = Get-StatusValue -BridgeState $BridgeState
    $approvalCount = Get-CountValue -Object $BridgeState -Names @("approval_needed_count", "approvals_needed", "waiting_approval_count")
    $blockedCount = Get-CountValue -Object $BridgeState -Names @("blocked_count", "blocker_count")
    $mustSeeCount = Get-MustSeeCount -BridgeState $BridgeState

    $cleanStatuses = @("PASS", "CLEAN")
    $isClean = ($cleanStatuses -contains $status) -and $approvalCount -eq 0 -and $blockedCount -eq 0 -and $mustSeeCount -eq 0

    [pscustomobject]@{
        IsClean = $isClean
        Status = $status
        ApprovalNeededCount = $approvalCount
        BlockedCount = $blockedCount
        MustSeeCount = $mustSeeCount
    }
}

function Select-BacklogCandidate {
    param($Backlog)

    if ($Backlog.PSObject.Properties.Name -notcontains "candidates" -or $null -eq $Backlog.candidates) {
        return $null
    }

    $readyGreen = @(
        $Backlog.candidates |
            Where-Object {
                ([string]$_.status).ToUpperInvariant() -eq "READY" -and
                ([string]$_.risk_level).ToUpperInvariant() -eq "GREEN"
            } |
            Sort-Object @{ Expression = { [int]$_.priority }; Descending = $true }, @{ Expression = { [string]$_.id }; Ascending = $true }
    )

    if ($readyGreen.Count -eq 0) {
        return $null
    }
    return $readyGreen[0]
}

function New-ApprovalItem {
    param(
        [Parameter(Mandatory = $true)]$Candidate,
        [Parameter(Mandatory = $true)][string]$BacklogPath,
        [Parameter(Mandatory = $true)][string]$PolicyPath,
        [Parameter(Mandatory = $true)][string]$GeneratedAt
    )

    [pscustomobject]@{
        schema = "AIOS_SELF_CONTINUATION_APPROVAL.v1"
        id = "self-continuation-$($Candidate.id)"
        title = "Self-continuation proposal: $($Candidate.title)"
        status = "WAITING_APPROVAL"
        source_store = "relay"
        source_type = "self_continuation_proposal"
        created_at = $GeneratedAt
        decided_at = $null
        decided_by = $null
        risk_level = [string]$Candidate.risk_level
        gate_flags = @($Candidate.gate_flags)
        origin_ref = $BacklogPath
        policy_ref = $PolicyPath
        proposed_goal = [pscustomobject]@{
            backlog_id = [string]$Candidate.id
            title = [string]$Candidate.title
            goal = [string]$Candidate.goal
            why = [string]$Candidate.why
            priority = [int]$Candidate.priority
            allowed_paths = @($Candidate.allowed_paths)
            forbidden_paths = @($Candidate.forbidden_paths)
        }
        provenance = [pscustomobject]@{
            proposed_by = "Invoke-AiOsSelfContinuation.DRY_RUN.ps1"
            bounded_backlog_only = $true
            requires_human_approval = $true
            writes_to_relay_inbox = $false
            auto_executes_goal = $false
        }
    }
}

$repoRoot = Resolve-RepoRoot
$backlogRel = "control/self_continuation/BACKLOG.json"
$stopRel = "control/self_continuation/STOP"
$policyRel = "docs/governance/SELF_CONTINUATION_POLICY.md"
$bridgeStateRel = "telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json"
$approvalDirRel = "relay/approvals"

$backlogPath = Join-Path $repoRoot $backlogRel
$stopPath = Join-Path $repoRoot $stopRel
$bridgeStatePath = Join-Path $repoRoot $bridgeStateRel
$approvalDir = Join-Path $repoRoot $approvalDirRel

$result = [ordered]@{
    mode = if ($Apply) { "APPLY" } else { "DRY_RUN" }
    status = "UNKNOWN"
    reason = $null
    cycle = $null
    selected_goal = $null
    approval_target = $null
    wrote_file = $false
}

try {
    if (Test-Path -LiteralPath $stopPath) {
        $result.status = "STOPPED"
        $result.reason = "kill switch present: $stopRel"
        [pscustomobject]$result | ConvertTo-Json -Depth 8
        exit 0
    }

    if (-not (Test-Path -LiteralPath $backlogPath)) {
        $result.status = "STOPPED"
        $result.reason = "backlog missing: $backlogRel"
        [pscustomobject]$result | ConvertTo-Json -Depth 8
        exit 0
    }

    $backlog = Read-JsonFile -Path $backlogPath
    if ($backlog.PSObject.Properties.Name -notcontains "enabled" -or -not [bool]$backlog.enabled) {
        $result.status = "STOPPED"
        $result.reason = "backlog disabled"
        [pscustomobject]$result | ConvertTo-Json -Depth 8
        exit 0
    }

    if (-not (Test-Path -LiteralPath $bridgeStatePath -PathType Leaf)) {
        $result.status = "STOPPED"
        $result.reason = "bridge state missing: $bridgeStateRel"
        [pscustomobject]$result | ConvertTo-Json -Depth 8
        exit 0
    }

    $bridgeState = Read-JsonFile -Path $bridgeStatePath
    $cycle = Test-CycleClean -BridgeState $bridgeState
    $result.cycle = $cycle

    if (-not $cycle.IsClean) {
        $result.status = "CYCLE_NOT_CLEAN"
        $result.reason = "latest cycle is $($cycle.Status); approvals=$($cycle.ApprovalNeededCount); blocked=$($cycle.BlockedCount); must_see=$($cycle.MustSeeCount)"
        [pscustomobject]$result | ConvertTo-Json -Depth 8
        exit 0
    }

    $candidate = Select-BacklogCandidate -Backlog $backlog
    if ($null -eq $candidate) {
        $result.status = "NO_ELIGIBLE_GOAL"
        $result.reason = "no READY GREEN backlog candidate exists"
        [pscustomobject]$result | ConvertTo-Json -Depth 8
        exit 0
    }

    $generatedAt = (Get-Date).ToUniversalTime().ToString("o")
    $approval = New-ApprovalItem -Candidate $candidate -BacklogPath $backlogRel -PolicyPath $policyRel -GeneratedAt $generatedAt
    $safeId = ([string]$candidate.id).ToLowerInvariant() -replace "[^a-z0-9_-]", "-"
    $approvalFile = Join-Path $approvalDir ("self-continuation-{0}.approval.json" -f $safeId)
    $approvalRel = ConvertTo-RelativePath -Root $repoRoot -Path $approvalFile

    $result.status = if ($Apply) { "APPROVAL_WRITTEN" } else { "DRY_RUN_READY" }
    $result.reason = "next goal is gated as an approval item; it is not written to relay/inbox"
    $result.selected_goal = [pscustomobject]@{
        id = [string]$candidate.id
        title = [string]$candidate.title
        risk_level = [string]$candidate.risk_level
        priority = [int]$candidate.priority
    }
    $result.approval_target = $approvalRel

    if ($Apply) {
        if (-not (Test-Path -LiteralPath $approvalDir)) {
            New-Item -ItemType Directory -Path $approvalDir | Out-Null
        }
        $approval | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $approvalFile -Encoding UTF8
        $result.wrote_file = $true
    }

    [pscustomobject]$result | ConvertTo-Json -Depth 12
}
catch {
    $result.status = "FAILED"
    $result.reason = $_.Exception.Message
    [pscustomobject]$result | ConvertTo-Json -Depth 8
    exit 1
}
