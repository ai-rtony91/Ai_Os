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

function Test-Text {
    param(
        [string]$Label,
        [string]$Text,
        [string]$Expected
    )

    if ($Text -match [regex]::Escape($Expected)) {
        Write-Host "[PASS] $Label"
        return
    }

    Write-Host "[FAIL] $Label"
    $script:failures.Add("Missing required text: $Expected") | Out-Null
}

Write-Host 'Task name: AI_OS Stage 19A-19D Full System Readiness Audit Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, settings-changed, broker-routed, webhook-fired, credential-accessed, secrets-accessed, telemetry-written, or traded.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Conceptual readiness state: FAIL_BLOCKED'
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO FULL READINESS ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'Major component checks:'
Test-RequiredFile -Label 'dashboard data contract' -RelativePath 'docs\AI_OS\dashboard\AIOS_DASHBOARD_DATA_CONTRACT_DRAFT.md'
Test-RequiredFile -Label 'operator panel mapping' -RelativePath 'docs\AI_OS\dashboard\AIOS_OPERATOR_PANEL_MAPPING_DRAFT.md'
Test-RequiredFile -Label 'production telemetry roadmap' -RelativePath 'docs\AI_OS\telemetry\AIOS_PRODUCTION_TELEMETRY_ROADMAP_DRAFT.md'
Test-RequiredFile -Label 'Morning Brief text contract' -RelativePath 'docs\AI_OS\morning_brief\AIOS_MORNING_BRIEF_TEXT_CONTRACT_DRAFT.md'
Test-RequiredFile -Label 'approval queue draft' -RelativePath 'docs\AI_OS\approval\AIOS_APPROVAL_QUEUE_DRAFT.md'
Test-RequiredFile -Label 'screener dashboard contract' -RelativePath 'docs\AI_OS\trading\AIOS_SCREENER_DASHBOARD_CONTRACT_DRAFT.md'
Test-RequiredFile -Label 'trading readiness boundary' -RelativePath 'docs\AI_OS\trading\AIOS_TRADING_READINESS_BOUNDARY_DRAFT.md'
Test-RequiredFile -Label 'execution blocking contract' -RelativePath 'docs\AI_OS\trading\AIOS_EXECUTION_BLOCKING_CONTRACT_DRAFT.md'
Test-RequiredFile -Label 'Mean Machine integration plan' -RelativePath 'docs\AI_OS\mean_machine\AIOS_MEAN_MACHINE_INTEGRATION_PLAN_DRAFT.md'
Test-RequiredFile -Label 'Mean Machine data contract' -RelativePath 'docs\AI_OS\mean_machine\AIOS_MEAN_MACHINE_DATA_CONTRACT_DRAFT.md'
Test-RequiredFile -Label 'workflow router dry run' -RelativePath 'automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1'
Test-RequiredFile -Label 'Mean Machine boundary validator' -RelativePath 'automation\status\Test-AiOsMeanMachineBoundary.DRY_RUN.ps1'
Test-RequiredFile -Label 'screener dashboard validator' -RelativePath 'automation\status\Test-AiOsScreenerDashboardContract.DRY_RUN.ps1'
Test-RequiredFile -Label 'operator telemetry map validator' -RelativePath 'automation\status\Test-AiOsOperatorTelemetryMap.DRY_RUN.ps1'

$filesToScan = @(
    'docs\AI_OS\readiness\AIOS_STAGE19_FULL_SYSTEM_READINESS_AUDIT_DRAFT.md',
    'docs\AI_OS\readiness\AIOS_AUTOMATION_INPUT_OWNERSHIP_MAP_DRAFT.md',
    'docs\AI_OS\trading\AIOS_EXECUTION_BLOCKING_CONTRACT_DRAFT.md',
    'docs\AI_OS\trading\AIOS_SCREENER_DASHBOARD_CONTRACT_DRAFT.md',
    'docs\AI_OS\trading\AIOS_TRADING_READINESS_BOUNDARY_DRAFT.md',
    'docs\AI_OS\mean_machine\AIOS_MEAN_MACHINE_INTEGRATION_PLAN_DRAFT.md',
    'docs\AI_OS\mean_machine\AIOS_MEAN_MACHINE_DATA_CONTRACT_DRAFT.md',
    'docs\AI_OS\telemetry\AIOS_PRODUCTION_TELEMETRY_ROADMAP_DRAFT.md'
)

$text = ''
foreach ($relativePath in $filesToScan) {
    $path = Join-Path $script:ResolvedRepoRoot $relativePath
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $text += "`n"
        $text += Get-Content -LiteralPath $path -Raw
    }
}

Write-Host ''
Write-Host 'Safety phrase checks:'
$requiredSafetyPhrases = @(
    'execution_allowed must remain false',
    'broker order placement',
    'webhook firing',
    'credential access',
    'paper-trading validation',
    'explicit human approval',
    'production telemetry requires separate approval'
)

foreach ($phrase in $requiredSafetyPhrases) {
    Test-Text -Label $phrase -Text $text -Expected $phrase
}

Write-Host ''
Write-Host 'Protected-file diff check:'
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

$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCommand) {
    Write-Host '[WARN] git command unavailable.'
    $warnings.Add('git command unavailable.') | Out-Null
}
else {
    Push-Location -LiteralPath $script:ResolvedRepoRoot
    try {
        Write-Host 'Unstaged protected-file diff check:'
        $protectedDiff = @(& git diff --name-only -- $protectedPaths 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Write-Host '[FAIL] unstaged protected-file diff check failed.'
            $protectedDiff | ForEach-Object { Write-Host $_ }
            $failures.Add('unstaged protected-file diff check failed.') | Out-Null
        }
        elseif ($protectedDiff.Count -gt 0) {
            Write-Host '[FAIL] unstaged protected files changed.'
            $protectedDiff | ForEach-Object { Write-Host $_ }
            $failures.Add('unstaged protected files changed.') | Out-Null
        }
        else {
            Write-Host '[PASS] unstaged protected-file diff is clean.'
        }

        Write-Host ''
        Write-Host 'Staged protected-file diff check:'
        $cachedProtectedDiff = @(& git diff --cached --name-only -- $protectedPaths 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Write-Host '[FAIL] staged protected-file diff check failed.'
            $cachedProtectedDiff | ForEach-Object { Write-Host $_ }
            $failures.Add('staged protected-file diff check failed.') | Out-Null
        }
        elseif ($cachedProtectedDiff.Count -gt 0) {
            Write-Host '[FAIL] staged protected files changed.'
            $cachedProtectedDiff | ForEach-Object { Write-Host $_ }
            $failures.Add('staged protected files changed.') | Out-Null
        }
        else {
            Write-Host '[PASS] staged protected-file diff is clean.'
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
    $readinessState = 'FAIL_BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $readinessState = 'WARN_REVIEW_REQUIRED'
}
else {
    $readinessState = 'FOUNDATION_READY_FOR_REVIEW'
}

Write-Host "Conceptual readiness state: $readinessState"
Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO FULL READINESS ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO FULL READINESS ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO FULL READINESS ACTIONS APPLIED.' -f [char]0x2014)
