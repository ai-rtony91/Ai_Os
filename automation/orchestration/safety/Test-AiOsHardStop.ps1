[CmdletBinding()]
param(
    [string]$RepoRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AiOsRepoRoot {
    param([string]$RequestedRepoRoot)

    if (-not [string]::IsNullOrWhiteSpace($RequestedRepoRoot)) {
        return (Resolve-Path -LiteralPath $RequestedRepoRoot).Path
    }

    $scriptRoot = Split-Path -Parent $PSCommandPath
    return (Resolve-Path -LiteralPath (Join-Path $scriptRoot "..\..\..")).Path
}

$resolvedRepoRoot = Resolve-AiOsRepoRoot -RequestedRepoRoot $RepoRoot
$flagPath = Join-Path $resolvedRepoRoot "HARD_STOP.flag"
$hardStopPresent = Test-Path -LiteralPath $flagPath -PathType Leaf

$result = [ordered]@{
    hard_stop_present = [bool]$hardStopPresent
    flag_path = $flagPath
    decision = if ($hardStopPresent) { "BLOCKED_HARD_STOP" } else { "CLEAR" }
    reason = if ($hardStopPresent) { "HARD_STOP.flag exists at repo root." } else { "No HARD_STOP.flag found at repo root." }
    checked_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

[pscustomobject]$result
