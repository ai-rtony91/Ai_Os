$ErrorActionPreference = "Stop"

Write-Host "AI_OS Stage 91-100 Production Readiness Review DRY_RUN Validator"
Write-Host "Mode: DRY_RUN ONLY"
Write-Host ""

$repoRoot = (& git rev-parse --show-toplevel).Trim()
$branch = (& git branch --show-current).Trim()
$gitStatus = & git status --short

Write-Host "Task name: AI_OS Stage 91-100 production-readiness review validation"
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

$expectedFiles = @(
    "Reports/health/STAGE91_100_PRODUCTION_READINESS_REVIEW_README.txt",
    "automation/status/Test-AiOsProductionReadinessReview.DRY_RUN.ps1",
    "docs/AI_OS/readiness/AIOS_STAGE91_PRODUCTION_READINESS_REVIEW_DRAFT.md",
    "docs/AI_OS/security/AIOS_STAGE92_SECURITY_DEPENDENCY_RUNTIME_ISOLATION_DRAFT.md",
    "docs/AI_OS/source_control/AIOS_STAGE93_SOURCE_CONTROL_ROLLBACK_DRAFT.md",
    "docs/AI_OS/operator/AIOS_STAGE94_OPERATOR_WORKFLOW_ESCALATION_DRAFT.md",
    "docs/AI_OS/startup/AIOS_STAGE95_STARTUP_AUTOMATION_BOUNDARY_REVIEW_DRAFT.md",
    "docs/AI_OS/trading/AIOS_STAGE96_TRADING_EXECUTION_SEPARATION_REVIEW_DRAFT.md",
    "docs/AI_OS/llm/AIOS_STAGE97_LLM_LIVE_ORDER_PATH_EXCLUSION_DRAFT.md",
    "docs/AI_OS/audits/AIOS_STAGE98_FINAL_AUDIT_PACKAGE_DRAFT.md",
    "docs/AI_OS/checkpoints/AIOS_STAGE99_FINAL_HUMAN_APPROVAL_CHECKPOINT_DRAFT.md",
    "docs/AI_OS/checkpoints/AIOS_STAGE100_FINAL_APPROVAL_GATE_REVIEW_DRAFT.md"
)

$approvedPrefixes = @(
    "Reports/health/",
    "automation/status/",
    "docs/AI_OS/readiness/",
    "docs/AI_OS/security/",
    "docs/AI_OS/source_control/",
    "docs/AI_OS/operator/",
    "docs/AI_OS/startup/",
    "docs/AI_OS/trading/",
    "docs/AI_OS/llm/",
    "docs/AI_OS/audits/",
    "docs/AI_OS/checkpoints/"
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
    "no live automation",
    "production readiness is not approved",
    "no trading automation",
    "LLMs must not be placed in the live order path"
)

$failures = New-Object System.Collections.Generic.List[string]

Write-Host "Checks performed:"
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

$stagedFiles = & git diff --cached --name-only
foreach ($protected in $protectedRootFiles) {
    if ($stagedFiles -contains $protected) {
        Write-Host "FAIL protected root file staged: $protected"
        $failures.Add("Protected root file staged: $protected")
    }
}
if (-not ($stagedFiles | Where-Object { $protectedRootFiles -contains $_ })) {
    Write-Host "PASS protected root files are not staged"
}

Write-Host ""

$textFiles = $expectedFiles | Where-Object { $_.EndsWith(".md") -or $_.EndsWith(".txt") }
foreach ($file in $textFiles) {
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
