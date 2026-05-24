param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "SilentlyContinue"

$scriptName = Split-Path -Leaf $PSCommandPath
$repoRoot = Split-Path (Split-Path (Split-Path (Split-Path $PSCommandPath -Parent) -Parent) -Parent) -Parent

function Resolve-RepoPath {
    param([string]$Rel)
    return [System.IO.Path]::GetFullPath((Join-Path $repoRoot $Rel))
}

# --- Canonical orchestration worker registry ---
$orchRegistryPath    = Resolve-RepoPath "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"
$orchProfilesPath    = Resolve-RepoPath "automation/orchestration/workers/AIOS_WORKER_PROFILES.json"
$orchInboxPath       = Resolve-RepoPath "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"
$windowRegistryPath  = Resolve-RepoPath "automation/window_identity/AIOS_WORKER_REGISTRY.json"
$heartbeatDir        = Resolve-RepoPath "automation/orchestration/workers"
$legacyHeartbeatScript = Resolve-RepoPath "scripts/write-worker-heartbeat.ps1"
$legacyStaleScript     = Resolve-RepoPath "scripts/detect-stale-workers.ps1"

function Read-JsonSafe {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try { return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json } catch { return $null }
}

function Count-ArrayOrProps {
    param($obj)
    if ($null -eq $obj) { return 0 }
    if ($obj -is [array]) { return $obj.Count }
    return ($obj | Get-Member -MemberType NoteProperty).Count
}

# --- Read registries ---
$orchRegistry  = Read-JsonSafe $orchRegistryPath
$orchProfiles  = Read-JsonSafe $orchProfilesPath
$orchInbox     = Read-JsonSafe $orchInboxPath
$windowReg     = Read-JsonSafe $windowRegistryPath

# --- Heartbeat artifacts ---
$heartbeatFiles = @()
if (Test-Path -LiteralPath $heartbeatDir) {
    $heartbeatFiles = Get-ChildItem -LiteralPath $heartbeatDir -Filter "*heartbeat.json" -File -ErrorAction SilentlyContinue
}

# --- Legacy scripts ---
$legacyScripts = @()
if (Test-Path -LiteralPath $legacyHeartbeatScript) {
    $legacyScripts += [ordered]@{
        path            = $legacyHeartbeatScript
        purpose         = "writes worker heartbeat JSON to orchestration workers dir"
        classification  = "NEEDS_USER_DECISION"
        note            = "Compare with orchestration worker heartbeat model before keeping or archiving."
    }
}
if (Test-Path -LiteralPath $legacyStaleScript) {
    $legacyScripts += [ordered]@{
        path            = $legacyStaleScript
        purpose         = "detects stale workers by heartbeat age; MUTATES heartbeat status field"
        classification  = "NEEDS_USER_DECISION"
        note            = "Script mutates heartbeat JSON files. Evaluate against orchestration-native stale detection before keeping."
    }
}

# --- Overlap analysis ---
$orchRegistryExists  = $null -ne $orchRegistry
$windowRegExists     = $null -ne $windowReg
$overlapPresent      = $orchRegistryExists -and $windowRegExists

# --- Summary report ---
$report = [ordered]@{
    mode                      = "READ_ONLY"
    script                    = $scriptName
    commit_performed          = $false
    push_performed            = $false

    orchestration_registry = [ordered]@{
        path              = $orchRegistryPath
        exists            = $orchRegistryExists
        classification    = "KEEP_ACTIVE"
        note              = "Canonical worker identity authority per active-system-map.md. High dependency risk."
        entry_count       = Count-ArrayOrProps $orchRegistry
    }

    worker_profiles = [ordered]@{
        path              = $orchProfilesPath
        exists            = ($null -ne $orchProfiles)
        classification    = "KEEP_ACTIVE"
        note              = "Worker capability source used by packet routing and bootstrap checks."
        entry_count       = Count-ArrayOrProps $orchProfiles
    }

    worker_inbox = [ordered]@{
        path              = $orchInboxPath
        exists            = ($null -ne $orchInbox)
        classification    = "KEEP_ACTIVE"
        note              = "Active runtime state. Do not delete or move without dependency test."
    }

    window_identity_registry = [ordered]@{
        path              = $windowRegistryPath
        exists            = $windowRegExists
        classification    = "NEEDS_USER_DECISION"
        note              = "Separate from orchestration registry. Currently used for terminal/window presentation. Decision needed on whether to consolidate."
    }

    heartbeat_artifacts = [ordered]@{
        directory         = $heartbeatDir
        file_count        = $heartbeatFiles.Count
        files             = @($heartbeatFiles | ForEach-Object { $_.Name })
        classification    = "REMOVE_RELOCATE_CANDIDATE"
        note              = "Generated runtime state. Relocate or clean up after retention decision. Do not delete while supervisor depends on them."
    }

    legacy_scripts = [ordered]@{
        count             = $legacyScripts.Count
        items             = $legacyScripts
    }

    overlap_summary = [ordered]@{
        dual_registry_present = $overlapPresent
        note                  = if ($overlapPresent) {
            "Both orchestration/workers/AIOS_WORKER_REGISTRY.json and window_identity/AIOS_WORKER_REGISTRY.json exist. Orchestration registry is canonical for worker identity. Window identity registry is for terminal/window presentation only per active-system-map.md."
        } else {
            "No dual-registry overlap detected."
        }
    }

    recommended_ownership_classification = @(
        "orchestration/workers/AIOS_WORKER_REGISTRY.json -> CANONICAL worker identity authority",
        "orchestration/workers/AIOS_WORKER_PROFILES.json -> CANONICAL worker capabilities",
        "orchestration/workers/inbox/AIOS_WORKER_INBOX.json -> ACTIVE runtime state (protect)",
        "window_identity/AIOS_WORKER_REGISTRY.json -> TERMINAL PRESENTATION (decision needed on consolidation)",
        "workers/*heartbeat.json -> GENERATED RUNTIME STATE (relocate after retention decision)",
        "scripts/write-worker-heartbeat.ps1 -> LEGACY SCRIPT (compare with orchestration model)",
        "scripts/detect-stale-workers.ps1 -> LEGACY SCRIPT (mutates heartbeat files; evaluate against orchestration-native approach)"
    )

    recommended_next_safe_action = "Read docs/audits/active-system-map.md Active Worker Chain section. Decide whether window_identity registry should merge with orchestration registry before any consolidation. No mutation performed here."
}

