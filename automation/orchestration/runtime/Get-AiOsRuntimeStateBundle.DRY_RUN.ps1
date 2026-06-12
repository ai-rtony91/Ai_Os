param(
    [string[]]$CandidateFile = @(),
    [string]$ValidatorRecommendationPath = "",
    [string]$ValidatorRunReportPath = "",
    [switch]$QuietJson,
    [switch]$OutputJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$checkedAt = (Get-Date).ToString("s")

function ConvertTo-RelativePath {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    $resolved = Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue
    if (-not $resolved) {
        return $Path.Replace("\", "/")
    }

    $rootPath = $repoRoot.Path.TrimEnd("\")
    $resolvedPath = $resolved.Path
    if ($resolvedPath.StartsWith($rootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $resolvedPath.Substring($rootPath.Length).TrimStart("\").Replace("\", "/")
    }

    return $resolvedPath.Replace("\", "/")
}

function Read-JsonSafe {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $null
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            parse_error = $_.Exception.Message
            path = ConvertTo-RelativePath -Path $Path
        }
    }
}

function Invoke-AiOsQuietJsonCommand {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string[]]$Arguments = @()
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        $rawOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $Path @Arguments 2>$null
        $jsonText = ($rawOutput | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($jsonText)) {
            return $null
        }
        return $jsonText | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            parse_error = $_.Exception.Message
            path = ConvertTo-RelativePath -Path $Path
        }
    }
}

function New-Freshness {
    param(
        [int]$TtlSeconds = 3600,
        [bool]$IsStale = $false
    )

    [pscustomobject]@{
        checked_at = $checkedAt
        ttl_seconds = $TtlSeconds
        is_stale = $IsStale
    }
}

function New-FrontendContract {
    param(
        [string]$DisplayState,
        [string[]]$SourcePaths,
        [string]$SourceType,
        [object]$Freshness,
        [string[]]$BlockedActions,
        [string]$NextSafeAction,
        [bool]$ApprovalRequired = $true,
        [bool]$StaleOrLegacy = $false
    )

    $relativeSources = @($SourcePaths | ForEach-Object { ConvertTo-RelativePath -Path $_ })
    $sourcePath = if ($relativeSources.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace([string]$relativeSources[0])) {
        [string]$relativeSources[0]
    } else {
        "runtime_state_bundle"
    }

    [pscustomobject]@{
        display_state = $DisplayState
        authority_state = "EVIDENCE_ONLY"
        source_path = $sourcePath
        source_type = $SourceType
        freshness = $Freshness
        blocked_actions = @($BlockedActions)
        next_safe_action = $NextSafeAction
        approval_required = $ApprovalRequired
        execution_allowed = $false
        mutation_allowed = $false
        stale_or_legacy = $StaleOrLegacy
        safe_for_frontend_display = $true
    }
}

function New-Section {
    param(
        [string]$Status,
        [string[]]$SourcePaths,
        [string]$Summary,
        [object[]]$Items = @(),
        [bool]$IsStale = $false,
        [string[]]$BlockedActions = @(),
        [string]$SourceType = "generated_projection",
        [string]$NextSafeAction = "Review this display-only evidence before any protected action.",
        [bool]$ApprovalRequired = $true
    )

    $freshness = New-Freshness -IsStale $IsStale

    [pscustomobject]@{
        status = $Status
        frontend_contract = New-FrontendContract `
            -DisplayState $Status `
            -SourcePaths $SourcePaths `
            -SourceType $SourceType `
            -Freshness $freshness `
            -BlockedActions $BlockedActions `
            -NextSafeAction $NextSafeAction `
            -ApprovalRequired $ApprovalRequired `
            -StaleOrLegacy $IsStale
        source_paths = @($SourcePaths | ForEach-Object { ConvertTo-RelativePath -Path $_ })
        summary = $Summary
        items = @($Items)
        freshness = $freshness
        blocked_actions = @($BlockedActions)
    }
}

function Get-JsonFiles {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return @()
    }

    @(Get-ChildItem -LiteralPath $Path -File -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object Name)
}

function Normalize-PathText {
    param([string]$Path)
    return (($Path -replace "\\", "/").Trim().Trim("/"))
}

function Test-PathOverlap {
    param(
        [string]$LeftPath,
        [string]$RightPath
    )

    $left = Normalize-PathText -Path $LeftPath
    $right = Normalize-PathText -Path $RightPath

    if ([string]::IsNullOrWhiteSpace($left) -or [string]::IsNullOrWhiteSpace($right)) {
        return $false
    }

    return ($left -eq $right -or $left.StartsWith("$right/") -or $right.StartsWith("$left/"))
}

