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

Write-Host 'Task name: AI_OS Stage 16A-16D Operator Telemetry Map Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, or settings-changed.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Conceptual operator telemetry state: FAIL_BLOCKED'
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO OPERATOR TELEMETRY ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File checks:'
Test-RequiredFile -Label 'operator panel mapping draft' -RelativePath 'docs\AI_OS\dashboard\AIOS_OPERATOR_PANEL_MAPPING_DRAFT.md'
Test-RequiredFile -Label 'production telemetry roadmap draft' -RelativePath 'docs\AI_OS\telemetry\AIOS_PRODUCTION_TELEMETRY_ROADMAP_DRAFT.md'
Test-RequiredFile -Label 'Morning Brief text contract draft' -RelativePath 'docs\AI_OS\morning_brief\AIOS_MORNING_BRIEF_TEXT_CONTRACT_DRAFT.md'
Test-RequiredFile -Label 'persistent snapshot boundary draft' -RelativePath 'docs\AI_OS\dashboard\AIOS_PERSISTENT_SNAPSHOT_BOUNDARY_DRAFT.md'
Test-RequiredFile -Label 'report writer boundary draft' -RelativePath 'docs\AI_OS\reporting\AIOS_REPORT_WRITER_BOUNDARY_DRAFT.md'
Test-RequiredFile -Label 'Morning Brief contract validator' -RelativePath 'automation\startup\Test-AiOsMorningBriefTextContract.DRY_RUN.ps1'
Test-RequiredFile -Label 'snapshot history boundary validator' -RelativePath 'automation\status\Test-AiOsSnapshotHistoryBoundary.DRY_RUN.ps1'

$operatorPanelPath = Join-Path $script:ResolvedRepoRoot 'docs\AI_OS\dashboard\AIOS_OPERATOR_PANEL_MAPPING_DRAFT.md'
$telemetryRoadmapPath = Join-Path $script:ResolvedRepoRoot 'docs\AI_OS\telemetry\AIOS_PRODUCTION_TELEMETRY_ROADMAP_DRAFT.md'
$operatorPanelText = ''
$telemetryRoadmapText = ''

if (Test-Path -LiteralPath $operatorPanelPath -PathType Leaf) {
    $operatorPanelText = Get-Content -LiteralPath $operatorPanelPath -Raw
}

if (Test-Path -LiteralPath $telemetryRoadmapPath -PathType Leaf) {
    $telemetryRoadmapText = Get-Content -LiteralPath $telemetryRoadmapPath -Raw
}

Write-Host ''
Write-Host 'Operator panel checks:'
$requiredPanels = @(
    'Repo Health',
    'Workflow Router',
    'Morning Brief',
    'Approval Queue',
    'Snapshot Boundary',
    'Report Boundary',
    'Daily Metrics',
    'Production Telemetry',
    'Protected File State'
)

foreach ($panel in $requiredPanels) {
    Test-Text -Label $panel -Text $operatorPanelText -Expected $panel
}

Write-Host ''
Write-Host 'Telemetry field checks:'
$requiredTelemetryFields = @(
    'production_ready',
    'telemetry_mode',
    'workflow_state',
    'dashboard_state',
    'approval_state',
    'protected_files_changed'
)

foreach ($field in $requiredTelemetryFields) {
    Test-Text -Label $field -Text $telemetryRoadmapText -Expected $field
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
    $operatorTelemetryState = 'FAIL_BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $operatorTelemetryState = 'WARN_REVIEW_REQUIRED'
}
else {
    $operatorTelemetryState = 'READY_FOR_REVIEW'
}

Write-Host "Conceptual operator telemetry state: $operatorTelemetryState"
Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO OPERATOR TELEMETRY ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO OPERATOR TELEMETRY ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO OPERATOR TELEMETRY ACTIONS APPLIED.' -f [char]0x2014)
