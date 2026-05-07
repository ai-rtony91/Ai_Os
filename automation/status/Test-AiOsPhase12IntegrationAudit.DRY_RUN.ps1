<# 
AI_OS Phase 12 Integration Audit DRY_RUN
Read-only validator. Does not create, modify, delete, move, rename, deploy, connect brokers, or place trades.
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path -LiteralPath ".").Path
)

$ErrorActionPreference = "Stop"

function New-Result {
    param(
        [string]$Check,
        [string]$Status,
        [string]$Evidence,
        [string]$NextAction
    )

    [PSCustomObject]@{
        Check = $Check
        Status = $Status
        Evidence = $Evidence
        NextAction = $NextAction
    }
}

$results = New-Object System.Collections.Generic.List[object]

$requiredFolders = @(
    "docs/AI_OS/productization",
    "docs/AI_OS/governance",
    "docs/AI_OS/operator",
    "docs/AI_OS/roadmap",
    "docs/AI_OS/dashboard",
    "docs/AI_OS/validators",
    "docs/AI_OS/progress",
    "Reports/daily",
    "Reports/checkpoints",
    "Reports/progress",
    "Reports/health"
)

foreach ($folder in $requiredFolders) {
    if (Test-Path -LiteralPath (Join-Path -Path $RepoRoot -ChildPath $folder)) {
        $results.Add((New-Result -Check "FolderExists" -Status "PASS" -Evidence $folder -NextAction "None"))
    } else {
        $results.Add((New-Result -Check "FolderExists" -Status "FAIL" -Evidence $folder -NextAction "Create a DRY_RUN gap plan"))
    }
}

$phase12Reports = Get-ChildItem -LiteralPath (Join-Path -Path $RepoRoot -ChildPath "Reports/daily") -File -Filter "*PHASE12*" -ErrorAction SilentlyContinue
if ($phase12Reports.Count -gt 0) {
    $results.Add((New-Result -Check "Phase12ReportCoverage" -Status "PASS" -Evidence "$($phase12Reports.Count) Phase 12 reports found" -NextAction "Review for latest checkpoint mapping"))
} else {
    $results.Add((New-Result -Check "Phase12ReportCoverage" -Status "FAIL" -Evidence "No Phase 12 reports found" -NextAction "Create report coverage gap plan"))
}

$phase12Checkpoints = Get-ChildItem -LiteralPath (Join-Path -Path $RepoRoot -ChildPath "Reports/checkpoints") -File -Filter "*PHASE12*" -ErrorAction SilentlyContinue
if ($phase12Checkpoints.Count -gt 0) {
    $results.Add((New-Result -Check "Phase12CheckpointCoverage" -Status "PASS" -Evidence "$($phase12Checkpoints.Count) Phase 12 checkpoints found" -NextAction "Review checkpoint index readiness"))
} else {
    $results.Add((New-Result -Check "Phase12CheckpointCoverage" -Status "FAIL" -Evidence "No Phase 12 checkpoints found" -NextAction "Create checkpoint coverage gap plan"))
}

$readmeGaps = foreach ($folder in $requiredFolders) {
    $fullFolder = Join-Path -Path $RepoRoot -ChildPath $folder
    if ((Test-Path -LiteralPath $fullFolder) -and -not (Test-Path -LiteralPath (Join-Path -Path $fullFolder -ChildPath "README_FOLDER_PURPOSE.txt"))) {
        $folder
    }
}

if ($readmeGaps.Count -gt 0) {
    $results.Add((New-Result -Check "ReadmeFolderPurposeCoverage" -Status "WARN" -Evidence ($readmeGaps -join "; ") -NextAction "Plan missing README_FOLDER_PURPOSE.txt files in a separate DRY_RUN"))
} else {
    $results.Add((New-Result -Check "ReadmeFolderPurposeCoverage" -Status "PASS" -Evidence "No immediate gaps in checked folders" -NextAction "None"))
}

$results | Format-Table -AutoSize

if ($results.Status -contains "FAIL") {
    exit 1
}

exit 0

