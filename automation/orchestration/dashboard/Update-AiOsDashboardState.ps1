[CmdletBinding()]
param(
    [string]$OutPath = "apps/dashboard/data/aios_live_state.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$resolvedOut = if ([System.IO.Path]::IsPathRooted($OutPath)) { $OutPath } else { Join-Path $repoRoot $OutPath }

function Read-JsonOrNull {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    try {
        return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    } catch {
        return [ordered]@{ parse_error = $_.Exception.Message; path = $Path }
    }
}

function Count-Files {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return 0
    }
    return @(Get-ChildItem -LiteralPath $Path -File -ErrorAction SilentlyContinue).Count
}

$markerPath = Join-Path $repoRoot "control\cycle\last_marker.json"
$modeScript = Join-Path $repoRoot "automation\orchestration\mode\Get-AiOsActiveMode.ps1"
$ledgerPath = Join-Path $repoRoot "control\mode\cost_ledger.jsonl"
$relayRoot = Join-Path $repoRoot "relay"

$cycle = Read-JsonOrNull -Path $markerPath
if ($null -eq $cycle) {
    $cycle = [ordered]@{ marker = "missing" }
}

try {
    $mode = & $modeScript
} catch {
    $mode = [ordered]@{ mode = "UNKNOWN"; reason = "MODE_READ_FAILED:$($_.Exception.Message)" }
}

$queues = [ordered]@{
    inbox = Count-Files (Join-Path $relayRoot "inbox")
    running = Count-Files (Join-Path $relayRoot "running")
    done = Count-Files (Join-Path $relayRoot "done")
    error = Count-Files (Join-Path $relayRoot "error")
    approvals = Count-Files (Join-Path $relayRoot "approvals")
}

$cost = [ordered]@{ entries_last_24h = 0; total_cost_last_24h = 0.0 }
if (Test-Path -LiteralPath $ledgerPath -PathType Leaf) {
    $cutoff = (Get-Date).ToUniversalTime().AddHours(-24)
    $entries = @()
    foreach ($line in Get-Content -LiteralPath $ledgerPath -ErrorAction SilentlyContinue) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try {
            $entry = $line | ConvertFrom-Json
            $stampText = if ($null -ne $entry.utc) { [string]$entry.utc } elseif ($null -ne $entry.timestamp_utc) { [string]$entry.timestamp_utc } else { "" }
            if (-not [string]::IsNullOrWhiteSpace($stampText) -and ([datetime]$stampText).ToUniversalTime() -ge $cutoff) {
                $entries += $entry
            }
        } catch {
            continue
        }
    }
    $total = 0.0
    foreach ($entry in $entries) {
        if ($null -ne $entry.cost_usd) { $total += [double]$entry.cost_usd }
        elseif ($null -ne $entry.estimated_cost_usd) { $total += [double]$entry.estimated_cost_usd }
    }
    $cost = [ordered]@{ entries_last_24h = @($entries).Count; total_cost_last_24h = [math]::Round($total, 6) }
}

$errors = @()
$errorDir = Join-Path $relayRoot "error"
if (Test-Path -LiteralPath $errorDir -PathType Container) {
    $errors = @(Get-ChildItem -LiteralPath $errorDir -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 10 |
        ForEach-Object {
            [ordered]@{
                id = $_.BaseName
                reason = $_.Name
                timestamp = $_.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
            }
        })
}

$approvalDir = Join-Path $relayRoot "approvals"
$prAdvisories = 0
if (Test-Path -LiteralPath $approvalDir -PathType Container) {
    $prAdvisories = @(Get-ChildItem -LiteralPath $approvalDir -File -Filter "pr-*.advisory.md" -ErrorAction SilentlyContinue).Count
}

$state = [ordered]@{
    cycle = $cycle
    mode = $mode
    queues = $queues
    cost = $cost
    errors = $errors
    prs = [ordered]@{ failed_check_advisories = $prAdvisories }
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

$outDir = Split-Path -Parent $resolvedOut
if (-not (Test-Path -LiteralPath $outDir -PathType Container)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}
$tmpPath = $resolvedOut + ".tmp"
Set-Content -LiteralPath $tmpPath -Value (($state | ConvertTo-Json -Depth 20) + "`n") -Encoding UTF8
Move-Item -LiteralPath $tmpPath -Destination $resolvedOut -Force
Write-Host ("DASHBOARD_STATE_WRITTEN path={0}" -f $resolvedOut)
