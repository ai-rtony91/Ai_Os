$ErrorActionPreference = "Stop"

function Invoke-GitLines {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>$null
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    if ($exitCode -ne 0) {
        return @()
    }

    return @($output)
}

function Get-RepoRoot {
    $root = @(Invoke-GitLines -Arguments @("rev-parse", "--show-toplevel"))
    if ($root.Count -eq 0 -or [string]::IsNullOrWhiteSpace([string]$root[0])) {
        return (Resolve-Path ".").Path
    }
    return ([string]$root[0]).Trim()
}

function Count-ExistingFiles {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return 0
    }

    return @(
        Get-ChildItem -LiteralPath $Path -File -Recurse -ErrorAction SilentlyContinue
    ).Count
}

function Get-AiOsDailyAutomationSnapshot {
    param([string]$RepoRoot)

    $snapshotScript = Join-Path $RepoRoot 'automation\orchestration\daily_snapshot\New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1'
    if (-not (Test-Path -LiteralPath $snapshotScript -PathType Leaf)) {
        throw "Daily snapshot script not found: $snapshotScript"
    }

    $snapshotOutput = @(& powershell -ExecutionPolicy Bypass -File $snapshotScript -Json 2>$null)
    if ($LASTEXITCODE -ne 0 -and $snapshotOutput.Count -eq 0) {
        throw "Daily snapshot script failed: $snapshotScript"
    }

    $snapshotJson = ($snapshotOutput -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($snapshotJson)) {
        throw "Daily snapshot script produced no JSON: $snapshotScript"
    }

    return $snapshotJson | ConvertFrom-Json
}

$repoRoot = Get-RepoRoot
Set-Location -LiteralPath $repoRoot

$telemetryDir = Join-Path $repoRoot "Reports\telemetry"
New-Item -ItemType Directory -Force -Path $telemetryDir | Out-Null

$ledgerPath = Join-Path $telemetryDir "AIOS_PRODUCTION_DAILY_LEDGER.csv"
$ledgerHeader = "date,timestamp,repo_root,current_head,branch,git_status_clean,tracked_files,modified_files,staged_files,untracked_files,commits_today,validator_script_count,telemetry_file_count,checkpoint_file_count,daily_report_file_count,worker_queue_file_count,daily_artifact_count,daily_folder_count,daily_total_bytes,daily_total_kb,daily_total_mb,skipped_secrets_count,validation_status,governance_status,success_failure,backup_size_bytes,backup_size_kb,backup_size_mb,snapshot_mode"

if (-not (Test-Path -LiteralPath $ledgerPath)) {
    Set-Content -LiteralPath $ledgerPath -Value $ledgerHeader -Encoding utf8
}

$now = Get-Date
$date = $now.ToString("yyyy-MM-dd")
$timestamp = $now.ToString("o")

$branch = @(Invoke-GitLines -Arguments @("branch", "--show-current"))
if ($branch.Count -eq 0 -or [string]::IsNullOrWhiteSpace([string]$branch[0])) {
    $branch = "UNKNOWN"
} else {
    $branch = ([string]$branch[0]).Trim()
}

$dailySnapshot = Get-AiOsDailyAutomationSnapshot -RepoRoot $repoRoot

$porcelain = Invoke-GitLines -Arguments @("status", "--porcelain")
$gitStatusClean = ($porcelain.Count -eq 0).ToString().ToUpperInvariant()

$trackedFiles = (Invoke-GitLines -Arguments @("ls-files")).Count
$untrackedFiles = (Invoke-GitLines -Arguments @("ls-files", "--others", "--exclude-standard")).Count
$modifiedFiles = (Invoke-GitLines -Arguments @("diff", "--name-only")).Count
$stagedFiles = (Invoke-GitLines -Arguments @("diff", "--cached", "--name-only")).Count

$todayStart = $now.Date.ToString("yyyy-MM-ddTHH:mm:ss")
$commitsToday = (Invoke-GitLines -Arguments @("log", "--since=$todayStart", "--format=%H")).Count

$validatorScriptCount = @(
    Get-ChildItem -LiteralPath (Join-Path $repoRoot "automation") -Filter "*.ps1" -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "^(Test|Validate)-" -or $_.Name -match "\.DRY_RUN\.ps1$" }
).Count

$telemetryFileCount = Count-ExistingFiles -Path $telemetryDir
$checkpointFileCount = Count-ExistingFiles -Path (Join-Path $repoRoot "Reports\checkpoints")
$dailyReportFileCount = Count-ExistingFiles -Path (Join-Path $repoRoot "Reports\daily")

$workerQueueRoots = @(
    (Join-Path $repoRoot "automation\operator\worker_queue"),
    (Join-Path $repoRoot "Reports\work_intelligence")
)
$workerQueueFileCount = 0
foreach ($queueRoot in $workerQueueRoots) {
    $workerQueueFileCount += Count-ExistingFiles -Path $queueRoot
}

$row = [pscustomobject]@{
    date                    = $date
    timestamp               = $timestamp
    repo_root               = $repoRoot
    current_head            = $dailySnapshot.current_head
    branch                  = $branch
    git_status_clean        = $gitStatusClean
    tracked_files           = $trackedFiles
    modified_files          = $modifiedFiles
    staged_files            = $stagedFiles
    untracked_files         = $untrackedFiles
    commits_today           = $commitsToday
    validator_script_count  = $validatorScriptCount
    telemetry_file_count    = $telemetryFileCount
    checkpoint_file_count   = $checkpointFileCount
    daily_report_file_count = $dailyReportFileCount
    worker_queue_file_count = $workerQueueFileCount
    daily_artifact_count    = $dailySnapshot.artifact_count
    daily_folder_count      = $dailySnapshot.folder_count
    daily_total_bytes       = $dailySnapshot.total_bytes_collected_today
    daily_total_kb          = $dailySnapshot.total_kb_collected_today
    daily_total_mb          = $dailySnapshot.total_mb_collected_today
    skipped_secrets_count   = $dailySnapshot.skipped_secrets_count
    validation_status       = $dailySnapshot.validation_status
    governance_status       = $dailySnapshot.governance_status
    success_failure         = $dailySnapshot.success_failure
    backup_size_bytes       = $dailySnapshot.backup_size_bytes
    backup_size_kb          = $dailySnapshot.backup_size_kb
    backup_size_mb          = $dailySnapshot.backup_size_mb
    snapshot_mode           = "APPLY"
}

$row | Export-Csv -LiteralPath $ledgerPath -NoTypeInformation -Append -Encoding utf8

Write-Host "PASS: AI_OS production snapshot appended to $ledgerPath"
