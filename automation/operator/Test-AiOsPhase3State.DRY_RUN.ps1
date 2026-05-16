param(
    [string]$RepoRoot = "."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $RepoRoot).Path
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
    param([string]$Message)
    $script:failures.Add($Message) | Out-Null
    Write-Host "FAIL: $Message" -ForegroundColor Red
}

function Read-Json {
    param([string]$RelativePath)
    $path = Join-Path $root $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Add-Failure "Missing file: $RelativePath"
        return $null
    }
    try {
        return Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    } catch {
        Add-Failure "JSON parse failed: $RelativePath :: $($_.Exception.Message)"
        return $null
    }
}

function Test-Parse {
    param([string]$RelativePath)
    $path = Join-Path $root $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Add-Failure "Missing PowerShell file: $RelativePath"
        return
    }
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors) | Out-Null
    foreach ($errorItem in @($errors)) {
        Add-Failure "PowerShell parse failed: $RelativePath :: $($errorItem.Message)"
    }
}

Write-Host "AI_OS Phase 3 Stateful Orchestration DRY_RUN Validator"

$required = @(
    "work_packets/state/aios_queue_state.example.json",
    "work_packets/approvals/aios_approval_inbox.example.json",
    "work_packets/lifecycle.schema.json",
    "automation/operator/Invoke-AiOsApprovalGate.ps1",
    "automation/operator/Invoke-AiOsStatefulDispatcher.ps1",
    "automation/operator/Test-AiOsPhase3State.DRY_RUN.ps1",
    "docs/AI_OS/orchestration/AIOS_PHASE3_STATEFUL_ORCHESTRATION.md"
)

foreach ($file in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $file) -PathType Leaf)) {
        Add-Failure "Missing required file: $file"
    }
}

$queue = Read-Json "work_packets/state/aios_queue_state.example.json"
$inbox = Read-Json "work_packets/approvals/aios_approval_inbox.example.json"
$schema = Read-Json "work_packets/lifecycle.schema.json"

if ($queue -and $queue.mode -ne "DRY_RUN_ONLY") { Add-Failure "Queue state mode must be DRY_RUN_ONLY" }
if ($inbox -and $inbox.mode -ne "DRY_RUN_ONLY") { Add-Failure "Approval inbox mode must be DRY_RUN_ONLY" }
if ($schema -and $schema.'$id' -ne "AIOS_PHASE3_LIFECYCLE.v1") { Add-Failure "Lifecycle schema id mismatch" }

foreach ($script in @("automation/operator/Invoke-AiOsApprovalGate.ps1", "automation/operator/Invoke-AiOsStatefulDispatcher.ps1", "automation/operator/Test-AiOsPhase3State.DRY_RUN.ps1")) {
    Test-Parse $script
    $text = Get-Content -LiteralPath (Join-Path $root $script) -Raw
    $blockedTokens = @(
        ("Start" + "-Process"),
        ("Register" + "-ScheduledTask"),
        ("git " + "commit"),
        ("git " + "push"),
        ("git " + "checkout"),
        ("Invoke" + "-Expression"),
        ("OAN" + "DA"),
        ("web" + "hook"),
        ("live " + "trading")
    )
    foreach ($blocked in $blockedTokens) {
        if ($text.Contains($blocked)) {
            Add-Failure "$script contains blocked token: $blocked"
        }
    }
}

if ($failures.Count -gt 0) {
    Write-Host "AI_OS PHASE 3 STATE VALIDATION: FAIL" -ForegroundColor Red
    exit 1
}

Write-Host "AI_OS PHASE 3 STATE VALIDATION: PASS" -ForegroundColor Green
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
exit 0
