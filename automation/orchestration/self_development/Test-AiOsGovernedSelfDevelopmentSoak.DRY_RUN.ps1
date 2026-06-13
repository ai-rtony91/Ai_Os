[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$ExpectedBranch = "main",
    [switch]$OutputJson,
    [ValidateRange(1, 1000)]
    [int]$Cycles = 3,
    [ValidateRange(1, 100)]
    [int]$MaxCycles = 10,
    [string]$GovernedLoopJson = "",
    [string]$ApprovalSosHardGateJson = "",
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
        "control/review_bridge/codex_reports",
        "control",
        "secrets",
        ".env",
        "AIOS_BACKUP_IN_PROGRESS.lock"
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

function Test-SoakValidationDirtyState {
    param([object]$State)
    $allowedExact = @(
        "automation/orchestration/self_development/Test-AiOsGovernedSelfDevelopmentSoak.DRY_RUN.ps1",
        "automation/orchestration/self_development/aios_governed_self_development_soak.py",
        "schemas/aios/orchestration/AIOS_GOVERNED_SELF_DEVELOPMENT_SOAK_RESULT.v1.schema.json",
        "schemas/aios/orchestration/ORCHESTRATION_SCHEMA_INDEX.json",
        "tests/orchestration/test_aios_governed_self_development_soak.py",
        "tests/orchestration/test_aios_governed_self_development_soak_runner.py",
        "automation/orchestration/operator_control/Test-AiOsApprovalSosHardGate.DRY_RUN.ps1",
        "automation/orchestration/self_development/Invoke-AiOsGovernedSelfDevelopmentLoop.DRY_RUN.ps1",
        "automation/orchestration/supervisor/Get-AiOsDayNightReadiness.DRY_RUN.ps1",
        "automation/orchestration/validators/Get-AiOsValidatorEvidenceRouter.DRY_RUN.ps1",
        "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1",
        "automation/orchestration/self_audit/Invoke-AiOsSelfAuditLoop.DRY_RUN.ps1"
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

function New-FailedSurfaceResult {
    param([string]$Schema, [string]$ErrorText)
    return [ordered]@{
        schema = $Schema
        safety = [ordered]@{
            status = "BLOCKED"
            writes_files = $false
            writes_reports = $false
            writes_telemetry = $false
            writes_packet_drafts = $false
            writes_proposed_packets = $false
            outputs_packet_body = $false
            creates_ready_stage = $false
            mutates_registry = $false
            mutates_queue = $false
            mutates_locks = $false
            mutates_approvals = $false
            writes_relay = $false
            starts_runtime = $false
            launches_workers = $false
            scheduler_or_daemon = $false
            protected_action_recommended = $false
            secrets_or_env_access = $false
            broker_or_live_trading = $false
        }
        stop_conditions = @($ErrorText)
    }
}

function Invoke-JsonSurface {
    param(
        [string]$Root,
        [string]$RelativeScript,
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
    $safeRoot = $Root -replace '"', '\"'
    $safeExpectedBranch = $ExpectedBranchValue -replace '"', '\"'
    $arguments = '-NoProfile -ExecutionPolicy Bypass -File "{0}" -RepoRoot "{1}" -ExpectedBranch "{2}" -OutputJson -TimeoutSeconds {3}' -f $safePath, $safeRoot, $safeExpectedBranch, $TimeoutSecondsValue
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = "powershell"
    $psi.Arguments = $arguments
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    try {
        [void]$process.Start()
    }
    catch {
        return [ordered]@{
            available = $true
            ok = $false
            error = "surface_start_failed"
            data = $null
        }
    }
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

function Invoke-PythonSoakLogic {
    param([string]$LogicPath, [object]$Payload, [int]$TimeoutSecondsValue)
    if (-not (Test-Path -LiteralPath $LogicPath -PathType Leaf)) {
        throw "Python governed self-development soak logic module missing: $LogicPath"
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
        throw "Python governed self-development soak logic timed out."
    }
    $rawText = $stdoutTask.Result.Trim()
    $errorText = $stderrTask.Result.Trim()
    if ([string]::IsNullOrWhiteSpace($rawText)) {
        throw "Python governed self-development soak logic returned no JSON. $errorText"
    }
    return $rawText | ConvertFrom-Json -ErrorAction Stop
}

function Write-ConsoleReport {
    param([object]$Result)
    Write-Host "AIOS Governed Self-Development Soak"
    Write-Host "Mode: $($Result.mode)"
    Write-Host "Schema: $($Result.schema)"
    Write-Host ""
    Write-Host "CURRENT STATE"
    Write-Host "cycles_requested: $($Result.cycles_requested)"
    Write-Host "cycles_completed: $($Result.cycles_completed)"
    Write-Host ""
    Write-Host "SOAK SIMULATION"
    Write-Host "aggregate_status: $($Result.aggregate_status)"
    Write-Host "governed_loop_pass: $($Result.safety.governed_loop_pass)"
    Write-Host "approval_sos_hard_gate_pass: $($Result.safety.approval_sos_hard_gate_pass)"
    Write-Host ""
    Write-Host "CYCLE RESULTS"
    foreach ($cycle in @($Result.cycle_results)) {
        Write-Host "- cycle $($cycle.cycle_index): $($cycle.status); governed_loop=$($cycle.governed_loop_status); hard_gate=$($cycle.approval_sos_hard_gate_status)"
    }
    Write-Host ""
    Write-Host "FORBIDDEN SURFACE DELTAS"
    if (@($Result.forbidden_surface_deltas).Count -eq 0) {
        Write-Host "- none"
    }
    else {
        foreach ($delta in @($Result.forbidden_surface_deltas)) {
            Write-Host "- cycle $($delta.cycle_index): $($delta.surface) $($delta.delta)"
        }
    }
    Write-Host ""
    Write-Host "APPROVAL REQUIRED"
    Write-Host "human_owner_required: $($Result.approval_required.human_owner_required)"
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
    Write-Host "STATUS: $($Result.aggregate_status)"
}

$resolvedRepoRoot = Get-RepoRoot -PathHint $RepoRoot
$logicPath = Join-Path $PSScriptRoot "aios_governed_self_development_soak.py"
$generatedUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$authorityContext = Read-AuthorityContext -Root $resolvedRepoRoot
$beforeState = Get-NoWriteState -Root $resolvedRepoRoot
$dirtyAllowedForValidation = Test-SoakValidationDirtyState -State $beforeState
$skipCycles = (-not $authorityContext.all_required_loaded) -or ([bool]$beforeState.dirty -and $FailOnDirtyWorktree -and (-not $dirtyAllowedForValidation)) -or ($Cycles -gt $MaxCycles)
$governedLoopEvidence = ConvertFrom-JsonEvidenceParameter -Name "GovernedLoopJson" -JsonText $GovernedLoopJson
$hardGateEvidence = ConvertFrom-JsonEvidenceParameter -Name "ApprovalSosHardGateJson" -JsonText $ApprovalSosHardGateJson
$cycleResults = @()

if (-not $skipCycles) {
    for ($i = 1; $i -le $Cycles; $i++) {
        $cycleBeforeState = Get-NoWriteState -Root $resolvedRepoRoot
        if ([bool]$governedLoopEvidence.supplied) {
            $governedLoopData = $governedLoopEvidence.data
        }
        else {
            $surface = Invoke-JsonSurface -Root $resolvedRepoRoot -RelativeScript "automation/orchestration/self_development/Invoke-AiOsGovernedSelfDevelopmentLoop.DRY_RUN.ps1" -ExpectedBranchValue $ExpectedBranch -TimeoutSecondsValue $TimeoutSeconds
            $governedLoopData = if ($surface.ok) { $surface.data } else { New-FailedSurfaceResult -Schema "AIOS_GOVERNED_SELF_DEVELOPMENT_LOOP_RESULT.v1" -ErrorText $surface.error }
        }
        if ([bool]$hardGateEvidence.supplied) {
            $hardGateData = $hardGateEvidence.data
        }
        else {
            $surface = Invoke-JsonSurface -Root $resolvedRepoRoot -RelativeScript "automation/orchestration/operator_control/Test-AiOsApprovalSosHardGate.DRY_RUN.ps1" -ExpectedBranchValue $ExpectedBranch -TimeoutSecondsValue $TimeoutSeconds
            $hardGateData = if ($surface.ok) { $surface.data } else { New-FailedSurfaceResult -Schema "AIOS_APPROVAL_SOS_HARD_GATE_RESULT.v1" -ErrorText $surface.error }
        }
        $cycleAfterState = Get-NoWriteState -Root $resolvedRepoRoot
        $cycleResults += [ordered]@{
            cycle_index = $i
            governed_loop_result = $governedLoopData
            approval_sos_hard_gate_result = $hardGateData
            no_write_proof = Compare-NoWriteState -Before $cycleBeforeState -After $cycleAfterState
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
    dirty_allowed_for_soak_validation = [bool]$dirtyAllowedForValidation
    fail_on_dirty_worktree = [bool]$FailOnDirtyWorktree
    status_lines = @($beforeState.status_lines)
    diff_name_only = @($beforeState.diff_name_only)
    untracked_files = @($beforeState.untracked_files)
}

$payload = [ordered]@{
    generated_utc = $generatedUtc
    cycles_requested = $Cycles
    max_cycles = $MaxCycles
    repo_state = $repoState
    authority_context = $authorityContext
    cycle_results = $cycleResults
    no_write_proof = $noWriteProof
}

$result = Invoke-PythonSoakLogic -LogicPath $logicPath -Payload $payload -TimeoutSecondsValue $TimeoutSeconds

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 90
}
else {
    Write-ConsoleReport -Result $result
}

if ([string]$result.aggregate_status -eq "PASS") {
    exit 0
}
exit 1
