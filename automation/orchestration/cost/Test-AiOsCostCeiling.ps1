[CmdletBinding()]
param(
    [string]$LedgerPath = "control/mode/cost_ledger.jsonl",
    [string]$PolicyPath = "control/mode/AIOS_MODE_POLICY.json",
    [string]$CycleId
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$ledger = if ([System.IO.Path]::IsPathRooted($LedgerPath)) { $LedgerPath } else { Join-Path $repoRoot $LedgerPath }
$policyFile = if ([System.IO.Path]::IsPathRooted($PolicyPath)) { $PolicyPath } else { Join-Path $repoRoot $PolicyPath }

try {
    $policy = Get-Content -Raw -LiteralPath $policyFile | ConvertFrom-Json
    $cycleCeiling = [decimal]$policy.cost_ceiling_per_cycle_usd
    $dayCeiling = [decimal]$policy.cost_ceiling_per_day_usd
    $today = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")
    $cycleSpend = [decimal]0
    $daySpend = [decimal]0

    if (Test-Path -LiteralPath $ledger -PathType Leaf) {
        foreach ($line in Get-Content -LiteralPath $ledger) {
            if ([string]::IsNullOrWhiteSpace($line)) { continue }
            $entry = $line | ConvertFrom-Json
            $cost = if ($entry.PSObject.Properties["cost_usd"]) { [decimal]$entry.cost_usd } else { [decimal]0 }
            if (-not [string]::IsNullOrWhiteSpace($CycleId) -and [string]$entry.cycle_id -eq $CycleId) { $cycleSpend += $cost }
            if ([string]$entry.date_utc -eq $today) { $daySpend += $cost }
        }
    }

    $ok = ($cycleSpend -lt $cycleCeiling -and ($daySpend + $cycleCeiling) -le $dayCeiling)
    $reason = if ($cycleSpend -ge $cycleCeiling) { "CYCLE_COST_CEILING_EXCEEDED" } elseif (($daySpend + $cycleCeiling) -gt $dayCeiling) { "DAY_COST_CEILING_EXCEEDED" } else { "" }
    return [pscustomobject]@{ ok = $ok; cycle_spend = $cycleSpend; day_spend = $daySpend; cycle_ceiling = $cycleCeiling; day_ceiling = $dayCeiling; reason = $reason }
} catch {
    return [pscustomobject]@{ ok = $false; cycle_spend = 0; day_spend = 0; cycle_ceiling = 0; day_ceiling = 0; reason = "COST_CHECK_FAILED:$($_.Exception.Message)" }
}
