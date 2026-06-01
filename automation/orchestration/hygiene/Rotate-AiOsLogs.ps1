[CmdletBinding()]
param(
    [string[]]$LogRoots = @("relay/logs", "automation/orchestration"),
    [int]$MaxSizeMB = 50,
    [int]$KeepDays = 30,
    [switch]$Apply,
    [int]$DeleteAfterDays = 90
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$hygieneLog = Join-Path $repoRoot "relay\logs\hygiene.log"

function Get-AiOsUtcStamp {
    return (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
}

function Write-HygieneLog {
    param([string]$Message)
    $dir = Split-Path -Parent $hygieneLog
    if (-not (Test-Path -LiteralPath $dir -PathType Container)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Add-Content -LiteralPath $hygieneLog -Value ("{0} Rotate-AiOsLogs {1}" -f (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"), $Message)
}

$maxBytes = [int64]$MaxSizeMB * 1MB
$now = (Get-Date).ToUniversalTime()
$rotated = @()
$compressed = @()
$deleted = @()

foreach ($root in $LogRoots) {
    $resolvedRoot = if ([System.IO.Path]::IsPathRooted($root)) { $root } else { Join-Path $repoRoot $root }
    if (-not (Test-Path -LiteralPath $resolvedRoot -PathType Container)) {
        continue
    }

    $logs = Get-ChildItem -LiteralPath $resolvedRoot -Recurse -File -Filter "*.log" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch [regex]::Escape(".archive") }

    foreach ($log in $logs) {
        if ($log.Length -le $maxBytes) {
            continue
        }

        $dateFolder = $now.ToString("yyyy-MM-dd")
        $archiveDir = Join-Path ($log.FullName + ".archive") $dateFolder
        $targetName = "{0}.{1}.log" -f $log.BaseName, (Get-AiOsUtcStamp)
        $target = Join-Path $archiveDir $targetName
        $rotated += [pscustomobject]@{ source = $log.FullName; archive = $target; bytes = $log.Length }

        if ($Apply) {
            New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
            Move-Item -LiteralPath $log.FullName -Destination $target -Force
            New-Item -ItemType File -Path $log.FullName -Force | Out-Null
        }
    }
}

$archiveRoots = foreach ($root in $LogRoots) {
    $resolvedRoot = if ([System.IO.Path]::IsPathRooted($root)) { $root } else { Join-Path $repoRoot $root }
    if (Test-Path -LiteralPath $resolvedRoot -PathType Container) {
        Get-ChildItem -LiteralPath $resolvedRoot -Recurse -Directory -Filter "*.archive" -ErrorAction SilentlyContinue
    }
}

foreach ($archiveRoot in @($archiveRoots)) {
    $archiveFiles = Get-ChildItem -LiteralPath $archiveRoot.FullName -Recurse -File -ErrorAction SilentlyContinue
    foreach ($archiveFile in $archiveFiles) {
        $ageDays = ($now - $archiveFile.LastWriteTimeUtc).TotalDays
        if ($ageDays -gt $DeleteAfterDays) {
            $manifest = Join-Path $archiveFile.DirectoryName ("SAFE_TO_DELETE_{0}.json" -f (Get-AiOsUtcStamp))
            $deleted += $archiveFile.FullName
            if ($Apply) {
                $entry = [ordered]@{
                    path = $archiveFile.FullName
                    bytes = $archiveFile.Length
                    age_days = [math]::Round($ageDays, 2)
                    deleted_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
                }
                Set-Content -LiteralPath $manifest -Value (($entry | ConvertTo-Json -Depth 5) + "`n") -Encoding UTF8
                Remove-Item -LiteralPath $archiveFile.FullName -Force
            }
        } elseif ($ageDays -gt $KeepDays -and $archiveFile.Extension -ne ".gz") {
            $gzPath = $archiveFile.FullName + ".gz"
            $compressed += $archiveFile.FullName
            if ($Apply -and -not (Test-Path -LiteralPath $gzPath -PathType Leaf)) {
                $inputStream = [System.IO.File]::OpenRead($archiveFile.FullName)
                try {
                    $outputStream = [System.IO.File]::Create($gzPath)
                    try {
                        $gzip = [System.IO.Compression.GzipStream]::new($outputStream, [System.IO.Compression.CompressionMode]::Compress)
                        try { $inputStream.CopyTo($gzip) } finally { $gzip.Dispose() }
                    } finally { $outputStream.Dispose() }
                } finally { $inputStream.Dispose() }
                Remove-Item -LiteralPath $archiveFile.FullName -Force
            }
        }
    }
}

$summary = [ordered]@{
    apply = [bool]$Apply
    max_size_mb = $MaxSizeMB
    keep_days = $KeepDays
    rotated = @($rotated).Count
    compressed = @($compressed).Count
    deleted = @($deleted).Count
}
Write-HygieneLog -Message (($summary | ConvertTo-Json -Compress -Depth 5))
Write-Output ($summary | ConvertTo-Json -Depth 5)
