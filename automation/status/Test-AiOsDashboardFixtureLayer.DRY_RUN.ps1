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

Write-Host 'Task name: AI_OS Stage 37A-37D Dashboard Fixture Layer Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, settings-changed, broker-routed, webhook-fired, credential-accessed, secrets-accessed, telemetry-written, report-written, dashboard-written, or traded.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO DASHBOARD FIXTURE ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File checks:'
$fixtureExists = Test-RequiredFile -Label 'dashboard fixture data' -RelativePath 'docs\AI_OS\dashboard\AIOS_DASHBOARD_FIXTURE_DATA_DRAFT.json'
Test-RequiredFile -Label 'dashboard panel layout draft' -RelativePath 'docs\AI_OS\dashboard\AIOS_DASHBOARD_PANEL_LAYOUT_DRAFT.md' | Out-Null
Test-RequiredFile -Label 'dashboard fixture validator' -RelativePath 'automation\status\Test-AiOsDashboardFixtureLayer.DRY_RUN.ps1' | Out-Null
Test-RequiredFile -Label 'Stage 37 health README' -RelativePath 'Reports\health\STAGE37A_37D_DASHBOARD_FIXTURE_LAYER_README.txt' | Out-Null
Test-RequiredFile -Label 'Stage 36 dashboard prep contract' -RelativePath 'docs\AI_OS\dashboard\AIOS_DASHBOARD_PREP_CONTRACT_DRAFT.md' | Out-Null
Test-RequiredFile -Label 'Stage 36 dashboard input map' -RelativePath 'docs\AI_OS\dashboard\AIOS_DASHBOARD_DATA_INPUT_MAP_DRAFT.md' | Out-Null
Test-RequiredFile -Label 'Stage 36 dashboard prep validator' -RelativePath 'automation\status\Test-AiOsDashboardPrepContract.DRY_RUN.ps1' | Out-Null

Write-Host ''
Write-Host 'Fixture JSON checks:'
if ($fixtureExists) {
    $fixturePath = Join-Path $script:ResolvedRepoRoot 'docs\AI_OS\dashboard\AIOS_DASHBOARD_FIXTURE_DATA_DRAFT.json'
    try {
        $fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json
        Write-Host '[PASS] fixture JSON parses.'

        foreach ($section in @(
            'system_status',
            'repo_health',
            'daily_analytics',
            'validator_status',
            'protected_file_status',
            'morning_brief',
            'trading_readiness',
            'azure_cloud_status',
            'alerts_emails',
            'next_safe_action'
        )) {
            if ($fixture.PSObject.Properties.Name -contains $section) {
                Write-Host "[PASS] fixture includes section: $section"
            }
            else {
                Add-Failure "Fixture missing section: $section"
            }
        }

        if ($fixture.safety.secrets_present -eq $false) { Write-Host '[PASS] fixture has no secrets' } else { Add-Failure 'Fixture indicates secrets present' }
        if ($fixture.safety.credentials_present -eq $false) { Write-Host '[PASS] fixture has no credentials' } else { Add-Failure 'Fixture indicates credentials present' }
        if ($fixture.safety.broker_tokens_present -eq $false) { Write-Host '[PASS] fixture has no broker tokens' } else { Add-Failure 'Fixture indicates broker tokens present' }
        if ($fixture.safety.live_trading_execution_data_present -eq $false) { Write-Host '[PASS] fixture has no live trading execution data' } else { Add-Failure 'Fixture indicates live trading execution data present' }
        if ($fixture.safety.startup_actions_present -eq $false) { Write-Host '[PASS] fixture has no startup actions' } else { Add-Failure 'Fixture indicates startup actions present' }
        if ($fixture.safety.report_writing_actions_present -eq $false) { Write-Host '[PASS] fixture has no report-writing actions' } else { Add-Failure 'Fixture indicates report-writing actions present' }
    }
    catch {
        Add-Failure "Fixture JSON failed to parse: $($_.Exception.Message)"
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
    Write-Host ('DRY_RUN COMPLETE {0} NO DASHBOARD FIXTURE ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO DASHBOARD FIXTURE ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO DASHBOARD FIXTURE ACTIONS APPLIED.' -f [char]0x2014)
