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

function Test-BooleanTrue {
    param(
        [string]$Label,
        [object]$Value
    )

    if ($Value -eq $true) {
        Write-Host "[PASS] $Label is true"
        return
    }

    Add-Failure "$Label must be true"
}

function Get-Variant {
    param(
        [object[]]$Variants,
        [string]$Name
    )

    return $Variants | Where-Object { $_.fixture_name -eq $Name }
}

Write-Host 'Task name: AI_OS Stage 30A-30D Writer Fixture Variants Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, settings-changed, broker-routed, webhook-fired, credential-accessed, secrets-accessed, telemetry-written, report-written, auto-filled, or traded.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO WRITER FIXTURE VARIANT ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File checks:'
$variantsExist = Test-RequiredFile -Label 'writer fixture variants' -RelativePath 'docs\AI_OS\writers\AIOS_WRITER_FIXTURE_VARIANTS_DRAFT.json'
Test-RequiredFile -Label 'writer fixture variant policy' -RelativePath 'docs\AI_OS\writers\AIOS_WRITER_FIXTURE_VARIANT_POLICY_DRAFT.md' | Out-Null
Test-RequiredFile -Label 'baseline writer fixture' -RelativePath 'docs\AI_OS\writers\AIOS_WRITER_DRY_RUN_OUTPUT_FIXTURE_DRAFT.json' | Out-Null
Test-RequiredFile -Label 'baseline writer fixture policy' -RelativePath 'docs\AI_OS\writers\AIOS_WRITER_FIXTURE_POLICY_DRAFT.md' | Out-Null
Test-RequiredFile -Label 'baseline writer fixture validator' -RelativePath 'automation\status\Test-AiOsWriterDryRunFixture.DRY_RUN.ps1' | Out-Null

Write-Host ''
Write-Host 'Fixture variant checks:'
if ($variantsExist) {
    $variantsPath = Join-Path $script:ResolvedRepoRoot 'docs\AI_OS\writers\AIOS_WRITER_FIXTURE_VARIANTS_DRAFT.json'
    try {
        $variantDocument = Get-Content -LiteralPath $variantsPath -Raw | ConvertFrom-Json
        Write-Host '[PASS] variant JSON parses.'

        if ($null -eq $variantDocument.fixture_variants) {
            Add-Failure 'fixture_variants array is missing'
        }
        else {
            $variants = @($variantDocument.fixture_variants)
            if ($variants.Count -gt 0) {
                Write-Host '[PASS] fixture_variants array exists.'
            }
            else {
                Add-Failure 'fixture_variants array is empty'
            }

            $requiredNames = @(
                'safe_baseline',
                'blocked_write_allowed_true',
                'blocked_credentials_present',
                'blocked_protected_file_target'
            )

            foreach ($name in $requiredNames) {
                $matches = @($variants | Where-Object { $_.fixture_name -eq $name })
                if ($matches.Length -eq 1) {
                    Write-Host "[PASS] required variant exists: $name"
                }
                else {
                    Add-Failure "required variant missing or duplicated: $name"
                }
            }

            $safe = @(Get-Variant -Variants $variants -Name 'safe_baseline')
            if ($safe.Count -eq 1) {
                if ($safe[0].expected_result -eq 'PASS') { Write-Host '[PASS] safe_baseline expected_result is PASS' } else { Add-Failure 'safe_baseline expected_result must be PASS' }
                Test-BooleanFalse -Label 'safe_baseline.write_allowed' -Value $safe[0].write_allowed
                Test-BooleanTrue -Label 'safe_baseline.approval_required' -Value $safe[0].approval_required
                if ($safe[0].approval_status -eq 'NOT_APPROVED') { Write-Host '[PASS] safe_baseline approval_status is NOT_APPROVED' } else { Add-Failure 'safe_baseline approval_status must be NOT_APPROVED' }
                foreach ($flag in @('secrets_present','credentials_present','protected_file_target','trading_execution_data_present','telemetry_persistence_requested','report_write_requested')) {
                    Test-BooleanFalse -Label "safe_baseline.safety.$flag" -Value $safe[0].safety.$flag
                }
            }

            $blockedWrite = @(Get-Variant -Variants $variants -Name 'blocked_write_allowed_true')
            if ($blockedWrite.Count -eq 1) {
                if ($blockedWrite[0].expected_result -eq 'FAIL') { Write-Host '[PASS] blocked_write_allowed_true expected_result is FAIL' } else { Add-Failure 'blocked_write_allowed_true expected_result must be FAIL' }
                Test-BooleanTrue -Label 'blocked_write_allowed_true.write_allowed' -Value $blockedWrite[0].write_allowed
            }

            $blockedCredentials = @(Get-Variant -Variants $variants -Name 'blocked_credentials_present')
            if ($blockedCredentials.Count -eq 1) {
                if ($blockedCredentials[0].expected_result -eq 'FAIL') { Write-Host '[PASS] blocked_credentials_present expected_result is FAIL' } else { Add-Failure 'blocked_credentials_present expected_result must be FAIL' }
                Test-BooleanTrue -Label 'blocked_credentials_present.safety.credentials_present' -Value $blockedCredentials[0].safety.credentials_present
            }

            $blockedProtected = @(Get-Variant -Variants $variants -Name 'blocked_protected_file_target')
            if ($blockedProtected.Count -eq 1) {
                if ($blockedProtected[0].expected_result -eq 'FAIL') { Write-Host '[PASS] blocked_protected_file_target expected_result is FAIL' } else { Add-Failure 'blocked_protected_file_target expected_result must be FAIL' }
                Test-BooleanTrue -Label 'blocked_protected_file_target.safety.protected_file_target' -Value $blockedProtected[0].safety.protected_file_target
            }
        }
    }
    catch {
        Add-Failure "variant JSON failed to parse: $($_.Exception.Message)"
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
    Write-Host ('DRY_RUN COMPLETE {0} NO WRITER FIXTURE VARIANT ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO WRITER FIXTURE VARIANT ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO WRITER FIXTURE VARIANT ACTIONS APPLIED.' -f [char]0x2014)
