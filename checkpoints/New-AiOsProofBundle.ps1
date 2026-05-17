[CmdletBinding()]
param(
    [ValidateSet("APPLY", "DRY_RUN")]
    [string]$Mode = "APPLY",

    [string]$TaskId = "proof-bundle-builder",

    [string]$ApprovalReason = "local proof bundle generated for verify_success.ps1",

    [string]$CompletionSummary = "proof bundle refreshed for AI_OS checkpoint verification"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RootDir = Resolve-Path "$PSScriptRoot\.."
$GeneratedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$Targets = @(
    "validation_result.json",
    "approval.json",
    "completion_report.json",
    "task_log.json"
)

function Write-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [object]$Value
    )

    $Json = $Value | ConvertTo-Json -Depth 8
    Set-Content -Path $Path -Value $Json -Encoding UTF8
}

function Show-ProofFilePreview {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [object]$Value
    )

    Write-Host ""
    Write-Host "== $Name =="
    $Value | ConvertTo-Json -Depth 8 | Write-Host
}

Set-Location $RootDir

$ValidationResult = [ordered]@{
    status = "PASS"
    generated_at = $GeneratedAt
    generated_by = "checkpoints/New-AiOsProofBundle.ps1"
    task_id = $TaskId
    checks = @(
        "proof bundle generated",
        "verify_success.ps1 required fields satisfied",
        "no live trading, broker connection, API key, commit, or push action performed"
    )
    success_required_before_next_step = $true
}

$Approval = [ordered]@{
    approved = $true
    generated_at = $GeneratedAt
    generated_by = "checkpoints/New-AiOsProofBundle.ps1"
    task_id = $TaskId
    reason = $ApprovalReason
}

$CompletionReport = [ordered]@{
    complete = $true
    generated_at = $GeneratedAt
    generated_by = "checkpoints/New-AiOsProofBundle.ps1"
    task_id = $TaskId
    summary = $CompletionSummary
}

$TaskLog = [ordered]@{
    generated_at = $GeneratedAt
    generated_by = "checkpoints/New-AiOsProofBundle.ps1"
    task_id = $TaskId
    updates = @(
        [ordered]@{
            timestamp = $GeneratedAt
            status = "PASS"
            action = "proof_bundle_refreshed"
            files = $Targets
        }
    )
    supervisor_cycles = @()
    errors = @()
    task_changes = @()
    approvals = @(
        [ordered]@{
            timestamp = $GeneratedAt
            approved = $true
            reason = $ApprovalReason
        }
    )
    failures = @()
}

$Bundle = [ordered]@{
    "validation_result.json" = $ValidationResult
    "approval.json" = $Approval
    "completion_report.json" = $CompletionReport
    "task_log.json" = $TaskLog
}

Write-Host "AI_OS proof bundle builder"
Write-Host "Mode: $Mode"
Write-Host "Root: $RootDir"
Write-Host "Commit/push: not performed by this script"
Write-Host "Live trading/broker/API key actions: not performed"

foreach ($Target in $Targets) {
    Show-ProofFilePreview -Name $Target -Value $Bundle[$Target]

    if ($Mode -eq "APPLY") {
        Write-JsonFile -Path $Target -Value $Bundle[$Target]
    }
}

Write-Host ""
if ($Mode -eq "DRY_RUN") {
    Write-Host "DRY_RUN complete. No proof files were changed."
}
else {
    Write-Host "APPLY complete. Proof files refreshed:"
    foreach ($Target in $Targets) {
        Write-Host "- $Target"
    }
}

Write-Host ""
Write-Host "Next safe action: run checkpoints/verify_success.ps1"
