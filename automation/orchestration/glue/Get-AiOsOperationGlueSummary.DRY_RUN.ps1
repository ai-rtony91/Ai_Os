[CmdletBinding()]
param(
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-AiOsJsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try { return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json } catch { return $null }
}

function Get-AiOsLatestJson {
    param([string]$Directory)
    if (-not (Test-Path -LiteralPath $Directory -PathType Container)) { return $null }
    $file = Get-ChildItem -LiteralPath $Directory -Filter "*.json" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $file) { return $null }
    $json = Read-AiOsJsonFile -Path $file.FullName
    return [pscustomobject]@{
        path = $file.FullName.Substring((Resolve-Path ".").Path.Length + 1)
        json = $json
    }
}

$goal = Read-AiOsJsonFile -Path "control/operation_glue/GOAL_INTAKE.example.json"
$packet = Get-AiOsLatestJson -Directory "control/operation_glue/worker_packets"
$result = Get-AiOsLatestJson -Directory "telemetry/operation_glue/worker_results"
$inbox = Read-AiOsJsonFile -Path "control/operation_glue/APPROVAL_INBOX.json"

$nextSafeAction = "Generate a worker packet from the latest goal intake."
if ($inbox -and $inbox.next_safe_action) {
    $nextSafeAction = [string]$inbox.next_safe_action
}
elseif ($result -and $result.json.next_safe_action) {
    $nextSafeAction = [string]$result.json.next_safe_action
}
elseif ($packet -and $packet.json.next_safe_action) {
    $nextSafeAction = [string]$packet.json.next_safe_action
}

$summary = [ordered]@{
    schema               = "AIOS_OPERATION_GLUE_SUPERVISOR_SUMMARY.v0_1"
    mode                 = "DRY_RUN"
    latest_goal_id       = if ($goal) { [string]$goal.goal_id } else { "MISSING" }
    latest_worker_packet = if ($packet) { $packet.path } else { "MISSING" }
    latest_worker_result = if ($result) { $result.path } else { "MISSING" }
    approval_inbox       = if ($inbox) { "control/operation_glue/APPROVAL_INBOX.json" } else { "MISSING" }
    approval_items       = if ($inbox) { [int]$inbox.item_count } else { 0 }
    blocked_items        = if ($inbox) { [int]$inbox.blocked_count } else { 0 }
    next_safe_action     = $nextSafeAction
    did_not              = @(
        "Did not stage files",
        "Did not commit",
        "Did not push",
        "Did not merge",
        "Did not reset",
        "Did not clean",
        "Did not delete branches",
        "Did not touch broker, OANDA, wallet, secrets, deploy, or live trading files"
    )
}

if ($OutputJson) {
    $summary | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Operation Glue Summary"
Write-Host ("Latest goal: {0}" -f $summary.latest_goal_id)
Write-Host ("Latest worker packet: {0}" -f $summary.latest_worker_packet)
Write-Host ("Latest worker result: {0}" -f $summary.latest_worker_result)
Write-Host ("Approval inbox: {0}" -f $summary.approval_inbox)
Write-Host ("Approval items: {0}" -f $summary.approval_items)
Write-Host ("Blocked items: {0}" -f $summary.blocked_items)
Write-Host ("Next safe action: {0}" -f $summary.next_safe_action)
Write-Host "No commit, push, merge, reset, clean, branch deletion, or protected action performed."
Write-Host ""
$summary | ConvertTo-Json -Depth 8
