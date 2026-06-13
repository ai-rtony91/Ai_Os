[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$ExpectedBranch = "main",
    [switch]$OutputJson,
    [string]$DayNightReadinessJson = "",
    [string]$CampaignNoReadyJson = "",
    [string]$CampaignNextTaskJson = "",
    [string]$ActionRecommendationJson = "",
    [bool]$FailOnDirtyWorktree = $true,
    [ValidateRange(1, 300)]
    [int]$TimeoutSeconds = 120
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

function Get-EnvFingerprint {
    param([string]$Root)
    $files = @(Get-ChildItem -LiteralPath $Root -File -Force -Recurse -Filter ".env*" -ErrorAction SilentlyContinue)
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
        path = ".env*"
        exists = ($files.Count -gt 0)
        file_count = $files.Count
        total_bytes = [int64]$totalBytes
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
        "control/relay_bus/messages",
        "control/review_bridge/codex_reports",
        "automation/orchestration/queue",
        "automation/orchestration/command_queue",
        "automation/orchestration/locks",
        "automation/orchestration/approval_inbox",
        "automation/orchestration/runtime",
        "automation/orchestration/workers/inbox",
        "control"
    )
    $fingerprints = [ordered]@{}
    foreach ($relative in $forbiddenRoots) {
        $fingerprints[$relative] = Get-PathFingerprint -Root $Root -RelativePath $relative
    }
    $fingerprints[".env*"] = Get-EnvFingerprint -Root $Root

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

function Test-GovernedLoopValidationDirtyState {
    param([object]$State)
    $allowedExact = @(
        "automation/orchestration/self_development/Invoke-AiOsGovernedSelfDevelopmentLoop.DRY_RUN.ps1",
        "automation/orchestration/self_development/aios_governed_self_development_loop.py",
        "schemas/aios/orchestration/AIOS_GOVERNED_SELF_DEVELOPMENT_LOOP_RESULT.v1.schema.json",
        "schemas/aios/orchestration/ORCHESTRATION_SCHEMA_INDEX.json",
        "tests/orchestration/test_aios_governed_self_development_loop.py",
        "tests/orchestration/test_aios_governed_self_development_loop_runner.py",
        "tests/orchestration/test_aios_self_audit_runner.py",
        "tests/orchestration/test_aios_self_development_packet_router_runner.py",
        "tests/orchestration/test_aios_validator_evidence_router_runner.py",
        "tests/orchestration/test_aios_day_night_readiness_runner.py",
        "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1",
        "automation/orchestration/self_audit/Invoke-AiOsSelfAuditLoop.DRY_RUN.ps1",
        "automation/orchestration/validators/Get-AiOsValidatorEvidenceRouter.DRY_RUN.ps1",
        "automation/orchestration/supervisor/Get-AiOsDayNightReadiness.DRY_RUN.ps1"
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

function Invoke-JsonSurface {
    param(
        [string]$Root,
        [string]$RelativeScript,
        [bool]$SupportsRepoArgs,
        [string]$ExpectedBranchValue,
        [int]$TimeoutSecondsValue
    )
    $scriptPath = Join-Path $Root $RelativeScript
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        return [ordered]@{
            available = $false
            ok = $false
            error = "surface_missing"
            data = $null
        }
    }
    $safePath = $scriptPath -replace '"', '\"'
    $arguments = '-NoProfile -ExecutionPolicy Bypass -File "{0}" -OutputJson' -f $safePath
    if ($SupportsRepoArgs) {
        $safeRoot = $Root -replace '"', '\"'
        $safeExpectedBranch = $ExpectedBranchValue -replace '"', '\"'
        $arguments = '-NoProfile -ExecutionPolicy Bypass -File "{0}" -RepoRoot "{1}" -ExpectedBranch "{2}" -OutputJson -TimeoutSeconds {3}' -f $safePath, $safeRoot, $safeExpectedBranch, $TimeoutSecondsValue
    }

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = "powershell"
    $psi.Arguments = $arguments
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    [void]$process.Start()
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit($TimeoutSecondsValue * 1000)) {
        $process.Kill()
        return [ordered]@{
            available = $true
            ok = $false
            error = "surface_timeout"
            data = $null
        }
    }
    $rawText = $stdoutTask.Result.Trim()
    if ($process.ExitCode -ne 0) {
        $null = $stderrTask.Result
        return [ordered]@{
            available = $true
            ok = $false
            error = "surface_exit_$($process.ExitCode)"
            data = $null
        }
    }
    try {
        return [ordered]@{
            available = $true
            ok = $true
            error = ""
            data = ($rawText | ConvertFrom-Json -ErrorAction Stop)
        }
    }
    catch {
        $null = $stderrTask.Result
        return [ordered]@{
            available = $true
            ok = $false
            error = "surface_json_parse_failed"
            data = $null
        }
    }
}

function Invoke-PythonGovernedLoopLogic {
    param([string]$LogicPath, [object]$Payload, [int]$TimeoutSecondsValue)
    if (-not (Test-Path -LiteralPath $LogicPath -PathType Leaf)) {
        throw "Python governed self-development loop logic module missing: $LogicPath"
    }
    $payloadJson = $Payload | ConvertTo-Json -Depth 80
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
        throw "Python governed self-development loop logic timed out."
    }
    $rawText = $stdoutTask.Result.Trim()
    $errorText = $stderrTask.Result.Trim()
    if ([string]::IsNullOrWhiteSpace($rawText)) {
        throw "Python governed self-development loop logic returned no JSON. $errorText"
    }
    return $rawText | ConvertFrom-Json -ErrorAction Stop
}

