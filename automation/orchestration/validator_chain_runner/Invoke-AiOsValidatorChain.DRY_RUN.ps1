[CmdletBinding()]
param(
    [string[]]$WorkerLanePath = @(),
    [string]$ValidationEvidencePath = "",
    [string]$WorkerReportPath = "",
    [string]$ApprovalReason = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"

function Get-AiOsRepoRoot {
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to find git repository root."
    }

    return $root.Trim()
}

function Invoke-AiOsNativeCommand {
    param(
        [string]$Command,
        [string[]]$Arguments = @()
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = @(& $Command @Arguments 2>&1)
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        ExitCode = $exitCode
        Output = @($output | ForEach-Object { [string]$_ })
    }
}

function Add-AiOsValidatorResult {
    param(
        [System.Collections.Generic.List[object]]$Results,
        [string]$ValidatorId,
        [ValidateSet("PASS", "REVIEW", "BLOCKED")][string]$Result,
        [string]$Message,
        [string[]]$Evidence = @(),
        [string]$Command = "",
        [string]$NextSafeAction = "Review this validator result before APPLY, commit, or push."
    )

    $Results.Add([pscustomobject]@{
        validator_id = $ValidatorId
        result = $Result
        command = $Command
        message = $Message
        evidence = @($Evidence)
        next_safe_action = $NextSafeAction
    }) | Out-Null
}

function Convert-AiOsStatusLineToPath {
    param([string]$Line)

    if ([string]::IsNullOrWhiteSpace($Line) -or $Line.Length -lt 4 -or $Line -like "##*") {
        return ""
    }

    $path = $Line.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }

    return ($path -replace "\\", "/")
}

