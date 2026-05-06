param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Add-Failure {
    param([string]$Message)
    Write-Host "[FAIL] $Message"
    $script:failures.Add($Message) | Out-Null
}

function Test-RequiredFile {
    param(
        [string]$Label,
        [string]$RelativePath
    )

    $path = Join-Path $script:ResolvedRepoRoot $RelativePath
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        Write-Host "[PASS] $Label`: $RelativePath"
        return $true
    }

    Add-Failure "Missing required file: $Label ($RelativePath)"
    return $false
}

function Test-BooleanFalse {
    param(
        [string]$Label,
        [object]$Value
    )

    if ($Value -eq $false) {
        Write-Host "[PASS] $Label is false"
        return
    }

    Add-Failure "$Label must be false"
}

Write-Host 'Task name: AI_OS Stage 29A-29D Writer DRY_RUN Fixture Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, settings-changed, broker-routed, webhook-fired, credential-accessed, secrets-accessed, telemetry-written, report-written, auto-filled, or traded.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO WRITER FIXTURE ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File checks:'
$fixtureExists = Test-RequiredFile -Label 'writer DRY_RUN output fixture' -RelativePath 'docs\AI_OS\writers\AIOS_WRITER_DRY_RUN_OUTPUT_FIXTURE_DRAFT.json'
Test-RequiredFile -Label 'writer fixture policy' -RelativePath 'docs\AI_OS\writers\AIOS_WRITER_FIXTURE_POLICY_DRAFT.md' | Out-Null
Test-RequiredFile -Label 'writer output schema draft' -RelativePath 'docs\AI_OS\writers\AIOS_WRITER_OUTPUT_SCHEMA_DRAFT.md' | Out-Null
Test-RequiredFile -Label 'writer output schema boundary' -RelativePath 'docs\AI_OS\writers\AIOS_WRITER_OUTPUT_SCHEMA_BOUNDARY_DRAFT.md' | Out-Null

Write-Host ''
Write-Host 'Fixture JSON checks:'
if ($fixtureExists) {
    $fixturePath = Join-Path $script:ResolvedRepoRoot 'docs\AI_OS\writers\AIOS_WRITER_DRY_RUN_OUTPUT_FIXTURE_DRAFT.json'
    try {
        $fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json
        Write-Host '[PASS] fixture JSON parses.'

        Test-BooleanFalse -Label 'write_allowed' -Value $fixture.write_allowed

        if ($fixture.approval_required -eq $true) {
            Write-Host '[PASS] approval_required is true'
        }
        else {
            Add-Failure 'approval_required must be true'
        }

        if ($fixture.approval_status -eq 'NOT_APPROVED') {
            Write-Host '[PASS] approval_status is NOT_APPROVED'
        }
        else {
            Add-Failure 'approval_status must be NOT_APPROVED'
        }

        $safetyFlags = @(
            'secrets_present',
            'credentials_present',
            'protected_file_target',
            'trading_execution_data_present',
            'telemetry_persistence_requested',
            'report_write_requested'
        )

        foreach ($flag in $safetyFlags) {
            Test-BooleanFalse -Label "safety.$flag" -Value $fixture.safety.$flag
        }
    }
    catch {
        Add-Failure "fixture JSON failed to parse: $($_.Exception.Message)"
    }
}

$protectedPaths = @(
    'README.md',
    'AGENTS.md',
    'RISK_POLICY.md',
    'SOURCE_LOG.md',
    'ERROR_LOG.md',
    'HALLUCINATION_LOG.md',
    'AAR.md',
    'DAILY_REPORT.md',
    'WHITEPAPER.md',
    'Reports\DAILY_METRICS.csv',
    'Reports\CHECKPOINT_INDEX.md'
)

Write-Host ''
$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCommand) {
    Write-Host '[WARN] git command unavailable.'
    $warnings.Add('git command unavailable.') | Out-Null
}
else {
    Push-Location -LiteralPath $script:ResolvedRepoRoot
    try {
        Write-Host 'Unstaged protected-file check:'
        $protectedDiff = @(& git diff --name-only -- $protectedPaths 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Add-Failure 'unstaged protected-file check failed.'
            $protectedDiff | ForEach-Object { Write-Host $_ }
        }
        elseif ($protectedDiff.Count -gt 0) {
            Add-Failure 'unstaged protected files changed.'
            $protectedDiff | ForEach-Object { Write-Host $_ }
        }
        else {
            Write-Host '[PASS] unstaged protected-file check is clean.'
        }

        Write-Host ''
        Write-Host 'Staged protected-file check:'
        $cachedProtectedDiff = @(& git diff --cached --name-only -- $protectedPaths 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Add-Failure 'staged protected-file check failed.'
            $cachedProtectedDiff | ForEach-Object { Write-Host $_ }
        }
        elseif ($cachedProtectedDiff.Count -gt 0) {
            Add-Failure 'staged protected files changed.'
            $cachedProtectedDiff | ForEach-Object { Write-Host $_ }
        }
        else {
            Write-Host '[PASS] staged protected-file check is clean.'
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
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO WRITER FIXTURE ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO WRITER FIXTURE ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO WRITER FIXTURE ACTIONS APPLIED.' -f [char]0x2014)