function Write-ConsoleReport {
    param([object]$Result)
    Write-Host "AIOS Governed Self-Development Loop"
    Write-Host "Mode: $($Result.mode)"
    Write-Host "Schema: $($Result.schema)"
    Write-Host ""
    Write-Host "CURRENT STATE"
    Write-Host "branch: $($Result.repo_state.branch)"
    Write-Host "dirty: $($Result.repo_state.dirty)"
    Write-Host "expected_branch: $($Result.repo_state.expected_branch)"
    Write-Host "branch_matches_expected: $($Result.repo_state.branch_matches_expected)"
    Write-Host ""
    Write-Host "GOVERNED SELF-DEVELOPMENT LOOP"
    Write-Host "status: $($Result.safety.status)"
    Write-Host "approval_required: $($Result.approval_required.human_owner_required)"
    Write-Host ""
    Write-Host "AUTONOMY CHAIN STATE"
    Write-Host "self_audit_status: $($Result.autonomy_chain_state.self_audit_status)"
    Write-Host "packet_router_status: $($Result.autonomy_chain_state.packet_router_status)"
    Write-Host "validator_evidence_router_status: $($Result.autonomy_chain_state.validator_evidence_router_status)"
    Write-Host "day_night_readiness_status: $($Result.autonomy_chain_state.day_night_readiness_status)"
    Write-Host "day_night_classification: $($Result.autonomy_chain_state.day_night_classification)"
    Write-Host ""
    Write-Host "SAFE SURFACES USED"
    foreach ($surface in @($Result.safe_surfaces_used)) {
        Write-Host "- $($surface.path): ok=$($surface.ok)"
    }
    Write-Host ""
    Write-Host "RECOMMENDED NEXT PACKET"
    if ($null -ne $Result.recommended_next_packet) {
        Write-Host "$($Result.recommended_next_packet.packet_id)"
    }
    else {
        Write-Host "none"
    }
    Write-Host ""
    Write-Host "VALIDATOR CHAIN"
    foreach ($validator in @($Result.validator_chain)) {
        Write-Host "- $($validator.name): $($validator.status)"
    }
    Write-Host ""
    Write-Host "READINESS"
    Write-Host "classification: $($Result.readiness.classification)"
    Write-Host "recommendation_allowed: $($Result.readiness.recommendation_allowed)"
    Write-Host "execution_allowed: $($Result.readiness.execution_allowed)"
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
$logicPath = Join-Path $PSScriptRoot "aios_governed_self_development_loop.py"
$generatedUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$authorityContext = Read-AuthorityContext -Root $resolvedRepoRoot
$beforeState = Get-NoWriteState -Root $resolvedRepoRoot
$dirtyAllowedForValidation = Test-GovernedLoopValidationDirtyState -State $beforeState
$skipSurfaceCalls = (-not $authorityContext.all_required_loaded) -or ([bool]$beforeState.dirty -and $FailOnDirtyWorktree -and (-not $dirtyAllowedForValidation))
$jsonEvidence = [ordered]@{
    day_night_readiness_result = ConvertFrom-JsonEvidenceParameter -Name "DayNightReadinessJson" -JsonText $DayNightReadinessJson
    campaign_no_ready = ConvertFrom-JsonEvidenceParameter -Name "CampaignNoReadyJson" -JsonText $CampaignNoReadyJson
    campaign_next_task = ConvertFrom-JsonEvidenceParameter -Name "CampaignNextTaskJson" -JsonText $CampaignNextTaskJson
    action_recommendation = ConvertFrom-JsonEvidenceParameter -Name "ActionRecommendationJson" -JsonText $ActionRecommendationJson
}

$safeSurfaces = [ordered]@{
    self_audit_result = [ordered]@{ path = "automation/orchestration/self_audit/Invoke-AiOsSelfAuditLoop.DRY_RUN.ps1"; supports_repo_args = $true; direct = $false }
    packet_router_result = [ordered]@{ path = "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1"; supports_repo_args = $true; direct = $false }
    validator_evidence_router_result = [ordered]@{ path = "automation/orchestration/validators/Get-AiOsValidatorEvidenceRouter.DRY_RUN.ps1"; supports_repo_args = $true; direct = $false }
    day_night_readiness_result = [ordered]@{ path = "automation/orchestration/supervisor/Get-AiOsDayNightReadiness.DRY_RUN.ps1"; supports_repo_args = $true; direct = $true }
    campaign_no_ready = [ordered]@{ path = "automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1"; supports_repo_args = $false; direct = $true }
    campaign_next_task = [ordered]@{ path = "automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1"; supports_repo_args = $false; direct = $true }
    action_recommendation = [ordered]@{ path = "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1"; supports_repo_args = $false; direct = $true }
}

$blockedSurfaces = @(
    "automation/orchestration/work_packets/*",
    "automation/orchestration/packet_generator/*",
    "automation/orchestration/approval_inbox/New-AiOsPacketApprovalRequest.DRY_RUN.ps1",
    "automation/orchestration/approval_inbox/Invoke-AiOsApprovalChain.DRY_RUN.ps1",
    "automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1",
    "automation/orchestration/approval_runner/Invoke-AiOsApprovedActionResume.ps1",
    "automation/orchestration/locks/Claim-AiOsFileLock.DRY_RUN.ps1",
    "automation/orchestration/locks/Release-AiOsFileLock.DRY_RUN.ps1",
    "automation/orchestration/relay_bus/New-AiOsRelayMessage.DRY_RUN.ps1",
    "automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1",
    "automation/orchestration/runtime/Start-AiOsRuntimeCycle.DRY_RUN.ps1",
    "automation/orchestration/workers/launcher/Open-AiOsWorkerWindow.DRY_RUN.ps1",
    "automation/orchestration/workers/daemon/Start-AiOsWorkerDaemon.DRY_RUN.ps1",
    "automation/orchestration/workers/loop/Start-AiOsWorkerLoop.DRY_RUN.ps1",
    "automation/orchestration/workers/cycle/Start-AiOsAutonomousWorkerCycle.DRY_RUN.ps1",
    "automation/orchestration/commit_packages/Invoke-AiOsExactCommitPackage.ps1",
    "Reports/*",
    "telemetry/*",
    ".env*",
    "secrets/*",
    "automation/trading/broker/*",
    "automation/trading/oanda/*",
    "automation/trading/webhooks/*",
    "automation/trading/live_orders/*"
)

$surfaceResults = [ordered]@{}
$surfaceDetails = @()
if (-not $skipSurfaceCalls) {
    foreach ($entry in $safeSurfaces.GetEnumerator()) {
        $surface = $entry.Value
        if (-not [bool]$surface.direct) {
            continue
        }
        $injected = $jsonEvidence[$entry.Key]
        if ($null -ne $injected -and [bool]$injected.supplied) {
            $surfaceResults[$entry.Key] = $injected.data
            $surfaceDetails += [ordered]@{
                name = $entry.Key
                path = $surface.path
                available = $true
                ok = $true
                error = ""
                source = "json_parameter"
            }
            continue
        }
        $surfaceResult = Invoke-JsonSurface -Root $resolvedRepoRoot -RelativeScript $surface.path -SupportsRepoArgs ([bool]$surface.supports_repo_args) -ExpectedBranchValue $ExpectedBranch -TimeoutSecondsValue $TimeoutSeconds
        $surfaceDetails += [ordered]@{
            name = $entry.Key
            path = $surface.path
            available = [bool]$surfaceResult.available
            ok = [bool]$surfaceResult.ok
            error = [string]$surfaceResult.error
            source = "live_dry_run"
        }
        if ($surfaceResult.ok) {
            $surfaceResults[$entry.Key] = $surfaceResult.data
        }
        else {
            $surfaceResults[$entry.Key] = $null
        }
    }

    $dayNight = $surfaceResults.day_night_readiness_result
    $chain = if ($null -ne $dayNight) { $dayNight.autonomy_chain_state } else { $null }
    $delegatedSources = @(
        [ordered]@{ key = "self_audit_result"; schema = "AIOS_SELF_AUDIT_LOOP_RESULT.v1"; status_field = "self_audit_status" },
        [ordered]@{ key = "packet_router_result"; schema = "AIOS_SELF_DEVELOPMENT_PACKET_ROUTER_RESULT.v1"; status_field = "packet_router_status" },
        [ordered]@{ key = "validator_evidence_router_result"; schema = "AIOS_VALIDATOR_EVIDENCE_ROUTER_RESULT.v1"; status_field = "validator_evidence_router_status" }
    )
    foreach ($source in $delegatedSources) {
        $surface = $safeSurfaces[$source.key]
        $statusValue = "UNKNOWN"
        if ($null -ne $chain -and $chain.PSObject.Properties.Name -contains $source.status_field) {
            $statusValue = [string]$chain.PSObject.Properties[$source.status_field].Value
        }
        $surfaceResults[$source.key] = [ordered]@{
            schema = $source.schema
            safety = [ordered]@{
                status = $statusValue
            }
            stop_conditions = @()
        }
        $surfaceDetails += [ordered]@{
            name = $source.key
            path = $surface.path
            available = [bool]($null -ne $dayNight)
            ok = ([string]$statusValue -eq "PASS")
            error = "delegated_via_day_night_readiness"
        }
    }
}
else {
    foreach ($entry in $safeSurfaces.GetEnumerator()) {
        $surface = $entry.Value
        $surfaceDetails += [ordered]@{
            name = $entry.Key
            path = $surface.path
            available = [bool](Test-Path -LiteralPath (Join-Path $resolvedRepoRoot $surface.path) -PathType Leaf)
            ok = $false
            error = "skipped_due_to_stop_condition"
        }
        $surfaceResults[$entry.Key] = $null
    }
}

$afterState = Get-NoWriteState -Root $resolvedRepoRoot
$noWriteProof = Compare-NoWriteState -Before $beforeState -After $afterState

$repoState = [ordered]@{
    repo_root = $resolvedRepoRoot
    branch = $beforeState.branch
    expected_branch = $ExpectedBranch
    branch_matches_expected = ([string]$beforeState.branch -eq [string]$ExpectedBranch)
    dirty = [bool]$beforeState.dirty
    dirty_allowed_for_governed_loop_validation = [bool]$dirtyAllowedForValidation
    fail_on_dirty_worktree = [bool]$FailOnDirtyWorktree
    status_lines = @($beforeState.status_lines)
    diff_name_only = @($beforeState.diff_name_only)
    untracked_files = @($beforeState.untracked_files)
}

$payload = [ordered]@{
    generated_utc = $generatedUtc
    repo_state = $repoState
    authority_context = $authorityContext
    self_audit_result = $surfaceResults.self_audit_result
    packet_router_result = $surfaceResults.packet_router_result
    validator_evidence_router_result = $surfaceResults.validator_evidence_router_result
    day_night_readiness_result = $surfaceResults.day_night_readiness_result
    campaign_no_ready = $surfaceResults.campaign_no_ready
    campaign_next_task = $surfaceResults.campaign_next_task
    action_recommendation = $surfaceResults.action_recommendation
    safe_surfaces_used = $surfaceDetails
    blocked_surfaces = $blockedSurfaces
    no_write_proof = $noWriteProof
}

$result = Invoke-PythonGovernedLoopLogic -LogicPath $logicPath -Payload $payload -TimeoutSecondsValue $TimeoutSeconds

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 80
}
else {
    Write-ConsoleReport -Result $result
}

if ([string]$result.safety.status -eq "PASS") {
    exit 0
}
exit 1