function Get-ActiveLocks {
    param([AllowNull()]$Registry)

    if ($null -eq $Registry -or $Registry.parse_error) {
        return @()
    }

    $locks = if ($Registry.PSObject.Properties.Name -contains "locks") { @($Registry.locks) } else { @($Registry) }

    @($locks | Where-Object {
        $status = if ($_.PSObject.Properties.Name -contains "status") { [string]$_.status } else { "" }
        $status -notin @("released", "RELEASED", "expired", "EXPIRED")
    })
}

function Get-LockPaths {
    param([AllowNull()]$Lock)

    if ($null -eq $Lock) {
        return @()
    }

    $paths = @()
    if ($Lock.PSObject.Properties.Name -contains "locked_paths") {
        $paths += @($Lock.locked_paths)
    }
    if ($Lock.PSObject.Properties.Name -contains "claimed_paths") {
        $paths += @($Lock.claimed_paths)
    }

    @($paths | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | ForEach-Object { Normalize-PathText -Path ([string]$_) } | Select-Object -Unique)
}

function Test-ExamplePath {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $false
    }

    return ((Normalize-PathText -Path $Path) -match "(?i)(^|[./_-])example([./_-]|$)")
}

function Get-TrustedJsonEvidencePath {
    param(
        [string]$Path,
        [string]$Filter
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return ""
    }

    $file = @(Get-ChildItem -LiteralPath $Path -File -Filter $Filter -ErrorAction SilentlyContinue |
        Where-Object { -not (Test-ExamplePath -Path $_.FullName) } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1)

    if ($file.Count -eq 0) {
        return ""
    }

    return [string]$file[0].FullName
}

function Convert-StatusLineToPath {
    param([string]$Line)

    if ([string]::IsNullOrWhiteSpace($Line) -or $Line.Length -lt 4 -or $Line.StartsWith("##")) {
        return ""
    }

    $path = $Line.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }

    return ($path -replace "\\", "/")
}

$runtimeStatePath = Join-Path $repoRoot.Path "automation\runtime\state\AIOS_RUNTIME_STATE.json"
$packetActivePath = Join-Path $repoRoot.Path "automation\orchestration\work_packets\active"
$packetBlockedPath = Join-Path $repoRoot.Path "automation\orchestration\work_packets\blocked"
$packetCompletePath = Join-Path $repoRoot.Path "automation\orchestration\work_packets\complete"
$workerRegistryPath = Join-Path $repoRoot.Path "automation\orchestration\workers\AIOS_WORKER_REGISTRY.json"
$workerProfilesPath = Join-Path $repoRoot.Path "automation\orchestration\workers\AIOS_WORKER_PROFILES.json"
$workerInboxPath = Join-Path $repoRoot.Path "automation\orchestration\workers\inbox\AIOS_WORKER_INBOX.json"
$lockRegistryPath = Join-Path $repoRoot.Path "automation\orchestration\locks\FILE_LOCK_REGISTRY.json"
$validatorConfigPath = Join-Path $repoRoot.Path "automation\orchestration\validators\VALIDATOR_CHAIN_CONFIG_001.json"
$validatorRecommendationHelperPath = Join-Path $repoRoot.Path "automation\orchestration\validators\Get-AiOsValidatorRecommendation.DRY_RUN.ps1"
$commitPackageRecommendationHelperPath = Join-Path $repoRoot.Path "automation\orchestration\commit_packages\New-AiOsCommitPackageRecommendation.DRY_RUN.ps1"
if ([string]::IsNullOrWhiteSpace($ValidatorRecommendationPath)) {
    $ValidatorRecommendationPath = Get-TrustedJsonEvidencePath -Path (Join-Path $repoRoot.Path "automation\orchestration\validators") -Filter "VALIDATOR_RECOMMENDATION*.json"
}
if ([string]::IsNullOrWhiteSpace($ValidatorRunReportPath)) {
    $ValidatorRunReportPath = Get-TrustedJsonEvidencePath -Path (Join-Path $repoRoot.Path "automation\orchestration\validator_chain_runner") -Filter "VALIDATOR_CHAIN_RUN_REPORT*.json"
}
$validatorConfidenceHelperPath = Join-Path $repoRoot.Path "automation\orchestration\validators\Get-AiOsValidatorConfidence.DRY_RUN.ps1"
$approvalInboxPath = Join-Path $repoRoot.Path "automation\orchestration\approval_inbox\APPROVAL_INBOX_001.json"
$approvalQueuePath = Join-Path $repoRoot.Path "automation\orchestration\approval_inbox\APPLY_APPROVAL_GATE_001.json"
$supervisorSchemaPath = Join-Path $repoRoot.Path "schemas\aios\orchestration\overnight_supervisor.schema.json"
$supervisorRulesPath = Join-Path $repoRoot.Path "automation\orchestration\supervisor\aios_supervision_rules.example.json"

