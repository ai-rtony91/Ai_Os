[CmdletBinding()]
param(
    [string]$SnapshotPath = "automation/operator/window_snapshots/AIOS_10_WORKER_MORNING_SNAPSHOT.example.json"
)

$ErrorActionPreference = "Stop"
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
    param([string]$Message)
    $script:failures.Add($Message) | Out-Null
}

if (-not (Test-Path -LiteralPath ".git")) {
    Add-Failure "Run this validator from the repository root."
}

$requiredFiles = @(
    "automation/operator/window_snapshots/README.md",
    "automation/operator/window_snapshots/AIOS_10_WORKER_MORNING_SNAPSHOT.example.json",
    "automation/operator/Start-AIOSCodexWindowSnapshot.ps1",
    "automation/operator/Test-AIOSCodexWindowSnapshot.DRY_RUN.ps1",
    "docs/AI_OS/dispatcher/runtime/CODEX_WINDOW_SNAPSHOT_BOOTSTRAP.md",
    "Reports/dispatcher/runtime/codex_window_snapshot_status.example.json"
)

Write-Host "AI_OS Codex Window Snapshot DRY_RUN Validator"
Write-Host ""
Write-Host "Required files:"
foreach ($file in $requiredFiles) {
    if (Test-Path -LiteralPath $file) {
        Write-Host " - FOUND: $file"
    }
    else {
        Write-Host " - MISSING: $file"
        Add-Failure "Missing required file: $file"
    }
}

Write-Host ""
Write-Host "Parsing JSON files:"
$jsonFiles = @(
    "automation/operator/window_snapshots/AIOS_10_WORKER_MORNING_SNAPSHOT.example.json",
    "Reports/dispatcher/runtime/codex_window_snapshot_status.example.json"
)

foreach ($json in $jsonFiles) {
    if (Test-Path -LiteralPath $json) {
        try {
            $parsed = Get-Content -LiteralPath $json -Raw | ConvertFrom-Json
            Write-Host " - JSON OK: $json"
            if ($parsed.schema -notlike "*.v1") {
                Add-Failure "Schema must end in .v1: $json"
            }
        }
        catch {
            Add-Failure "JSON parse failed: $json"
        }
    }
}

if (Test-Path -LiteralPath $SnapshotPath) {
    $snapshot = Get-Content -LiteralPath $SnapshotPath -Raw | ConvertFrom-Json
    if ($snapshot.workers.Count -ne 10) {
        Add-Failure "Snapshot must contain exactly 10 workers."
    }
    foreach ($worker in $snapshot.workers) {
        if (-not $worker.worker_id -or -not $worker.worker_label -or -not $worker.next_safe_action) {
            Add-Failure "Worker entry missing required fields."
        }
    }
}

Write-Host ""
Write-Host "PowerShell parse checks:"
$psFiles = @(
    "automation/operator/Start-AIOSCodexWindowSnapshot.ps1",
    "automation/operator/Test-AIOSCodexWindowSnapshot.DRY_RUN.ps1"
)

foreach ($psFile in $psFiles) {
    if (Test-Path -LiteralPath $psFile) {
        $tokens = $null
        $errors = $null
        [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath $psFile), [ref]$tokens, [ref]$errors) | Out-Null
        if ($errors.Count -gt 0) {
            Add-Failure "PowerShell parse failed: $psFile"
        }
        else {
            Write-Host " - PowerShell OK: $psFile"
        }
    }
}

Write-Host ""
Write-Host "Git status:"
& git status --short --branch
if ($LASTEXITCODE -ne 0) {
    Add-Failure "git status failed."
}

Write-Host ""
Write-Host "Git diff check:"
& git diff --check
if ($LASTEXITCODE -ne 0) {
    Add-Failure "git diff --check failed."
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "RESULT: PASS"
    exit 0
}

Write-Host "RESULT: FAIL"
foreach ($failure in $failures) {
    Write-Host " - $failure"
}
exit 1

