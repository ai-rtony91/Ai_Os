<#
.SYNOPSIS
Archives stale low-value relay approval files without touching protected approvals.
#>

[CmdletBinding()]
param(
    [switch]$Apply,
    [int]$AgeHours = 72
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$approvalRoot = Join-Path $repoRoot "relay\approvals"
$protectedNames = @(
    "register-night-scheduler.approval.md",
    "enable-sos-notifier.approval.md",
    "enable-telegram-bridge.approval.md"
)

function Get-AiOsApprovalTimestamp {
    param([Parameter(Mandatory = $true)][System.IO.FileInfo]$File)

    if ($File.Name -match "^(?<stamp>\d{8}-\d{6})-") {
        return [datetime]::ParseExact($Matches.stamp, "yyyyMMdd-HHmmss", [Globalization.CultureInfo]::InvariantCulture).ToUniversalTime()
    }

    return $File.LastWriteTimeUtc
}

if (-not (Test-Path -LiteralPath $approvalRoot -PathType Container)) {
    Write-Host "NO_APPROVAL_ROOT path=$approvalRoot"
    exit 0
}

$now = (Get-Date).ToUniversalTime()
$candidates = @(Get-ChildItem -LiteralPath $approvalRoot -File -Filter "*.md" -ErrorAction SilentlyContinue | Sort-Object Name)
$moves = @()

foreach ($file in $candidates) {
    $lowerName = $file.Name.ToLowerInvariant()
    if ($protectedNames -contains $lowerName) {
        Write-Host "PROTECTED_SKIP $($file.Name)"
        continue
    }

    if ($lowerName -match "scheduler|sos|telegram|register|secret") {
        Write-Host "PROTECTED_TERM_SKIP $($file.Name)"
        continue
    }

    if ($lowerName -notmatch "dirty-repo|danger|state-revalidation") {
        continue
    }

    $ageHoursActual = [int]($now - (Get-AiOsApprovalTimestamp -File $file)).TotalHours
    if ($ageHoursActual -le $AgeHours) {
        continue
    }

    $archiveDay = $now.ToString("yyyy-MM-dd")
    $targetDir = Join-Path $approvalRoot ("archive\{0}" -f $archiveDay)
    $targetPath = Join-Path $targetDir $file.Name
    $moves += [pscustomobject]@{
        source = $file.FullName
        target_dir = $targetDir
        target = $targetPath
        age_hours = $ageHoursActual
    }
}

if ($moves.Count -eq 0) {
    Write-Host "NO_STALE_APPROVALS_TO_ARCHIVE"
    exit 0
}

foreach ($move in $moves) {
    if ($Apply) {
        if (-not (Test-Path -LiteralPath $move.target_dir -PathType Container)) {
            New-Item -ItemType Directory -Path $move.target_dir -Force | Out-Null
        }
        Move-Item -LiteralPath $move.source -Destination $move.target -Force
        Write-Host ("ARCHIVED {0} -> {1} age_hours={2}" -f $move.source, $move.target, $move.age_hours)
    } else {
        Write-Host ("WOULD_ARCHIVE {0} -> {1} age_hours={2}" -f $move.source, $move.target, $move.age_hours)
    }
}
