[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$CycleId,
    [decimal]$Cost = 0,
    [int]$InputTokens = 0,
    [int]$OutputTokens = 0,
    [string]$PacketId = "",
    [string]$Worker = "",
    [bool]$Estimated = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$ledger = Join-Path $repoRoot "control\mode\cost_ledger.jsonl"
$entry = [ordered]@{
    utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    date_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")
    cycle_id = $CycleId
    packet_id = $PacketId
    worker = $Worker
    cost_usd = [decimal]$Cost
    input_tokens = $InputTokens
    output_tokens = $OutputTokens
    estimated = [bool]$Estimated
}

$dir = Split-Path -Parent $ledger
if (-not (Test-Path -LiteralPath $dir -PathType Container)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
Add-Content -LiteralPath $ledger -Value (($entry | ConvertTo-Json -Compress -Depth 5))
return [pscustomobject]$entry
