param(
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START - New-AiOsTaskFromNextStep.DRY_RUN.ps1"
Write-Host "AI_OS Auto Task Generator" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"

$next = powershell -ExecutionPolicy Bypass -File automation/orchestration/next_step/Resolve-AiOsNextStep.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json

$intent = "Auto task from next step: $($next.next_step)"
$title = "Auto Task - $($next.status)"
$ownerLane = "route_dispatch"
$worker = "task_generator"
$repo = "ai-rtony91/Ai_Os"
$branch = git branch --show-current
$validator = "powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
$nextAction = $next.next_step

Write-Host ""
Write-Host "NEXT STEP SOURCE"
Write-Host "packet_id: $($next.packet_id)"
Write-Host "status: $($next.status)"
Write-Host "next_step: $($next.next_step)"

Write-Host ""
Write-Host "GENERATED TASK"
Write-Host "title: $title"
Write-Host "intent: $intent"
Write-Host "owner_lane: $ownerLane"
Write-Host "worker: $worker"
Write-Host "branch: $branch"

if ($Apply) {
    powershell -ExecutionPolicy Bypass -File automation/orchestration/work_packets/New-AiOsWorkPacket.ps1 `
    -Intent $intent `
    -Title $title `
    -OwnerLane $ownerLane `
    -AssignedWorker $worker `
    -Repo $repo `
    -Branch $branch `
    -Validator $validator `
    -NextAction $nextAction

    Write-Host "Task packet created: YES"
} else {
    Write-Host "Task packet created: NO"
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - New-AiOsTaskFromNextStep.DRY_RUN.ps1"
