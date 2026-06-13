[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$ExpectedBranch = "main",
    [switch]$OutputJson,
    [ValidateSet("Core", "ExtendedReadOnly")]
    [string]$SurfaceProfile = "Core",
    [ValidateRange(1, 20)]
    [int]$MaxCandidatePackets = 5,
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

function Test-SelfAuditValidationDirtyState {
    param([object]$State)
    $allowedExact = @(
        "automation/orchestration/self_audit/Invoke-AiOsSelfAuditLoop.DRY_RUN.ps1",
        "automation/orchestration/self_audit/aios_self_audit_loop.py",
        "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1",
        "automation/orchestration/self_audit/aios_self_development_packet_router.py",
        "schemas/aios/orchestration/AIOS_SELF_AUDIT_LOOP_RESULT.v1.schema.json",
        "schemas/aios/orchestration/AIOS_SELF_DEVELOPMENT_PACKET_ROUTER_RESULT.v1.schema.json",
        "automation/orchestration/validators/Get-AiOsValidatorEvidenceRouter.DRY_RUN.ps1",
        "automation/orchestration/validators/aios_validator_evidence_router.py",
        "schemas/aios/orchestration/AIOS_VALIDATOR_EVIDENCE_ROUTER_RESULT.v1.schema.json",
        "automation/orchestration/supervisor/Get-AiOsDayNightReadiness.DRY_RUN.ps1",
        "automation/orchestration/supervisor/aios_day_night_readiness.py",
        "schemas/aios/orchestration/AIOS_DAY_NIGHT_READINESS_RESULT.v1.schema.json",
        "schemas/aios/orchestration/ORCHESTRATION_SCHEMA_INDEX.json",
        "tests/orchestration/test_aios_self_audit_loop.py",
        "tests/orchestration/test_aios_self_audit_runner.py",
        "tests/orchestration/test_aios_self_development_packet_router.py",
        "tests/orchestration/test_aios_self_development_packet_router_runner.py",
        "tests/orchestration/test_aios_validator_evidence_router.py",
        "tests/orchestration/test_aios_validator_evidence_router_runner.py",
        "tests/orchestration/test_aios_day_night_readiness.py",
        "tests/orchestration/test_aios_day_night_readiness_runner.py",
        "automation/orchestration/self_development/Invoke-AiOsGovernedSelfDevelopmentLoop.DRY_RUN.ps1",
        "automation/orchestration/self_development/aios_governed_self_development_loop.py",
        "schemas/aios/orchestration/AIOS_GOVERNED_SELF_DEVELOPMENT_LOOP_RESULT.v1.schema.json",
        "tests/orchestration/test_aios_governed_self_development_loop.py",
        "tests/orchestration/test_aios_governed_self_development_loop_runner.py",
        "automation/orchestration/operator_control/Test-AiOsApprovalSosHardGate.DRY_RUN.ps1",
        "automation/orchestration/operator_control/aios_approval_sos_hard_gate.py",
        "schemas/aios/orchestration/AIOS_APPROVAL_SOS_HARD_GATE_RESULT.v1.schema.json",
        "tests/orchestration/test_aios_approval_sos_hard_gate.py",
        "tests/orchestration/test_aios_approval_sos_hard_gate_runner.py",
        "automation/orchestration/self_development/Test-AiOsGovernedSelfDevelopmentSoak.DRY_RUN.ps1",
        "automation/orchestration/self_development/aios_governed_self_development_soak.py",
        "schemas/aios/orchestration/AIOS_GOVERNED_SELF_DEVELOPMENT_SOAK_RESULT.v1.schema.json",
        "tests/orchestration/test_aios_governed_self_development_soak.py",
        "tests/orchestration/test_aios_governed_self_development_soak_runner.py"
    )
    $changedPaths = @($State.changed_entries | ForEach-Object { Get-ChangedPathFromStatusLine -Line ([string]$_) } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($changedPaths.Count -eq 0) {
        return $false
    }
    foreach ($path in $changedPaths) {
        $isAllowed = $allowedExact -contains $path
        if (-not $isAllowed) {
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
        "docs/AI_OS/autonomy/AIOS_SELF_AUDIT_LOOP_CONTRACT_V1.md"
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
    param([string]$Root, [string]$RelativeScript)
    $scriptPath = Join-Path $Root $RelativeScript
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        return [ordered]@{
            available = $false
            ok = $false
            error = "surface_missing"
            data = $null
        }
    }
    $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $scriptPath -OutputJson 2>&1
    $exitCode = $LASTEXITCODE
    $rawText = ($raw | Out-String).Trim()
    if ($exitCode -ne 0) {
        return [ordered]@{
            available = $true
            ok = $false
            error = "surface_exit_$exitCode"
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
        return [ordered]@{
            available = $true
            ok = $false
            error = "surface_json_parse_failed"
            data = $null
        }
    }
}

function Invoke-PythonSelfAuditLogic {
    param([string]$LogicPath, [object]$Payload, [int]$TimeoutSeconds)
    if (-not (Test-Path -LiteralPath $LogicPath -PathType Leaf)) {
        throw "Python logic module missing: $LogicPath"
    }
    $payloadJson = $Payload | ConvertTo-Json -Depth 40
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
        throw "Python self-audit logic timed out."
    }
    $rawText = $stdoutTask.Result.Trim()
    $errorText = $stderrTask.Result.Trim()
    if ([string]::IsNullOrWhiteSpace($rawText)) {
        throw "Python self-audit logic returned no JSON. $errorText"
    }
    return $rawText | ConvertFrom-Json -ErrorAction Stop
}

function Write-ConsoleReport {
    param([object]$Result)
    Write-Host "AIOS Self-Audit Loop"
    Write-Host "Mode: $($Result.mode)"
    Write-Host "Schema: $($Result.schema)"
    Write-Host ""
    Write-Host "CURRENT STATE"
    Write-Host "branch: $($Result.repo_state.branch)"
    Write-Host "dirty: $($Result.repo_state.dirty)"
    Write-Host "expected_branch: $($Result.repo_state.expected_branch)"
    Write-Host "branch_matches_expected: $($Result.repo_state.branch_matches_expected)"
    Write-Host ""
    Write-Host "AUTHORITY CONTEXT"
    Write-Host "all_required_loaded: $($Result.authority_context.all_required_loaded)"
    Write-Host ""
    Write-Host "COMPLETE IDLE STATE"
    Write-Host "overall_readiness: $($Result.complete_idle_state.overall_readiness)"
    Write-Host "classification: $($Result.complete_idle_state.classification)"
    Write-Host "idle_allowed: $($Result.complete_idle_state.idle_allowed)"
    Write-Host ""
    Write-Host "SAFE SURFACES USED"
    foreach ($surface in @($Result.safe_surfaces_used)) {
        Write-Host "- $surface"
    }
    Write-Host ""
    Write-Host "GAP CLASSIFICATIONS"
    foreach ($gap in @($Result.gap_classifications)) {
        Write-Host "- $($gap.classification): $($gap.severity)"
    }
    Write-Host ""
    Write-Host "CANDIDATE PACKETS"
    foreach ($candidate in @($Result.candidate_packets)) {
        Write-Host "- #$($candidate.rank) $($candidate.packet_id) [$($candidate.mode)] blocked=$($candidate.blocked)"
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
    Write-Host "NO-WRITE PROOF"
    Write-Host "changed: $($Result.safety.no_write_proof.changed)"
    Write-Host "git_state_changed: $($Result.safety.no_write_proof.git_state_changed)"
    Write-Host "forbidden_surface_changed: $($Result.safety.no_write_proof.forbidden_surface_changed)"
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
$logicPath = Join-Path $PSScriptRoot "aios_self_audit_loop.py"
$generatedUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$authorityContext = Read-AuthorityContext -Root $resolvedRepoRoot
$beforeState = Get-NoWriteState -Root $resolvedRepoRoot
$dirtyAllowedForSelfValidation = Test-SelfAuditValidationDirtyState -State $beforeState

$safeSurfaces = [ordered]@{
    no_ready_stage_discovery = "automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1"
    campaign_next_task = "automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1"
    action_recommendation = "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1"
}

if ($SurfaceProfile -eq "ExtendedReadOnly") {
    $safeSurfaces.relay_bus_state = "automation/orchestration/relay_bus/Get-AiOsRelayBusState.DRY_RUN.ps1"
    $safeSurfaces.relay_operator_state = "automation/orchestration/review_bridge/Get-AiOsRelayOperatorState.DRY_RUN.ps1"
    $safeSurfaces.relay_human_review = "automation/orchestration/relay_bus/Resolve-AiOsRelayHumanReview.DRY_RUN.ps1"
}

$blockedSurfaces = @(
    "automation/self_build/aios_self_build_cycle.py",
    "automation/self_build/aios_self_build_inspector.py",
    "automation/orchestration/autonomy_reports/*",
    "automation/orchestration/autonomy_control_plane/Invoke-AiOsAutonomyControlPlane.DRY_RUN.ps1",
    "automation/orchestration/autonomy_router/Get-AiOsAutonomyNextAction.DRY_RUN.ps1",
    "automation/orchestration/autonomy_loop/Invoke-AiOsAutonomyLoop.DRY_RUN.ps1",
    "automation/orchestration/autonomy_discovery/Get-AiOsAutonomyInventory.DRY_RUN.ps1",
    "automation/orchestration/review_bridge/New-AiOsCodexReportRelayItem.DRY_RUN.ps1",
    "automation/orchestration/reports/New-AiOsMorningBrief.ps1",
    "automation/telemetry/Update-AiOsProductionReadout.ps1",
    "automation/reporting/New-AiOsReport.ps1",
    "automation/orchestration/commit_packages/Invoke-AiOsExactCommitPackage.ps1",
    "automation/orchestration/relay_bus/New-AiOsRelayMessage.DRY_RUN.ps1"
)

$evidence = [ordered]@{}
$safeSurfacesUsed = @()
$surfaceDetails = @()
$skipSurfaceCalls = (-not $authorityContext.all_required_loaded) -or ([bool]$beforeState.dirty -and $FailOnDirtyWorktree -and (-not $dirtyAllowedForSelfValidation))

if (-not $skipSurfaceCalls) {
    foreach ($entry in $safeSurfaces.GetEnumerator()) {
        $surfaceResult = Invoke-JsonSurface -Root $resolvedRepoRoot -RelativeScript $entry.Value
        $surfaceDetails += [ordered]@{
            name = $entry.Key
            path = $entry.Value
            available = [bool]$surfaceResult.available
            ok = [bool]$surfaceResult.ok
            error = [string]$surfaceResult.error
        }
        if ($surfaceResult.ok) {
            $evidence[$entry.Key] = $surfaceResult.data
            $safeSurfacesUsed += $entry.Value
        }
    }
}
else {
    foreach ($entry in $safeSurfaces.GetEnumerator()) {
        $surfaceDetails += [ordered]@{
            name = $entry.Key
            path = $entry.Value
            available = [bool](Test-Path -LiteralPath (Join-Path $resolvedRepoRoot $entry.Value) -PathType Leaf)
            ok = $false
            error = "skipped_due_to_stop_condition"
        }
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
    dirty_allowed_for_self_validation = [bool]$dirtyAllowedForSelfValidation
    fail_on_dirty_worktree = [bool]$FailOnDirtyWorktree
    status_lines = @($beforeState.status_lines)
    diff_name_only = @($beforeState.diff_name_only)
    untracked_files = @($beforeState.untracked_files)
}

$payload = [ordered]@{
    generated_utc = $generatedUtc
    repo_state = $repoState
    authority_context = $authorityContext
    evidence = $evidence
    surface_inventory = [ordered]@{
        profile = $SurfaceProfile
        timeout_seconds = $TimeoutSeconds
        safe_surface_count = $safeSurfaces.Count
        blocked_surface_count = $blockedSurfaces.Count
        surfaces = $surfaceDetails
    }
    blocked_surfaces = $blockedSurfaces
    safe_surfaces_used = $safeSurfacesUsed
    no_write_proof = $noWriteProof
    max_candidate_packets = $MaxCandidatePackets
    candidate_packet_ids = @(
        "AIOS-SELF-DEVELOPMENT-PACKET-ROUTER-DRYRUN-V1",
        "AIOS-VALIDATOR-EVIDENCE-ROUTER-DRYRUN-V1",
        "AIOS-DAY-NIGHT-SUPERVISOR-READINESS-DRYRUN-V1",
        "AIOS-DASHBOARD-DATA-CONTRACT-REVIEW-DRYRUN-V1",
        "AIOS-DASHBOARD-LAYER-TAXONOMY-DOCS-APPLY-V1"
    )
}

$result = Invoke-PythonSelfAuditLogic -LogicPath $logicPath -Payload $payload -TimeoutSeconds $TimeoutSeconds

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 40
}
else {
    Write-ConsoleReport -Result $result
}

if ([string]$result.safety.status -eq "PASS") {
    exit 0
}
exit 1
