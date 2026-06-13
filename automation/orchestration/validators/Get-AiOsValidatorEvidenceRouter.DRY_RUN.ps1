[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$ExpectedBranch = "main",
    [switch]$OutputJson,
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

function Test-ValidatorEvidenceRouterDirtyState {
    param([object]$State)
    $allowedExact = @(
        "automation/orchestration/validators/Get-AiOsValidatorEvidenceRouter.DRY_RUN.ps1",
        "automation/orchestration/validators/aios_validator_evidence_router.py",
        "schemas/aios/orchestration/AIOS_VALIDATOR_EVIDENCE_ROUTER_RESULT.v1.schema.json",
        "automation/orchestration/supervisor/Get-AiOsDayNightReadiness.DRY_RUN.ps1",
        "automation/orchestration/supervisor/aios_day_night_readiness.py",
        "schemas/aios/orchestration/AIOS_DAY_NIGHT_READINESS_RESULT.v1.schema.json",
        "schemas/aios/orchestration/ORCHESTRATION_SCHEMA_INDEX.json",
        "tests/orchestration/test_aios_validator_evidence_router.py",
        "tests/orchestration/test_aios_validator_evidence_router_runner.py",
        "tests/orchestration/test_aios_day_night_readiness.py",
        "tests/orchestration/test_aios_day_night_readiness_runner.py",
        "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1",
        "automation/orchestration/self_audit/Invoke-AiOsSelfAuditLoop.DRY_RUN.ps1",
        "automation/orchestration/self_development/Invoke-AiOsGovernedSelfDevelopmentLoop.DRY_RUN.ps1",
        "automation/orchestration/self_development/aios_governed_self_development_loop.py",
        "schemas/aios/orchestration/AIOS_GOVERNED_SELF_DEVELOPMENT_LOOP_RESULT.v1.schema.json",
        "tests/orchestration/test_aios_governed_self_development_loop.py",
        "tests/orchestration/test_aios_governed_self_development_loop_runner.py",
        "tests/orchestration/test_aios_self_audit_runner.py",
        "tests/orchestration/test_aios_self_development_packet_router_runner.py"
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

function Invoke-JsonSurface {
    param([string]$Root, [string]$RelativeScript, [int]$TimeoutSeconds, [string]$ExpectedBranchValue = $ExpectedBranch)
    $scriptPath = Join-Path $Root $RelativeScript
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        return [ordered]@{
            available = $false
            ok = $false
            error = "surface_missing"
            data = $null
        }
    }
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = "powershell"
    $safePath = $scriptPath -replace '"', '\"'
    $safeRoot = $Root -replace '"', '\"'
    $safeExpectedBranch = $ExpectedBranchValue -replace '"', '\"'
    $branchAwareScripts = @(
        "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1"
    )
    $normalizedRelativeScript = $RelativeScript -replace "\\", "/"
    if ($branchAwareScripts -contains $normalizedRelativeScript) {
        $psi.Arguments = '-NoProfile -ExecutionPolicy Bypass -File "{0}" -RepoRoot "{1}" -ExpectedBranch "{2}" -OutputJson -TimeoutSeconds {3}' -f $safePath, $safeRoot, $safeExpectedBranch, $TimeoutSeconds
    } else {
        $psi.Arguments = '-NoProfile -ExecutionPolicy Bypass -File "{0}" -OutputJson' -f $safePath
    }
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    [void]$process.Start()
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
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

function Get-SurfaceInventory {
    param([string]$Root)
    $paths = @(
        "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
        "automation/orchestration/validators/Test-ApplyApprovalGate.DRY_RUN.ps1",
        "automation/orchestration/validators/Test-ApprovalInboxIntegrity.DRY_RUN.ps1",
        "automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1",
        "automation/orchestration/validators/Test-WorkerClaimCollision.DRY_RUN.ps1",
        "automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
        "automation/orchestration/validators/Test-AiOsOrchestrationSchemaContracts.DRY_RUN.ps1",
        "automation/orchestration/validators/Test-CommitPackageManifest.DRY_RUN.ps1",
        "automation/orchestration/validators/Invoke-AiOsAuthorityDuplicationGuard.ps1",
        "automation/orchestration/validators/New-CommitPackagePreview.DRY_RUN.ps1",
        "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1",
        "automation/orchestration/commit_packages/Test-AiOsCommitPushGate.DRY_RUN.ps1",
        "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1",
        "automation/orchestration/self_audit/Invoke-AiOsSelfAuditLoop.DRY_RUN.ps1",
        "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1",
        "automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1",
        "automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1",
        "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1",
        "automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1",
        "automation/orchestration/workers/Get-AiOsWorkerRegistry.DRY_RUN.ps1",
        "automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1",
        "automation/orchestration/relay_bus/Get-AiOsRelayBusState.DRY_RUN.ps1",
        "automation/orchestration/relay_bus/Resolve-AiOsRelayHumanReview.DRY_RUN.ps1",
        "automation/orchestration/runtime/Get-AiOsRuntimeStateBundle.DRY_RUN.ps1",
        "automation/orchestration/commit_packages/Invoke-AiOsExactCommitPackage.ps1",
        "automation/orchestration/approval_inbox/New-AiOsPacketApprovalRequest.DRY_RUN.ps1",
        "automation/orchestration/approval_inbox/Invoke-AiOsApprovalChain.DRY_RUN.ps1",
        "automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1",
        "automation/orchestration/approval_runner/Invoke-AiOsApprovedActionResume.ps1",
        "automation/orchestration/locks/Claim-AiOsFileLock.DRY_RUN.ps1",
        "automation/orchestration/locks/Release-AiOsFileLock.DRY_RUN.ps1",
        "automation/orchestration/relay_bus/New-AiOsRelayMessage.DRY_RUN.ps1",
        "automation/orchestration/workers/inbox/New-AiOsWorkerReadyPacket.DRY_RUN.ps1",
        "automation/orchestration/workers/inbox/Add-AiOsWorkerInboxItem.DRY_RUN.ps1",
        "automation/orchestration/workers/state/Set-AiOsWorkerTaskState.DRY_RUN.ps1",
        "automation/orchestration/workers/launcher/Open-AiOsWorkerWindow.DRY_RUN.ps1",
        "automation/orchestration/workers/daemon/Start-AiOsWorkerDaemon.DRY_RUN.ps1",
        "automation/orchestration/workers/loop/Start-AiOsWorkerLoop.DRY_RUN.ps1",
        "automation/orchestration/workers/cycle/Start-AiOsAutonomousWorkerCycle.DRY_RUN.ps1",
        "automation/orchestration/workers/execution/Invoke-AiOsWorkerSafeExecute.DRY_RUN.ps1",
        "automation/orchestration/runtime/Start-AiOsRuntimeCycle.DRY_RUN.ps1",
        "automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1",
        "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1",
        "automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1"
    )
    return @($paths | ForEach-Object {
        [ordered]@{
            path = $_
            exists = [bool](Test-Path -LiteralPath (Join-Path $Root $_) -PathType Leaf)
        }
    })
}

function Invoke-PythonRouterLogic {
    param([string]$LogicPath, [object]$Payload, [int]$TimeoutSeconds)
    if (-not (Test-Path -LiteralPath $LogicPath -PathType Leaf)) {
        throw "Python router logic module missing: $LogicPath"
    }
    $payloadJson = $Payload | ConvertTo-Json -Depth 60
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
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        $process.Kill()
        throw "Python validator evidence router logic timed out."
    }
    $rawText = $stdoutTask.Result.Trim()
    $errorText = $stderrTask.Result.Trim()
    if ([string]::IsNullOrWhiteSpace($rawText)) {
        throw "Python validator evidence router logic returned no JSON. $errorText"
    }
    return $rawText | ConvertFrom-Json -ErrorAction Stop
}

function Write-ConsoleReport {
    param([object]$Result)
    Write-Host "AIOS Validator Evidence Router"
    Write-Host "Mode: $($Result.mode)"
    Write-Host "Schema: $($Result.schema)"
    Write-Host ""
    Write-Host "CURRENT STATE"
    Write-Host "branch: $($Result.repo_state.branch)"
    Write-Host "dirty: $($Result.repo_state.dirty)"
    Write-Host "expected_branch: $($Result.repo_state.expected_branch)"
    Write-Host "branch_matches_expected: $($Result.repo_state.branch_matches_expected)"
    Write-Host ""
    Write-Host "SAFE VALIDATORS"
    foreach ($surface in @($Result.validator_catalog | Where-Object { $_.classification -eq "SAFE_READ_ONLY_VALIDATOR" })) {
        Write-Host "- $($surface.surface_id): $($surface.path)"
    }
    Write-Host ""
    Write-Host "SAFE EVIDENCE"
    foreach ($surface in @($Result.evidence_sources | Where-Object { $_.classification -in @("SAFE_READ_ONLY_EVIDENCE", "SAFE_WITH_SANITIZATION") })) {
        Write-Host "- $($surface.surface_id): $($surface.classification)"
    }
    Write-Host ""
    Write-Host "BLOCKED SURFACES"
    foreach ($surface in @($Result.excluded_surfaces)) {
        Write-Host "- $($surface.surface_id): $($surface.classification)"
    }
    Write-Host ""
    Write-Host "RECOMMENDED CHAINS"
    foreach ($chain in @($Result.recommended_chains)) {
        Write-Host "- $($chain.name): $($chain.chain_id)"
    }
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
$logicPath = Join-Path $PSScriptRoot "aios_validator_evidence_router.py"
$generatedUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$authorityContext = Read-AuthorityContext -Root $resolvedRepoRoot
$beforeState = Get-NoWriteState -Root $resolvedRepoRoot
$dirtyAllowedForValidation = Test-ValidatorEvidenceRouterDirtyState -State $beforeState
$skipSurfaceCalls = (-not $authorityContext.all_required_loaded) -or ([bool]$beforeState.dirty -and $FailOnDirtyWorktree -and (-not $dirtyAllowedForValidation))

$sourcePacketRouterResult = $null
if (-not $skipSurfaceCalls) {
    $surfaceResult = Invoke-JsonSurface -Root $resolvedRepoRoot -RelativeScript "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1" -TimeoutSeconds $TimeoutSeconds
    if ($surfaceResult.ok) {
        $sourcePacketRouterResult = $surfaceResult.data
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
    dirty_allowed_for_validator_evidence_router_validation = [bool]$dirtyAllowedForValidation
    fail_on_dirty_worktree = [bool]$FailOnDirtyWorktree
    status_lines = @($beforeState.status_lines)
    diff_name_only = @($beforeState.diff_name_only)
    untracked_files = @($beforeState.untracked_files)
}

$payload = [ordered]@{
    generated_utc = $generatedUtc
    repo_state = $repoState
    authority_context = $authorityContext
    source_packet_router_result = $sourcePacketRouterResult
    source_packet_router_schema = "AIOS_SELF_DEVELOPMENT_PACKET_ROUTER_RESULT.v1"
    surface_inventory = Get-SurfaceInventory -Root $resolvedRepoRoot
    action_recommendation = [ordered]@{
        recommended_command = ""
    }
    no_write_proof = $noWriteProof
}

$result = Invoke-PythonRouterLogic -LogicPath $logicPath -Payload $payload -TimeoutSeconds $TimeoutSeconds

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 60
}
else {
    Write-ConsoleReport -Result $result
}

if ([string]$result.safety.status -eq "PASS") {
    exit 0
}
exit 1
