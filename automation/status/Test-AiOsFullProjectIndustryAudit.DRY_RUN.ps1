param(
    [string]$RepoRoot = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
)

$ErrorActionPreference = "Stop"

Write-Host "Task name: AI_OS Stage 47 Full Project Industry Standard Audit Dry Run"
Write-Host "Mode: DRY_RUN"
Write-Host "Repo root: $RepoRoot"
Write-Host "Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, screenshots-captured, videos-captured, settings-changed, broker-routed, webhook-fired, credential-accessed, secrets-accessed, telemetry-written, report-written, dashboard-written, background-service-created, autonomous-action-enabled, or traded."
Write-Host ""

$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Test-RequiredFile {
    param(
        [string]$Label,
        [string]$RelativePath
    )

    $fullPath = Join-Path $RepoRoot $RelativePath
    if (Test-Path -LiteralPath $fullPath) {
        Write-Host "[PASS] ${Label}: $RelativePath"
        return $true
    }

    Write-Host "[FAIL] ${Label}: missing $RelativePath"
    $script:failures.Add("Missing required file: $RelativePath")
    return $false
}

function Test-RequiredPhrase {
    param(
        [string]$Phrase,
        [string]$RelativePath
    )

    $fullPath = Join-Path $RepoRoot $RelativePath
    if ((Test-Path -LiteralPath $fullPath) -and ((Get-Content -LiteralPath $fullPath -Raw) -match [regex]::Escape($Phrase))) {
        Write-Host "[PASS] $Phrase"
        return $true
    }

    Write-Host "[FAIL] $Phrase"
    $script:failures.Add("Missing required audit phrase: $Phrase")
    return $false
}

Push-Location $RepoRoot
try {
    $auditReport = "docs\AI_OS\audits\AIOS_FULL_PROJECT_INDUSTRY_STANDARD_AUDIT_DRAFT.md"
    $decisionMatrix = "docs\AI_OS\audits\AIOS_FULL_PROJECT_AUDIT_DECISION_MATRIX_DRAFT.json"
    $refactorRecommendations = "docs\AI_OS\audits\AIOS_FULL_PROJECT_REFACTOR_RECOMMENDATIONS_DRAFT.md"
    $validator = "automation\status\Test-AiOsFullProjectIndustryAudit.DRY_RUN.ps1"
    $readme = "Reports\health\STAGE47_FULL_PROJECT_INDUSTRY_AUDIT_README.txt"

    Write-Host "File checks:"
    Test-RequiredFile "full project audit report" $auditReport | Out-Null
    Test-RequiredFile "full project audit decision matrix" $decisionMatrix | Out-Null
    Test-RequiredFile "full project refactor recommendations" $refactorRecommendations | Out-Null
    Test-RequiredFile "full project industry audit validator" $validator | Out-Null
    Test-RequiredFile "Stage 47 health README" $readme | Out-Null

    Write-Host ""
    Write-Host "Decision matrix JSON parse check:"
    if (Test-Path -LiteralPath (Join-Path $RepoRoot $decisionMatrix)) {
        try {
            $matrix = Get-Content -LiteralPath (Join-Path $RepoRoot $decisionMatrix) -Raw | ConvertFrom-Json
            Write-Host "[PASS] decision matrix JSON parses."
            $validStatuses = @("PASS", "REVIEW", "NEEDS_REFACTOR", "BLOCKED")
            foreach ($entry in $matrix.entries) {
                if ($validStatuses -notcontains $entry.current_status) {
                    Write-Host "[FAIL] invalid current_status for $($entry.audit_area): $($entry.current_status)"
                    $failures.Add("Invalid current_status in decision matrix.")
                }
            }
        } catch {
            Write-Host "[FAIL] decision matrix JSON parse failed."
            $failures.Add("Decision matrix JSON parse failed.")
        }
    }

    Write-Host ""
    Write-Host "Audit report phrase checks:"
    $phrases = @(
        "full project audit",
        "industry standard",
        "AI agent governance",
        "protected-file boundaries",
        "DRY_RUN",
        "human approval",
        "trading-system separation",
        "low-latency execution path",
        "credential safety",
        "refactor recommendations",
        "continue stages"
    )

    foreach ($phrase in $phrases) {
        Test-RequiredPhrase $phrase $auditReport | Out-Null
    }

    $protectedPaths = @(
        "README.md",
        "AGENTS.md",
        "RISK_POLICY.md",
        "SOURCE_LOG.md",
        "ERROR_LOG.md",
        "HALLUCINATION_LOG.md",
        "AAR.md",
        "DAILY_REPORT.md",
        "WHITEPAPER.md",
        "Reports\DAILY_METRICS.csv",
        "Reports\CHECKPOINT_INDEX.md"
    )

    Write-Host ""
    Write-Host "Unstaged protected-file check:"
    $unstaged = @(git diff --name-only -- $protectedPaths)
    if ($unstaged.Count -eq 0) {
        Write-Host "[PASS] unstaged protected-file check is clean."
    } else {
        Write-Host "[FAIL] unstaged protected-file changes detected:"
        $unstaged | ForEach-Object { Write-Host " - $_" }
        $failures.Add("Unstaged protected-file changes detected.")
    }

    Write-Host ""
    Write-Host "Staged protected-file check:"
    $staged = @(git diff --cached --name-only -- $protectedPaths)
    if ($staged.Count -eq 0) {
        Write-Host "[PASS] staged protected-file check is clean."
    } else {
        Write-Host "[FAIL] staged protected-file changes detected:"
        $staged | ForEach-Object { Write-Host " - $_" }
        $failures.Add("Staged protected-file changes detected.")
    }

    Write-Host ""
    Write-Host "Git status check:"
    $gitStatus = @(git status --short --branch)
    $gitStatus | ForEach-Object { Write-Host $_ }
    if ($gitStatus.Count -gt 1) {
        Write-Host "[WARN] git status is not clean."
        $warnings.Add("git status is not clean.")
    } else {
        Write-Host "[PASS] git status has no file changes."
    }

    Write-Host ""
    if ($failures.Count -gt 0) {
        Write-Host "PASS/WARN/FAIL summary: FAIL"
        $failures | ForEach-Object { Write-Host "- $_" }
    } elseif ($warnings.Count -gt 0) {
        Write-Host "PASS/WARN/FAIL summary: WARN"
        $warnings | ForEach-Object { Write-Host "- $_" }
    } else {
        Write-Host "PASS/WARN/FAIL summary: PASS"
    }
}
finally {
    Pop-Location
}

Write-Host "DRY_RUN COMPLETE - NO FULL PROJECT INDUSTRY AUDIT ACTIONS APPLIED."
