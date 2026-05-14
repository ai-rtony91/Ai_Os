[CmdletBinding()]
param(
    [string]$ManifestPath = "automation/orchestration/commit_packages/COMMIT_PACKAGE_MANIFEST_001.json"
)

$ErrorActionPreference = "Stop"

function Get-AIOSChangedPath {
    param([string]$StatusLine)

    if ($StatusLine -like "##*") { return $null }
    if ($StatusLine.Length -lt 4) { return $null }

    $path = $StatusLine.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }
    return ($path -replace "\\", "/")
}

Write-Host "AI_OS Commit Package Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Manifest: $ManifestPath"

if (-not (Test-Path -LiteralPath $ManifestPath)) {
    throw "Manifest not found: $ManifestPath"
}

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$manifestFiles = @($manifest.files_to_stage | ForEach-Object { ([string]$_) -replace "\\", "/" })

$statusLines = @(& git status --short)
if ($LASTEXITCODE -ne 0) {
    throw "git status --short failed."
}

$changedFiles = @(
    foreach ($line in $statusLines) {
        $path = Get-AIOSChangedPath -StatusLine $line
        if ($null -ne $path) { $path }
    }
)

$filesToStage = @(
    foreach ($file in $manifestFiles) {
        if ($changedFiles -contains $file) {
            $file
        }
    }
)

Write-Host ""
Write-Host "Changed files:"
if ($changedFiles.Count -eq 0) {
    Write-Host "- none"
}
else {
    foreach ($file in $changedFiles) {
        Write-Host "- $file"
    }
}

Write-Host ""
Write-Host "Approved files to stage:"
if ($filesToStage.Count -eq 0) {
    Write-Host "- none"
}
else {
    foreach ($file in $filesToStage) {
        Write-Host "- $file"
    }
}

$untrackedNotInManifest = @(
    foreach ($line in $statusLines) {
        if ($line -like "?? *") {
            $path = Get-AIOSChangedPath -StatusLine $line
            if ($null -ne $path -and $manifestFiles -notcontains $path) {
                $path
            }
        }
    }
)

Write-Host ""
if ($untrackedNotInManifest.Count -gt 0) {
    Write-Host "Warnings:"
    foreach ($file in $untrackedNotInManifest) {
        Write-Host "- Untracked file not in manifest: $file"
    }
}
else {
    Write-Host "Warnings: none"
}

Write-Host ""
Write-Host "Exact staging commands for human review only:"
if ($filesToStage.Count -eq 0) {
    Write-Host "- none"
}
else {
    foreach ($file in $filesToStage) {
        Write-Host ("git add -- `"{0}`"" -f $file)
    }
}

Write-Host ""
Write-Host "No files were staged. No commit was created. No push was performed."