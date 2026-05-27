[CmdletBinding()]
param(
    [string[]]$CandidateFile = @(),
    [string[]]$AllowedPath = @(),
    [string]$CommitMessage = "",
    [string]$RemoteName = "origin",
    [string]$PushBranch = "",
    [string]$PrTitle = "",
    [string]$PrBody = "",
    [string]$BaseBranch = "main",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-AiOsGit {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        exit_code = $exitCode
        lines = @($output | ForEach-Object { [string]$_ })
        text = (@($output | ForEach-Object { [string]$_ }) -join "`n").Trim()
    }
}

function ConvertTo-AiOsRepoPath {
    param([AllowNull()][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    $repoPath = ($Path -replace "\\", "/").Trim()
    while ($repoPath.StartsWith("./")) {
        $repoPath = $repoPath.Substring(2)
    }

    return $repoPath.Trim("/")
}

function Convert-AiOsStatusLineToPath {
    param([string]$Line)

    if ([string]::IsNullOrWhiteSpace($Line) -or $Line.Length -lt 4 -or $Line.StartsWith("##")) {
        return ""
    }

    $path = $Line.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }

    return ConvertTo-AiOsRepoPath -Path $path
}

function Test-AiOsPathInsideBoundary {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string[]]$Boundary
    )

    if ($Boundary.Count -eq 0) {
        return $false
    }

    $normalizedPath = ConvertTo-AiOsRepoPath -Path $Path
    foreach ($item in $Boundary) {
        if ([string]::IsNullOrWhiteSpace($item)) {
            continue
        }

        $normalizedBoundary = ConvertTo-AiOsRepoPath -Path $item
        if ($normalizedPath -eq $normalizedBoundary -or $normalizedPath.StartsWith($normalizedBoundary + "/")) {
            return $true
        }
    }

    return $false
}

function ConvertTo-AiOsShellArgument {
    param([Parameter(Mandatory = $true)][string]$Value)

    if ($Value -match "^[A-Za-z0-9_./:-]+$") {
        return $Value
    }

    return '"' + ($Value -replace '"', '\"') + '"'
}

function Get-AiOsJsonTextFromLines {
    param([string[]]$Lines)

    $startIndex = -1
    $endIndex = -1

    for ($i = 0; $i -lt $Lines.Count; $i++) {
        $trimmed = $Lines[$i].Trim()
        if ($trimmed.StartsWith("{")) {
            $startIndex = $i
            break
        }
    }

    for ($i = $Lines.Count - 1; $i -ge 0; $i--) {
        $trimmed = $Lines[$i].Trim()
        if ($trimmed.EndsWith("}")) {
            $endIndex = $i
            break
        }
    }

    if ($startIndex -lt 0 -or $endIndex -lt $startIndex) {
        return ""
    }

    return (@($Lines[$startIndex..$endIndex]) -join "`n").Trim()
}

function Invoke-AiOsHelperJson {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string[]]$Arguments = @()
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            path = $Path
            status = "MISSING"
            exit_code = $null
            json = $null
            error = "Helper not found."
            text = ""
        }
    }

    $commandArguments = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Path)
    $commandArguments += @($Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & powershell @commandArguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    $lines = @($output | ForEach-Object { [string]$_ })
    $json = $null
    $errorText = ""

    try {
        $jsonText = Get-AiOsJsonTextFromLines -Lines $lines
        if (-not [string]::IsNullOrWhiteSpace($jsonText)) {
            $json = $jsonText | ConvertFrom-Json
        }
        else {
            $errorText = "No JSON object found in helper output."
        }
    }
    catch {
        $errorText = "JSON parse failed: $($_.Exception.Message)"
    }

    $status = if ($exitCode -eq 0 -and $null -ne $json) { "PASS" } else { "REVIEW" }

    return [pscustomobject]@{
        path = $Path
        status = $status
        exit_code = $exitCode
        json = $json
        error = $errorText
        text = ($lines -join "`n").Trim()
    }
}

