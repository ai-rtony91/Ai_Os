Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$packagePath = Join-Path $orchestrationRoot "commit_packages\COMMIT_PACKAGE_RECOMMENDATION.example.json"
$legacyPackagePath = Join-Path $orchestrationRoot "commit_package.example.json"

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

function Get-JsonValue {
    param(
        [AllowNull()]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Default = ""
    )

    if ($null -eq $Object) { return $Default }
    if ($Object.PSObject.Properties.Name -contains $Name) {
        $value = $Object.$Name
        if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
            return $value
        }
    }
    return $Default
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

$usedLegacyPackage = $false
$package = if (Test-Path -LiteralPath $packagePath -PathType Leaf) {
    Read-JsonFile -Path $packagePath
} elseif (Test-Path -LiteralPath $legacyPackagePath -PathType Leaf) {
    $usedLegacyPackage = $true
    Read-JsonFile -Path $legacyPackagePath
} else {
    $null
}

if ($null -eq $package) {
    Write-Host "AI_OS Commit Package Display"
    Write-Host "Mode: UNKNOWN"
    Write-Host "Package: unavailable"
    Write-Host "Purpose: Display commit package recommendation without staging, committing, or pushing."
    Write-Host ""
    Write-Host "Safety: display-only. No files are staged. No git add is run. No commit is created. No push is performed."
    Write-Host ""
    Write-Host "Commit package summary:"
    Write-Host "  Canonical source missing: automation/orchestration/commit_packages/COMMIT_PACKAGE_RECOMMENDATION.example.json"
    Write-Host "  Legacy fallback not found; no commit package source available."
    Write-Host ""
    Write-Host "Next safe action: create a canonical commit package recommendation through an approved workflow."
    exit 0
}

$approvedFiles = if ($package.PSObject.Properties.Name -contains "approved_files") { @($package.approved_files) } else { @($package.recommended_files) }
$blockedFiles = if ($package.PSObject.Properties.Name -contains "blocked_files") { @($package.blocked_files) } else { @($package.excluded_files) }
$packetIds = if ($package.PSObject.Properties.Name -contains "packet_ids") { @($package.packet_ids) } else { @() }

Write-Host "AI_OS Commit Package Display"
Write-Host "Mode: $($package.mode)"
Write-Host "Package: $(Get-JsonValue -Object $package -Name 'package_name' -Default (Get-JsonValue -Object $package -Name 'recommendation_name' -Default 'UNKNOWN'))"
Write-Host "Purpose: $($package.purpose)"
Write-Host "Approval state: $(Get-JsonValue -Object $package -Name 'approval_state' -Default 'recommendation_only')"
Write-Host ""
Write-Host "Safety: display-only. No files are staged. No git add is run. No commit is created. No push is performed."
Write-Host ""

if ($usedLegacyPackage) {
    Write-Host "Commit package source: legacy commit_package.example.json used because canonical source was unavailable."
} elseif (Test-Path -LiteralPath $legacyPackagePath -PathType Leaf) {
    Write-Host "Legacy fallback: commit_package.example.json available"
} else {
    Write-Host "Legacy fallback not found; canonical source used."
}
Write-Host ""

Write-Host "Commit message:"
Write-Host "  $(Get-JsonValue -Object $package -Name 'commit_message' -Default (Get-JsonValue -Object $package -Name 'commit_message_suggestion' -Default 'UNKNOWN'))"
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
if ($package.PSObject.Properties.Name -contains "safety_rules") {
    foreach ($rule in @($package.safety_rules)) {
        Write-Host "  - $rule"
    }
} elseif ($package.PSObject.Properties.Name -contains "safety") {
    foreach ($item in @($package.safety.PSObject.Properties)) {
        Write-Host "  - $($item.Name): $($item.Value)"
    }
} else {
    Write-Host "  - display-only"
    Write-Host "  - no git add"
    Write-Host "  - no commit"
    Write-Host "  - no push"
}
Write-Host ""

Write-Host "Next safe action: review package contents only; use a separate explicit selective staging approval before running any git add command."
