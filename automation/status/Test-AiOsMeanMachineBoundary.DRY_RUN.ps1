param(
    [string]$RepoRoot = 'C:\Dev\Ai.Os'
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

Write-Host 'Task name: AI_OS Stage 18A-18D Mean Machine Boundary Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, settings-changed, broker-routed, webhook-fired, credential-accessed, secrets-accessed, or traded.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Conceptual Mean Machine boundary state: FAIL_BLOCKED'
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO MEAN MACHINE OR TRADING ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File checks:'
Test-RequiredFile -Label 'Mean Machine integration plan draft' -RelativePath 'docs\AI_OS\mean_machine\AIOS_MEAN_MACHINE_INTEGRATION_PLAN_DRAFT.md'
Test-RequiredFile -Label 'Mean Machine data contract draft' -RelativePath 'docs\AI_OS\mean_machine\AIOS_MEAN_MACHINE_DATA_CONTRACT_DRAFT.md'
Test-RequiredFile -Label 'execution blocking contract draft' -RelativePath 'docs\AI_OS\trading\AIOS_EXECUTION_BLOCKING_CONTRACT_DRAFT.md'
Test-RequiredFile -Label 'screener dashboard contract draft' -RelativePath 'docs\AI_OS\trading\AIOS_SCREENER_DASHBOARD_CONTRACT_DRAFT.md'
Test-RequiredFile -Label 'trading readiness boundary draft' -RelativePath 'docs\AI_OS\trading\AIOS_TRADING_READINESS_BOUNDARY_DRAFT.md'
Test-RequiredFile -Label 'production telemetry roadmap draft' -RelativePath 'docs\AI_OS\telemetry\AIOS_PRODUCTION_TELEMETRY_ROADMAP_DRAFT.md'

$text = ''
$filesToScan = @(
    'docs\AI_OS\mean_machine\AIOS_MEAN_MACHINE_INTEGRATION_PLAN_DRAFT.md',
    'docs\AI_OS\mean_machine\AIOS_MEAN_MACHINE_DATA_CONTRACT_DRAFT.md',
    'docs\AI_OS\trading\AIOS_EXECUTION_BLOCKING_CONTRACT_DRAFT.md',
    'docs\AI_OS\trading\AIOS_SCREENER_DASHBOARD_CONTRACT_DRAFT.md',
    'docs\AI_OS\trading\AIOS_TRADING_READINESS_BOUNDARY_DRAFT.md',
    'docs\AI_OS\telemetry\AIOS_PRODUCTION_TELEMETRY_ROADMAP_DRAFT.md'
)

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
    'explicit human approval'
)

foreach ($phrase in $requiredSafetyPhrases) {
    Test-Text -Label $phrase -Text $text -Expected $phrase
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
    $meanMachineBoundaryState = 'FAIL_BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $meanMachineBoundaryState = 'WARN_REVIEW_REQUIRED'
}
else {
    $meanMachineBoundaryState = 'VISIBILITY_READY'
}

Write-Host "Conceptual Mean Machine boundary state: $meanMachineBoundaryState"
Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO MEAN MACHINE OR TRADING ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO MEAN MACHINE OR TRADING ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO MEAN MACHINE OR TRADING ACTIONS APPLIED.' -f [char]0x2014)
