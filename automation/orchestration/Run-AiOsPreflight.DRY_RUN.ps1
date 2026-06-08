[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "AI_OS Preflight"
Write-Host "Mode: DRY_RUN"
Write-Host ""

Write-Host "Step 1: Commit package preview"
powershell -ExecutionPolicy Bypass -File "automation\orchestration\commit_packages\New-AiOsCommitPackageRecommendation.DRY_RUN.ps1"

Write-Host ""
Write-Host "Step 2: Validator chain"
powershell -ExecutionPolicy Bypass -File "automation\orchestration\validators\Invoke-OrchestrationValidatorChain.DRY_RUN.ps1"

Write-Host ""
Write-Host "Step 3: Final git status"
git status --short --branch

Write-Host ""
Write-Host "Preflight complete. No files were staged. No commit was created. No push was performed."