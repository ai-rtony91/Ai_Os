[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$ExpectedBranch = "main",
    [switch]$OutputJson,
    [ValidateSet("LEVEL_0_MANUAL", "LEVEL_1_ASSISTED", "LEVEL_2_SEMI_AUTONOMOUS", "LEVEL_3_SUPERVISED_AUTONOMY", "LEVEL_4_CONDITIONAL_FULL_AUTONOMY", "LEVEL_5_FULL_AUTONOMY_REQUESTED")]
    [string]$RequestedAutonomyLevel = "LEVEL_4_CONDITIONAL_FULL_AUTONOMY",
    [ValidateSet("12H_SUPERVISED", "24H_SUPERVISED", "WEEKEND", "VACATION", "OVERNIGHT", "EMERGENCY_REVIEW", "FULL_AUTONOMY_SUPERVISED")]
    [string]$OperatingProfile = "12H_SUPERVISED",
    [string]$ActivationGateJson = "",
    [string]$HumanOwnerApprovalEvidence = "",
    [string]$IdentitySpineStatus = "PASS",
    [string]$ValidatorChainStatus = "PASS",
    [string]$ApprovalSosStatus = "CLEAR",
    [string]$GovernedSoakStatus = "PASS",
    [string]$NowUtc = "",
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

function Test-FullAutonomyWorkerPostureBridgeDirtyState {
    param([object]$State)
    $allowedExact = @(
        "automation/orchestration/self_development/aios_full_autonomy_activation_gate.py",
        "automation/orchestration/self_development/Test-AiOsFullAutonomyActivationGate.DRY_RUN.ps1",
        "schemas/aios/orchestration/AIOS_FULL_AUTONOMY_ACTIVATION_GATE_RESULT.v1.schema.json",
        "tests/orchestration/test_aios_full_autonomy_activation_gate.py",
        "tests/orchestration/test_aios_full_autonomy_activation_gate_runner.py",
        "automation/orchestration/self_development/aios_full_autonomy_worker_posture_bridge.py",
        "automation/orchestration/self_development/Get-AiOsFullAutonomyWorkerPostureBridge.DRY_RUN.ps1",
        "schemas/aios/orchestration/AIOS_FULL_AUTONOMY_WORKER_POSTURE_BRIDGE_RESULT.v1.schema.json",
        "tests/orchestration/test_aios_full_autonomy_worker_posture_bridge.py",
        "tests/orchestration/test_aios_full_autonomy_worker_posture_bridge_runner.py",
        "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1",
        "aios.ps1",
        "schemas/aios/orchestration/ORCHESTRATION_SCHEMA_INDEX.json"
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

function ConvertFrom-JsonEvidenceParameter {
    param([string]$Name, [string]$JsonText)
    if ([string]::IsNullOrWhiteSpace($JsonText)) {
        return [ordered]@{
            supplied = $false
            data = $null
        }
    }
    $trimmed = $JsonText.Trim()
    if (-not $trimmed.StartsWith("{")) {
        throw "$Name must be a JSON object string, not a file path or command."
    }
    try {
        $data = $trimmed | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        throw "$Name must be valid JSON evidence."
    }
    if ($null -eq $data -or $data -is [System.Array]) {
        throw "$Name must decode to one JSON object."
    }
    return [ordered]@{
        supplied = $true
        data = $data
    }
}

function Invoke-PythonJsonLogic {
    param([string]$LogicPath, [object]$Payload, [int]$TimeoutSecondsValue, [string]$Label)
    if (-not (Test-Path -LiteralPath $LogicPath -PathType Leaf)) {
        throw "Python $Label logic module missing: $LogicPath"
    }
    $payloadJson = $Payload | ConvertTo-Json -Depth 90
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = "python"
    $psi.Arguments = ('"{0}"' -f ($LogicPath -replace '"', '\"'))
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.WorkingDirectory = $resolvedRepoRoot
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    [void]$process.Start()
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.StandardInput.Write($payloadJson)
    $process.StandardInput.Close()
    if (-not $process.WaitForExit($TimeoutSecondsValue * 1000)) {
        $process.Kill()
        throw "Python $Label logic timed out."
    }
    $rawText = $stdoutTask.Result.Trim()
    $errorText = $stderrTask.Result.Trim()
    if ([string]::IsNullOrWhiteSpace($rawText)) {
        throw "Python $Label logic returned no JSON. $errorText"
    }
    return $rawText | ConvertFrom-Json -ErrorAction Stop
}

function Write-ConsoleReport {
    param([object]$Result)
    Write-Host "AIOS Full Autonomy Worker Posture Bridge"
    Write-Host "Mode: $($Result.mode)"
    Write-Host "Schema: $($Result.schema)"
    Write-Host ""
    Write-Host "CURRENT STATE"
    Write-Host "branch: $($Result.repo_state.branch)"
    Write-Host "dirty: $($Result.repo_state.dirty)"
    Write-Host "expected_branch: $($Result.repo_state.expected_branch)"
    Write-Host "branch_matches_expected: $($Result.repo_state.branch_matches_expected)"
    Write-Host ""
    Write-Host "ACTIVATION SUMMARY"
    Write-Host "requested_level: $($Result.activation_summary.requested_autonomy_level)"
    Write-Host "activation_status: $($Result.activation_summary.activation_status)"
    Write-Host "operating_profile: $($Result.activation_summary.operating_profile)"
    Write-Host ""
    Write-Host "WORKER POSTURE"
    Write-Host "worker_posture: $($Result.worker_posture)"
    Write-Host "worker_shift_mode: $($Result.worker_shift_mode)"
    Write-Host "recommended_worker_count: $($Result.recommended_worker_count)"
    Write-Host "max_parallel_workers: $($Result.max_parallel_workers)"
    Write-Host "worker_launch_allowed: $($Result.worker_launch_allowed)"
    Write-Host "worker_launch_reason: $($Result.worker_launch_reason)"
    Write-Host ""
    Write-Host "LANES"
    Write-Host "allowed_worker_lanes: $(@($Result.allowed_worker_lanes) -join ', ')"
    Write-Host "blocked_worker_lanes: $(@($Result.blocked_worker_lanes) -join ', ')"
    Write-Host ""
    Write-Host "HUMAN WAKE POLICY"
    Write-Host $Result.human_wake_policy
    Write-Host ""
    Write-Host "SAFETY"
    Write-Host "status: $($Result.safety.status)"
    Write-Host "starts_runtime: $($Result.safety.starts_runtime)"
    Write-Host "launches_workers: $($Result.safety.launches_workers)"
    Write-Host "enables_scheduler: $($Result.safety.enables_scheduler)"
    Write-Host "starts_daemon: $($Result.safety.starts_daemon)"
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
$bridgeLogicPath = Join-Path $PSScriptRoot "aios_full_autonomy_worker_posture_bridge.py"
$activationLogicPath = Join-Path $PSScriptRoot "aios_full_autonomy_activation_gate.py"
$generatedUtc = if ([string]::IsNullOrWhiteSpace($NowUtc)) { (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") } else { $NowUtc }
$beforeState = Get-NoWriteState -Root $resolvedRepoRoot
$dirtyAllowedForValidation = Test-FullAutonomyWorkerPostureBridgeDirtyState -State $beforeState
$afterState = Get-NoWriteState -Root $resolvedRepoRoot
$noWriteProof = Compare-NoWriteState -Before $beforeState -After $afterState

$repoState = [ordered]@{
    repo_root = $resolvedRepoRoot
    branch = $beforeState.branch
    expected_branch = $ExpectedBranch
    branch_matches_expected = ([string]$beforeState.branch -eq [string]$ExpectedBranch)
    dirty = [bool]$beforeState.dirty
    dirty_allowed_for_full_autonomy_worker_posture_bridge_validation = [bool]$dirtyAllowedForValidation
    fail_on_dirty_worktree = [bool]$FailOnDirtyWorktree
    status_lines = @($beforeState.status_lines)
    diff_name_only = @($beforeState.diff_name_only)
    untracked_files = @($beforeState.untracked_files)
}

$activationEvidence = ConvertFrom-JsonEvidenceParameter -Name "ActivationGateJson" -JsonText $ActivationGateJson
if ([bool]$activationEvidence.supplied) {
    $activationGateResult = $activationEvidence.data
}
else {
    $activationPayload = [ordered]@{
        generated_utc = $generatedUtc
        repo_state = [ordered]@{
            repo_root = $resolvedRepoRoot
            branch = $beforeState.branch
            expected_branch = $ExpectedBranch
            branch_matches_expected = ([string]$beforeState.branch -eq [string]$ExpectedBranch)
            dirty = [bool]$beforeState.dirty
            dirty_allowed_for_full_autonomy_activation_gate_validation = [bool]$dirtyAllowedForValidation
            fail_on_dirty_worktree = [bool]$FailOnDirtyWorktree
            status_lines = @($beforeState.status_lines)
            diff_name_only = @($beforeState.diff_name_only)
            untracked_files = @($beforeState.untracked_files)
        }
        requested_autonomy_level = $RequestedAutonomyLevel
        operating_profile = $OperatingProfile
        human_owner_approval_evidence = $HumanOwnerApprovalEvidence
        identity_spine_status = $IdentitySpineStatus
        validator_chain_status = $ValidatorChainStatus
        approval_sos_status = $ApprovalSosStatus
        governed_soak_status = $GovernedSoakStatus
        no_write_proof = $noWriteProof
    }
    $activationGateResult = Invoke-PythonJsonLogic -LogicPath $activationLogicPath -Payload $activationPayload -TimeoutSecondsValue $TimeoutSeconds -Label "full-autonomy activation gate"
}

$payload = [ordered]@{
    generated_utc = $generatedUtc
    repo_state = $repoState
    operating_profile = $OperatingProfile
    activation_gate_result = $activationGateResult
    no_write_proof = $noWriteProof
}

$result = Invoke-PythonJsonLogic -LogicPath $bridgeLogicPath -Payload $payload -TimeoutSecondsValue $TimeoutSeconds -Label "full-autonomy worker posture bridge"

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
