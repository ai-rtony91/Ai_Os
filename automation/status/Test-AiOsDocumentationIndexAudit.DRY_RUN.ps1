$ErrorActionPreference = "Stop"

Write-Host "AI_OS Stage 47-50 Documentation Index Audit DRY_RUN Validator"
Write-Host "Mode: DRY_RUN ONLY"
Write-Host ""

$repoRoot = (& git rev-parse --show-toplevel).Trim()
$branch = (& git branch --show-current).Trim()
$gitStatus = & git status --short

Write-Host "Repo root: $repoRoot"
Write-Host "Current git branch: $branch"
Write-Host "Current git status:"
if ($gitStatus) {
    $gitStatus | ForEach-Object { Write-Host $_ }
} else {
    Write-Host "CLEAN"
}
Write-Host ""

$expectedFiles = @(
    "Reports/health/STAGE47_50_DOCUMENTATION_INDEX_AUDIT_README.txt",
    "automation/status/Test-AiOsDocumentationIndexAudit.DRY_RUN.ps1",
    "docs/AI_OS/index/AIOS_DOCUMENTATION_INDEX_DRAFT.md",
    "docs/AI_OS/index/AIOS_FILE_OWNERSHIP_INDEX_DRAFT.md",
    "docs/AI_OS/audits/AIOS_STAGE47_50_FULL_PROJECT_INDUSTRY_STANDARD_AUDIT_DRAFT.md",
    "docs/AI_OS/audits/AIOS_AUDIT_DECISION_MATRIX_DRAFT.json",
    "docs/AI_OS/roadmap/AIOS_STAGE_50_TO_100_ROADMAP_DRAFT.md"
)

$protectedRootFiles = @(
    "README.md",
    "WHITEPAPER.md",
    "ARCHITECTURE.md",
    "RISK_POLICY.md",
    "DEPLOYMENT.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "CLAUDE.md",
    "TODO.md",
    "REQUIREMENTS.md",
    "SOURCE_LOG.md",
    "ERROR_LOG.md",
    "HALLUCINATION_LOG.md",
    "DAILY_REPORT.md",
    "AAR.md"
)

$failures = New-Object System.Collections.Generic.List[string]

foreach ($file in $expectedFiles) {
    $fullPath = Join-Path $repoRoot $file
    if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
        Write-Host "PASS expected file exists: $file"
    } else {
        Write-Host "FAIL expected file missing: $file"
        $failures.Add("Missing expected file: $file")
    }
}

Write-Host ""

$changedFiles = @()
$statusLines = & git status --short
foreach ($line in $statusLines) {
    if ($line.Length -ge 4) {
        $changedFiles += $line.Substring(3)
    }
}

foreach ($protected in $protectedRootFiles) {
    if ($changedFiles -contains $protected) {
        Write-Host "FAIL protected root file targeted: $protected"
        $failures.Add("Protected root file targeted: $protected")
    }
}

if (-not ($changedFiles | Where-Object { $protectedRootFiles -contains $_ })) {
    Write-Host "PASS protected root files were not targeted"
}

Write-Host ""

$jsonPath = Join-Path $repoRoot "docs/AI_OS/audits/AIOS_AUDIT_DECISION_MATRIX_DRAFT.json"
try {
    $null = Get-Content -LiteralPath $jsonPath -Raw | ConvertFrom-Json
    Write-Host "PASS JSON audit matrix parses as valid JSON"
} catch {
    Write-Host "FAIL JSON audit matrix did not parse"
    $failures.Add("JSON parse failed: docs/AI_OS/audits/AIOS_AUDIT_DECISION_MATRIX_DRAFT.json")
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "SUMMARY: PASS"
    exit 0
}

Write-Host "SUMMARY: FAIL"
foreach ($failure in $failures) {
    Write-Host "FAIL: $failure"
}
exit 1
