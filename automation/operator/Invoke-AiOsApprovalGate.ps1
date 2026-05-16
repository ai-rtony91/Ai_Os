param(
    [string]$RepoRoot = ".",
    [string]$ApprovalInboxPath = "work_packets/approvals/aios_approval_inbox.example.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $RepoRoot).Path
$path = Join-Path $root $ApprovalInboxPath
if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
    Write-Host "FAIL: Missing approval inbox: $ApprovalInboxPath" -ForegroundColor Red
    exit 1
}

$inbox = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
if ($inbox.mode -ne "DRY_RUN_ONLY") {
    Write-Host "FAIL: Approval inbox mode must be DRY_RUN_ONLY" -ForegroundColor Red
    exit 1
}

Write-Host "AI_OS Phase 3 Approval Gate"
Write-Host "Mode: DRY_RUN_ONLY"
foreach ($request in @($inbox.requests)) {
    Write-Host "$($request.request_id): $($request.packet_id) -> $($request.preview_transition)"
}
Write-Host "APPLY: BLOCKED"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
exit 0
