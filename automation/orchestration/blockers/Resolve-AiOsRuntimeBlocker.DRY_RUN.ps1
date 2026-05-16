param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$health = powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$next = powershell -ExecutionPolicy Bypass -File automation/orchestration/next_step/Resolve-AiOsNextStep.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json

$severity = "NONE"
$blocker = "No blocker detected."
$fix = "Run operator day."

if ($health.health -eq "BLOCKED") {
    $severity = "BLOCKED"
    $blocker = "Runtime health is blocked."
    $fix = "Run health monitor and restore missing runtime files."
}
elseif ($health.health -eq "WARNING") {
    $severity = "WARNING"
    $blocker = "Runtime health warning."
    $fix = "Clean working tree or return to main."
}
elseif ($next.status -eq "awaiting_approval") {
    $severity = "WAITING"
    $blocker = "Packet is waiting for approval."
    $fix = "Run approval processor or create approval file."
}
elseif ($next.status -eq "blocked") {
    $severity = "BLOCKED"
    $blocker = "Packet is blocked."
    $fix = "Inspect packet blocked_by and reroute."
}
elseif ($next.status -eq "failed") {
    $severity = "FAILED"
    $blocker = "Packet failed."
    $fix = "Inspect failure, fix issue, then reroute packet."
}

$result = [pscustomobject]@{
    mode = "READ_ONLY"
    severity = $severity
    blocker = $blocker
    fix = $fix
    health = $health.health
    packet_id = $next.packet_id
    packet_status = $next.status
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 6
    exit 0
}

Write-Host "COPY START - Resolve-AiOsRuntimeBlocker.DRY_RUN.ps1"
Write-Host "AI_OS Runtime Blocker Resolver" -ForegroundColor Cyan
Write-Host "severity: $severity"
Write-Host "blocker: $blocker"
Write-Host "fix: $fix"
Write-Host "health: $($health.health)"
Write-Host "packet_id: $($next.packet_id)"
Write-Host "packet_status: $($next.status)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Resolve-AiOsRuntimeBlocker.DRY_RUN.ps1"
