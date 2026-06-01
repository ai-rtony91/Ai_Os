$ErrorActionPreference = "Stop"

Write-Host "AI_OS Stage 51-60 Documentation Consolidation DRY_RUN Validator"
Write-Host "Mode: DRY_RUN ONLY"
Write-Host ""

$repoRoot = (& git rev-parse --show-toplevel).Trim()
$branch = (& git branch --show-current).Trim()
$gitStatus = & git status --short

Write-Host "Task name: AI_OS Stage 51-60 documentation consolidation validation"
Write-Host "Mode: DRY_RUN ONLY"
Write-Host "Repo root: $repoRoot"
Write-Host "Current git branch: $branch"
Write-Host "Current git status:"
if ($gitStatus) {
    $gitStatus | ForEach-Object { Write-Host $_ }
} else {
    Write-Host "CLEAN"
}
Write-Host ""

$legacyDocsAiosExpectedFiles = @(
    "Reports/health/STAGE51_60_DOCUMENTATION_CONSOLIDATION_README.txt",
    "automation/status/Test-AiOsDocumentationConsolidation.DRY_RUN.ps1",
    "docs/AI_OS/index/AIOS_INDEX_CATEGORY_COVERAGE_VALIDATION_DRAFT.md",
    "docs/AI_OS/index/AIOS_SOURCE_OF_TRUTH_MAPPING_DRAFT.md",
    "docs/AI_OS/index/AIOS_OWNERSHIP_PATH_PATTERN_VALIDATION_DRAFT.md",
    "docs/AI_OS/validators/AIOS_VALIDATOR_NAMING_STATUS_EXITCODE_CONVENTION_DRAFT.md",
    "docs/AI_OS/operator/AIOS_OPERATOR_DOCUMENTATION_NAVIGATION_GUIDE_DRAFT.md",
    "docs/AI_OS/runbooks/AIOS_RUNBOOK_COVERAGE_GAP_REVIEW_DRAFT.md",
    "docs/AI_OS/governance/AIOS_DOCUMENTATION_PROMOTION_CRITERIA_DRAFT.md",
    "docs/AI_OS/governance/AIOS_INVALID_DATA_AND_MISMATCH_HANDLING_DRAFT.md"
)
$expectedFiles = @(
    $legacyDocsAiosExpectedFiles
    "docs/architecture/aios-system-architecture.md",
    "docs/workflows/aios-operator-workflows.md"
)

$approvedPrefixes = @(
    "Reports/health/",
    "automation/status/",
    "docs/AI_OS/index/",
    "docs/AI_OS/validators/",
    "docs/AI_OS/operator/",
    "docs/AI_OS/runbooks/",
    "docs/AI_OS/governance/",
    "docs/architecture/",
    "docs/workflows/"
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

$requiredPhrases = @(
    "protected root files",
    "human approval",
    "no live automation"
)

$failures = New-Object System.Collections.Generic.List[string]

Write-Host "Checks performed:"
Write-Host "- Legacy docs/AI_OS source-material references only; canonical summaries remain docs/architecture and docs/workflows"
Write-Host "- Expected file existence"
Write-Host "- Approved path prefix validation"
Write-Host "- Protected root files not staged"
Write-Host "- Required boundary phrase scan"
Write-Host "- Branch/status reporting"
Write-Host ""

foreach ($file in $expectedFiles) {
    $fullPath = Join-Path $repoRoot $file
    if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
        Write-Host "PASS expected file exists: $file"
    } else {
        Write-Host "FAIL expected file missing: $file"
        $failures.Add("Missing expected file: $file")
    }

    $isApprovedPath = $false
    foreach ($prefix in $approvedPrefixes) {
        if ($file.StartsWith($prefix, [System.StringComparison]::Ordinal)) {
            $isApprovedPath = $true
            break
        }
    }
    if ($isApprovedPath) {
        Write-Host "PASS approved path: $file"
    } else {
        Write-Host "FAIL unapproved path: $file"
        $failures.Add("Unapproved path: $file")
    }
}

Write-Host ""

$stagedLines = & git diff --cached --name-only
foreach ($protected in $protectedRootFiles) {
    if ($stagedLines -contains $protected) {
        Write-Host "FAIL protected root file staged: $protected"
        $failures.Add("Protected root file staged: $protected")
    }
}
if (-not ($stagedLines | Where-Object { $protectedRootFiles -contains $_ })) {
    Write-Host "PASS protected root files are not staged"
}

Write-Host ""

$canonicalSummaryFiles = @(
    "docs/architecture/aios-system-architecture.md",
    "docs/workflows/aios-operator-workflows.md"
)
$textFiles = $expectedFiles | Where-Object { $_.EndsWith(".md") -or $_.EndsWith(".txt") }
$phraseScanFiles = $textFiles | Where-Object { $canonicalSummaryFiles -notcontains $_ }
foreach ($file in $phraseScanFiles) {
    $fullPath = Join-Path $repoRoot $file
    if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
        $content = Get-Content -LiteralPath $fullPath -Raw
        foreach ($phrase in $requiredPhrases) {
            if ($content -like "*$phrase*") {
                Write-Host "PASS phrase '$phrase' found in $file"
            } else {
                Write-Host "FAIL phrase '$phrase' missing from $file"
                $failures.Add("Required phrase missing from ${file}: $phrase")
            }
        }
    }
}
foreach ($file in $canonicalSummaryFiles) {
    if ($expectedFiles -contains $file) {
        Write-Host "INFO canonical summary checked for existence only; legacy docs folder not required: $file"
    }
}

Write-Host ""
Write-Host "Stop condition: exit 0 only on full PASS; exit 1 on any FAIL"

if ($failures.Count -eq 0) {
    Write-Host "SUMMARY: PASS"
    exit 0
}

Write-Host "SUMMARY: FAIL"
foreach ($failure in $failures) {
    Write-Host "FAIL: $failure"
}
exit 1
