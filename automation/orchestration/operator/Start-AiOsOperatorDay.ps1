Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START — Start-AiOsOperatorDay.ps1"
Write-Host "AI_OS DAILY OPERATOR" -ForegroundColor Cyan
Write-Host ""

Write-Host "STEP 1 — GIT STATUS" -ForegroundColor Yellow
git status --short --branch

Write-Host ""
Write-Host "STEP 2 — ACTIVE BRANCH" -ForegroundColor Yellow
$branch = git branch --show-current
Write-Host "Branch: $branch"

Write-Host ""
Write-Host "STEP 3 — NEXT STEP DETECTOR" -ForegroundColor Yellow

powershell -ExecutionPolicy Bypass -File `
automation/orchestration/next_step/Resolve-AiOsNextStep.DRY_RUN.ps1

Write-Host ""
Write-Host "STEP 4 — OPEN PRS" -ForegroundColor Yellow
gh pr list

Write-Host ""
Write-Host "STEP 5 — RECOMMENDED NEXT COMMAND" -ForegroundColor Yellow

Write-Host ""
Write-Host "Recommended:"
Write-Host "powershell -ExecutionPolicy Bypass -File automation/orchestration/next_step/Resolve-AiOsNextStep.DRY_RUN.ps1"

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END — Start-AiOsOperatorDay.ps1"
