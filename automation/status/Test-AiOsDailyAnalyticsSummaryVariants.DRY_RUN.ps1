param(
    [string]$RepoRoot = 'C:\Dev\Ai.Os'
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

function Get-Variant {
    param(
        [object[]]$Variants,
        [string]$Name
    )

    return $Variants | Where-Object { $_.variant_name -eq $Name }
}

Write-Host 'Task name: AI_OS Stage 35A-35D Daily Analytics Summary Variants Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, settings-changed, broker-routed, webhook-fired, credential-accessed, secrets-accessed, telemetry-written, report-written, auto-filled, or traded.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO DAILY ANALYTICS SUMMARY VARIANT ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File checks:'
$variantsExist = Test-RequiredFile -Label 'analytics summary variants' -RelativePath 'docs\AI_OS\analytics\AIOS_DAILY_ANALYTICS_SUMMARY_VARIANTS_DRAFT.json'
Test-RequiredFile -Label 'analytics variant policy' -RelativePath 'docs\AI_OS\analytics\AIOS_DAILY_ANALYTICS_VARIANT_POLICY_DRAFT.md' | Out-Null
Test-RequiredFile -Label 'Stage 34 schema' -RelativePath 'docs\AI_OS\analytics\AIOS_DAILY_ANALYTICS_SUMMARY_SCHEMA_DRAFT.md' | Out-Null
Test-RequiredFile -Label 'Stage 34 fixture' -RelativePath 'docs\AI_OS\analytics\AIOS_DAILY_ANALYTICS_SUMMARY_FIXTURE_DRAFT.json' | Out-Null
Test-RequiredFile -Label 'Stage 34 schema validator' -RelativePath 'automation\status\Test-AiOsDailyAnalyticsSummarySchema.DRY_RUN.ps1' | Out-Null

Write-Host ''
Write-Host 'Variant checks:'
if ($variantsExist) {
    $variantsPath = Join-Path $script:ResolvedRepoRoot 'docs\AI_OS\analytics\AIOS_DAILY_ANALYTICS_SUMMARY_VARIANTS_DRAFT.json'
    try {
        $variantDocument = Get-Content -LiteralPath $variantsPath -Raw | ConvertFrom-Json
        Write-Host '[PASS] variant JSON parses.'

        if ($null -eq $variantDocument.analytics_summary_variants) {
            Add-Failure 'analytics_summary_variants array is missing'
        }
        else {
            $variants = @($variantDocument.analytics_summary_variants)
            if ($variants.Count -gt 0) {
                Write-Host '[PASS] analytics_summary_variants array exists.'
            }
            else {
                Add-Failure 'analytics_summary_variants array is empty'
            }

            foreach ($name in @('safe_baseline','blocked_missing_repo_size','blocked_progress_percent_invalid','blocked_live_trading_data_present')) {
                $matches = @($variants | Where-Object { $_.variant_name -eq $name })
                if ($matches.Length -eq 1) {
                    Write-Host "[PASS] required variant exists: $name"
                }
                else {
                    Add-Failure "required variant missing or duplicated: $name"
                }
            }

            $safe = Get-Variant -Variants $variants -Name 'safe_baseline'
            if ($safe.Count -eq 1) {
                if ($safe[0].expected_result -eq 'PASS') { Write-Host '[PASS] safe_baseline expected_result is PASS' } else { Add-Failure 'safe_baseline expected_result must be PASS' }
                if ($safe[0].sections.'Repo Size' -eq $true) { Write-Host '[PASS] safe_baseline includes Repo Size' } else { Add-Failure 'safe_baseline must include Repo Size' }
                if ($safe[0].sections.'Progress Percent' -eq $true) { Write-Host '[PASS] safe_baseline includes valid Progress Percent' } else { Add-Failure 'safe_baseline must include valid Progress Percent' }
                if ($safe[0].safety.live_trading_data_present -eq $false) { Write-Host '[PASS] safe_baseline has no live trading data' } else { Add-Failure 'safe_baseline must not include live trading data' }
            }

            $missingRepo = Get-Variant -Variants $variants -Name 'blocked_missing_repo_size'
            if ($missingRepo.Count -eq 1) {
                if ($missingRepo[0].expected_result -eq 'FAIL') { Write-Host '[PASS] blocked_missing_repo_size expected_result is FAIL' } else { Add-Failure 'blocked_missing_repo_size expected_result must be FAIL' }
                if ($missingRepo[0].sections.'Repo Size' -eq $false) { Write-Host '[PASS] blocked_missing_repo_size fails for missing Repo Size' } else { Add-Failure 'blocked_missing_repo_size must have Repo Size false' }
            }

            $invalidProgress = Get-Variant -Variants $variants -Name 'blocked_progress_percent_invalid'
            if ($invalidProgress.Count -eq 1) {
                if ($invalidProgress[0].expected_result -eq 'FAIL') { Write-Host '[PASS] blocked_progress_percent_invalid expected_result is FAIL' } else { Add-Failure 'blocked_progress_percent_invalid expected_result must be FAIL' }
                if ($invalidProgress[0].sections.'Progress Percent' -eq 'INVALID') { Write-Host '[PASS] blocked_progress_percent_invalid fails for invalid Progress Percent' } else { Add-Failure 'blocked_progress_percent_invalid must have Progress Percent INVALID' }
            }

            $liveTrading = Get-Variant -Variants $variants -Name 'blocked_live_trading_data_present'
            if ($liveTrading.Count -eq 1) {
                if ($liveTrading[0].expected_result -eq 'FAIL') { Write-Host '[PASS] blocked_live_trading_data_present expected_result is FAIL' } else { Add-Failure 'blocked_live_trading_data_present expected_result must be FAIL' }
                if ($liveTrading[0].safety.live_trading_data_present -eq $true) { Write-Host '[PASS] blocked_live_trading_data_present fails for live trading data' } else { Add-Failure 'blocked_live_trading_data_present must have live_trading_data_present true' }
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
    Write-Host ('DRY_RUN COMPLETE {0} NO DAILY ANALYTICS SUMMARY VARIANT ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO DAILY ANALYTICS SUMMARY VARIANT ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO DAILY ANALYTICS SUMMARY VARIANT ACTIONS APPLIED.' -f [char]0x2014)
