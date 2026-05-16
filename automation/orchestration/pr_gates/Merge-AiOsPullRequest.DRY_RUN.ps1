param(
    [Parameter(Mandatory = $true)][int]$PrNumber,
    [string]$ApprovalPath = "",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START — Merge-AiOsPullRequest.DRY_RUN.ps1"
Write-Host "AI_OS PR Merge Gate" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"

if ([string]::IsNullOrWhiteSpace($ApprovalPath)) {
    $ApprovalPath = "automation/orchestration/approvals/APPROVE_PR_$PrNumber.json"
}

if (-not (Test-Path -LiteralPath $ApprovalPath -PathType Leaf)) {
    throw "Blocked: approval file missing: $ApprovalPath"
}

$approval = Get-Content -Raw -LiteralPath $ApprovalPath | ConvertFrom-Json

if (-not $approval.approved) {
    throw "Blocked: approval file does not say approved=true."
}

if ($approval.pr_number -ne $PrNumber) {
    throw "Blocked: approval file PR number mismatch."
}

$status = @(git status --short)
if ($status | Where-Object { $_ -match "server.py" }) {
    throw "Blocked: server.py is uncommitted and must not be included."
}

$checks = cmd /c "gh pr checks $PrNumber 2>&1"; if ($LASTEXITCODE -ne 0 -and (($checks -join " ") -notmatch "no checks reported")) { throw "Blocked: PR checks failed or unavailable." }
Write-Host $checks

Write-Host "Approval: PASS"
Write-Host "PR: $PrNumber"

if ($Apply) {
    gh pr merge $PrNumber --squash --delete-branch
    Write-Host "Merge attempted: YES"
} else {
    Write-Host "Merge attempted: NO"
    Write-Host "Would run: gh pr merge $PrNumber --squash --delete-branch"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END — Merge-AiOsPullRequest.DRY_RUN.ps1"