$repoRootResult = Invoke-AiOsGit -Arguments @("rev-parse", "--show-toplevel")
if ($repoRootResult.exit_code -ne 0 -or [string]::IsNullOrWhiteSpace($repoRootResult.text)) {
    throw "Unable to resolve git repository root."
}

$repoRoot = $repoRootResult.text.Trim()
Set-Location -LiteralPath $repoRoot

$generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$branchResult = Invoke-AiOsGit -Arguments @("branch", "--show-current")
$statusResult = Invoke-AiOsGit -Arguments @("status", "--short", "--branch")
$headResult = Invoke-AiOsGit -Arguments @("rev-parse", "--short", "HEAD")

$currentBranch = if ($branchResult.exit_code -eq 0 -and -not [string]::IsNullOrWhiteSpace($branchResult.text)) {
    $branchResult.text.Trim()
}
else {
    "UNKNOWN"
}

$resolvedPushBranch = if (-not [string]::IsNullOrWhiteSpace($PushBranch)) {
    $PushBranch
}
else {
    $currentBranch
}

$statusLines = @($statusResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$fileStatusLines = @($statusLines | Where-Object { -not $_.StartsWith("##") })
$changedFiles = @($fileStatusLines | ForEach-Object { Convert-AiOsStatusLineToPath -Line $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
$candidateFiles = @($CandidateFile | ForEach-Object { ConvertTo-AiOsRepoPath -Path $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
if ($candidateFiles.Count -eq 0) {
    $candidateFiles = @($changedFiles)
}

$normalizedAllowedPaths = @($AllowedPath | ForEach-Object { ConvertTo-AiOsRepoPath -Path $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
$allowedFileEntries = @($candidateFiles | ForEach-Object {
    $insideBoundary = if ($normalizedAllowedPaths.Count -gt 0) {
        Test-AiOsPathInsideBoundary -Path $_ -Boundary $normalizedAllowedPaths
    }
    else {
        $false
    }

    [pscustomobject]@{
        path = $_
        allowed = $insideBoundary
        reason = if ($normalizedAllowedPaths.Count -eq 0) { "No AllowedPath boundary supplied." } elseif ($insideBoundary) { "Inside allowed boundary." } else { "Outside allowed boundary." }
    }
})

$allowedFileCheckResult = if ($candidateFiles.Count -eq 0) {
    "NO_CANDIDATES"
}
elseif ($normalizedAllowedPaths.Count -eq 0) {
    "REVIEW"
}
elseif (@($allowedFileEntries | Where-Object { -not $_.allowed }).Count -gt 0) {
    "BLOCKED"
}
else {
    "PASS"
}

$commitPackage = Invoke-AiOsHelperJson -Path "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1" -Arguments @("-OutputJson")
$validatorRecommendation = Invoke-AiOsHelperJson -Path "automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1" -Arguments @("-OutputJson")
$cleanState = Invoke-AiOsHelperJson -Path "automation/orchestration/clean_state/Test-AiOsCleanState.DRY_RUN.ps1" -Arguments @("-Json")

$commitPushGateArguments = @("-Json")
if ($normalizedAllowedPaths.Count -gt 0) {
    $commitPushGateArguments += "-ApprovedPath"
    $commitPushGateArguments += @($normalizedAllowedPaths)
}
$commitPushGate = Invoke-AiOsHelperJson -Path "automation/orchestration/commit_packages/Test-AiOsCommitPushGate.DRY_RUN.ps1" -Arguments $commitPushGateArguments
$prLaneRunner = Invoke-AiOsHelperJson -Path "automation/orchestration/pr_gates/Invoke-AiOsPrLaneRunner.DRY_RUN.ps1" -Arguments @("-Json")

$recommendedGitAddCommands = @()
if ($commitPackage.json -and $commitPackage.json.PSObject.Properties.Name -contains "recommended_git_add_commands") {
    $recommendedGitAddCommands = @($commitPackage.json.recommended_git_add_commands)
}
elseif ($candidateFiles.Count -gt 0) {
    $recommendedGitAddCommands = @($candidateFiles | ForEach-Object { "git add -- $(ConvertTo-AiOsShellArgument -Value $_)" })
}

$exactCommitPreview = if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
    [pscustomobject]@{
        status = "MISSING_APPROVAL_DETAIL"
        command = ""
        reason = "Commit message was not supplied."
    }
}
else {
    [pscustomobject]@{
        status = "PREVIEW_ONLY"
        command = "git commit -m $(ConvertTo-AiOsShellArgument -Value $CommitMessage)"
        reason = "Requires APPROVE_COMMIT before any future execution."
    }
}

$exactPushPreview = if ([string]::IsNullOrWhiteSpace($resolvedPushBranch) -or $resolvedPushBranch -eq "UNKNOWN") {
    [pscustomobject]@{
        status = "BLOCKED"
        command = ""
        reason = "Push branch is unknown."
    }
}
elseif ($resolvedPushBranch -eq "main") {
    [pscustomobject]@{
        status = "BLOCKED"
        command = ""
        reason = "Direct push preview to main is blocked. Use a PR lane branch unless Anthony explicitly approves a separate protected-main exception."
    }
}
else {
    [pscustomobject]@{
        status = "PREVIEW_ONLY"
        command = "git push -u $(ConvertTo-AiOsShellArgument -Value $RemoteName) $(ConvertTo-AiOsShellArgument -Value $resolvedPushBranch)"
        reason = "Requires APPROVE_PUSH before any future execution."
    }
}

$exactPrCreatePreview = if ([string]::IsNullOrWhiteSpace($PrTitle) -or [string]::IsNullOrWhiteSpace($resolvedPushBranch) -or $resolvedPushBranch -eq "UNKNOWN") {
    [pscustomobject]@{
        status = "MISSING_APPROVAL_DETAIL"
        command = ""
        reason = "PR title and known head branch are required for an exact PR create preview."
    }
}
else {
    $bodyText = if ([string]::IsNullOrWhiteSpace($PrBody)) { "AI_OS generated PR body required before APPLY." } else { $PrBody }
    [pscustomobject]@{
        status = "PREVIEW_ONLY"
        command = "gh pr create --base $(ConvertTo-AiOsShellArgument -Value $BaseBranch) --head $(ConvertTo-AiOsShellArgument -Value $resolvedPushBranch) --title $(ConvertTo-AiOsShellArgument -Value $PrTitle) --body $(ConvertTo-AiOsShellArgument -Value $bodyText)"
        reason = "Requires APPROVE_PR_CREATE before any future execution."
    }
}

$blockingSignals = [System.Collections.Generic.List[string]]::new()
if ($statusResult.exit_code -ne 0) {
    $blockingSignals.Add("git status failed") | Out-Null
}
if ($allowedFileCheckResult -eq "BLOCKED") {
    $blockingSignals.Add("candidate file outside allowed boundary") | Out-Null
}
foreach ($helper in @($validatorRecommendation, $cleanState, $commitPackage, $commitPushGate, $prLaneRunner)) {
    if ($helper.status -eq "MISSING") {
        $blockingSignals.Add("helper missing: $($helper.path)") | Out-Null
    }
}

$reviewSignals = [System.Collections.Generic.List[string]]::new()
if ($allowedFileCheckResult -eq "REVIEW") {
    $reviewSignals.Add("allowed path boundary not supplied") | Out-Null
}
foreach ($helper in @($validatorRecommendation, $cleanState, $commitPackage, $commitPushGate, $prLaneRunner)) {
    if ($helper.status -eq "REVIEW") {
        $reviewSignals.Add("helper returned review: $($helper.path)") | Out-Null
    }
}
if ($candidateFiles.Count -eq 0) {
    $reviewSignals.Add("no candidate files detected") | Out-Null
}
if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
    $reviewSignals.Add("commit message missing") | Out-Null
}
if ([string]::IsNullOrWhiteSpace($PrTitle)) {
    $reviewSignals.Add("PR title missing") | Out-Null
}

$dryRunResult = if ($blockingSignals.Count -gt 0) {
    "BLOCKED"
}
elseif ($reviewSignals.Count -gt 0) {
    "REVIEW"
}
else {
    "READY_FOR_HUMAN_APPROVAL"
}

$packet = [pscustomobject]@{
    schema = "AIOS_COMMIT_PUSH_PR_CONTROLLER_PREVIEW.v1"
    mode = "DRY_RUN"
    generated_at = $generatedAt
    dry_run_result = [pscustomobject]@{
        result = $dryRunResult
        repo_root = $repoRoot
        branch = $currentBranch
        head = if ($headResult.exit_code -eq 0) { $headResult.text.Trim() } else { "UNKNOWN" }
        helper_failures_are_reported_only = $true
        mutations_performed = 0
    }
    changed_file_list = [pscustomobject]@{
        source = "git status --short --branch"
        changed_files = @($changedFiles)
        candidate_files = @($candidateFiles)
    }
    allowed_file_check = [pscustomobject]@{
        result = $allowedFileCheckResult
        allowed_paths = @($normalizedAllowedPaths)
        files = @($allowedFileEntries)
    }
    validator_recommendation = [pscustomobject]@{
        helper = $validatorRecommendation.path
        status = $validatorRecommendation.status
        exit_code = $validatorRecommendation.exit_code
        result = if ($validatorRecommendation.json) { $validatorRecommendation.json.result } else { "UNKNOWN" }
        recommended_commands = if ($validatorRecommendation.json -and $validatorRecommendation.json.PSObject.Properties.Name -contains "recommended_commands") { @($validatorRecommendation.json.recommended_commands) } else { @() }
        error = $validatorRecommendation.error
    }
    clean_state_check = [pscustomobject]@{
        helper = $cleanState.path
        status = $cleanState.status
        exit_code = $cleanState.exit_code
        result = if ($cleanState.json) { $cleanState.json.result } else { "UNKNOWN" }
        blocked_count = if ($cleanState.json -and $cleanState.json.PSObject.Properties.Name -contains "blocked_count") { $cleanState.json.blocked_count } else { "UNKNOWN" }
        warn_count = if ($cleanState.json -and $cleanState.json.PSObject.Properties.Name -contains "warn_count") { $cleanState.json.warn_count } else { "UNKNOWN" }
        error = $cleanState.error
    }
    commit_package_preview = [pscustomobject]@{
        helper = $commitPackage.path
        status = $commitPackage.status
        exit_code = $commitPackage.exit_code
        recommended_file_count = if ($commitPackage.json -and $commitPackage.json.PSObject.Properties.Name -contains "summary") { $commitPackage.json.summary.recommended_file_count } else { "UNKNOWN" }
        suggested_commit_message = if ($commitPackage.json -and $commitPackage.json.PSObject.Properties.Name -contains "commit_message_suggestion") { $commitPackage.json.commit_message_suggestion } else { "" }
        error = $commitPackage.error
    }
    exact_git_add_preview = [pscustomobject]@{
        status = "PREVIEW_ONLY"
        commands = @($recommendedGitAddCommands)
        git_add_dot_used = "NO"
        requires_token = "APPROVE_COMMIT"
    }
    exact_commit_preview = $exactCommitPreview
    exact_push_preview = $exactPushPreview
    exact_pr_create_preview = $exactPrCreatePreview
    commit_push_gate = [pscustomobject]@{
        helper = $commitPushGate.path
        status = $commitPushGate.status
        exit_code = $commitPushGate.exit_code
        gate_state = if ($commitPushGate.json) { $commitPushGate.json.gate_state } else { "UNKNOWN" }
        error = $commitPushGate.error
    }
    pr_lane_runner = [pscustomobject]@{
        helper = $prLaneRunner.path
        status = $prLaneRunner.status
        exit_code = $prLaneRunner.exit_code
        lane_state = if ($prLaneRunner.json) { $prLaneRunner.json.lane_state } else { "UNKNOWN" }
        error = $prLaneRunner.error
    }
    approval_tokens_required = @(
        [pscustomobject]@{
            approval_marker = "APPROVE_COMMIT"
            required_for = "future exact git add and git commit execution"
            does_not_authorize = @("push", "PR create", "merge", "git add .")
        }
        [pscustomobject]@{
            approval_marker = "APPROVE_PUSH"
            required_for = "future exact git push execution"
            does_not_authorize = @("commit", "PR create", "merge", "direct protected-main bypass")
        }
        [pscustomobject]@{
            approval_marker = "APPROVE_PR_CREATE"
            required_for = "future exact gh pr create execution"
            does_not_authorize = @("commit", "push", "merge")
        }
    )
    blocked_actions = @(
        "git add .",
        "staging unnamed files",
        "commit without APPROVE_COMMIT",
        "push without APPROVE_PUSH",
        "PR creation without APPROVE_PR_CREATE",
        "merge automation",
        "broker/OANDA/live trading/webhook/secrets/dashboard work"
    )
    stop_conditions = @(
        @($blockingSignals),
        @($reviewSignals),
        @("human approval required before commit, push, or PR creation"),
        @("merge automation remains blocked")
    ) | ForEach-Object { $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Select-Object -Unique
    safety = [pscustomobject]@{
        files_edited = 0
        files_staged = 0
        commits_performed = 0
        pushes_performed = 0
        prs_created = 0
        merges_performed = 0
        dashboard_edits = "NO"
        broker_oanda_live_trading_webhook_secrets = "NO"
    }
    next_safe_action = if ($dryRunResult -eq "BLOCKED") {
        "Stop. Resolve blocking signals before any commit, push, or PR request."
    }
    elseif ($dryRunResult -eq "REVIEW") {
        "Review preview details and supply exact approval tokens only if the scope is correct."
    }
    else {
        "Await explicit Anthony approval token for the next protected action."
    }
}

if ($OutputJson) {
    $packet | ConvertTo-Json -Depth 14
    exit 0
}

Write-Host "AI_OS Commit/Push/PR Controller Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($packet.schema)"
Write-Host "Result: $($packet.dry_run_result.result)"
Write-Host "Branch: $($packet.dry_run_result.branch)"
Write-Host "Candidate files: $($packet.changed_file_list.candidate_files.Count)"
Write-Host "Allowed file check: $($packet.allowed_file_check.result)"
Write-Host "Validator: $($packet.validator_recommendation.status) / $($packet.validator_recommendation.result)"
Write-Host "Clean state: $($packet.clean_state_check.status) / $($packet.clean_state_check.result)"
Write-Host "Commit gate: $($packet.commit_push_gate.status) / $($packet.commit_push_gate.gate_state)"
Write-Host "PR lane: $($packet.pr_lane_runner.status) / $($packet.pr_lane_runner.lane_state)"
Write-Host ""
Write-Host "Exact git add preview:"
if ($packet.exact_git_add_preview.commands.Count -eq 0) {
    Write-Host "  NONE"
}
else {
    foreach ($command in $packet.exact_git_add_preview.commands) {
        Write-Host "  $command"
    }
}
Write-Host ""
Write-Host "Exact commit preview: $($packet.exact_commit_preview.command)"
Write-Host "Exact push preview: $($packet.exact_push_preview.command)"
Write-Host "Exact PR create preview: $($packet.exact_pr_create_preview.command)"
Write-Host ""
Write-Host "Required approval tokens: APPROVE_COMMIT, APPROVE_PUSH, APPROVE_PR_CREATE"
Write-Host "Next safe action: $($packet.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "PR created: NO"
Write-Host "Merge performed: NO"
