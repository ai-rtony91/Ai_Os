[CmdletBinding()]
param(
    [string]$PacketCandidatePath,
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsAutoLoopFullPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $Path))
}

function Test-AiOsAutoLoopReportPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $allowedRoot = [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path "telemetry\auto_loop\reports"))
    $fullPath = Get-AiOsAutoLoopFullPath -Path $Path
    return $fullPath.StartsWith($allowedRoot, [System.StringComparison]::OrdinalIgnoreCase)
}

$packet = $null
if ($PacketCandidatePath) {
    $packet = Get-Content -Raw -LiteralPath $PacketCandidatePath | ConvertFrom-Json
}

$packetId = if ($packet -and $packet.packet_id) { $packet.packet_id } else { "UNBOUND_DRY_RUN" }
$proposedFiles = if ($packet -and $packet.allowed_paths) { @($packet.allowed_paths) } else { @("automation/orchestration/auto_loop/", "telemetry/auto_loop/") }

$record = [ordered]@{
    approval_id = "AUTO_LOOP_APPROVAL_CANDIDATE_{0}" -f (Get-Date -Format "yyyyMMddHHmmss")
    packet_id = $packetId
    proposed_action = "Review auto-loop DRY_RUN packet candidate and validator route before any APPLY lane."
    proposed_files = $proposedFiles
    risk_tier = if ($packet -and $packet.risk_tier) { $packet.risk_tier } else { "low" }
    validator_recommendation = [ordered]@{
        required_validators = @("git diff --check", "PowerShell parse for changed scripts", "JSON parse for changed templates")
        manual_review_required = $true
    }
    blocked_actions = @(
        "commit",
        "push",
        "merge",
        "live_trading",
        "broker_execution",
        "secret_access",
        "active_queue_mutation",
        "active_approval_inbox_mutation",
        "worker_dispatch"
    )
    human_approval_required = $true
    apply_allowed = $false
    commit_allowed = $false
    push_allowed = $false
    reason = "DRY_RUN approval candidate only. Human Owner must approve any APPLY, commit, push, merge, or protected action."
    next_safe_command = "Review the generated packet candidate, validator route, and diff before approving a focused APPLY/commit package."
    did = @("Created approval candidate evidence for operator review.")
    did_not = @("Did not mutate active APPROVAL_INBOX_001.json, approve work, commit, push, merge, dispatch workers, or touch secrets.")
}

$json = $record | ConvertTo-Json -Depth 10

if ($OutputPath) {
    if (-not (Test-AiOsAutoLoopReportPath -Path $OutputPath)) {
        throw "OutputPath must be under telemetry/auto_loop/reports."
    }

    $fullOutputPath = Get-AiOsAutoLoopFullPath -Path $OutputPath
    $parent = Split-Path -Parent $fullOutputPath
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    Set-Content -LiteralPath $fullOutputPath -Value ($json + [Environment]::NewLine) -Encoding UTF8
}

Write-Output $json
