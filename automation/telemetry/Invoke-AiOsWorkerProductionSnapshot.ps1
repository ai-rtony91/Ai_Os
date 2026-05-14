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

function Get-StatusGuess {
    param([string]$Content)

    if ($Content -match "BLOCKED") {
        return "BLOCKED"
    }
    if ($Content -match "DONE|COMPLETE") {
        return "COMPLETE"
    }
    if ($Content -match "IN_PROGRESS|ACTIVE") {
        return "ACTIVE"
    }
    if ($Content -match "WAITING|PENDING") {
        return "WAITING"
    }
    return "UNKNOWN"
}

function Get-AssignedArea {
    param([string]$FileName)

    if ($FileName -match "DEVOPS") {
        return "DevOps"
    }
    if ($FileName -match "TRADING") {
        return "Trading Lab"
    }
    if ($FileName -match "VALIDATOR") {
        return "Validator"
    }
    if ($FileName -match "TELEMETRY") {
        return "Telemetry"
    }
    if ($FileName -match "UI|UX") {
        return "UI/UX"
    }
    if ($FileName -match "DOCS") {
        return "Docs"
    }
    if ($FileName -match "REPORTING") {
        return "Reporting"
    }
    if ($FileName -match "SANDBOX") {
        return "Sandbox"
    }
    return "Unknown"
}

function Get-StaleStatus {
    param([int]$StaleMinutes)

    if ($StaleMinutes -le 30) {
        return "FRESH"
    }
    if ($StaleMinutes -le 120) {
        return "WARM"
    }
    return "STALE"
}

$repoRoot = Get-RepoRoot
Set-Location -LiteralPath $repoRoot

$now = Get-Date
$date = $now.ToString("yyyy-MM-dd")
$timestamp = $now.ToString("o")

$telemetryDir = Join-Path $repoRoot "Reports\telemetry"
New-Item -ItemType Directory -Force -Path $telemetryDir | Out-Null

$snapshotPath = Join-Path $telemetryDir "AIOS_WORKER_PRODUCTION_SNAPSHOT.csv"
$snapshotHeader = "date,timestamp,worker_id,assigned_area,status_guess,stale_status,stale_minutes,size_bytes,path,notes"
if (-not (Test-Path -LiteralPath $snapshotPath)) {
    Set-Content -LiteralPath $snapshotPath -Value $snapshotHeader -Encoding utf8
}

$summaryPath = Join-Path $telemetryDir "AIOS_WORKER_PRODUCTION_SUMMARY.json"
$workerQueueDir = Join-Path $repoRoot "automation\operator\worker_queue\active"
$rows = @()

if (Test-Path -LiteralPath $workerQueueDir) {
    $workerFiles = @(Get-ChildItem -LiteralPath $workerQueueDir -File -ErrorAction SilentlyContinue | Sort-Object Name)
} else {
    $workerFiles = @()
}

foreach ($workerFile in $workerFiles) {
    $content = Get-Content -LiteralPath $workerFile.FullName -Raw -ErrorAction SilentlyContinue
    $staleMinutes = [int][Math]::Floor(($now - $workerFile.LastWriteTime).TotalMinutes)
    if ($staleMinutes -lt 0) {
        $staleMinutes = 0
    }

    $rows += [pscustomobject]@{
        date          = $date
        timestamp     = $timestamp
        worker_id     = [System.IO.Path]::GetFileNameWithoutExtension($workerFile.Name)
        assigned_area = Get-AssignedArea -FileName $workerFile.Name
        status_guess  = Get-StatusGuess -Content $content
        stale_status  = Get-StaleStatus -StaleMinutes $staleMinutes
        stale_minutes = $staleMinutes
        size_bytes    = $workerFile.Length
        path          = $workerFile.FullName.Substring($repoRoot.Length + 1).Replace("\", "/")
        notes         = "Local worker queue snapshot only. No execution performed."
    }
}

if ($rows.Count -gt 0) {
    $rows | Export-Csv -LiteralPath $snapshotPath -NoTypeInformation -Append -Encoding utf8
}

$workerCount = $rows.Count
$activeCount = @($rows | Where-Object { $_.status_guess -eq "ACTIVE" }).Count
$completeCount = @($rows | Where-Object { $_.status_guess -eq "COMPLETE" }).Count
$blockedCount = @($rows | Where-Object { $_.status_guess -eq "BLOCKED" }).Count
$waitingCount = @($rows | Where-Object { $_.status_guess -eq "WAITING" }).Count
$unknownCount = @($rows | Where-Object { $_.status_guess -eq "UNKNOWN" }).Count
$freshCount = @($rows | Where-Object { $_.stale_status -eq "FRESH" }).Count
$warmCount = @($rows | Where-Object { $_.stale_status -eq "WARM" }).Count
$staleCount = @($rows | Where-Object { $_.stale_status -eq "STALE" }).Count

if ($workerCount -eq 0) {
    $summaryText = "No active worker queue files found."
} elseif ($staleCount -gt $activeCount) {
    $summaryText = "Worker queue needs review. More workers appear stale than active."
} elseif ($blockedCount -gt 0) {
    $summaryText = "Worker queue has blockers that need review."
} elseif ($activeCount -gt 0 -and $blockedCount -eq 0) {
    $summaryText = "Worker queue is moving."
} else {
    $summaryText = "Worker queue needs review."
}

$summary = [ordered]@{
    schema           = "AIOS_WORKER_PRODUCTION_SUMMARY.v1"
    status           = "generated"
    generated_at     = $timestamp
    worker_count     = $workerCount
    active_count     = $activeCount
    complete_count   = $completeCount
    blocked_count    = $blockedCount
    waiting_count    = $waitingCount
    unknown_count    = $unknownCount
    fresh_count      = $freshCount
    warm_count       = $warmCount
    stale_count      = $staleCount
    summary_text     = $summaryText
    next_safe_action = "Review worker production summary before assigning new Codex workload."
}

$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding utf8

Write-Host "PASS: AI_OS worker production snapshot updated."
Write-Host "Worker count: $workerCount"
Write-Host "Summary: $summaryText"