if ($QuietJson) {
    $report | ConvertTo-Json -Depth 6
    exit 0
}

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Worker State Ownership Inspector" -ForegroundColor Cyan
Write-Host "Mode: READ_ONLY - no files modified"
Write-Host ""

Write-Host "=== Orchestration Registry ===" -ForegroundColor Yellow
Write-Host "  path:    $($report.orchestration_registry.path)"
Write-Host "  exists:  $($report.orchestration_registry.exists)"
Write-Host "  entries: $($report.orchestration_registry.entry_count)"
Write-Host "  class:   $($report.orchestration_registry.classification)" -ForegroundColor Green

Write-Host ""
Write-Host "=== Worker Profiles ===" -ForegroundColor Yellow
Write-Host "  path:    $($report.worker_profiles.path)"
Write-Host "  exists:  $($report.worker_profiles.exists)"
Write-Host "  entries: $($report.worker_profiles.entry_count)"
Write-Host "  class:   $($report.worker_profiles.classification)" -ForegroundColor Green

Write-Host ""
Write-Host "=== Worker Inbox ===" -ForegroundColor Yellow
Write-Host "  path:    $($report.worker_inbox.path)"
Write-Host "  exists:  $($report.worker_inbox.exists)"
Write-Host "  class:   $($report.worker_inbox.classification)" -ForegroundColor Green

Write-Host ""
Write-Host "=== Window Identity Registry ===" -ForegroundColor Yellow
Write-Host "  path:    $($report.window_identity_registry.path)"
Write-Host "  exists:  $($report.window_identity_registry.exists)"
Write-Host "  class:   $($report.window_identity_registry.classification)" -ForegroundColor Cyan

Write-Host ""
Write-Host "=== Heartbeat Artifacts ===" -ForegroundColor Yellow
Write-Host "  directory:  $($report.heartbeat_artifacts.directory)"
Write-Host "  file count: $($report.heartbeat_artifacts.file_count)"
if ($report.heartbeat_artifacts.files.Count -gt 0) {
    foreach ($f in $report.heartbeat_artifacts.files) { Write-Host "    - $f" }
}
Write-Host "  class: $($report.heartbeat_artifacts.classification)" -ForegroundColor Cyan

Write-Host ""
Write-Host "=== Legacy Scripts ===" -ForegroundColor Yellow
if ($legacyScripts.Count -eq 0) {
    Write-Host "  None detected."
} else {
    foreach ($ls in $legacyScripts) {
        Write-Host "  $($ls.path)"
        Write-Host "  purpose: $($ls.purpose)"
        Write-Host "  class:   $($ls.classification)" -ForegroundColor Cyan
        Write-Host "  note:    $($ls.note)"
    }
}

Write-Host ""
Write-Host "=== Overlap Summary ===" -ForegroundColor Yellow
Write-Host "  dual_registry_present: $($report.overlap_summary.dual_registry_present)"
Write-Host "  $($report.overlap_summary.note)"

Write-Host ""
Write-Host "=== Ownership Classification ===" -ForegroundColor Yellow
foreach ($line in $report.recommended_ownership_classification) {
    Write-Host "  $line"
}

Write-Host ""
Write-Host "=== Recommended Next Safe Action ===" -ForegroundColor Green
Write-Host "  $($report.recommended_next_safe_action)"

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")

exit 0