function Get-AiOsChangedFiles {
    param([string[]]$StatusLines)

    $paths = New-Object System.Collections.Generic.List[string]

    foreach ($line in $StatusLines) {
        $path = Convert-AiOsStatusLineToPath -Line $line
        if ([string]::IsNullOrWhiteSpace($path)) {
            continue
        }

        $fullPath = Join-Path (Get-Location).Path $path
        if (Test-Path -LiteralPath $fullPath -PathType Container) {
            Get-ChildItem -LiteralPath $fullPath -Recurse -File |
                ForEach-Object {
                    $relative = Resolve-Path -LiteralPath $_.FullName -Relative
                    $paths.Add(($relative.TrimStart(".", "\", "/") -replace "\\", "/")) | Out-Null
                }
        }
        else {
            $paths.Add($path) | Out-Null
        }
    }

    return @($paths | Select-Object -Unique)
}

function Invoke-AiOsJsonScript {
    param([string[]]$CommandArguments)

    $result = Invoke-AiOsNativeCommand -Command "powershell" -Arguments $CommandArguments
    $text = ($result.Output -join [Environment]::NewLine)
    $parsed = $null

    try {
        $parsed = $text | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            ExitCode = $result.ExitCode
            Parsed = $null
            Raw = $text
            ParseError = $_.Exception.Message
        }
    }

    return [pscustomobject]@{
        ExitCode = $result.ExitCode
        Parsed = $parsed
        Raw = $text
        ParseError = ""
    }
}

$repoRoot = Get-AiOsRepoRoot
Set-Location -LiteralPath $repoRoot

$generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$validators = [System.Collections.Generic.List[object]]::new()

$branchResult = Invoke-AiOsNativeCommand -Command "git" -Arguments @("branch", "--show-current")
$currentBranch = if ($branchResult.Output.Count -gt 0) { [string]$branchResult.Output[0] } else { "" }

$statusResult = Invoke-AiOsNativeCommand -Command "git" -Arguments @("status", "--short", "--branch")
$statusLines = @($statusResult.Output | Where-Object { $_ -notmatch "warning: unable to access" })
$changedFiles = Get-AiOsChangedFiles -StatusLines $statusLines

$diffCheck = Invoke-AiOsNativeCommand -Command "git" -Arguments @("diff", "--check")
if ($diffCheck.ExitCode -eq 0) {
    Add-AiOsValidatorResult -Results $validators -ValidatorId "git_diff_check" -Result "PASS" -Command "git diff --check" -Message "git diff --check passed."
}
else {
    Add-AiOsValidatorResult -Results $validators -ValidatorId "git_diff_check" -Result "BLOCKED" -Command "git diff --check" -Message "git diff --check failed." -Evidence $diffCheck.Output -NextSafeAction "Fix whitespace or conflict marker issues before continuing."
}

$changedPs1Files = @($changedFiles | Where-Object { $_ -like "*.ps1" })
$psFailures = New-Object System.Collections.Generic.List[string]
foreach ($file in $changedPs1Files) {
    $fullPath = Join-Path $repoRoot $file
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        continue
    }

    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($fullPath, [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors.Count -gt 0) {
        foreach ($error in $errors) {
            $psFailures.Add(("{0}: {1}" -f $file, $error.Message)) | Out-Null
        }
    }
}

if ($psFailures.Count -eq 0) {
    Add-AiOsValidatorResult -Results $validators -ValidatorId "powershell_parse_changed" -Result "PASS" -Message ("Parsed changed PowerShell files: {0}" -f $changedPs1Files.Count) -Evidence $changedPs1Files
}
else {
    Add-AiOsValidatorResult -Results $validators -ValidatorId "powershell_parse_changed" -Result "BLOCKED" -Message "One or more changed PowerShell files failed to parse." -Evidence @($psFailures) -NextSafeAction "Fix PowerShell syntax before continuing."
}

$changedJsonFiles = @($changedFiles | Where-Object { $_ -like "*.json" })
$jsonFailures = New-Object System.Collections.Generic.List[string]
foreach ($file in $changedJsonFiles) {
    $fullPath = Join-Path $repoRoot $file
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        continue
    }

    try {
        Get-Content -LiteralPath $fullPath -Raw | ConvertFrom-Json | Out-Null
    }
    catch {
        $jsonFailures.Add(("{0}: {1}" -f $file, $_.Exception.Message)) | Out-Null
    }
}

if ($jsonFailures.Count -eq 0) {
    Add-AiOsValidatorResult -Results $validators -ValidatorId "json_parse_changed" -Result "PASS" -Message ("Parsed changed JSON files: {0}" -f $changedJsonFiles.Count) -Evidence $changedJsonFiles
}
else {
    Add-AiOsValidatorResult -Results $validators -ValidatorId "json_parse_changed" -Result "BLOCKED" -Message "One or more changed JSON files failed to parse." -Evidence @($jsonFailures) -NextSafeAction "Fix JSON syntax before continuing."
}

$cleanStatePath = "automation/orchestration/clean_state/Test-AiOsCleanState.DRY_RUN.ps1"
if (Test-Path -LiteralPath $cleanStatePath -PathType Leaf) {
    $cleanArgs = @("-ExecutionPolicy", "Bypass", "-File", $cleanStatePath, "-Json")
    foreach ($lane in $WorkerLanePath) {
        $cleanArgs += @("-WorkerLanePath", $lane)
    }

    $cleanRun = Invoke-AiOsJsonScript -CommandArguments $cleanArgs
    if ($null -eq $cleanRun.Parsed) {
        Add-AiOsValidatorResult -Results $validators -ValidatorId "clean_state_verifier" -Result "REVIEW" -Command "Test-AiOsCleanState.DRY_RUN.ps1 -Json" -Message "Clean-state verifier ran but JSON output could not be parsed." -Evidence @($cleanRun.ParseError) -NextSafeAction "Run clean-state verifier directly and review output."
    }
    elseif ($cleanRun.Parsed.result -eq "BLOCKED") {
        Add-AiOsValidatorResult -Results $validators -ValidatorId "clean_state_verifier" -Result "BLOCKED" -Command "Test-AiOsCleanState.DRY_RUN.ps1 -Json" -Message "Clean-state verifier returned BLOCKED." -Evidence @($cleanRun.Parsed.next_safe_action) -NextSafeAction $cleanRun.Parsed.next_safe_action
    }
    elseif ($cleanRun.Parsed.result -eq "REVIEW") {
        Add-AiOsValidatorResult -Results $validators -ValidatorId "clean_state_verifier" -Result "REVIEW" -Command "Test-AiOsCleanState.DRY_RUN.ps1 -Json" -Message "Clean-state verifier returned REVIEW." -Evidence @($cleanRun.Parsed.next_safe_action) -NextSafeAction $cleanRun.Parsed.next_safe_action
    }
    else {
        Add-AiOsValidatorResult -Results $validators -ValidatorId "clean_state_verifier" -Result "PASS" -Command "Test-AiOsCleanState.DRY_RUN.ps1 -Json" -Message "Clean-state verifier returned CLEAN." -Evidence @($cleanRun.Parsed.next_safe_action)
    }
}
else {
    Add-AiOsValidatorResult -Results $validators -ValidatorId "clean_state_verifier" -Result "REVIEW" -Message "Clean-state verifier is not available." -NextSafeAction "Create or restore clean-state verifier before relying on chain result."
}

$approvalRunnerPath = "automation/orchestration/approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1"
if (Test-Path -LiteralPath $approvalRunnerPath -PathType Leaf) {
    $approvalArgs = @("-ExecutionPolicy", "Bypass", "-File", $approvalRunnerPath, "-Json")
    if (-not [string]::IsNullOrWhiteSpace($ValidationEvidencePath)) {
        $approvalArgs += @("-ValidationEvidencePath", $ValidationEvidencePath)
    }
    if (-not [string]::IsNullOrWhiteSpace($WorkerReportPath)) {
        $approvalArgs += @("-WorkerReportPath", $WorkerReportPath)
    }
    if (-not [string]::IsNullOrWhiteSpace($ApprovalReason)) {
        $approvalArgs += @("-ApprovalReason", $ApprovalReason)
    }
    foreach ($lane in $WorkerLanePath) {
        $approvalArgs += @("-WorkerLanePath", $lane)
    }

    $approvalRun = Invoke-AiOsJsonScript -CommandArguments $approvalArgs
    if ($null -eq $approvalRun.Parsed) {
        Add-AiOsValidatorResult -Results $validators -ValidatorId "approval_runner" -Result "REVIEW" -Command "Get-AiOsApprovalDecision.DRY_RUN.ps1 -Json" -Message "Approval runner ran but JSON output could not be parsed." -Evidence @($approvalRun.ParseError) -NextSafeAction "Run approval runner directly and review output."
    }
    elseif ($approvalRun.Parsed.decision -eq "BLOCKED") {
        Add-AiOsValidatorResult -Results $validators -ValidatorId "approval_runner" -Result "BLOCKED" -Command "Get-AiOsApprovalDecision.DRY_RUN.ps1 -Json" -Message "Approval runner returned BLOCKED." -Evidence @($approvalRun.Parsed.next_safe_action) -NextSafeAction $approvalRun.Parsed.next_safe_action
    }
    elseif ($approvalRun.Parsed.decision -eq "REVIEW") {
        Add-AiOsValidatorResult -Results $validators -ValidatorId "approval_runner" -Result "REVIEW" -Command "Get-AiOsApprovalDecision.DRY_RUN.ps1 -Json" -Message "Approval runner returned REVIEW." -Evidence @($approvalRun.Parsed.next_safe_action) -NextSafeAction $approvalRun.Parsed.next_safe_action
    }
    else {
        Add-AiOsValidatorResult -Results $validators -ValidatorId "approval_runner" -Result "PASS" -Command "Get-AiOsApprovalDecision.DRY_RUN.ps1 -Json" -Message "Approval runner returned SAFE." -Evidence @($approvalRun.Parsed.next_safe_action)
    }
}
else {
    Add-AiOsValidatorResult -Results $validators -ValidatorId "approval_runner" -Result "REVIEW" -Message "Approval runner is not available." -NextSafeAction "Create or restore approval runner before relying on chain result."
}

if ($currentBranch -eq "main") {
    $postPushVerifierCandidates = @(
        "automation/orchestration/post_push/Test-AiOsPostPush.DRY_RUN.ps1",
        "automation/orchestration/post_push_verifier/Test-AiOsPostPush.DRY_RUN.ps1"
    )
    $postPushVerifier = @($postPushVerifierCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1)
    if ($postPushVerifier.Count -gt 0) {
        $postPushRun = Invoke-AiOsJsonScript -CommandArguments @("-ExecutionPolicy", "Bypass", "-File", $postPushVerifier[0], "-Json")
        if ($null -eq $postPushRun.Parsed) {
            Add-AiOsValidatorResult -Results $validators -ValidatorId "post_push_verifier_main_only" -Result "REVIEW" -Command "$($postPushVerifier[0]) -Json" -Message "Post-push verifier ran but JSON output could not be parsed." -Evidence @($postPushRun.ParseError) -NextSafeAction "Run post-push verifier directly and review output."
        }
        else {
            $postResult = ""
            if ($postPushRun.Parsed.PSObject.Properties.Name -contains "result") {
                $postResult = [string]$postPushRun.Parsed.result
            }
            elseif ($postPushRun.Parsed.PSObject.Properties.Name -contains "decision") {
                $postResult = [string]$postPushRun.Parsed.decision
            }
            elseif ($postPushRun.Parsed.PSObject.Properties.Name -contains "overall_result") {
                $postResult = [string]$postPushRun.Parsed.overall_result
            }
            if ($postResult -match "BLOCKED|FAIL") {
                Add-AiOsValidatorResult -Results $validators -ValidatorId "post_push_verifier_main_only" -Result "BLOCKED" -Command "$($postPushVerifier[0]) -Json" -Message "Post-push verifier returned blocked/fail." -Evidence @($postPushRun.Parsed.next_safe_action) -NextSafeAction "Resolve post-push verifier failures before continuing."
            }
            elseif ($postResult -match "REVIEW|WARN") {
                Add-AiOsValidatorResult -Results $validators -ValidatorId "post_push_verifier_main_only" -Result "REVIEW" -Command "$($postPushVerifier[0]) -Json" -Message "Post-push verifier returned review/warn." -Evidence @($postPushRun.Parsed.next_safe_action) -NextSafeAction "Review post-push verifier warnings before continuing."
            }
            else {
                Add-AiOsValidatorResult -Results $validators -ValidatorId "post_push_verifier_main_only" -Result "PASS" -Command "$($postPushVerifier[0]) -Json" -Message "Post-push verifier passed." -Evidence @($postPushRun.Parsed.next_safe_action)
            }
        }
    }
    else {
        Add-AiOsValidatorResult -Results $validators -ValidatorId "post_push_verifier_main_only" -Result "REVIEW" -Message "On main branch, but no post-push verifier was found." -NextSafeAction "Add or run a post-push verifier before declaring main clean."
    }
}
else {
    Add-AiOsValidatorResult -Results $validators -ValidatorId "post_push_verifier_main_only" -Result "PASS" -Message "Post-push verifier skipped because current branch is not main." -Evidence @($currentBranch) -NextSafeAction "Run post-push verifier only when on main."
}

$blockedCount = @($validators | Where-Object { $_.result -eq "BLOCKED" }).Count
$reviewCount = @($validators | Where-Object { $_.result -eq "REVIEW" }).Count
$passCount = @($validators | Where-Object { $_.result -eq "PASS" }).Count
$overall = if ($blockedCount -gt 0) { "BLOCKED" } elseif ($reviewCount -gt 0) { "REVIEW" } else { "PASS" }
$failedValidators = @($validators | Where-Object { $_.result -ne "PASS" } | ForEach-Object { $_.validator_id })
$nextSafeAction = switch ($overall) {
    "PASS" { "Validator chain passed. Human approval is still required before APPLY, commit, or push." }
    "REVIEW" { "Review validator warnings before approving APPLY, commit, or push." }
    default { "Do not APPLY, commit, or push. Resolve blocked validators first." }
}

$report = [pscustomobject]@{
    schema = "AIOS_VALIDATOR_CHAIN_RUN_REPORT.v1"
    mode = "DRY_RUN"
    generated_at = $generatedAt
    repo_root = $repoRoot
    current_branch = $currentBranch
    overall_result = $overall
    pass_count = $passCount
    review_count = $reviewCount
    blocked_count = $blockedCount
    changed_files = @($changedFiles)
    validators_run = @($validators)
    failed_validators = @($failedValidators)
    files_changed_by_runner = @()
    commit_performed = $false
    push_performed = $false
    next_safe_action = $nextSafeAction
}

if (-not $Json) {
    Write-Host "AI_OS Validator Chain Runner"
    Write-Host "Mode: DRY_RUN"
    Write-Host "Result: $overall"
    Write-Host "Branch: $currentBranch"
    Write-Host "PASS: $passCount  REVIEW: $reviewCount  BLOCKED: $blockedCount"
    Write-Host ""
    Write-Host "Validators run:"
    foreach ($validator in $validators) {
        Write-Host ("- {0}: {1} - {2}" -f $validator.result, $validator.validator_id, $validator.message)
    }
    Write-Host ""
    if ($failedValidators.Count -gt 0) {
        Write-Host "Failed/review validators: $($failedValidators -join ', ')"
    }
    else {
        Write-Host "Failed/review validators: none"
    }
    Write-Host "Next safe action: $nextSafeAction"
    Write-Host ""
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ""
}

$report | ConvertTo-Json -Depth 14

if ($overall -eq "BLOCKED") {
    exit 1
}

exit 0
