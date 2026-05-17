[CmdletBinding()]
param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-AiOsChangedPath {
    param([string]$StatusLine)

    if ([string]::IsNullOrWhiteSpace($StatusLine) -or $StatusLine.Length -lt 4) {
        return $null
    }

    $path = $StatusLine.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }

    return ($path -replace "\\", "/")
}

$statusLines = @(git status --short)
if ($LASTEXITCODE -ne 0) {
    throw "git status --short failed."
}

$changedFiles = @(
    foreach ($line in $statusLines) {
        $path = Get-AiOsChangedPath -StatusLine $line
        if ($null -ne $path) { $path }
    }
) | Sort-Object -Unique

$recommendedValidatorCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
$reason = "Default read-only runtime health validator for current repo state."
$approvalRequired = "NO"

if ($changedFiles.Count -eq 0) {
    $reason = "No changed files detected; run health check only if the operator wants a fresh status."
}
elseif ($changedFiles | Where-Object { $_ -like "*.ps1" }) {
    $recommendedValidatorCommand = "PowerShell parser check for changed .ps1 files, then git diff --check"
    $reason = "PowerShell files changed and should parse before any staging decision."
}
elseif ($changedFiles | Where-Object { $_ -like "*.json" }) {
    $recommendedValidatorCommand = "JSON parse check for changed .json files, then git diff --check"
    $reason = "JSON files changed and should parse before any staging decision."
}
elseif ($changedFiles | Where-Object { $_ -eq ".gitignore" }) {
    $recommendedValidatorCommand = "git diff --check; git check-ignore -v --no-index <runtime-paths>"
    $reason = ".gitignore changed and runtime ignore matching should be verified."
}
elseif ($changedFiles | Where-Object { $_ -like "automation/orchestration/commit_packages/*" }) {
    $recommendedValidatorCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1"
    $reason = "Commit package tooling changed; run the read-only recommendation preview."
}
elseif ($changedFiles | Where-Object { $_ -like "automation/orchestration/approval_inbox/*" }) {
    $recommendedValidatorCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-ApprovalInboxIntegrity.DRY_RUN.ps1"
    $reason = "Approval inbox files changed; validate inbox schema and readiness."
}
elseif ($changedFiles | Where-Object { $_ -like "automation/orchestration/locks/*" }) {
    $recommendedValidatorCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1"
    $reason = "Lock files changed; validate lock registry integrity."
}

if ($changedFiles | Where-Object { $_ -like "apps/dashboard/*" -or $_ -like "apps/trading_lab/*" -or $_ -like "automation/trading_lab/*" -or $_ -like "aios/modules/trader/*" }) {
    $approvalRequired = "YES"
    $reason = "$reason Blocked or high-risk application/trading path present; human review required."
}

$result = [ordered]@{
    schema = "aios_validator_recommendation.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    changed_files = $changedFiles
    recommended_validator_command = $recommendedValidatorCommand
    reason = $reason
    approval_required = $approvalRequired
    blocked_actions = @("run_apply_without_approval", "stage_without_review", "commit_without_package", "push_without_approval")
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AIOS Validator Recommendation"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host ""
Write-Host "changed_files:"
if ($changedFiles.Count -eq 0) { Write-Host "- none" } else { $changedFiles | ForEach-Object { Write-Host "- $_" } }
Write-Host ""
Write-Host "recommended_validator_command:"
Write-Host $recommendedValidatorCommand
Write-Host ""
Write-Host "reason:"
Write-Host $reason
Write-Host ""
Write-Host "approval_required:"
Write-Host $approvalRequired
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
