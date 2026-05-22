[CmdletBinding()]
param(
    [string]$WorkerId = "UNKNOWN",
    [string]$ExpectedLaneId = "",
    [string[]]$ProposedPaths = @(),
    [string]$WorkerProfilesPath = "automation/orchestration/workers/AIOS_WORKER_PROFILES.json",
    [string]$WorkerRegistryPath = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json",
    [string]$LockRegistryPath = "automation/orchestration/locks/FILE_LOCK_REGISTRY_001.json",
    [int]$StaleMinutes = 60,
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Add-Finding {
    param(
        [System.Collections.Generic.List[object]]$Findings,
        [string]$Severity,
        [string]$CheckId,
        [string]$Message,
        [string]$Evidence = "UNKNOWN",
        [string]$NextSafeAction = "Review before continuing."
    )

    $Findings.Add([pscustomobject]@{
        severity = $Severity
        check_id = $CheckId
        message = $Message
        evidence = $Evidence
        next_safe_action = $NextSafeAction
    }) | Out-Null
}

function Resolve-AiOsPath {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) { return "" }
    if ([System.IO.Path]::IsPathRooted($Path)) { return $Path }
    return (Join-Path (Get-Location).Path $Path)
}

function Read-AiOsJson {
    param(
        [string]$Path,
        [string]$Label,
        [System.Collections.Generic.List[object]]$Findings
    )

    $resolved = Resolve-AiOsPath -Path $Path
    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
        Add-Finding -Findings $Findings -Severity "BLOCKED" -CheckId "json_missing" -Message "$Label file is missing." -Evidence $Path -NextSafeAction "Stop and restore or correct the read path."
        return $null
    }

    try {
        return Get-Content -LiteralPath $resolved -Raw | ConvertFrom-Json
    }
    catch {
        Add-Finding -Findings $Findings -Severity "BLOCKED" -CheckId "json_parse_failed" -Message "$Label JSON parse failed." -Evidence $_.Exception.Message -NextSafeAction "Stop and repair JSON through an approved APPLY task."
        return $null
    }
}

