param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Test-Component {
    param(
        [string]$Label,
        [string]$RelativePath
    )

    $path = Join-Path $script:ResolvedRepoRoot $RelativePath
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        Write-Host "[PASS] $Label`: $RelativePath"
        return
    }

    Write-Host "[FAIL] $Label`: $RelativePath"
    $script:failures.Add("Missing required component: $Label ($RelativePath)") | Out-Null
}

Write-Host 'Task name: AI_OS Stage 14A-14D Snapshot History Boundary Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, or settings-changed.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Conceptual snapshot boundary state: FAIL_BLOCKED'
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO SNAPSHOT HISTORY ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'Component checks:'
Test-Component -Label 'snapshot writer draft' -RelativePath 'docs\AI_OS\dashboard\AIOS_SNAPSHOT_WRITER_DRAFT.md'
Test-Component -Label 'persistent snapshot boundary draft' -RelativePath 'docs\AI_OS\dashboard\AIOS_PERSISTENT_SNAPSHOT_BOUNDARY_DRAFT.md'
Test-Component -Label 'report writer boundary draft' -RelativePath 'docs\AI_OS\reporting\AIOS_REPORT_WRITER_BOUNDARY_DRAFT.md'
Test-Component -Label 'dashboard snapshot helper' -RelativePath 'automation\status\Get-AiOsDashboardSnapshot.DRY_RUN.ps1'
Test-Component -Label 'Morning Brief state helper' -RelativePath 'automation\startup\Get-AiOsMorningBriefState.DRY_RUN.ps1'
Test-Component -Label 'approval queue validator' -RelativePath 'automation\status\Test-AiOsApprovalQueueValidator.DRY_RUN.ps1'

Write-Host ''
Write-Host 'Protected-file diff check:'
$protectedDiffClean = $false
$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCommand) {
    Write-Host '[FAIL] git command unavailable.'
    $failures.Add('git command unavailable for protected-file diff check.') | Out-Null
}
else {
    Push-Location -LiteralPath $script:ResolvedRepoRoot
    try {
        $protectedDiff = @(& git diff --name-only -- README.md AGENTS.md RISK_POLICY.md SOURCE_LOG.md ERROR_LOG.md HALLUCINATION_LOG.md AAR.md DAILY_REPORT.md WHITEPAPER.md Reports\DAILY_METRICS.csv Reports\CHECKPOINT_INDEX.md 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Write-Host '[FAIL] protected-file diff check failed.'
            $protectedDiff | ForEach-Object { Write-Host $_ }
            $failures.Add('protected-file diff check failed.') | Out-Null
        }
        elseif ($protectedDiff.Count -gt 0) {
            Write-Host '[FAIL] protected files changed:'
            $protectedDiff | ForEach-Object { Write-Host "- $_" }
            $failures.Add('protected files changed.') | Out-Null
        }
        else {
            Write-Host '[PASS] protected-file diff is clean.'
            $protectedDiffClean = $true
        }

        Write-Host ''
        Write-Host 'Git status check:'
        $gitStatus = @(& git status --short --branch 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Write-Host '[WARN] git status failed.'
            $gitStatus | ForEach-Object { Write-Host $_ }
            $warnings.Add('git status failed.') | Out-Null
        }
        else {
            $gitStatus | ForEach-Object { Write-Host $_ }
            if ($gitStatus.Count -gt 1) {
                Write-Host '[WARN] git status is not clean.'
                $warnings.Add('git status is not clean.') | Out-Null
            }
            else {
                Write-Host '[PASS] git status has no listed changes.'
            }
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host ''
if ($failures.Count -gt 0) {
    $boundaryState = 'FAIL_BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $boundaryState = 'WARN_REVIEW_REQUIRED'
}
elseif ($protectedDiffClean) {
    $boundaryState = 'READY_FOR_REVIEW'
}
else {
    $boundaryState = 'FAIL_BLOCKED'
}

Write-Host "Conceptual snapshot boundary state: $boundaryState"
Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO SNAPSHOT HISTORY ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO SNAPSHOT HISTORY ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO SNAPSHOT HISTORY ACTIONS APPLIED.' -f [char]0x2014)