$runtimeState = Read-JsonSafe -Path $runtimeStatePath
$workerRegistry = Read-JsonSafe -Path $workerRegistryPath
$workerProfiles = Read-JsonSafe -Path $workerProfilesPath
$workerInbox = Read-JsonSafe -Path $workerInboxPath
$lockRegistry = Read-JsonSafe -Path $lockRegistryPath
$validatorConfig = Read-JsonSafe -Path $validatorConfigPath
$validatorRecommendation = if ([string]::IsNullOrWhiteSpace($ValidatorRecommendationPath)) {
    Invoke-AiOsQuietJsonCommand -Path $validatorRecommendationHelperPath -Arguments @("-OutputJson")
} else {
    Read-JsonSafe -Path $ValidatorRecommendationPath
}
if ([string]::IsNullOrWhiteSpace($ValidatorRecommendationPath) -and $validatorRecommendation) {
    $ValidatorRecommendationPath = $validatorRecommendationHelperPath
}
$validatorRunReport = Read-JsonSafe -Path $ValidatorRunReportPath
$approvalInbox = Read-JsonSafe -Path $approvalInboxPath
$approvalQueue = Read-JsonSafe -Path $approvalQueuePath
$supervisorRules = Read-JsonSafe -Path $supervisorRulesPath

$gitLines = @(& git -C $repoRoot.Path status --short --branch 2>&1 | ForEach-Object { [string]$_ })
$branchLine = @($gitLines | Where-Object { $_ -like "## *" } | Select-Object -First 1)
$changedLines = @($gitLines | Where-Object { $_ -notlike "## *" })
$candidateFiles = @($changedLines | ForEach-Object { Convert-StatusLineToPath -Line $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) -and $_ -ne ".codex_worktrees/" })
$approvedCandidateFiles = @($CandidateFile | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { Normalize-PathText -Path $_ } | Select-Object -Unique)
$validatorCandidateFiles = if ($approvedCandidateFiles.Count -gt 0) { @($approvedCandidateFiles) } else { @() }
$commitPackageRecommendation = if ($candidateFiles.Count -gt 0) {
    Invoke-AiOsQuietJsonCommand -Path $commitPackageRecommendationHelperPath -Arguments @("-OutputJson")
} else {
    $null
}
$unexpectedDirtyFiles = @()
if ($approvedCandidateFiles.Count -gt 0) {
    $unexpectedDirtyFiles = @($candidateFiles | Where-Object { $approvedCandidateFiles -notcontains (Normalize-PathText -Path $_) })
}
else {
    $unexpectedDirtyFiles = @()
}

$validatorConfidence = $null
if (
    -not [string]::IsNullOrWhiteSpace($ValidatorRecommendationPath) -and
    -not [string]::IsNullOrWhiteSpace($ValidatorRunReportPath) -and
    (Test-Path -LiteralPath $validatorConfidenceHelperPath -PathType Leaf)
) {
    try {
        $validatorConfidenceJson = & $validatorConfidenceHelperPath -CandidateFile $validatorCandidateFiles -ValidatorRecommendationPath $ValidatorRecommendationPath -ValidatorRunReportPath $ValidatorRunReportPath -Json
        $validatorConfidence = $validatorConfidenceJson | ConvertFrom-Json
    }
    catch {
        $validatorConfidence = [pscustomobject]@{
            overall_result = "BLOCKED"
            confidence_score = 0
            confidence_band = "BLOCKED"
            safe_auto_allowed_eligible = $false
            blocked_findings = @("Validator confidence helper failed: $($_.Exception.Message)")
            review_findings = @()
            stop_conditions = @("validator confidence helper failure")
        }
    }
}