function ConvertTo-AiOsPathKey {
    param([AllowNull()][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) { return "" }
    $key = $Path.Replace("\", "/").Trim()
    while ($key.StartsWith("./")) {
        $key = $key.Substring(2)
    }
    return $key.TrimEnd("/")
}

function Test-AiOsPathOverlap {
    param(
        [string]$LeftPath,
        [string]$RightPath
    )

    $left = ConvertTo-AiOsPathKey -Path $LeftPath
    $right = ConvertTo-AiOsPathKey -Path $RightPath
    if ([string]::IsNullOrWhiteSpace($left) -or [string]::IsNullOrWhiteSpace($right)) { return $false }
    return ($left -eq $right -or $left.StartsWith("$right/") -or $right.StartsWith("$left/"))
}

function Test-AiOsProtectedPath {
    param([string]$Path)

    $normalized = ConvertTo-AiOsPathKey -Path $Path
    $patterns = @(
        "^AGENTS\.md$",
        "^README\.md$",
        "^RISK_POLICY\.md$",
        "^WHITEPAPER\.md$",
        "^\.git(/|$)",
        "^\.codex_backups(/|$)",
        "^apps(/|$)",
        "^services(/|$)",
        "^telemetry(/|$)",
        "^Reports(/|$)",
        "^archive(/|$)",
        "^secrets?(/|$)",
        "^credentials?(/|$)",
        "(^|/)\.env($|\.)",
        "(^|/)(broker|oanda|webhook|live[-_]?trading|real[-_]?order)(/|$)",
        "api[-_]?key"
    )

    foreach ($pattern in $patterns) {
        if ($normalized -match $pattern) { return $true }
    }
    return $false
}

function Get-AiOsDateValue {
    param($Object)

    foreach ($field in @("last_heartbeat", "claimed_at", "created_at", "updated_at", "expires_at", "expires_at_placeholder")) {
        if ($Object.PSObject.Properties.Name -contains $field) {
            $value = [string]$Object.$field
            if ([string]::IsNullOrWhiteSpace($value) -or $value -like "*PLACEHOLDER*") { continue }
            try { return [datetime]$value } catch { continue }
        }
    }
    return $null
}

function Get-AiOsLockItems {
    param($LockData)

    if ($null -eq $LockData) { return @() }
    if ($LockData.PSObject.Properties.Name -contains "locks") { return @($LockData.locks) }
    return @($LockData)
}

function Get-AiOsLockPaths {
    param($Lock)

    $paths = @()
    foreach ($field in @("claimed_paths", "locked_paths", "paths")) {
        if ($Lock.PSObject.Properties.Name -contains $field) {
            $paths += @($Lock.$field)
        }
    }
    return @($paths | ForEach-Object { ConvertTo-AiOsPathKey -Path ([string]$_) } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

function Invoke-AiOsGitReadOnly {
    param([string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        exit_code = $exitCode
        output = @($output | ForEach-Object { [string]$_ })
    }
}

$findings = [System.Collections.Generic.List[object]]::new()
$repoRootResult = Invoke-AiOsGitReadOnly -Arguments @("rev-parse", "--show-toplevel")
$branchResult = Invoke-AiOsGitReadOnly -Arguments @("branch", "--show-current")
$statusResult = Invoke-AiOsGitReadOnly -Arguments @("status", "--short", "--branch")

$repoRoot = if ($repoRootResult.exit_code -eq 0 -and $repoRootResult.output.Count -gt 0) { [string]$repoRootResult.output[0] } else { "UNKNOWN" }
$currentBranch = if ($branchResult.exit_code -eq 0 -and $branchResult.output.Count -gt 0) { [string]$branchResult.output[0] } else { "UNKNOWN" }
$currentPath = (Get-Location).Path

if ($repoRootResult.exit_code -ne 0 -or $branchResult.exit_code -ne 0) {
    Add-Finding -Findings $findings -Severity "BLOCKED" -CheckId "git_read_failed" -Message "Could not read repo root or branch." -Evidence (($repoRootResult.output + $branchResult.output) -join " | ") -NextSafeAction "Stop and verify this is the active AI_OS repo."
}

foreach ($authorityPath in @("AGENTS.md", "README.md", "docs/governance/source-of-truth-map.md")) {
    if (-not (Test-Path -LiteralPath $authorityPath -PathType Leaf)) {
        Add-Finding -Findings $findings -Severity "BLOCKED" -CheckId "authority_missing" -Message "Required authority file is missing." -Evidence $authorityPath -NextSafeAction "Stop until active authority is restored."
    }
}

$workerProfiles = Read-AiOsJson -Path $WorkerProfilesPath -Label "Worker profiles" -Findings $findings
$workerRegistry = Read-AiOsJson -Path $WorkerRegistryPath -Label "Worker registry" -Findings $findings
$lockRegistry = Read-AiOsJson -Path $LockRegistryPath -Label "Lock registry" -Findings $findings

$profileWorker = $null
$registryWorker = $null
if ($null -ne $workerProfiles -and ($workerProfiles.PSObject.Properties.Name -contains "workers")) {
    $profileWorker = @($workerProfiles.workers | Where-Object { [string]$_.worker_id -eq $WorkerId }) | Select-Object -First 1
}
if ($null -ne $workerRegistry -and ($workerRegistry.PSObject.Properties.Name -contains "workers")) {
    $registryWorker = @($workerRegistry.workers | Where-Object { [string]$_.worker_id -eq $WorkerId }) | Select-Object -First 1
}

if ($WorkerId -eq "UNKNOWN" -or [string]::IsNullOrWhiteSpace($WorkerId)) {
    Add-Finding -Findings $findings -Severity "WARN" -CheckId "worker_unknown" -Message "WorkerId was not supplied." -Evidence $WorkerId -NextSafeAction "Rerun with a known WorkerId before APPLY or worker escalation."
}
elseif ($null -eq $profileWorker -and $null -eq $registryWorker) {
    Add-Finding -Findings $findings -Severity "BLOCKED" -CheckId "worker_not_registered" -Message "WorkerId was not found in worker profiles or registry." -Evidence $WorkerId -NextSafeAction "Stop until the worker identity is registered or explicitly approved."
}
elseif ($null -eq $profileWorker) {
    Add-Finding -Findings $findings -Severity "WARN" -CheckId "worker_profile_missing" -Message "Worker found in registry but not in profiles." -Evidence $WorkerId -NextSafeAction "Review profile coverage before assigning scoped work."
}

if (-not [string]::IsNullOrWhiteSpace($ExpectedLaneId) -and $ExpectedLaneId -ne $WorkerId) {
    Add-Finding -Findings $findings -Severity "BLOCKED" -CheckId "lane_mismatch" -Message "ExpectedLaneId does not match WorkerId." -Evidence "$ExpectedLaneId != $WorkerId" -NextSafeAction "Stop and resolve lane assignment before continuing."
}

$workerAllowedPaths = @()
$workerBlockedPaths = @()
$workerCannotOverlapWith = @()
$expectedPath = "UNKNOWN"
$expectedBranch = "UNKNOWN"
$workerType = "UNKNOWN"
$workerTitle = "UNKNOWN"
if ($null -ne $profileWorker) {
    $workerAllowedPaths = @($profileWorker.owns_paths | ForEach-Object { ConvertTo-AiOsPathKey -Path ([string]$_) } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $workerBlockedPaths = @($profileWorker.blocked_paths | ForEach-Object { ConvertTo-AiOsPathKey -Path ([string]$_) } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $workerCannotOverlapWith = @($profileWorker.cannot_overlap_with)
    $expectedPath = [string]$profileWorker.default_path
    $expectedBranch = [string]$profileWorker.default_branch
    $workerType = [string]$profileWorker.worker_type
    $workerTitle = [string]$profileWorker.display_title

    if (-not [string]::IsNullOrWhiteSpace($expectedPath) -and $expectedPath -ne $currentPath) {
        Add-Finding -Findings $findings -Severity "WARN" -CheckId "path_mismatch" -Message "Current path differs from worker profile default path." -Evidence "$currentPath != $expectedPath" -NextSafeAction "Confirm this worker is operating in the intended repo or worktree."
    }
    if (-not [string]::IsNullOrWhiteSpace($expectedBranch) -and $expectedBranch -ne $currentBranch) {
        Add-Finding -Findings $findings -Severity "WARN" -CheckId "branch_mismatch" -Message "Current branch differs from worker profile default branch." -Evidence "$currentBranch != $expectedBranch" -NextSafeAction "Confirm lane branch before applying changes."
    }
}

$normalizedProposedPaths = @($ProposedPaths | ForEach-Object { ConvertTo-AiOsPathKey -Path ([string]$_) } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
if ($normalizedProposedPaths.Count -eq 0) {
    Add-Finding -Findings $findings -Severity "WARN" -CheckId "no_proposed_paths" -Message "No ProposedPaths were supplied." -Evidence "ProposedPaths empty" -NextSafeAction "Rerun with proposed paths before APPLY or path ownership decisions."
}

foreach ($path in $normalizedProposedPaths) {
    if (Test-AiOsProtectedPath -Path $path) {
        Add-Finding -Findings $findings -Severity "BLOCKED" -CheckId "protected_path_risk" -Message "Proposed path matches protected path rules." -Evidence $path -NextSafeAction "Stop unless the operator explicitly approves this exact protected scope."
    }

    foreach ($blockedPath in $workerBlockedPaths) {
        if (Test-AiOsPathOverlap -LeftPath $path -RightPath $blockedPath) {
            Add-Finding -Findings $findings -Severity "BLOCKED" -CheckId "worker_blocked_path" -Message "Proposed path overlaps worker blocked paths." -Evidence "$path overlaps $blockedPath" -NextSafeAction "Choose a non-blocked path or request explicit operator approval."
        }
    }

    if ($workerAllowedPaths.Count -gt 0) {
        $owned = $false
        foreach ($ownedPath in $workerAllowedPaths) {
            if (Test-AiOsPathOverlap -LeftPath $path -RightPath $ownedPath) {
                $owned = $true
                break
            }
        }
        if (-not $owned) {
            Add-Finding -Findings $findings -Severity "BLOCKED" -CheckId "outside_worker_scope" -Message "Proposed path is outside worker owned paths." -Evidence $path -NextSafeAction "Stop and assign the correct worker or approved lane."
        }
    }
    elseif ($null -ne $profileWorker) {
        Add-Finding -Findings $findings -Severity "WARN" -CheckId "worker_scope_empty" -Message "Worker profile has no owned paths, so proposed path ownership is not proven." -Evidence $path -NextSafeAction "Review lane ownership before APPLY."
    }
}

$locks = Get-AiOsLockItems -LockData $lockRegistry
$now = Get-Date
$lockSummaries = @()
foreach ($lock in $locks) {
    $lockId = if ($lock.PSObject.Properties.Name -contains "lock_id") { [string]$lock.lock_id } else { "UNKNOWN" }
    $lockWorkerId = if ($lock.PSObject.Properties.Name -contains "worker_id") { [string]$lock.worker_id } else { "UNKNOWN" }
    $lockStatus = if ($lock.PSObject.Properties.Name -contains "status") { [string]$lock.status } else { "UNKNOWN" }
    $lockPaths = Get-AiOsLockPaths -Lock $lock
    $lockDate = Get-AiOsDateValue -Object $lock
    $ageMinutes = $null
    if ($null -ne $lockDate) {
        $ageMinutes = [math]::Round(($now - $lockDate).TotalMinutes, 2)
    }

    if (($lockStatus -match "^(?i:ACTIVE|CLAIMED)$") -and $null -ne $ageMinutes -and $ageMinutes -gt $StaleMinutes) {
        Add-Finding -Findings $findings -Severity "WARN" -CheckId "stale_lock_warning" -Message "Active lock appears stale by age threshold." -Evidence "$lockId age=$ageMinutes minutes" -NextSafeAction "Review lock ownership before APPLY."
    }
    if ($lockStatus -match "^(?i:EXPIRED|STALE|REVIEW_REQUIRED)$") {
        Add-Finding -Findings $findings -Severity "WARN" -CheckId "review_lock_status" -Message "Lock status requires review." -Evidence "$lockId status=$lockStatus" -NextSafeAction "Resolve lock status before APPLY."
    }

    foreach ($path in $normalizedProposedPaths) {
        foreach ($lockPath in $lockPaths) {
            if (($lockStatus -match "^(?i:ACTIVE|CLAIMED)$") -and (Test-AiOsPathOverlap -LeftPath $path -RightPath $lockPath)) {
                $severity = if ($lockWorkerId -eq $WorkerId) { "WARN" } else { "BLOCKED" }
                Add-Finding -Findings $findings -Severity $severity -CheckId "lock_path_overlap" -Message "Proposed path overlaps an active lock." -Evidence "$path overlaps $lockPath owned by $lockWorkerId" -NextSafeAction "Resolve path ownership before APPLY."
            }
        }
    }

    $lockSummaries += [pscustomobject]@{
        lock_id = $lockId
        worker_id = $lockWorkerId
        status = $lockStatus
        paths = $lockPaths
        age_minutes = $ageMinutes
    }
}

foreach ($worker in @($workerRegistry.workers)) {
    $workerDate = Get-AiOsDateValue -Object $worker
    if ($null -ne $workerDate) {
        $ageMinutes = [math]::Round(($now - $workerDate).TotalMinutes, 2)
        if ($ageMinutes -gt $StaleMinutes) {
            $staleWorkerId = if ($worker.PSObject.Properties.Name -contains "worker_id") { [string]$worker.worker_id } else { "UNKNOWN" }
            Add-Finding -Findings $findings -Severity "WARN" -CheckId "stale_worker_warning" -Message "Worker record appears stale by age threshold." -Evidence "$staleWorkerId age=$ageMinutes minutes" -NextSafeAction "Review worker state before assigning more work."
        }
    }
}

$blockedCount = @($findings | Where-Object { $_.severity -eq "BLOCKED" }).Count
$warnCount = @($findings | Where-Object { $_.severity -eq "WARN" }).Count
$overallStatus = if ($blockedCount -gt 0) { "BLOCKED" } elseif ($warnCount -gt 0) { "WARN" } else { "PASS" }
$nextSafeAction = switch ($overallStatus) {
    "BLOCKED" { "Stop. Resolve BLOCKED findings before APPLY, worker launch, commit, or push." }
    "WARN" { "Review WARN findings and rerun this preflight with exact WorkerId and ProposedPaths before APPLY." }
    default { "Preflight passed. Human approval is still required before APPLY, commit, push, worker launch, or runtime mutation." }
}

$result = [ordered]@{
    schema = "aios_worker_self_awareness_preflight.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    worker_id = $WorkerId
    expected_lane_id = $ExpectedLaneId
    worker_known_in_profiles = [bool]($null -ne $profileWorker)
    worker_known_in_registry = [bool]($null -ne $registryWorker)
    worker_title = $workerTitle
    worker_type = $workerType
    repo_root = $repoRoot
    current_path = $currentPath
    current_branch = $currentBranch
    git_status = @($statusResult.output)
    expected_path = $expectedPath
    expected_branch = $expectedBranch
    allowed_paths = $workerAllowedPaths
    blocked_paths = $workerBlockedPaths
    cannot_overlap_with = $workerCannotOverlapWith
    proposed_paths = $normalizedProposedPaths
    lock_registry_path = $LockRegistryPath
    lock_count = @($locks).Count
    lock_summaries = $lockSummaries
    findings = @($findings)
    overall_status = $overallStatus
    next_safe_action = $nextSafeAction
    commit_status = "NO"
    push_status = "NO"
    write_count = 0
    delete_count = 0
    move_count = 0
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AI_OS Worker Self-Awareness Preflight"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host "Overall status: $overallStatus"
Write-Host ""
Write-Host "Identity:"
Write-Host "  worker_id: $WorkerId"
Write-Host "  expected_lane_id: $ExpectedLaneId"
Write-Host "  known_in_profiles: $($result.worker_known_in_profiles)"
Write-Host "  known_in_registry: $($result.worker_known_in_registry)"
Write-Host "  worker_title: $workerTitle"
Write-Host "  worker_type: $workerType"
Write-Host ""
Write-Host "Repo:"
Write-Host "  current_path: $currentPath"
Write-Host "  repo_root: $repoRoot"
Write-Host "  current_branch: $currentBranch"
Write-Host "  expected_path: $expectedPath"
Write-Host "  expected_branch: $expectedBranch"
Write-Host ""
Write-Host "Scope:"
Write-Host "  proposed_paths:"
if ($normalizedProposedPaths.Count -eq 0) { Write-Host "    - none" } else { $normalizedProposedPaths | ForEach-Object { Write-Host "    - $_" } }
Write-Host "  allowed_paths:"
if ($workerAllowedPaths.Count -eq 0) { Write-Host "    - none" } else { $workerAllowedPaths | ForEach-Object { Write-Host "    - $_" } }
Write-Host "  blocked_paths:"
if ($workerBlockedPaths.Count -eq 0) { Write-Host "    - none" } else { $workerBlockedPaths | ForEach-Object { Write-Host "    - $_" } }
Write-Host ""
Write-Host "Findings:"
if ($findings.Count -eq 0) {
    Write-Host "  - PASS: no findings"
}
else {
    foreach ($severity in @("BLOCKED", "WARN", "PASS")) {
        foreach ($finding in @($findings | Where-Object { $_.severity -eq $severity })) {
            Write-Host "  - $($finding.severity): $($finding.check_id) - $($finding.message)"
            Write-Host "    Evidence: $($finding.evidence)"
            Write-Host "    Next: $($finding.next_safe_action)"
        }
    }
}
Write-Host ""
Write-Host "Audit:"
Write-Host "  write_count: 0"
Write-Host "  delete_count: 0"
Write-Host "  move_count: 0"
Write-Host "  commit_status: NO"
Write-Host "  push_status: NO"
Write-Host ""
Write-Host "Next safe action: $nextSafeAction"

if ($overallStatus -eq "BLOCKED") { exit 2 }
if ($overallStatus -eq "WARN") { exit 1 }
exit 0
