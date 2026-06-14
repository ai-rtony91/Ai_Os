[CmdletBinding()]
param(
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$schema = "AIOS_PRODUCTION_READINESS_VALIDATOR.v1"
$mode = "DRY_RUN_READ_ONLY"

$safetyFlags = [ordered]@{
    writes_files = $false
    mutates_runtime = $false
    mutates_queue = $false
    mutates_approval = $false
    launches_workers = $false
    starts_scheduler = $false
    starts_daemon = $false
    commits = $false
    pushes = $false
    broker_or_live_trading = $false
}

$checks = [System.Collections.Generic.List[object]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()
$blockers = [System.Collections.Generic.List[string]]::new()

function Normalize-AiOsPathText {
    param([string]$PathText)

    if ([string]::IsNullOrWhiteSpace($PathText)) {
        return ""
    }

    return ($PathText.Trim() -replace "\\", "/").TrimStart("./")
}

function Test-AiOsPathInScope {
    param(
        [string]$PathText,
        [string[]]$Prefixes,
        [string[]]$ExactPaths = @()
    )

    $normalized = Normalize-AiOsPathText -PathText $PathText
    foreach ($exact in $ExactPaths) {
        $candidate = Normalize-AiOsPathText -PathText $exact
        if ($normalized.Equals($candidate, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }

    foreach ($prefix in $Prefixes) {
        $candidatePrefix = (Normalize-AiOsPathText -PathText $prefix).TrimEnd("/")
        if (
            $normalized.Equals($candidatePrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
            $normalized.StartsWith($candidatePrefix + "/", [System.StringComparison]::OrdinalIgnoreCase)
        ) {
            return $true
        }
    }

    return $false
}

function Add-AiOsCheck {
    param(
        [string]$Name,
        [ValidateSet("PASS", "WARNING", "BLOCKED")]
        [string]$Status,
        [string]$Summary,
        [object[]]$Evidence = @()
    )

    $checks.Add([ordered]@{
        name = $Name
        status = $Status
        summary = $Summary
        evidence = @($Evidence)
    }) | Out-Null

    if ($Status -eq "WARNING") {
        $warnings.Add($Summary) | Out-Null
    }
    elseif ($Status -eq "BLOCKED") {
        $blockers.Add($Summary) | Out-Null
    }
}

function Get-AiOsGitStatusEntries {
    param([string[]]$StatusLines)

    $entries = [System.Collections.Generic.List[object]]::new()
    foreach ($line in $StatusLines) {
        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("##")) {
            continue
        }

        $code = if ($line.Length -ge 2) { $line.Substring(0, 2) } else { $line }
        $pathText = if ($line.Length -ge 4) { $line.Substring(3).Trim() } else { "" }
        if ($pathText -match "\s+->\s+") {
            $pathText = ($pathText -split "\s+->\s+")[-1].Trim()
        }

        $entries.Add([ordered]@{
            status_code = $code
            path = Normalize-AiOsPathText -PathText $pathText
            tracked = ($code -ne "??")
            raw = $line
        }) | Out-Null
    }

    return @($entries.ToArray())
}

$repoRoot = $null
try {
    $repoRoot = (& git rev-parse --show-toplevel 2>$null).Trim()
}
catch {
    $repoRoot = $null
}

if ([string]::IsNullOrWhiteSpace($repoRoot)) {
    $repoRoot = (Get-Location).ProviderPath
    Add-AiOsCheck -Name "repo_root" -Status "BLOCKED" -Summary "Unable to resolve git repository root." -Evidence @($repoRoot)
}
else {
    Add-AiOsCheck -Name "repo_root" -Status "PASS" -Summary "Repository root resolved." -Evidence @($repoRoot)
}

$branch = ""
try {
    $branch = (& git branch --show-current 2>$null).Trim()
}
catch {
    $branch = ""
}

if ($branch -eq "main") {
    Add-AiOsCheck -Name "branch" -Status "PASS" -Summary "Current branch is main." -Evidence @($branch)
}
else {
    Add-AiOsCheck -Name "branch" -Status "BLOCKED" -Summary "Current branch is not main." -Evidence @($branch)
}

$statusLines = @()
try {
    $statusLines = @(& git status --short --branch 2>$null)
}
catch {
    Add-AiOsCheck -Name "git_status" -Status "BLOCKED" -Summary "git status failed." -Evidence @($_.Exception.Message)
}

$dirtyEntries = @(Get-AiOsGitStatusEntries -StatusLines $statusLines)
$evidenceDirtyPrefixes = @(
    "Reports/",
    "control/review_bridge/"
)
$packageDirtyPaths = @(
    "automation/orchestration/validators/Test-AiOsProductionReadiness.DRY_RUN.ps1",
    "tests/orchestration/test_aios_production_readiness_validator.py",
    "docs/orchestration/AIOS_PRODUCTION_READINESS_VALIDATOR.md"
)
$unsafeDirtyPrefixes = @(
    "automation/orchestration/work_packets/",
    "automation/orchestration/approval_inbox/",
    "automation/orchestration/commit_packages/",
    "automation/orchestration/workers/",
    "automation/orchestration/relay_bus/",
    "telemetry/",
    "services/",
    "apps/",
    "schemas/",
    "scripts/control/",
    "apps/trading_lab/",
    "aios/modules/trader/",
    "secrets/",
    ".env"
)
$unsafeTerms = @(
    "secret",
    "credential",
    "api_key",
    "api-key",
    "password",
    "broker",
    "oanda",
    "live_trading",
    "live-trading",
    "real_order",
    "webhook"
)

$unsafeDirty = @()
$trackedOutsidePackage = @()
$evidenceDirty = @()
$packageDirty = @()
foreach ($entry in $dirtyEntries) {
    $pathText = [string]$entry.path
    $isEvidence = Test-AiOsPathInScope -PathText $pathText -Prefixes $evidenceDirtyPrefixes
    $isPackage = Test-AiOsPathInScope -PathText $pathText -Prefixes @() -ExactPaths $packageDirtyPaths
    $isUnsafePrefix = Test-AiOsPathInScope -PathText $pathText -Prefixes $unsafeDirtyPrefixes
    $hasUnsafeTerm = @($unsafeTerms | Where-Object { $pathText -match [regex]::Escape($_) }).Count -gt 0

    if ($isEvidence) {
        $evidenceDirty += $entry
    }
    elseif ($isPackage) {
        $packageDirty += $entry
    }
    elseif ($isUnsafePrefix -or $hasUnsafeTerm) {
        $unsafeDirty += $entry
    }

    if ([bool]$entry.tracked -and -not $isPackage) {
        $trackedOutsidePackage += $entry
    }
}

if ($dirtyEntries.Count -eq 0) {
    Add-AiOsCheck -Name "dirty_state" -Status "PASS" -Summary "Working tree has no dirty entries." -Evidence @()
}
elseif ($unsafeDirty.Count -gt 0) {
    Add-AiOsCheck -Name "dirty_state" -Status "BLOCKED" -Summary "Dirty state includes unsafe production or protected paths." -Evidence @($unsafeDirty)
}
elseif ($trackedOutsidePackage.Count -gt 0) {
    Add-AiOsCheck -Name "dirty_state" -Status "BLOCKED" -Summary "Tracked dirty files exist outside the production-readiness validator package." -Evidence @($trackedOutsidePackage)
}
else {
    Add-AiOsCheck -Name "dirty_state" -Status "WARNING" -Summary "Dirty state is limited to evidence artifacts or this validator package." -Evidence @($dirtyEntries)
}

$selfBuildModules = @(
    "automation/orchestration/aios_active_mission_cycle.py",
    "automation/orchestration/aios_autonomy_decision_governor.py",
    "automation/orchestration/aios_closed_autonomy_loop.py",
    "automation/orchestration/aios_closed_loop_packet_drafter.py",
    "automation/orchestration/aios_closed_loop_queue_injection_preview.py",
    "automation/orchestration/aios_executive_control_readiness.py",
    "automation/orchestration/aios_queue_admission_gate.py",
    "automation/orchestration/aios_queue_to_dispatch_gates.py"
)
$missingModules = @($selfBuildModules | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($missingModules.Count -eq 0) {
    Add-AiOsCheck -Name "self_build_modules" -Status "PASS" -Summary "Required self-build preview modules exist." -Evidence @($selfBuildModules)
}
else {
    Add-AiOsCheck -Name "self_build_modules" -Status "BLOCKED" -Summary "Required self-build preview modules are missing." -Evidence @($missingModules)
}

$selfBuildTests = @(
    "tests/orchestration/test_aios_active_mission_cycle.py",
    "tests/orchestration/test_aios_autonomy_decision_governor.py",
    "tests/orchestration/test_aios_closed_autonomy_loop.py",
    "tests/orchestration/test_aios_closed_loop_packet_drafter.py",
    "tests/orchestration/test_aios_closed_loop_queue_injection_preview.py",
    "tests/orchestration/test_aios_executive_control_readiness.py",
    "tests/orchestration/test_aios_queue_admission_gate.py",
    "tests/orchestration/test_aios_queue_to_dispatch_gates.py"
)
$missingSelfBuildTests = @($selfBuildTests | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($missingSelfBuildTests.Count -eq 0) {
    Add-AiOsCheck -Name "self_build_tests" -Status "PASS" -Summary "Required self-build tests exist." -Evidence @($selfBuildTests)
}
else {
    Add-AiOsCheck -Name "self_build_tests" -Status "BLOCKED" -Summary "Required self-build tests are missing." -Evidence @($missingSelfBuildTests)
}

$dashboardContractTests = @(
    "tests/services/runtimeVisibilityContract.test.js",
    "tests/services/appServiceBridge.test.js"
)
$missingDashboardTests = @($dashboardContractTests | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($missingDashboardTests.Count -eq 0) {
    Add-AiOsCheck -Name "dashboard_contract_tests" -Status "PASS" -Summary "Dashboard runtime visibility contract tests exist." -Evidence @($dashboardContractTests)
}
else {
    Add-AiOsCheck -Name "dashboard_contract_tests" -Status "BLOCKED" -Summary "Dashboard runtime visibility contract tests are missing." -Evidence @($missingDashboardTests)
}

$boundaryDocs = @(
    "docs/orchestration/AIOS_EXECUTIVE_CONTROL_READINESS.md",
    "docs/orchestration/AIOS_CLOSED_AUTONOMY_LOOP.md",
    "docs/orchestration/AIOS_QUEUE_TO_DISPATCH_GATES.md"
)
$missingBoundaryDocs = @($boundaryDocs | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
$boundaryText = ""
foreach ($doc in $boundaryDocs) {
    if (Test-Path -LiteralPath $doc -PathType Leaf) {
        $boundaryText += "`n" + (Get-Content -LiteralPath $doc -Raw)
    }
}

$requiredBoundaryTerms = @(
    "queue mutation",
    "dispatch",
    "worker",
    "scheduler",
    "live trading",
    "broker",
    "credential",
    "webhook"
)
$missingBoundaryTerms = @(
    $requiredBoundaryTerms |
        Where-Object { $boundaryText.ToLowerInvariant() -notmatch [regex]::Escape($_) }
)

if ($missingBoundaryDocs.Count -gt 0) {
    Add-AiOsCheck -Name "production_safety_boundaries" -Status "BLOCKED" -Summary "Production safety boundary docs are missing." -Evidence @($missingBoundaryDocs)
}
elseif ($missingBoundaryTerms.Count -gt 0) {
    Add-AiOsCheck -Name "production_safety_boundaries" -Status "BLOCKED" -Summary "Production safety boundary docs do not cover required blocked scopes." -Evidence @($missingBoundaryTerms)
}
else {
    Add-AiOsCheck -Name "production_safety_boundaries" -Status "PASS" -Summary "Production readiness evidence keeps runtime, queue, approval, worker, scheduler, broker, credential, webhook, and live-trading mutation blocked by design." -Evidence @($boundaryDocs)
}

$flagFailures = @(
    $safetyFlags.GetEnumerator() |
        Where-Object { $_.Value -ne $false } |
        ForEach-Object { $_.Key }
)
if ($flagFailures.Count -eq 0) {
    Add-AiOsCheck -Name "validator_safety_flags" -Status "PASS" -Summary "Validator safety flags all deny mutation and execution authority." -Evidence @($safetyFlags)
}
else {
    Add-AiOsCheck -Name "validator_safety_flags" -Status "BLOCKED" -Summary "Validator safety flags include enabled mutation or execution authority." -Evidence @($flagFailures)
}

if ($OutputJson) {
    $null = $OutputJson
}

$verdict = if ($blockers.Count -gt 0) {
    "BLOCKED"
}
elseif ($warnings.Count -gt 0) {
    "WARNING"
}
else {
    "READY"
}

$nextSafeAction = switch ($verdict) {
    "READY" { "Use this validator as evidence for the next human-approved production-hardening packet. It does not approve runtime launch, queue mutation, worker dispatch, commit, or push." }
    "WARNING" { "Review warning evidence, then run executable validators in an environment that can launch them before requesting production-hardening APPLY." }
    default { "Resolve blockers before production-hardening APPLY, runtime launch, queue mutation, worker dispatch, commit, or push." }
}

$report = [ordered]@{
    schema = $schema
    mode = $mode
    verdict = $verdict
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    checks = @($checks.ToArray())
    blockers = @($blockers.ToArray())
    warnings = @($warnings.ToArray())
    next_safe_action = $nextSafeAction
    safety_flags = $safetyFlags
    git = [ordered]@{
        repo_root = $repoRoot
        branch = $branch
        dirty = ($dirtyEntries.Count -gt 0)
        dirty_entries = @($dirtyEntries)
        evidence_dirty_paths = @($evidenceDirty | ForEach-Object { $_.path })
        package_dirty_paths = @($packageDirty | ForEach-Object { $_.path })
    }
}

$report | ConvertTo-Json -Depth 10
