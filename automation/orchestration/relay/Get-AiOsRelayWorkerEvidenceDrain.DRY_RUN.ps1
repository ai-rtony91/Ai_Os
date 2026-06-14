[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolved = (Resolve-Path -LiteralPath $RepoRoot).Path
$relayRoot = Join-Path $repoRootResolved "relay"

function ConvertTo-AiOsRelativePath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $base = $repoRootResolved.TrimEnd("\") + "\"
    if ($Path.StartsWith($base, [StringComparison]::OrdinalIgnoreCase)) {
        return $Path.Substring($base.Length).Replace("\", "/")
    }
    return $Path
}

function Get-AiOsEvidenceFiles {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$Filter = "*"
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return @()
    }

    return @(Get-ChildItem -LiteralPath $Path -File -Filter $Filter -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc, Name)
}

function New-AiOsLatestFileSummary {
    param([object[]]$Files)

    $items = @($Files)
    if ($items.Count -eq 0) {
        return $null
    }

    $latest = @($items | Sort-Object LastWriteTimeUtc, Name | Select-Object -Last 1)[0]
    return [ordered]@{
        name = $latest.Name
        relative_path = ConvertTo-AiOsRelativePath -Path $latest.FullName
        last_write_time_utc = $latest.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
        length_bytes = [int64]$latest.Length
    }
}

$folders = [ordered]@{
    inbox = Join-Path $relayRoot "inbox"
    running = Join-Path $relayRoot "running"
    done = Join-Path $relayRoot "done"
    error = Join-Path $relayRoot "error"
    outbox = Join-Path $relayRoot "outbox"
    approvals = Join-Path $relayRoot "approvals"
}

$files = [ordered]@{}
foreach ($name in $folders.Keys) {
    $files[$name] = @(Get-AiOsEvidenceFiles -Path $folders[$name])
}
$outboxReports = @(Get-AiOsEvidenceFiles -Path $folders.outbox -Filter "*.report.txt")

$counts = [ordered]@{}
foreach ($name in $folders.Keys) {
    $counts[$name] = @($files[$name]).Count
}

$hasPendingInbox = ($counts.inbox -gt 0)
$hasRunningPackets = ($counts.running -gt 0)
$approvalWaitCount = $counts.approvals
$recommendation = if ($hasRunningPackets) {
    "Review relay/running evidence before any worker execution."
} elseif ($approvalWaitCount -gt 0) {
    "Review relay/approvals before any next queue action."
} elseif ($hasPendingInbox) {
    "Relay inbox has pending packets; keep direct worker invocation blocked until a no-write drain is approved."
} else {
    "No pending relay worker action detected from existing evidence."
}

[pscustomobject][ordered]@{
    mode = "DRY_RUN"
    adapter = "relay_worker_evidence_drain"
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    repo_root = $repoRootResolved
    relay_root = $relayRoot
    counts = $counts
    latest_done = New-AiOsLatestFileSummary -Files $files.done
    latest_error = New-AiOsLatestFileSummary -Files $files.error
    latest_outbox_report = New-AiOsLatestFileSummary -Files $outboxReports
    approval_wait_count = $approvalWaitCount
    has_pending_inbox = [bool]$hasPendingInbox
    has_running_packets = [bool]$hasRunningPackets
    recommendation = $recommendation
    blocked_direct_worker_reason = "Direct worker invocation remains blocked because the current worker dry-run path can move relay packets and write reports."
    mutation_performed = $false
    worker_invoked = $false
    provider_cli_invoked = $false
    relay_state_mutated = $false
}
