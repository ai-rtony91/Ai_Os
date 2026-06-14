[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$ExpectedBranch = "main",
    [switch]$OutputJson,
    [ValidateSet("LEVEL_0_MANUAL", "LEVEL_1_ASSISTED", "LEVEL_2_SEMI_AUTONOMOUS", "LEVEL_3_SUPERVISED_AUTONOMY", "LEVEL_4_CONDITIONAL_FULL_AUTONOMY", "LEVEL_5_FULL_AUTONOMY_REQUESTED")]
    [string]$RequestedAutonomyLevel = "LEVEL_3_SUPERVISED_AUTONOMY",
    [ValidateSet("12H_SUPERVISED", "24H_SUPERVISED", "WEEKEND", "VACATION", "OVERNIGHT", "EMERGENCY_REVIEW", "FULL_AUTONOMY_SUPERVISED")]
    [string]$OperatingProfile = "12H_SUPERVISED",
    [string]$NowUtc = "",
    [bool]$HumanAvailable = $true,
    [bool]$WeekendMode = $false,
    [bool]$VacationMode = $false,
    [bool]$SleepWindowActive = $false,
    [ValidateRange(0, 168)]
    [int]$MaxAutonomyHours = 12,
    [string]$RecentValidatorStatus = "UNKNOWN",
    [string]$RecentSosStatus = "CLEAR",
    [bool]$FailOnDirtyWorktree = $true,
    [ValidateRange(1, 300)]
    [int]$TimeoutSeconds = 30
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    param([string]$PathHint)
    if (-not [string]::IsNullOrWhiteSpace($PathHint)) {
        return (Resolve-Path -LiteralPath $PathHint).Path
    }
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to resolve repository root."
    }
    return $root.Trim()
}

