[CmdletBinding()]
param(
    [string]$ManifestPath = "automation/orchestration/commit_packages/COMMIT_PACKAGE_MANIFEST_001.json"
)

$ErrorActionPreference = "Stop"
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
    param([string]$Message)
    $script:failures.Add($Message) | Out-Null
}

Write-Host "AI_OS Commit Package Manifest Validator"
Write-Host "Mode: DRY_RUN"
Write-Host "Manifest: $ManifestPath"

if (-not (Test-Path -LiteralPath $ManifestPath)) {
    Add-Failure "Manifest does not exist: $ManifestPath"
}

$manifest = $null
if (Test-Path -LiteralPath $ManifestPath) {
    try {
        $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
        Write-Host "JSON parse: PASS"
    }
    catch {
        Add-Failure "Manifest failed JSON parse."
    }
}

if ($null -ne $manifest) {
    if (-not ($manifest.PSObject.Properties.Name -contains "files_to_stage")) {
        Add-Failure "Missing required field: files_to_stage"
    }
    if (-not ($manifest.PSObject.Properties.Name -contains "files_not_to_stage")) {
        Add-Failure "Missing required field: files_not_to_stage"
    }
    if (-not ($manifest.PSObject.Properties.Name -contains "commit_message") -or [string]::IsNullOrWhiteSpace([string]$manifest.commit_message)) {
        Add-Failure "Missing required field or value: commit_message"
    }
    if (-not ($manifest.PSObject.Properties.Name -contains "approval_gate_status") -or [string]::IsNullOrWhiteSpace([string]$manifest.approval_gate_status)) {
        Add-Failure "Missing required field or value: approval_gate_status"
    }
    if (-not ($manifest.PSObject.Properties.Name -contains "validator_chain_status") -or [string]::IsNullOrWhiteSpace([string]$manifest.validator_chain_status)) {
        Add-Failure "Missing required field or value: validator_chain_status"
    }
    if ($manifest.PSObject.Properties.Name -contains "git_add_strategy") {
        if ([string]$manifest.git_add_strategy -ne "EXPLICIT_FILE_STAGING_ONLY") {
            Add-Failure "git_add_strategy must be EXPLICIT_FILE_STAGING_ONLY when present."
        }
    }
}

if ($failures.Count -eq 0) {
    Write-Host "RESULT: PASS"
    exit 0
}

Write-Host "RESULT: REVIEW_REQUIRED"
foreach ($failure in $failures) {
    Write-Host "- $failure"
}
exit 1