$activePackets = Get-JsonFiles -Path $packetActivePath
$blockedPackets = Get-JsonFiles -Path $packetBlockedPath
$completePackets = Get-JsonFiles -Path $packetCompletePath
$packetItems = @()
foreach ($packetFile in @($activePackets + $blockedPackets + $completePackets)) {
    $packet = Read-JsonSafe -Path $packetFile.FullName
    $packetItems += [pscustomobject]@{
        source_path = ConvertTo-RelativePath -Path $packetFile.FullName
        packet_id = if ($packet -and $packet.packet_id) { [string]$packet.packet_id } else { "" }
        status = if ($packet -and $packet.status) { [string]$packet.status } else { "UNKNOWN" }
        title = if ($packet -and $packet.title) { [string]$packet.title } elseif ($packet -and $packet.intent) { [string]$packet.intent } else { "" }
    }
}

$workerItems = @(
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $workerRegistryPath
        kind = "registry"
        count = if ($workerRegistry -and $workerRegistry.workers) { @($workerRegistry.workers).Count } else { 0 }
    },
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $workerProfilesPath
        kind = "profiles"
        count = if ($workerProfiles -and $workerProfiles.workers) { @($workerProfiles.workers).Count } else { 0 }
    },
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $workerInboxPath
        kind = "inbox"
        count = if ($workerInbox -and $workerInbox.items) { @($workerInbox.items).Count } else { 0 }
    }
)

$validatorItems = @(
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $validatorConfigPath
        kind = "config"
        count = if ($validatorConfig -and $validatorConfig.validators) { @($validatorConfig.validators).Count } else { 0 }
    },
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $ValidatorRecommendationPath
        kind = "recommendation"
        result = if ($validatorRecommendation -and $validatorRecommendation.result) { [string]$validatorRecommendation.result } else { "UNKNOWN" }
        trusted_runtime_evidence = [bool](-not [string]::IsNullOrWhiteSpace($ValidatorRecommendationPath))
    },
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $ValidatorRunReportPath
        kind = "run_report"
        result = if ($validatorRunReport -and $validatorRunReport.overall_result) { [string]$validatorRunReport.overall_result } else { "UNKNOWN" }
        trusted_runtime_evidence = [bool](-not [string]::IsNullOrWhiteSpace($ValidatorRunReportPath))
    }
)

$approvalItems = @(
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $approvalInboxPath
        kind = "approval_inbox"
        count = if ($approvalInbox -and $approvalInbox.approvals) { @($approvalInbox.approvals).Count } else { 1 }
    },
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $approvalQueuePath
        kind = "apply_gate"
        packet_id = if ($approvalQueue -and $approvalQueue.packet_id) { [string]$approvalQueue.packet_id } else { "" }
        approval_status = if ($approvalQueue -and $approvalQueue.approval_status) { [string]$approvalQueue.approval_status } else { "UNKNOWN" }
    }
)

