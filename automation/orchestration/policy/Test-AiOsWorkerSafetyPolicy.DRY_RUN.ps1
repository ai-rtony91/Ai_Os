param(
    [Parameter(Mandatory = $true)][string]$Action,
    [string]$Path = "",
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$policyPath = "automation/orchestration/policy/AIOS_WORKER_SAFETY_POLICY.json"

if (-not (Test-Path $policyPath)) {
    throw "Safety policy missing: $policyPath"
}

$policy = Get-Content -Raw $policyPath | ConvertFrom-Json

$result = "UNKNOWN"
$reason = "Action not listed."

if ($policy.allowed_actions -contains $Action) {
    $result = "ALLOWED"
    $reason = "Action is allowed."
}

if ($policy.approval_required_actions -contains $Action) {
    $result = "APPROVAL_REQUIRED"
    $reason = "Human approval required."
}

if ($policy.human_only_actions -contains $Action) {
    $result = "BLOCKED"
    $reason = "Human-only action."
}

foreach ($blocked in @($policy.blocked_roots)) {
    if (-not [string]::IsNullOrWhiteSpace($Path) -and $Path.StartsWith($blocked)) {
        $result = "BLOCKED"
        $reason = "Path is blocked by safety policy."
    }
}

$output = [pscustomobject]@{
    mode = "READ_ONLY"
    action = $Action
    path = $Path
    result = $result
    reason = $reason
}

if ($QuietJson) {
    $output | ConvertTo-Json -Depth 6
    exit 0
}

Write-Host "COPY START - Test-AiOsWorkerSafetyPolicy.DRY_RUN.ps1"
Write-Host "AI_OS Worker Safety Policy" -ForegroundColor Cyan
Write-Host "action: $Action"
Write-Host "path: $Path"
Write-Host "result: $result"
Write-Host "reason: $reason"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Test-AiOsWorkerSafetyPolicy.DRY_RUN.ps1"
