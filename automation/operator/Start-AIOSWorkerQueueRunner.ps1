param(
    [Parameter(Mandatory = $true)]
    [string]$WorkerId
)

if ($WorkerId -notmatch '^AIOS-\d{2}$') {
    Write-Host "BLOCKED: WorkerId must use AIOS-## format. Example: AIOS-01" -ForegroundColor Red
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Repo = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$ActiveQueue = Join-Path $ScriptDir "worker_queue\active"

Write-Host "AI_OS WORKER QUEUE RUNNER v0.1" -ForegroundColor Cyan
Write-Host "Worker ID: $WorkerId" -ForegroundColor Cyan

if (!(Test-Path $ActiveQueue)) {
    Write-Host "WARN: active worker queue folder not found: $ActiveQueue" -ForegroundColor Yellow
    Write-Host "Next safe action: verify automation/operator/worker_queue/active exists before assigning this worker." -ForegroundColor Yellow
    Write-Host "DRY_RUN only. Manual approval required before APPLY. No commits. No pushes." -ForegroundColor Magenta
    exit 0
}

$Matches = Get-ChildItem -LiteralPath $ActiveQueue -Filter "$WorkerId-*.md" -File | Sort-Object Name

if ($Matches.Count -eq 0) {
    Write-Host "WARN: no active role packet found for $WorkerId" -ForegroundColor Yellow
    Write-Host "Expected pattern: automation/operator/worker_queue/active/$WorkerId-*.md" -ForegroundColor Yellow
    Write-Host "Next safe action: create or restore one active role packet for $WorkerId, then rerun this worker." -ForegroundColor Yellow
    Write-Host "DRY_RUN only. Manual approval required before APPLY. No commits. No pushes." -ForegroundColor Magenta
    exit 0
}

if ($Matches.Count -gt 1) {
    Write-Host "WARN: multiple active role packets found for $WorkerId. Refusing to choose silently." -ForegroundColor Yellow
    foreach ($Match in $Matches) {
        Write-Host "- $($Match.FullName)" -ForegroundColor Yellow
    }
    Write-Host "Next safe action: leave exactly one active packet for $WorkerId before launching this worker." -ForegroundColor Yellow
    Write-Host "DRY_RUN only. Manual approval required before APPLY. No commits. No pushes." -ForegroundColor Magenta
    exit 0
}

$Packet = $Matches[0]
$RelativePacket = Resolve-Path -LiteralPath $Packet.FullName -Relative

Write-Host "Matched packet: $RelativePacket" -ForegroundColor Green
Write-Host ""
Write-Host "===== ROLE PACKET START =====" -ForegroundColor Cyan
Get-Content -LiteralPath $Packet.FullName
Write-Host "===== ROLE PACKET END =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next safe action: read the role packet, keep work in DRY_RUN unless the operator explicitly approves APPLY, and report findings before changes." -ForegroundColor Yellow
Write-Host "DRY_RUN only. Manual approval required before APPLY. No commits. No pushes." -ForegroundColor Magenta
