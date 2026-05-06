param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Test-RequiredFile {
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
    $script:failures.Add("Missing required file: $Label ($RelativePath)") | Out-Null
}

function Test-ContractSection {
    param(
        [string]$SectionName,
        [string]$ContractText
    )

    if ($ContractText -match [regex]::Escape($SectionName)) {
        Write-Host "[PASS] $SectionName"
        return
    }

    Write-Host "[FAIL] $SectionName"
    $script:failures.Add("Missing required contract section: $SectionName") | Out-Null
}

Write-Host 'Task name: AI_OS Stage 15A-15D Morning Brief Text Contract Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, or settings-changed.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Conceptual contract state: FAIL_BLOCKED'
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO MORNING BRIEF TEXT ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File checks:'
Test-RequiredFile -Label 'Morning Brief integration draft' -RelativePath 'docs\AI_OS\morning_brief\AIOS_MORNING_BRIEF_INTEGRATION_DRAFT.md'
Test-RequiredFile -Label 'Morning Brief text contract draft' -RelativePath 'docs\AI_OS\morning_brief\AIOS_MORNING_BRIEF_TEXT_CONTRACT_DRAFT.md'
Test-RequiredFile -Label 'Morning Brief state helper' -RelativePath 'automation\startup\Get-AiOsMorningBriefState.DRY_RUN.ps1'
Test-RequiredFile -Label 'snapshot history boundary validator' -RelativePath 'automation\status\Test-AiOsSnapshotHistoryBoundary.DRY_RUN.ps1'
Test-RequiredFile -Label 'report writer boundary draft' -RelativePath 'docs\AI_OS\reporting\AIOS_REPORT_WRITER_BOUNDARY_DRAFT.md'

$contractPath = Join-Path $script:ResolvedRepoRoot 'docs\AI_OS\morning_brief\AIOS_MORNING_BRIEF_TEXT_CONTRACT_DRAFT.md'
$contractText = ''
if (Test-Path -LiteralPath $contractPath -PathType Leaf) {
    $contractText = Get-Content -LiteralPath $contractPath -Raw
}

Write-Host ''
Write-Host 'Contract section checks:'
$requiredSections = @(
    'Header',
    'Repo State',
    'Workflow State',
    'Approval State',
    'Dashboard State',
    'Snapshot Boundary State',
    'Report Boundary State',
    'Pending Approvals',
    'Warnings',
    'Next Safe Action'
)

foreach ($section in $requiredSections) {
    Test-ContractSection -SectionName $section -ContractText $contractText
}

Write-Host ''
Write-Host 'Git status check:'
$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCommand) {
    Write-Host '[WARN] git command unavailable.'
    $warnings.Add('git command unavailable.') | Out-Null
}
else {
    Push-Location -LiteralPath $script:ResolvedRepoRoot
    try {
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
    $contractState = 'FAIL_BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $contractState = 'WARN_REVIEW_REQUIRED'
}
else {
    $contractState = 'READY_FOR_REVIEW'
}

Write-Host "Conceptual contract state: $contractState"
Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO MORNING BRIEF TEXT ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO MORNING BRIEF TEXT ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO MORNING BRIEF TEXT ACTIONS APPLIED.' -f [char]0x2014)