$level5SuggestedValidators = @(
    "git diff --check",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-WorkerClaimCollision.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1"
)
$commitPackageExactChangedFiles = @()
$commitPackageRecommendedFiles = @()
$commitPackageRiskFlags = @()
if ($commitPackageRecommendation) {
    $commitPackageExactChangedFiles = @(
        @($commitPackageRecommendation.changed_files)
        @($commitPackageRecommendation.new_files)
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Sort-Object -Unique
    $commitPackageRecommendedFiles = @($commitPackageRecommendation.recommended_files | ForEach-Object { [string]$_.path } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
    $commitPackageRiskFlags = @($commitPackageRecommendation.risks | ForEach-Object {
        if ($_.path -and $_.risk) {
            "$($_.path): $($_.risk)"
        } else {
            [string]$_
        }
    } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}
$commitPackageItems = @(
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $commitPackageRecommendationHelperPath
        kind = "level5_commit_package_preview"
        available = [bool]($null -ne $commitPackageRecommendation)
        status = if ($commitPackageRecommendation -and $commitPackageRecommendation.orchestration_result_contract.status) { [string]$commitPackageRecommendation.orchestration_result_contract.status } elseif ($candidateFiles.Count -gt 0) { "REVIEW" } else { "NOT_NEEDED" }
        exact_changed_files = @($commitPackageExactChangedFiles)
        recommended_files = @($commitPackageRecommendedFiles)
        suggested_validators = @($level5SuggestedValidators)
        risk_flags = @($commitPackageRiskFlags)
        stop_before_staging = "STOP: preview only. Do not run git add, git commit, git push, PR, or merge without separate explicit approval."
        next_safe_action = if ($commitPackageRecommendation -and $commitPackageRecommendation.next_safe_action) { [string]$commitPackageRecommendation.next_safe_action } elseif ($candidateFiles.Count -gt 0) { "Run the commit package preview and review exact files before staging." } else { "No commit package preview is needed while the repo is clean." }
    }
)

$staleConditions = @()
$blockingSignals = @()
$humanRequiredSignals = @()
$parseErrors = @()
$missingSources = @()
$lockConflictSignals = @()

$lockCandidateFiles = @(
    @($candidateFiles)
    @($approvedCandidateFiles)
) | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | ForEach-Object { Normalize-PathText -Path ([string]$_) } | Select-Object -Unique

foreach ($lock in @(Get-ActiveLocks -Registry $lockRegistry)) {
    $workerId = if ($lock.PSObject.Properties.Name -contains "worker_id" -and -not [string]::IsNullOrWhiteSpace([string]$lock.worker_id)) {
        [string]$lock.worker_id
    }
    else {
        "UNKNOWN_WORKER"
    }

    foreach ($lockPath in @(Get-LockPaths -Lock $lock)) {
        foreach ($candidateFile in $lockCandidateFiles) {
            if (Test-PathOverlap -LeftPath $candidateFile -RightPath $lockPath) {
                $lockConflictSignals += "lock_conflict: $candidateFile held by $workerId"
            }
        }
    }
}

if ($lockConflictSignals.Count -gt 0) {
    $blockingSignals += @($lockConflictSignals | Select-Object -Unique)
}

if ($null -eq $runtimeState) {
    $missingSources += ConvertTo-RelativePath -Path $runtimeStatePath
    $staleConditions += [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $runtimeStatePath
        condition = "runtime_state_missing"
        severity = "REVIEW"
        next_safe_action = "Review runtime state source before trusting runtime recommendations."
    }
}
if ($changedLines.Count -gt 0) {
    $staleConditions += [pscustomobject]@{
        source = "git status"
        condition = "working_tree_has_visible_changes"
        severity = "REVIEW"
        next_safe_action = "Review changed and untracked files before protected actions."
    }
}
if ($unexpectedDirtyFiles.Count -gt 0) {
    $humanRequiredSignals += "working_tree_has_unexpected_changes"
    $staleConditions += [pscustomobject]@{
        source = "git status"
        condition = "working_tree_has_unexpected_changes"
        severity = "BLOCKED"
        next_safe_action = "Resolve or explicitly approve unexpected dirty files before protected actions."
        files = @($unexpectedDirtyFiles)
    }
}
if ($activePackets.Count -eq 0) {
    $staleConditions += [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $packetActivePath
        condition = "no_active_packet_files"
        severity = "WARNING"
        next_safe_action = "Confirm whether the active packet queue is intentionally empty."
    }
}

foreach ($sourceObject in @($runtimeState, $workerRegistry, $workerProfiles, $workerInbox, $lockRegistry, $validatorConfig, $validatorRecommendation, $validatorRunReport, $approvalInbox, $approvalQueue, $supervisorRules)) {
    if ($sourceObject -and $sourceObject.parse_error) {
        $parseErrors += ("{0}: {1}" -f $sourceObject.path, $sourceObject.parse_error)
    }
}

if ($validatorConfidence -and $validatorConfidence.blocked_findings) {
    $blockingSignals += @($validatorConfidence.blocked_findings | ForEach-Object { [string]$_ })
}
if ($validatorConfidence -and $validatorConfidence.review_findings) {
    $humanRequiredSignals += @($validatorConfidence.review_findings | ForEach-Object { [string]$_ })
}

$confidenceScore = 80
$confidenceReasons = @("Runtime bundle is generated from read-only evidence.")
if ($staleConditions.Count -gt 0) {
    $confidenceScore = 60
    $confidenceReasons += "Review conditions are present."
}
if ($changedLines.Count -gt 0) {
    $confidenceScore -= 10
    $confidenceReasons += "Working tree is not clean."
}
if ($null -eq $runtimeState) {
    $confidenceScore -= 10
    $confidenceReasons += "Runtime state source is missing."
}
if ($validatorConfidence) {
    $confidenceScore = [Math]::Min($confidenceScore, [int]$validatorConfidence.confidence_score)
    $confidenceReasons += "Validator confidence evidence is included."
    if ($validatorConfidence.overall_result -eq "BLOCKED") {
        $confidenceReasons += "Validator confidence is blocked."
    }
}
elseif ($validatorRecommendation -and -not $validatorRecommendation.parse_error) {
    $confidenceScore -= 5
    $confidenceReasons += "Validator recommendation evidence is included without a validator confidence run report."
}
else {
    $confidenceScore -= 20
    $confidenceReasons += "Validator confidence evidence is missing."
    $humanRequiredSignals += "validator_confidence_missing"
}
if ($confidenceScore -lt 0) {
    $confidenceScore = 0
}

$overallConfidence = "HIGH"
if ($confidenceScore -lt 75) { $overallConfidence = "MEDIUM" }
if ($confidenceScore -lt 50) { $overallConfidence = "LOW" }
if (@($staleConditions | Where-Object { $_.severity -eq "BLOCKED" }).Count -gt 0) { $overallConfidence = "BLOCKED" }
if ($validatorConfidence -and $validatorConfidence.overall_result -eq "BLOCKED") { $overallConfidence = "BLOCKED" }
if ($blockingSignals.Count -gt 0) { $overallConfidence = "BLOCKED" }

$autoGitStopConditions = @(
    "confidence score below 90",
    "blocked validator finding",
    "human-required signal present",
    "validator result is not PASS",
    "runtime confidence is not HIGH",
    "exact-file scope missing",
    "gate result is not clean"
)
$safeAutoAllowed = (
    $confidenceScore -ge 90 -and
    $overallConfidence -eq "HIGH" -and
    $validatorConfidence -and
    $validatorConfidence.overall_result -eq "PASS" -and
    $blockingSignals.Count -eq 0 -and
    $humanRequiredSignals.Count -eq 0
)

$sourceFreshness = @(
    [pscustomobject]@{ source = ConvertTo-RelativePath -Path $runtimeStatePath; checked_at = $checkedAt; is_present = [bool]($null -ne $runtimeState); is_stale = [bool]($null -eq $runtimeState) },
    [pscustomobject]@{ source = ConvertTo-RelativePath -Path $validatorConfigPath; checked_at = $checkedAt; is_present = [bool]($null -ne $validatorConfig); is_stale = [bool]($null -eq $validatorConfig) },
    [pscustomobject]@{ source = ConvertTo-RelativePath -Path $validatorConfidenceHelperPath; checked_at = $checkedAt; is_present = [bool](Test-Path -LiteralPath $validatorConfidenceHelperPath -PathType Leaf); is_stale = [bool]($null -eq $validatorConfidence) },
    [pscustomobject]@{ source = ConvertTo-RelativePath -Path $lockRegistryPath; checked_at = $checkedAt; is_present = [bool]($null -ne $lockRegistry); is_stale = [bool]($null -eq $lockRegistry) },
    [pscustomobject]@{ source = ConvertTo-RelativePath -Path $approvalQueuePath; checked_at = $checkedAt; is_present = [bool]($null -ne $approvalQueue); is_stale = [bool]($null -eq $approvalQueue) }
)

$bundleIntegrityStatus = "PASS"
if ($missingSources.Count -gt 0 -or $humanRequiredSignals.Count -gt 0) { $bundleIntegrityStatus = "REVIEW" }
if ($parseErrors.Count -gt 0 -or $blockingSignals.Count -gt 0) { $bundleIntegrityStatus = "BLOCKED" }

$blockedRuntimeActions = @(
    "write_runtime_state",
    "write_heartbeat",
    "move_packet_state",
    "release_lock",
    "launch_worker",
    "run_apply_path",
    "stage_files",
    "commit_changes",
    "push_changes",
    "schedule_tasks",
    "start_daemon"
)

$bundle = [pscustomobject]@{
    schema = "AIOS_RUNTIME_STATE_BUNDLE.v1"
    schema_version = "1.0"
    generated_at = $checkedAt
    mode = "DRY_RUN"
    authority_boundary = [pscustomobject]@{
        read_only = $true
        approval_authority = "ANTHONY_ONLY"
        generated_evidence_only = $true
        blocked_capabilities = $blockedRuntimeActions
    }
    frontend_contract = New-FrontendContract `
        -DisplayState "DISPLAY_ONLY" `
        -SourcePaths @("automation/orchestration/runtime/Get-AiOsRuntimeStateBundle.DRY_RUN.ps1") `
        -SourceType "runtime_state_bundle" `
        -Freshness (New-Freshness -IsStale $false) `
        -BlockedActions $blockedRuntimeActions `
        -NextSafeAction "Use this bundle as frontend display evidence only. Do not expose execution or mutation controls from it." `
        -ApprovalRequired $false `
        -StaleOrLegacy $false
    packet_state = New-Section -Status "REVIEW" -SourcePaths @($packetActivePath, $packetBlockedPath, $packetCompletePath) -SourceType "canonical_work_packet_evidence" -Summary "Packet folders inspected as read-only runtime evidence." -Items $packetItems -BlockedActions @("packet_state_change", "packet_assignment") -NextSafeAction "Display packet state only; move or assign packets only through a separately approved packet workflow."
    worker_state = New-Section -Status "REVIEW" -SourcePaths @($workerRegistryPath, $workerProfilesPath, $workerInboxPath) -SourceType "canonical_worker_evidence" -Summary "Worker registry, profiles, and inbox inspected without heartbeat writes." -Items $workerItems -BlockedActions @("worker_launch", "heartbeat_write", "worker_state_change") -NextSafeAction "Display worker state only; launch or mutate workers only through a separately approved worker workflow."
    lock_state = New-Section -Status "REVIEW" -SourcePaths @($lockRegistryPath) -SourceType "canonical_lock_evidence" -Summary "Lock registry evidence inspected without lock release." -Items @($lockRegistry) -BlockedActions @("lock_claim", "lock_release", "force_unlock") -NextSafeAction "Display lock state only; claim or release locks only through a separately approved lock workflow."
    validator_state = New-Section -Status "REVIEW" -SourcePaths @($validatorConfigPath, $ValidatorRecommendationPath, $ValidatorRunReportPath) -SourceType "validator_evidence" -Summary "Validator config and report evidence inspected without running mutation paths." -Items $validatorItems -BlockedActions @("apply_repair", "approval_grant") -NextSafeAction "Display validator evidence only; validator PASS does not approve APPLY or protected actions."
    approval_state = New-Section -Status "REVIEW" -SourcePaths @($approvalInboxPath, $approvalQueuePath) -SourceType "canonical_approval_evidence" -Summary "Approval evidence inspected without creating or resolving approvals." -Items $approvalItems -BlockedActions @("approval_create", "approval_resolve") -NextSafeAction "Display approval state only; Human Owner approval remains required before protected actions."
    commit_package_state = New-Section -Status $(if ($candidateFiles.Count -gt 0) { "REVIEW" } else { "READY" }) -SourcePaths @($commitPackageRecommendationHelperPath) -SourceType "commit_package_preview" -Summary "Level 5 commit-package preview evidence inspected without staging, committing, pushing, PR, or merge actions." -Items $commitPackageItems -BlockedActions @("stage_files", "commit_changes", "push_changes", "create_pr", "merge_pr") -NextSafeAction "Display exact-file preview only; do not stage, commit, push, create PRs, or merge from a frontend."
    escalation_state = New-Section -Status $(if ($staleConditions.Count -gt 0) { "REVIEW" } else { "READY" }) -SourcePaths @() -SourceType "generated_projection" -Summary "Escalation persistence is not enabled; review conditions are included in stale_conditions." -Items @($staleConditions) -BlockedActions @("escalation_append", "escalation_resolve") -NextSafeAction "Display escalation conditions only; do not persist or resolve escalations from this bundle."
    git_state = New-Section -Status $(if ($unexpectedDirtyFiles.Count -gt 0) { "BLOCKED" } elseif ($changedLines.Count -gt 0) { "REVIEW" } else { "READY" }) -SourcePaths @("git status --short --branch") -SourceType "git_status_projection" -Summary "Git status inspected read-only." -Items @([pscustomobject]@{ branch = [string]$branchLine; changed_lines = $changedLines; candidate_files = $candidateFiles; approved_candidate_files = $approvedCandidateFiles; unexpected_dirty_files = $unexpectedDirtyFiles }) -BlockedActions @("stage_files", "commit_changes", "push_changes") -NextSafeAction "Display git status only; protected git actions require separate approval and exact-file scope."
    supervisor_state = New-Section -Status "READY" -SourcePaths @($supervisorSchemaPath, $supervisorRulesPath) -SourceType "supervisor_schema_evidence" -Summary "Supervisor schema and rules inspected as read-only authority evidence." -Items @($supervisorRules) -BlockedActions @("start_loop", "start_daemon", "launch_worker") -NextSafeAction "Display supervisor readiness only; do not schedule, launch, or daemonize from this bundle."
    next_safe_actions = @(
        [pscustomobject]@{
            rank = 1
            action = "Review runtime bundle output before approving any routing or gate enforcement."
            requires_human_approval = $false
            reason = "This bundle is evidence only."
        },
        [pscustomobject]@{
            rank = 2
            action = "Approve a separate APPLY packet before any runtime state persistence or router enforcement."
            requires_human_approval = $true
            reason = "Runtime writes and routing gates remain outside this DRY_RUN helper."
        }
    )
    stale_conditions = $staleConditions
    confidence_state = [pscustomobject]@{
        overall_confidence = $overallConfidence
        confidence_score = $confidenceScore
        confidence_reasons = $confidenceReasons
    }
    validator_confidence = if ($validatorConfidence) { $validatorConfidence } else {
        [pscustomobject]@{
            overall_result = "UNKNOWN"
            confidence_score = 0
            confidence_band = "BLOCKED"
            safe_auto_allowed_eligible = $false
        }
    }
    auto_git_eligibility = [pscustomobject]@{
        safe_auto_allowed = [bool]$safeAutoAllowed
        minimum_confidence_score = 90
        eligible_actions = if ($safeAutoAllowed) { @("commit") } else { @() }
        blocked_actions = @("push", "merge", "direct_push_to_main", "protected_path_change", "validator_bypass")
        stop_conditions = $autoGitStopConditions
    }
    level5_commit_package_preview = [pscustomobject]@{
        available = [bool]($null -ne $commitPackageRecommendation)
        status = if ($commitPackageRecommendation -and $commitPackageRecommendation.orchestration_result_contract.status) { [string]$commitPackageRecommendation.orchestration_result_contract.status } elseif ($candidateFiles.Count -gt 0) { "REVIEW" } else { "NOT_NEEDED" }
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1 -OutputJson"
        exact_changed_files = @($commitPackageExactChangedFiles)
        recommended_files = @($commitPackageRecommendedFiles)
        suggested_validators = @($level5SuggestedValidators)
        risk_flags = @($commitPackageRiskFlags)
        stop_before_staging = "STOP: preview only. Do not run git add, git commit, git push, PR, or merge without separate explicit approval."
    }
    blocking_signals = @($blockingSignals | Select-Object -Unique)
    human_required_signals = @($humanRequiredSignals | Select-Object -Unique)
    source_freshness = $sourceFreshness
    bundle_integrity = [pscustomobject]@{
        status = $bundleIntegrityStatus
        parse_errors = @($parseErrors)
        missing_sources = @($missingSources)
    }
    required_evidence_present = [pscustomobject]@{
        validator_config = [bool]($null -ne $validatorConfig)
        validator_confidence = [bool]($null -ne $validatorConfidence)
        validator_recommendation = [bool]($null -ne $validatorRecommendation -and -not [string]::IsNullOrWhiteSpace($ValidatorRecommendationPath))
        validator_run_report = [bool]($null -ne $validatorRunReport -and -not [string]::IsNullOrWhiteSpace($ValidatorRunReportPath))
        git_state = [bool]($gitLines.Count -gt 0)
        lock_registry = [bool]($null -ne $lockRegistry)
        approval_evidence = [bool]($null -ne $approvalInbox -or $null -ne $approvalQueue)
        packet_evidence = [bool](($activePackets.Count + $blockedPackets.Count + $completePackets.Count) -gt 0)
    }
    validator_evidence_paths = [pscustomobject]@{
        recommendation = ConvertTo-RelativePath -Path $ValidatorRecommendationPath
        run_report = ConvertTo-RelativePath -Path $ValidatorRunReportPath
    }
}

if ($QuietJson -or $OutputJson) {
    $bundle | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "[RUNTIME HEALTH]"
Write-Host "AI_OS Runtime State Bundle"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($bundle.schema)"
Write-Host "Confidence: $($bundle.confidence_state.overall_confidence) $($bundle.confidence_state.confidence_score)"
Write-Host "Auto-git eligible: $($bundle.auto_git_eligibility.safe_auto_allowed)"
Write-Host "Git: $branchLine"
Write-Host "Packets: $($packetItems.Count)"
Write-Host "Workers sources: $($workerItems.Count)"
Write-Host "Approval sources: $($approvalItems.Count)"
Write-Host "Commit package preview: $($bundle.level5_commit_package_preview.status)"
Write-Host "Stale/review conditions: $($staleConditions.Count)"
Write-Host ""
Write-Host "[VALIDATOR RESULT]"
Write-Host "Validator confidence: $($bundle.validator_confidence.overall_result) $($bundle.validator_confidence.confidence_score)"
Write-Host "Validator sources: $($validatorItems.Count)"
Write-Host "Bundle integrity: $($bundle.bundle_integrity.status)"
Write-Host ""
Write-Host "[CREW RECOMMENDATION]"
Write-Host "Next safe actions:"
foreach ($action in $bundle.next_safe_actions) {
    Write-Host ("{0}. {1}" -f $action.rank, $action.action)
}
Write-Host ""
Write-Host "[VALIDATOR RESULT]"
Write-Host "Runtime mutation skipped: Runtime State Bundle DRY_RUN is read-only."
Write-Host "Files changed by helper: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
