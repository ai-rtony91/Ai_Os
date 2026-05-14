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

function Import-LatestCsvRow {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    $rows = @(Import-Csv -LiteralPath $Path)
    if ($rows.Count -eq 0) {
        return $null
    }
    return $rows[-1]
}

function Get-PlainLanguageStatus {
    param([int]$Score)

    if ($Score -le 29) {
        return "DRAGGING"
    }
    if ($Score -le 59) {
        return "MOVING"
    }
    if ($Score -le 79) {
        return "HAULING"
    }
    return "HAULING HARD"
}

$repoRoot = Get-RepoRoot
Set-Location -LiteralPath $repoRoot

$now = Get-Date
$date = $now.ToString("yyyy-MM-dd")
$timestamp = $now.ToString("o")
$telemetryDir = Join-Path $repoRoot "Reports\telemetry"
New-Item -ItemType Directory -Force -Path $telemetryDir | Out-Null

$productionLedgerPath = Join-Path $telemetryDir "AIOS_PRODUCTION_DAILY_LEDGER.csv"
$stageLedgerPath = Join-Path $telemetryDir "AIOS_STAGE_PROGRESS_LEDGER.csv"
$workerSnapshotPath = Join-Path $telemetryDir "AIOS_WORKER_PRODUCTION_SNAPSHOT.csv"
$workerSummaryPath = Join-Path $telemetryDir "AIOS_WORKER_PRODUCTION_SUMMARY.json"
$readoutPath = Join-Path $telemetryDir "AIOS_DAILY_PRODUCTION_READOUT.json"
$readoutLedgerPath = Join-Path $telemetryDir "AIOS_DAILY_PRODUCTION_READOUT_LEDGER.csv"
$readoutLedgerHeader = "date,timestamp,production_score,plain_language_status,branch,git_status_clean,modified_files,staged_files,untracked_files,latest_stage,latest_stage_percent,blocked_worker_count,notes"

if (-not (Test-Path -LiteralPath $readoutLedgerPath)) {
    Set-Content -LiteralPath $readoutLedgerPath -Value $readoutLedgerHeader -Encoding utf8
}

$productionLedgerExists = Test-Path -LiteralPath $productionLedgerPath
$stageLedgerExists = Test-Path -LiteralPath $stageLedgerPath
$workerSnapshotExists = Test-Path -LiteralPath $workerSnapshotPath
$validatorScriptCount = @(
    Get-ChildItem -LiteralPath (Join-Path $repoRoot "automation") -Filter "*.ps1" -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "^(Test|Validate)-" -or $_.Name -match "\.DRY_RUN\.ps1$" }
).Count

$branchLines = @(Invoke-GitLines -Arguments @("branch", "--show-current"))
$statusLines = @(Invoke-GitLines -Arguments @("status", "--porcelain"))
$modifiedLines = @(Invoke-GitLines -Arguments @("diff", "--name-only"))
$stagedLines = @(Invoke-GitLines -Arguments @("diff", "--cached", "--name-only"))
$untrackedLines = @(Invoke-GitLines -Arguments @("ls-files", "--others", "--exclude-standard"))

$gitStatusReadable = $branchLines.Count -gt 0
$branch = if ($branchLines.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace([string]$branchLines[0])) { ([string]$branchLines[0]).Trim() } else { "UNKNOWN" }
$gitStatusClean = ($statusLines.Count -eq 0)
$modifiedFiles = $modifiedLines.Count
$stagedFiles = $stagedLines.Count
$untrackedFiles = $untrackedLines.Count

$latestStageRow = Import-LatestCsvRow -Path $stageLedgerPath
$latestStage = "UNKNOWN"
$latestStagePercent = 0
if ($null -ne $latestStageRow) {
    $latestStage = $latestStageRow.stage
    [int]::TryParse([string]$latestStageRow.percent_complete, [ref]$latestStagePercent) | Out-Null
}

$workerSummaryAvailable = Test-Path -LiteralPath $workerSummaryPath
$blockedWorkerCount = 0
if ($workerSummaryAvailable) {
    $workerSummary = Get-Content -LiteralPath $workerSummaryPath -Raw | ConvertFrom-Json
    $blockedWorkerCount = [int]$workerSummary.blocked_count
}

$telemetryFilesFound = @()
foreach ($path in @($productionLedgerPath, $stageLedgerPath, $workerSnapshotPath)) {
    if (Test-Path -LiteralPath $path) {
        $telemetryFilesFound += $path.Substring($repoRoot.Length + 1).Replace("\", "/")
    }
}

$missingFiles = @()
foreach ($path in @($productionLedgerPath, $stageLedgerPath, $workerSnapshotPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        $missingFiles += $path.Substring($repoRoot.Length + 1).Replace("\", "/")
    }
}

$productionScore = 0
if ($productionLedgerExists) { $productionScore += 10 }
if ($stageLedgerExists) { $productionScore += 10 }
if ($workerSnapshotExists) { $productionScore += 10 }
if ($validatorScriptCount -gt 0) { $productionScore += 10 }
if ($gitStatusReadable) { $productionScore += 10 }
if ($branch -eq "main") { $productionScore += 10 }
if ($stagedFiles -eq 0) { $productionScore += 10 }
if ($untrackedFiles -eq 0) { $productionScore += 10 }
if ($modifiedFiles -eq 0) { $productionScore += 10 }
if ($workerSummaryAvailable -and $blockedWorkerCount -eq 0) { $productionScore += 10 }

if ($productionScore -gt 100) {
    $productionScore = 100
}

$plainLanguageStatus = Get-PlainLanguageStatus -Score $productionScore
$notes = "Local production readout only. Does not perform execution."
if ($missingFiles.Count -gt 0) {
    $notes = "$notes Missing files: $($missingFiles -join ', ')."
}

$readout = [ordered]@{
    schema                   = "AIOS_DAILY_PRODUCTION_READOUT.v1"
    status                   = "generated"
    generated_at             = $timestamp
    production_score         = $productionScore
    plain_language_status    = $plainLanguageStatus
    branch                   = $branch
    git_status_clean         = $gitStatusClean
    modified_files           = $modifiedFiles
    staged_files             = $stagedFiles
    untracked_files          = $untrackedFiles
    telemetry_files_found    = $telemetryFilesFound
    latest_stage             = $latestStage
    latest_stage_percent     = $latestStagePercent
    worker_summary_available = $workerSummaryAvailable
    blocked_worker_count     = $blockedWorkerCount
    notes                    = $notes
    next_safe_action         = "Review worker production summary before assigning new Codex workload."
}

$readout | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $readoutPath -Encoding utf8

$ledgerRow = [pscustomobject]@{
    date                  = $date
    timestamp             = $timestamp
    production_score      = $productionScore
    plain_language_status = $plainLanguageStatus
    branch                = $branch
    git_status_clean      = $gitStatusClean.ToString().ToUpperInvariant()
    modified_files        = $modifiedFiles
    staged_files          = $stagedFiles
    untracked_files       = $untrackedFiles
    latest_stage          = $latestStage
    latest_stage_percent  = $latestStagePercent
    blocked_worker_count  = $blockedWorkerCount
    notes                 = "Local production readout only. Does not perform execution."
}

$ledgerRow | Export-Csv -LiteralPath $readoutLedgerPath -NoTypeInformation -Append -Encoding utf8

Write-Host "PASS: AI_OS daily production readout updated."
Write-Host "Production score: $productionScore"
Write-Host "Plain-language status: $plainLanguageStatus"
