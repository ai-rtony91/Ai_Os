param(
    [string]$RepoRoot = 'C:\Dev\Ai.Os'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$failures = New-Object System.Collections.Generic.List[string]

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

Write-Host 'Task name: AI_OS Daily Data Snapshot Contract Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, settings-changed, broker-routed, credential-accessed, secrets-accessed, telemetry-written, report-written, or traded.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO DAILY DATA SNAPSHOT CONTRACT ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File checks:'
Test-RequiredFile -Label 'daily snapshot source' -RelativePath 'automation\orchestration\daily_snapshot\New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1'
Test-RequiredFile -Label 'daily snapshot readme' -RelativePath 'automation\orchestration\daily_snapshot\README.md'
Test-RequiredFile -Label 'daily report writer' -RelativePath 'automation\reporting\New-AiOsReport.ps1'
Test-RequiredFile -Label 'telemetry snapshot writer' -RelativePath 'automation\telemetry\Invoke-AiOsProductionSnapshot.ps1'
Test-RequiredFile -Label 'backup planner' -RelativePath 'automation\orchestration\backups\Start-AiOsPostMainUpdateBackup.DRY_RUN.ps1'
Test-RequiredFile -Label 'reporting standard' -RelativePath 'docs\AI_OS\reporting\AIOS_REPORTING_AND_CHECKPOINT_STANDARD.md'

$sourceText = Get-Content -LiteralPath (Join-Path $script:ResolvedRepoRoot 'automation\orchestration\daily_snapshot\New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1') -Raw
$reportText = Get-Content -LiteralPath (Join-Path $script:ResolvedRepoRoot 'automation\reporting\New-AiOsReport.ps1') -Raw
$telemetryText = Get-Content -LiteralPath (Join-Path $script:ResolvedRepoRoot 'automation\telemetry\Invoke-AiOsProductionSnapshot.ps1') -Raw
$backupText = Get-Content -LiteralPath (Join-Path $script:ResolvedRepoRoot 'automation\orchestration\backups\Start-AiOsPostMainUpdateBackup.DRY_RUN.ps1') -Raw
$readmeText = Get-Content -LiteralPath (Join-Path $script:ResolvedRepoRoot 'automation\orchestration\daily_snapshot\README.md') -Raw
$reportingStandardText = Get-Content -LiteralPath (Join-Path $script:ResolvedRepoRoot 'docs\AI_OS\reporting\AIOS_REPORTING_AND_CHECKPOINT_STANDARD.md') -Raw

Write-Host ''
Write-Host 'Snapshot field checks:'
$requiredFields = @(
    'date_time_local',
    'repo_path',
    'current_head',
    'files_changed_generated_today',
    'artifact_count',
    'folder_count',
    'total_bytes_collected_today',
    'total_kb_collected_today',
    'total_mb_collected_today',
    'backup_size_bytes',
    'skipped_secrets_count',
    'validation_governance_status',
    'success_failure'
)

foreach ($field in $requiredFields) {
    Test-Text -Label $field -Text $sourceText -Expected $field
}

Write-Host ''
Write-Host 'Consumer linkage checks:'
Test-Text -Label 'daily report consumes snapshot script' -Text $reportText -Expected 'New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1'
Test-Text -Label 'telemetry consumes snapshot script' -Text $telemetryText -Expected 'New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1'
Test-Text -Label 'backup consumes snapshot script' -Text $backupText -Expected 'New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1'
Test-Text -Label 'daily snapshot readme mentions canonical source' -Text $readmeText -Expected 'canonical source for the `DAILY DATA SNAPSHOT` section'
Test-Text -Label 'reporting standard mentions daily data snapshot' -Text $reportingStandardText -Expected 'DAILY DATA SNAPSHOT REQUIREMENT'

Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO DAILY DATA SNAPSHOT CONTRACT ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO DAILY DATA SNAPSHOT CONTRACT ACTIONS APPLIED.' -f [char]0x2014)
