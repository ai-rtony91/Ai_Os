Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$packagePath = Join-Path $orchestrationRoot "commit_package.example.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Write-FileList {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,

        [Parameter(Mandatory = $true)]
        [object[]]$Files
    )

    Write-Host $Title

    if ($Files.Count -eq 0) {
        Write-Host "  None"
        Write-Host ""
        return
    }

    foreach ($file in $Files) {
        Write-Host "  - $($file.path)"
        Write-Host "    Reason: $($file.reason)"
    }

    Write-Host ""
}

$package = Read-JsonFile -Path $packagePath
$approvedFiles = @($package.approved_files)
$blockedFiles = @($package.blocked_files)
$packetIds = @($package.packet_ids)

Write-Host "AI_OS Commit Package Display"
Write-Host "Mode: $($package.mode)"
Write-Host "Package: $($package.package_name)"
Write-Host "Purpose: $($package.purpose)"
Write-Host "Approval state: $($package.approval_state)"
Write-Host ""
Write-Host "Safety: display-only. No files are staged. No git add is run. No commit is created. No push is performed."
Write-Host ""

Write-Host "Commit message:"
Write-Host "  $($package.commit_message)"
Write-Host ""

Write-Host "Packet IDs:"
if ($packetIds.Count -eq 0) {
    Write-Host "  None"
} else {
    foreach ($packetId in $packetIds) {
        Write-Host "  - $packetId"
    }
}
Write-Host ""

Write-Host "Commit package summary:"
Write-Host "  Approved files for future commit: $($approvedFiles.Count)"
Write-Host "  Blocked files: $($blockedFiles.Count)"
Write-Host ""

Write-FileList -Title "Approved files for future commit:" -Files $approvedFiles
Write-FileList -Title "Blocked files:" -Files $blockedFiles

Write-Host "Safety rules:"
foreach ($rule in @($package.safety_rules)) {
    Write-Host "  - $rule"
}
Write-Host ""

Write-Host "Next safe action: review package contents only; use a separate explicit selective staging approval before running any git add command."
