param(
    [string]$RepoRoot = ".",
    [string]$QueueStatePath = "work_packets/state/aios_queue_state.example.json",
    [string]$ApprovalInboxPath = "work_packets/approvals/aios_approval_inbox.example.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $RepoRoot).Path
$queuePath = Join-Path $root $QueueStatePath
$approvalPath = Join-Path $root $ApprovalInboxPath
foreach ($path in @($queuePath, $approvalPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Write-Host "FAIL: Missing required state file: $path" -ForegroundColor Red
        exit 1
    }
}

$queue = Get-Content -LiteralPath $queuePath -Raw | ConvertFrom-Json
$approvals = Get-Content -LiteralPath $approvalPath -Raw | ConvertFrom-Json
if ($queue.mode -ne "DRY_RUN_ONLY" -or $approvals.mode -ne "DRY_RUN_ONLY") {
    Write-Host "FAIL: Stateful dispatcher only accepts DRY_RUN_ONLY files" -ForegroundColor Red
    exit 1
}

Write-Host "AI_OS Phase 3 Stateful Dispatcher"
Write-Host "Mode: DRY_RUN_ONLY"
Write-Host "Queue: $($queue.queue_id)"
foreach ($lane in @($queue.lanes)) {
    Write-Host "$($lane.lane): $($lane.status); current=$($lane.current_packet); backlog=$($lane.backlog_count)"
}
Write-Host "Queue state changed: NO"
Write-Host "Codex auto-launch performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
exit 0
