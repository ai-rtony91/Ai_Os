param(
    [Parameter(Mandatory = $true)][string]$Goal,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$intakePath = "automation/intake/AIOS_GOAL_INTAKE.json"
$outboxPath = "automation/outbox/AIOS_NEXT_ACTION.json"

$slug = ($Goal.ToLowerInvariant() -replace '[^a-z0-9]+','-').Trim('-')
if ([string]::IsNullOrWhiteSpace($slug)) { $slug = "goal-intake" }

$result = [ordered]@{
    mode = $(if ($Apply) { "APPLY" } else { "DRY_RUN" })
    goal = $Goal
    goal_slug = $slug
    next_action = "Create repo-scoped work packet for: $Goal"
    safety = "repo_scoped_only_no_live_trading_no_secrets_no_broker"
    created_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

if ($Apply) {
    $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $intakePath -Encoding UTF8
    $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $outboxPath -Encoding UTF8

    powershell -ExecutionPolicy Bypass -File automation/orchestration/work_packets/New-AiOsWorkPacket.ps1 `
        -Intent "Goal intake: $Goal" `
        -Title "Goal Intake - $slug" `
        -OwnerLane "goal_intake" `
        -AssignedWorker "dispatcher" `
        -Repo "ai-rtony91_Ai_Os_CLEAN" `
        -Branch (git branch --show-current) `
        -Validator "powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1" `
        -NextAction "Plan and execute next repo-scoped step for: $Goal"
}

Write-Host "AIOS Goal Intake Runner"
Write-Host "Mode: $($result.mode)"
Write-Host "Goal: $Goal"
Write-Host "Next action: $($result.next_action)"
Write-Host "Safety: $($result.safety)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