function ConvertTo-RelativePath {
    param([string]$Root, [string]$Path)
    $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd("\", "/")
    $pathFull = [System.IO.Path]::GetFullPath($Path)
    if ($pathFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $pathFull.Substring($rootFull.Length).TrimStart("\", "/").Replace("\", "/")
    }
    return $pathFull.Replace("\", "/")
}

function New-MetadataHash {
    param([object[]]$Items)
    $text = ($Items | Sort-Object -Property relative_path | ConvertTo-Json -Depth 6 -Compress)
    if ([string]::IsNullOrWhiteSpace($text)) {
        $text = "[]"
    }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
}

function Get-PathFingerprint {
    param([string]$Root, [string]$RelativePath)
    $target = Join-Path $Root $RelativePath
    if (-not (Test-Path -LiteralPath $target)) {
        return [ordered]@{
            path = $RelativePath.Replace("\", "/")
            exists = $false
            file_count = 0
            total_bytes = 0
            metadata_hash = New-MetadataHash -Items @()
        }
    }
    $files = @(Get-ChildItem -LiteralPath $target -File -Recurse -Force -ErrorAction SilentlyContinue)
    $items = @($files | ForEach-Object {
        [ordered]@{
            relative_path = ConvertTo-RelativePath -Root $Root -Path $_.FullName
            length = [int64]$_.Length
            last_write_utc_ticks = [int64]$_.LastWriteTimeUtc.Ticks
        }
    })
    $totalBytes = 0
    foreach ($file in $files) {
        $totalBytes += [int64]$file.Length
    }
    return [ordered]@{
        path = $RelativePath.Replace("\", "/")
        exists = $true
        file_count = $files.Count
        total_bytes = $totalBytes
        metadata_hash = New-MetadataHash -Items $items
    }
}

function Get-NoWriteState {
    param([string]$Root)
    Push-Location -LiteralPath $Root
    try {
        $oldErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        $statusLines = @(& git status --short --branch --untracked-files=all 2>$null)
        $statusExitCode = $LASTEXITCODE
        $diffNames = @(& git diff --name-only 2>$null)
        $diffExitCode = $LASTEXITCODE
        $branch = (& git branch --show-current 2>$null).Trim()
        $branchExitCode = $LASTEXITCODE
        $ErrorActionPreference = $oldErrorActionPreference
        if ($statusExitCode -ne 0) { throw "git status failed." }
        if ($diffExitCode -ne 0) { throw "git diff --name-only failed." }
        if ($branchExitCode -ne 0) { throw "git branch --show-current failed." }
    }
    finally {
        if ($null -ne $oldErrorActionPreference) {
            $ErrorActionPreference = $oldErrorActionPreference
        }
        Pop-Location
    }

    $untracked = @($statusLines | Where-Object { $_ -match "^\?\? " } | ForEach-Object { $_.Substring(3).Trim().Replace("\", "/") })
    $changed = @($statusLines | Where-Object { $_ -notlike "##*" })
    $forbiddenRoots = @(
        "Reports",
        "telemetry",
        "automation/orchestration/work_packets",
        "automation/orchestration/packet_generator",
        "automation/orchestration/queue",
        "automation/orchestration/command_queue",
        "automation/orchestration/locks",
        "automation/orchestration/approval_inbox",
        "automation/orchestration/runtime",
        "automation/orchestration/workers/inbox",
        "automation/orchestration/relay_bus",
        "control/relay_bus/messages",
        "control/review_bridge/codex_reports"
    )
    $fingerprints = [ordered]@{}
    foreach ($relative in $forbiddenRoots) {
        $fingerprints[$relative] = Get-PathFingerprint -Root $Root -RelativePath $relative
    }

    return [ordered]@{
        branch = $branch
        status_lines = $statusLines
        diff_name_only = $diffNames
        untracked_files = $untracked
        changed_entries = $changed
        dirty = ($changed.Count -gt 0)
        forbidden_fingerprints = $fingerprints
    }
}

function Get-ChangedPathFromStatusLine {
    param([string]$Line)
    if ([string]::IsNullOrWhiteSpace($Line) -or $Line -like "##*") {
        return $null
    }
    if ($Line.Length -lt 4) {
        return $null
    }
    $path = $Line.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }
    return $path.Replace("\", "/")
}

function Test-FullAutonomySupervisionDirtyState {
    param([object]$State)
    $allowedExact = @(
        "automation/orchestration/self_development/Get-AiOsFullAutonomySupervisionState.DRY_RUN.ps1",
        "automation/orchestration/self_development/aios_full_autonomy_supervision_state.py",
        "schemas/aios/orchestration/AIOS_FULL_AUTONOMY_SUPERVISION_STATE_RESULT.v1.schema.json",
        "schemas/aios/orchestration/ORCHESTRATION_SCHEMA_INDEX.json",
        "tests/orchestration/test_aios_full_autonomy_supervision_state.py",
        "tests/orchestration/test_aios_full_autonomy_supervision_state_runner.py"
    )
    $changedPaths = @($State.changed_entries | ForEach-Object { Get-ChangedPathFromStatusLine -Line ([string]$_) } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($changedPaths.Count -eq 0) {
        return $false
    }
    foreach ($path in $changedPaths) {
        if (-not ($allowedExact -contains $path)) {
            return $false
        }
    }
    return $true
}

function ConvertTo-StableJson {
    param([object]$Value)
    return ($Value | ConvertTo-Json -Depth 30 -Compress)
}

function Compare-NoWriteState {
    param([object]$Before, [object]$After)
    $gitChanged = (ConvertTo-StableJson -Value $Before.status_lines) -ne (ConvertTo-StableJson -Value $After.status_lines) -or
        (ConvertTo-StableJson -Value $Before.diff_name_only) -ne (ConvertTo-StableJson -Value $After.diff_name_only)
    $forbiddenChanged = (ConvertTo-StableJson -Value $Before.forbidden_fingerprints) -ne (ConvertTo-StableJson -Value $After.forbidden_fingerprints)
    return [ordered]@{
        changed = [bool]($gitChanged -or $forbiddenChanged)
        git_state_changed = [bool]$gitChanged
        forbidden_surface_changed = [bool]$forbiddenChanged
        before_dirty = [bool]$Before.dirty
        after_dirty = [bool]$After.dirty
        before_changed_entries = @($Before.changed_entries)
        after_changed_entries = @($After.changed_entries)
        before_untracked_files = @($Before.untracked_files)
        after_untracked_files = @($After.untracked_files)
    }
}

function Read-AuthorityContext {
    param([string]$Root)
    $files = @(
        "AGENTS.md",
        "README.md",
        "RISK_POLICY.md",
        "docs/AI_OS/autonomy/AIOS_SELF_AUDIT_LOOP_CONTRACT_V1.md",
        "docs/governance/aios-identity-and-lane-governance.md",
        "docs/governance/AI_OS_REPO_MEMORY.md"
    )
    $items = @()
    foreach ($relative in $files) {
        $path = Join-Path $Root $relative
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $text = Get-Content -LiteralPath $path -Raw
            $items += [ordered]@{
                path = $relative
                exists = $true
                bytes = [System.Text.Encoding]::UTF8.GetByteCount($text)
            }
        }
        else {
            $items += [ordered]@{
                path = $relative
                exists = $false
                bytes = 0
            }
        }
    }
    return [ordered]@{
        files = $items
        all_required_loaded = [bool](-not @($items | Where-Object { -not $_.exists }))
    }
}

function Read-FilePresence {
    param([string]$Root)
    $files = @(
        "automation/orchestration/operator_control/Test-AiOsApprovalSosHardGate.DRY_RUN.ps1",
        "automation/orchestration/operator_control/aios_approval_sos_hard_gate.py",
        "automation/orchestration/self_development/Test-AiOsGovernedSelfDevelopmentSoak.DRY_RUN.ps1",
        "automation/orchestration/self_development/aios_governed_self_development_soak.py",
        "automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1",
        "schemas/aios/orchestration/WORKER_REGISTRY_SCHEMA.json",
        "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
        "automation/orchestration/locks/PATH_CONFLICT_POLICY_001.md",
        "automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
        "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1"
    )
    $presence = [ordered]@{}
    foreach ($relative in $files) {
        $path = Join-Path $Root $relative
        $presence[$relative] = [ordered]@{
            exists = [bool](Test-Path -LiteralPath $path -PathType Leaf)
        }
    }
    return $presence
}

function Invoke-PythonFullAutonomySupervisionLogic {
    param([string]$LogicPath, [object]$Payload, [int]$TimeoutSecondsValue)
    if (-not (Test-Path -LiteralPath $LogicPath -PathType Leaf)) {
        throw "Python full-autonomy supervision logic module missing: $LogicPath"
    }
    $payloadJson = $Payload | ConvertTo-Json -Depth 90
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = "python"
    $psi.Arguments = ('"{0}"' -f ($LogicPath -replace '"', '\"'))
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    [void]$process.Start()
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.StandardInput.Write($payloadJson)
    $process.StandardInput.Close()
    if (-not $process.WaitForExit($TimeoutSecondsValue * 1000)) {
        $process.Kill()
        throw "Python full-autonomy supervision logic timed out."
    }
    $rawText = $stdoutTask.Result.Trim()
    $errorText = $stderrTask.Result.Trim()
    if ([string]::IsNullOrWhiteSpace($rawText)) {
        throw "Python full-autonomy supervision logic returned no JSON. $errorText"
    }
    return $rawText | ConvertFrom-Json -ErrorAction Stop
}

function Write-ConsoleReport {
    param([object]$Result)
    Write-Host "AIOS Full Autonomy Supervision State"
    Write-Host "Mode: $($Result.mode)"
    Write-Host "Schema: $($Result.schema)"
    Write-Host ""
    Write-Host "CURRENT STATE"
    Write-Host "branch: $($Result.repo_state.branch)"
    Write-Host "dirty: $($Result.repo_state.dirty)"
    Write-Host "expected_branch: $($Result.repo_state.expected_branch)"
    Write-Host "branch_matches_expected: $($Result.repo_state.branch_matches_expected)"
    Write-Host ""
    Write-Host "AUTONOMY LEVEL"
    Write-Host "requested: $($Result.requested_autonomy_level)"
    Write-Host "resolved: $($Result.resolved_autonomy_level)"
    Write-Host "full_autonomy_state: $($Result.full_autonomy_state.status)"
    Write-Host ""
    Write-Host "OPERATING PROFILE"
    Write-Host "profile: $($Result.operating_profile)"
    Write-Host "recommended_next_action: $($Result.recommended_next_action)"
    Write-Host ""
    Write-Host "WORKER SUPERVISION"
    Write-Host "status: $($Result.worker_supervision.worker_supervision_status)"
    Write-Host "shift_mode: $($Result.worker_supervision.worker_shift_mode)"
    Write-Host "recommended_worker_count: $($Result.worker_supervision.recommended_worker_count)"
    Write-Host "max_parallel_workers: $($Result.worker_supervision.max_parallel_workers)"
    Write-Host "worker_launch_allowed: $($Result.worker_supervision.worker_launch_allowed)"
    Write-Host ""
    Write-Host "WAKE POLICY"
    Write-Host "wake_required: $($Result.human_wake_policy.wake_required)"
    Write-Host "wake_class: $($Result.human_wake_policy.wake_class)"
    Write-Host ""
    Write-Host "SAFETY"
    Write-Host "status: $($Result.safety.status)"
    Write-Host "protected_actions_blocked: $($Result.safety.protected_actions_blocked)"
    Write-Host "self_approval_allowed: $($Result.safety.self_approval_allowed)"
    Write-Host "starts_runtime: $($Result.safety.starts_runtime)"
    Write-Host "launches_workers: $($Result.safety.launches_workers)"
    Write-Host "broker_or_live_trading: $($Result.safety.broker_or_live_trading)"
    Write-Host ""
    Write-Host "NO-WRITE PROOF"
    Write-Host "changed: $($Result.no_write_proof.changed)"
    Write-Host "git_state_changed: $($Result.no_write_proof.git_state_changed)"
    Write-Host "forbidden_surface_changed: $($Result.no_write_proof.forbidden_surface_changed)"
    Write-Host ""
    Write-Host "STOP CONDITIONS"
    if (@($Result.stop_conditions).Count -eq 0) {
        Write-Host "- none"
    }
    else {
        foreach ($condition in @($Result.stop_conditions)) {
            Write-Host "- $condition"
        }
    }
    Write-Host ""
    Write-Host "NEXT SAFE ACTION"
    Write-Host $Result.next_safe_action
    Write-Host ""
    Write-Host "STATUS: $($Result.safety.status)"
}

$resolvedRepoRoot = Get-RepoRoot -PathHint $RepoRoot
$logicPath = Join-Path $PSScriptRoot "aios_full_autonomy_supervision_state.py"
$generatedUtc = if ([string]::IsNullOrWhiteSpace($NowUtc)) { (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") } else { $NowUtc }
$authorityContext = Read-AuthorityContext -Root $resolvedRepoRoot
$filePresence = Read-FilePresence -Root $resolvedRepoRoot
$beforeState = Get-NoWriteState -Root $resolvedRepoRoot
$dirtyAllowedForValidation = Test-FullAutonomySupervisionDirtyState -State $beforeState
$afterState = Get-NoWriteState -Root $resolvedRepoRoot
$noWriteProof = Compare-NoWriteState -Before $beforeState -After $afterState

$repoState = [ordered]@{
    repo_root = $resolvedRepoRoot
    branch = $beforeState.branch
    expected_branch = $ExpectedBranch
    branch_matches_expected = ([string]$beforeState.branch -eq [string]$ExpectedBranch)
    dirty = [bool]$beforeState.dirty
    dirty_allowed_for_full_autonomy_supervision_state_validation = [bool]$dirtyAllowedForValidation
    fail_on_dirty_worktree = [bool]$FailOnDirtyWorktree
    status_lines = @($beforeState.status_lines)
    diff_name_only = @($beforeState.diff_name_only)
    untracked_files = @($beforeState.untracked_files)
}

$payload = [ordered]@{
    generated_utc = $generatedUtc
    repo_state = $repoState
    authority_context = $authorityContext
    file_presence = $filePresence
    requested_autonomy_level = $RequestedAutonomyLevel
    operating_profile = $OperatingProfile
    human_available = [bool]$HumanAvailable
    weekend_mode = [bool]$WeekendMode
    vacation_mode = [bool]$VacationMode
    sleep_window_active = [bool]$SleepWindowActive
    max_autonomy_hours = [int]$MaxAutonomyHours
    recent_validator_status = $RecentValidatorStatus
    recent_sos_status = $RecentSosStatus
    no_write_proof = $noWriteProof
}

$result = Invoke-PythonFullAutonomySupervisionLogic -LogicPath $logicPath -Payload $payload -TimeoutSecondsValue $TimeoutSeconds

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 90
}
else {
    Write-ConsoleReport -Result $result
}

if ([string]$result.safety.status -in @("PASS", "REVIEW_REQUIRED")) {
    exit 0
}
exit 1
