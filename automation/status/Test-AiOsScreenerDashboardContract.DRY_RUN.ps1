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

Write-Host 'Task name: AI_OS Stage 17A-17D Screener Dashboard Contract Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, settings-changed, broker-routed, webhook-fired, credential-accessed, or traded.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Conceptual screener dashboard state: FAIL_BLOCKED'
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO SCREENER OR TRADING ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File checks:'
Test-RequiredFile -Label 'screener dashboard contract draft' -RelativePath 'docs\AI_OS\trading\AIOS_SCREENER_DASHBOARD_CONTRACT_DRAFT.md'
Test-RequiredFile -Label 'trading readiness boundary draft' -RelativePath 'docs\AI_OS\trading\AIOS_TRADING_READINESS_BOUNDARY_DRAFT.md'
Test-RequiredFile -Label 'screener dashboard contract validator' -RelativePath 'automation\status\Test-AiOsScreenerDashboardContract.DRY_RUN.ps1'
Test-RequiredFile -Label 'Stage 17 health README' -RelativePath 'Reports\health\STAGE17A_17D_SCREENER_DASHBOARD_README.txt'

$contractPath = Join-Path $script:ResolvedRepoRoot 'docs\AI_OS\trading\AIOS_SCREENER_DASHBOARD_CONTRACT_DRAFT.md'
$boundaryPath = Join-Path $script:ResolvedRepoRoot 'docs\AI_OS\trading\AIOS_TRADING_READINESS_BOUNDARY_DRAFT.md'
$contractText = ''
$boundaryText = ''

if (Test-Path -LiteralPath $contractPath -PathType Leaf) {
    $contractText = Get-Content -LiteralPath $contractPath -Raw
}

if (Test-Path -LiteralPath $boundaryPath -PathType Leaf) {
    $boundaryText = Get-Content -LiteralPath $boundaryPath -Raw
}

Write-Host ''
Write-Host 'Contract field checks:'
$requiredContractFields = @(
    'symbol',
    'signal_type',
    'signal_strength',
    'confidence_score',
    'risk_state',
    'execution_allowed',
    'approval_required'
)

foreach ($field in $requiredContractFields) {
    Test-Text -Label $field -Text $contractText -Expected $field
}

Write-Host ''
Write-Host 'Trading boundary checks:'
$requiredBoundaryText = @(
    'broker order placement',
    'live trading',
    'credential access',
    'paper-trading validation'
)

foreach ($item in $requiredBoundaryText) {
    Test-Text -Label $item -Text $boundaryText -Expected $item
}

Write-Host ''
Write-Host 'Execution safety checks:'
Test-Text -Label 'execution_allowed remains false' -Text $contractText -Expected 'execution_allowed` must remain `false`'
Test-Text -Label 'no broker routing' -Text $contractText -Expected 'No broker routing'
Test-Text -Label 'no webhook firing' -Text $contractText -Expected 'No webhook firing'
Test-Text -Label 'no credential access' -Text $contractText -Expected 'No credential access'
Test-Text -Label 'separate approval required' -Text $boundaryText -Expected 'Separate approval'

Write-Host ''
if ($failures.Count -gt 0) {
    $screenerDashboardState = 'FAIL_BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $screenerDashboardState = 'WARN_REVIEW_REQUIRED'
}
else {
    $screenerDashboardState = 'READY_FOR_REVIEW'
}

Write-Host "Conceptual screener dashboard state: $screenerDashboardState"
Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO SCREENER OR TRADING ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO SCREENER OR TRADING ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO SCREENER OR TRADING ACTIONS APPLIED.' -f [char]0x2014)
