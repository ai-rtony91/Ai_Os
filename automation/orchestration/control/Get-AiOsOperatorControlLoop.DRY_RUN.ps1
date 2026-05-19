[CmdletBinding()]
param(
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-AiOsGitText {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        Output = @($output | ForEach-Object { [string]$_ })
        ExitCode = $exitCode
    }
}

function Remove-AiOsGitWarnings {
    param([string[]]$Lines)

    return @($Lines | Where-Object { $_ -notmatch "^warning:" })
}

function Get-AiOsGitWarnings {
    param([string[]]$Lines)

    return @($Lines | Where-Object { $_ -match "^warning:" })
}

function Get-AiOsFirstCleanLine {
    param([string[]]$Lines)

    $cleanLines = @(Remove-AiOsGitWarnings -Lines $Lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($cleanLines.Count -eq 0) {
        return "UNKNOWN"
    }

    return $cleanLines[0].Trim()
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

function Test-AiOsTool {
    param(
        [Parameter(Mandatory = $true)][string]$Id,
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$Path,
        [string[]]$Arguments = @(),
        [string]$MissingSeverity = "REVIEW"
    )

    $exists = Test-Path -LiteralPath $Path -PathType Leaf
    return [pscustomobject]@{
        id = $Id
        label = $Label
        path = $Path
        arguments = @($Arguments)
        available = $exists
        status = if ($exists) { "AVAILABLE" } else { "MISSING" }
        missing_severity = if ($exists) { "NONE" } else { $MissingSeverity }
    }
}

function Invoke-AiOsTool {
    param([Parameter(Mandatory = $true)]$Tool)

    if (-not $Tool.available) {
        return [pscustomobject]@{
            id = $Tool.id
            status = "MISSING"
            exit_code = $null
            json = $null
            summary = "Tool missing: $($Tool.path)"
            error = ""
        }
    }

    $arguments = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Tool.path)
    $arguments += @($Tool.arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & powershell @arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    $lines = @($output | ForEach-Object { [string]$_ })
    $json = $null
    $errorText = ""

    if ($lines.Count -gt 0) {
        try {
            $jsonText = Get-AiOsJsonTextFromLines -Lines $lines
            if ([string]::IsNullOrWhiteSpace($jsonText)) {
                $jsonText = ($lines -join "`n").Trim()
            }
            $json = $jsonText | ConvertFrom-Json
        }
        catch {
            $errorText = "Output was not valid JSON."
        }
    }

    $status = "PASS"
    if ($exitCode -ne 0) {
        $status = "REVIEW"
    }
    if ($null -eq $json) {
        $status = "REVIEW"
    }

    return [pscustomobject]@{
        id = $Tool.id
        status = $status
        exit_code = $exitCode
        json = $json
        summary = if ($null -eq $json) { $errorText } else { "JSON read successfully." }
        error = $errorText
    }
}

function Add-AiOsReason {
    param(
        [System.Collections.Generic.List[string]]$List,
        [string]$Reason
    )

    if (-not [string]::IsNullOrWhiteSpace($Reason) -and -not $List.Contains($Reason)) {
        $List.Add($Reason) | Out-Null
    }
}

function Get-AiOsProp {
    param(
        [AllowNull()]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Default = "UNKNOWN"
    )

    if ($null -eq $Object) {
        return $Default
    }

    if ($Object.PSObject.Properties.Name -contains $Name) {
        $value = $Object.$Name
        if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
            return $value
        }
    }

    return $Default
}

function Get-AiOsJsonTextFromLines {
    param([string[]]$Lines)

    $startIndex = -1
    $endIndex = -1

    for ($i = 0; $i -lt $Lines.Count; $i++) {
        $trimmed = $Lines[$i].Trim()
        if ($trimmed.StartsWith("{") -or $trimmed.StartsWith("[")) {
            $startIndex = $i
            break
        }
    }

    for ($i = $Lines.Count - 1; $i -ge 0; $i--) {
        $trimmed = $Lines[$i].Trim()
        if ($trimmed.EndsWith("}") -or $trimmed.EndsWith("]")) {
            $endIndex = $i
            break
        }
    }

    if ($startIndex -lt 0 -or $endIndex -lt $startIndex) {
        return ""
    }

    return (@($Lines[$startIndex..$endIndex]) -join "`n").Trim()
}

$repoRootResult = Invoke-AiOsGitText -Arguments @("rev-parse", "--show-toplevel")
if ($repoRootResult.ExitCode -eq 0) {
    $repoRoot = Get-AiOsFirstCleanLine -Lines $repoRootResult.Output
    Set-Location -LiteralPath $repoRoot
}

$branchResult = Invoke-AiOsGitText -Arguments @("branch", "--show-current")
$statusResult = Invoke-AiOsGitText -Arguments @("status", "--short", "--branch")
$gitWarnings = @(
    @(
        Get-AiOsGitWarnings -Lines $repoRootResult.Output
        Get-AiOsGitWarnings -Lines $branchResult.Output
        Get-AiOsGitWarnings -Lines $statusResult.Output
    ) | Sort-Object -Unique
)

$branch = Get-AiOsFirstCleanLine -Lines $branchResult.Output
$statusLines = @(Remove-AiOsGitWarnings -Lines $statusResult.Output | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$fileStatusLines = @($statusLines | Where-Object { $_ -notlike "##*" })
$dirtyFiles = @($fileStatusLines | Where-Object { -not $_.StartsWith("?? ") } | ForEach-Object { Convert-AiOsStatusLineToPath -Line $_ })
$untrackedFiles = @($fileStatusLines | Where-Object { $_.StartsWith("?? ") } | ForEach-Object { Convert-AiOsStatusLineToPath -Line $_ })
$repoState = if ($fileStatusLines.Count -eq 0) { "clean" } else { "dirty" }

$tools = @(
    Test-AiOsTool -Id "runtime_health" -Label "Runtime health" -Path "automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1" -Arguments @("-QuietJson") -MissingSeverity "BLOCKED"
    Test-AiOsTool -Id "action_recommendation" -Label "Action recommendation" -Path "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1" -Arguments @("-QuietJson") -MissingSeverity "BLOCKED"
    Test-AiOsTool -Id "worker_inbox" -Label "Worker inbox" -Path "automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1" -MissingSeverity "REVIEW"
    Test-AiOsTool -Id "lock_status" -Label "Worker lock status" -Path "automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1" -Arguments @("-OutputJson") -MissingSeverity "REVIEW"
    Test-AiOsTool -Id "validator_recommendation" -Label "Validator recommendation" -Path "automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1" -Arguments @("-OutputJson") -MissingSeverity "REVIEW"
    Test-AiOsTool -Id "commit_package" -Label "Commit package recommendation" -Path "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1" -Arguments @("-OutputJson") -MissingSeverity "REVIEW"
    Test-AiOsTool -Id "github_status" -Label "GitHub status check" -Path "automation/orchestration/github_status/Get-AiOsGitHubStatusCheck.DRY_RUN.ps1" -Arguments @("-OutputJson") -MissingSeverity "REVIEW"
    Test-AiOsTool -Id "health_summary" -Label "Orchestration health summary" -Path "automation/orchestration/health_summary/Get-AiOsOrchestrationHealth.DRY_RUN.ps1" -Arguments @("-OutputJson") -MissingSeverity "REVIEW"
    Test-AiOsTool -Id "daily_snapshot" -Label "Daily automation snapshot" -Path "automation/orchestration/daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1" -Arguments @("-Json") -MissingSeverity "REVIEW"
    Test-AiOsTool -Id "approval_decision" -Label "Approval inbox decision" -Path "automation/orchestration/approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1" -Arguments @("-Json") -MissingSeverity "REVIEW"
    Test-AiOsTool -Id "clean_state" -Label "Clean-state verifier" -Path "automation/orchestration/clean_state/Test-AiOsCleanState.DRY_RUN.ps1" -Arguments @("-Json") -MissingSeverity "REVIEW"
)

$toolResults = @()
foreach ($tool in $tools) {
    if ($tool.id -eq "worker_inbox") {
        $toolResults += [pscustomobject]@{
            id = $tool.id
            status = if ($tool.available) { "AVAILABLE" } else { "MISSING" }
            exit_code = $null
            json = $null
            summary = if ($tool.available) { "Display tool available; inbox file read separately when present." } else { "Tool missing: $($tool.path)" }
            error = ""
        }
    }
    else {
        $toolResults += Invoke-AiOsTool -Tool $tool
    }
}

$inboxPath = "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"
$workerInbox = $null
$workerItems = @()
if (Test-Path -LiteralPath $inboxPath -PathType Leaf) {
    try {
        $workerInbox = Get-Content -Raw -LiteralPath $inboxPath | ConvertFrom-Json
        $workerItems = @($workerInbox.items)
    }
    catch {
        $workerItems = @()
    }
}

$missingTools = @($tools | Where-Object { -not $_.available })
$blockedReasons = [System.Collections.Generic.List[string]]::new()
$reviewReasons = [System.Collections.Generic.List[string]]::new()

if ($branchResult.ExitCode -ne 0 -or $branch -eq "UNKNOWN") {
    Add-AiOsReason -List $blockedReasons -Reason "Current branch could not be read."
}

if ($statusResult.ExitCode -ne 0) {
    Add-AiOsReason -List $blockedReasons -Reason "git status could not be read."
}

if ($repoState -eq "dirty") {
    Add-AiOsReason -List $reviewReasons -Reason "Repository has changed or untracked files."
}

foreach ($tool in $missingTools) {
    $reason = "Missing tool: $($tool.path)"
    if ($tool.missing_severity -eq "BLOCKED") {
        Add-AiOsReason -List $blockedReasons -Reason $reason
    }
    else {
        Add-AiOsReason -List $reviewReasons -Reason $reason
    }
}

foreach ($result in $toolResults) {
    if ($result.status -eq "REVIEW") {
        Add-AiOsReason -List $reviewReasons -Reason "Tool needs review: $($result.id)"
    }
}

$health = (@($toolResults | Where-Object { $_.id -eq "runtime_health" }) | Select-Object -First 1).json
$recommendation = (@($toolResults | Where-Object { $_.id -eq "action_recommendation" }) | Select-Object -First 1).json
$locks = (@($toolResults | Where-Object { $_.id -eq "lock_status" }) | Select-Object -First 1).json
$commitPackage = (@($toolResults | Where-Object { $_.id -eq "commit_package" }) | Select-Object -First 1).json
$githubStatus = (@($toolResults | Where-Object { $_.id -eq "github_status" }) | Select-Object -First 1).json
$healthSummary = (@($toolResults | Where-Object { $_.id -eq "health_summary" }) | Select-Object -First 1).json
$dailySnapshot = (@($toolResults | Where-Object { $_.id -eq "daily_snapshot" }) | Select-Object -First 1).json
$approvalDecision = (@($toolResults | Where-Object { $_.id -eq "approval_decision" }) | Select-Object -First 1).json
$cleanState = (@($toolResults | Where-Object { $_.id -eq "clean_state" }) | Select-Object -First 1).json

$activeWorkerItems = @($workerItems | Where-Object { $_.status -ne "complete" -and $_.status -ne "failed" })
$resultStatus = "READY"
if ($blockedReasons.Count -gt 0) {
    $resultStatus = "BLOCKED"
}
elseif ($reviewReasons.Count -gt 0) {
    $resultStatus = "REVIEW"
}

$nextSafeAction = "Continue with the recommended DRY_RUN action."
if ($resultStatus -eq "BLOCKED") {
    $nextSafeAction = "Stop and resolve blocked reasons before APPLY, commit, push, or handoff."
}
elseif ($resultStatus -eq "REVIEW") {
    $nextSafeAction = "Review dirty state, missing tools, and tool warnings before APPLY, commit, push, or handoff."
}

$report = [pscustomobject]@{
    schema = "AIOS_OPERATOR_CONTROL_LOOP.v1"
    mode = "DRY_RUN"
    result = $resultStatus
    branch = $branch
    repo_state = $repoState
    dirty_file_count = $dirtyFiles.Count
    untracked_file_count = $untrackedFiles.Count
    tool_availability = @($tools | ForEach-Object {
        [pscustomobject]@{
            id = $_.id
            label = $_.label
            status = $_.status
            path = $_.path
        }
    })
    missing_tools = @($missingTools | ForEach-Object { $_.path })
    worker_packet_status = [pscustomobject]@{
        inbox_path = $inboxPath
        inbox_available = $null -ne $workerInbox
        open_item_count = $activeWorkerItems.Count
        open_items = @($activeWorkerItems | Select-Object -First 5)
        recommendation_packet_id = Get-AiOsProp -Object $recommendation -Name "packet_id"
        recommendation_packet_status = Get-AiOsProp -Object $recommendation -Name "packet_status"
    }
    lock_status = [pscustomobject]@{
        result = Get-AiOsProp -Object $locks -Name "mode"
        active_lock_count = Get-AiOsProp -Object $locks -Name "active_lock_count" -Default "UNKNOWN"
        collision_risk_count = Get-AiOsProp -Object $locks -Name "collision_risk_count" -Default "UNKNOWN"
    }
    approval_inbox_status = [pscustomobject]@{
        decision = Get-AiOsProp -Object $approvalDecision -Name "decision"
        warn_count = Get-AiOsProp -Object $approvalDecision -Name "warn_count" -Default "UNKNOWN"
        blocked_count = Get-AiOsProp -Object $approvalDecision -Name "blocked_count" -Default "UNKNOWN"
    }
    validator_recommendation = [pscustomobject]@{
        status = if (@($missingTools | Where-Object { $_.id -eq "validator_recommendation" }).Count -gt 0) { "MISSING" } else { "AVAILABLE" }
        note = "Use automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1 when present; fallback validator chain exists separately."
    }
    commit_package_recommendation = [pscustomobject]@{
        git_status = Get-AiOsProp -Object $commitPackage -Name "git_status"
        recommended_file_count = if ($null -ne $commitPackage -and $commitPackage.PSObject.Properties.Name -contains "summary") { Get-AiOsProp -Object $commitPackage.summary -Name "recommended_file_count" } else { "UNKNOWN" }
        risk_count = if ($null -ne $commitPackage -and $commitPackage.PSObject.Properties.Name -contains "summary") { Get-AiOsProp -Object $commitPackage.summary -Name "risk_count" } else { "UNKNOWN" }
    }
    clean_state_result = [pscustomobject]@{
        result = Get-AiOsProp -Object $cleanState -Name "result"
        warn_count = Get-AiOsProp -Object $cleanState -Name "warn_count" -Default "UNKNOWN"
        blocked_count = Get-AiOsProp -Object $cleanState -Name "blocked_count" -Default "UNKNOWN"
    }
    github_status_result = [pscustomobject]@{
        result = Get-AiOsProp -Object $githubStatus -Name "result"
        check_count = if ($null -ne $githubStatus -and $githubStatus.PSObject.Properties.Name -contains "summary") { Get-AiOsProp -Object $githubStatus.summary -Name "check_count" } else { "UNKNOWN" }
        fallback_message = Get-AiOsProp -Object $githubStatus -Name "fallback_message" -Default ""
    }
    health = [pscustomobject]@{
        runtime_health = Get-AiOsProp -Object $health -Name "health"
        health_summary_result = Get-AiOsProp -Object $healthSummary -Name "result"
        daily_snapshot_status = Get-AiOsProp -Object $dailySnapshot -Name "today_status"
    }
    blocked_reasons = @($blockedReasons)
    review_reasons = @($reviewReasons)
    git_warnings = $gitWarnings
    safety = [pscustomobject]@{
        writes_performed = 0
        files_staged = 0
        git_add_performed = "NO"
        commits_performed = 0
        pushes_performed = 0
        dashboard_edits = "NO"
        broker_oanda_api_webhook_live_trading = "NO"
    }
    next_safe_action = $nextSafeAction
}

if ($OutputJson) {
    $report | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AI_OS Operator Control Loop" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "Result: $resultStatus"
Write-Host "Branch: $branch"
Write-Host "Repo state: $repoState"
Write-Host "Dirty file count: $($dirtyFiles.Count)"
Write-Host "Untracked file count: $($untrackedFiles.Count)"
Write-Host ""

Write-Host "Tool availability:"
foreach ($tool in $report.tool_availability) {
    Write-Host ("  - {0}: {1}" -f $tool.label, $tool.status)
    Write-Host ("    Path: {0}" -f $tool.path)
}
Write-Host ""

Write-Host "Worker/packet status:"
Write-Host "  Open inbox items: $($report.worker_packet_status.open_item_count)"
Write-Host "  Packet id: $($report.worker_packet_status.recommendation_packet_id)"
Write-Host "  Packet status: $($report.worker_packet_status.recommendation_packet_status)"
Write-Host ""

Write-Host "Lock status:"
Write-Host "  Active locks: $($report.lock_status.active_lock_count)"
Write-Host "  Collision risks: $($report.lock_status.collision_risk_count)"
Write-Host ""

Write-Host "Approval inbox status:"
Write-Host "  Decision: $($report.approval_inbox_status.decision)"
Write-Host "  Warnings: $($report.approval_inbox_status.warn_count)"
Write-Host "  Blocked: $($report.approval_inbox_status.blocked_count)"
Write-Host ""

Write-Host "Validator recommendation:"
Write-Host "  Status: $($report.validator_recommendation.status)"
Write-Host "  Note: $($report.validator_recommendation.note)"
Write-Host ""

Write-Host "Commit package recommendation:"
Write-Host "  Git status: $($report.commit_package_recommendation.git_status)"
Write-Host "  Recommended files: $($report.commit_package_recommendation.recommended_file_count)"
Write-Host "  Risks: $($report.commit_package_recommendation.risk_count)"
Write-Host ""

Write-Host "Clean-state result:"
Write-Host "  Result: $($report.clean_state_result.result)"
Write-Host "  Warnings: $($report.clean_state_result.warn_count)"
Write-Host "  Blocked: $($report.clean_state_result.blocked_count)"
Write-Host ""

Write-Host "GitHub status result:"
Write-Host "  Result: $($report.github_status_result.result)"
Write-Host "  Check count: $($report.github_status_result.check_count)"
if (-not [string]::IsNullOrWhiteSpace($report.github_status_result.fallback_message)) {
    Write-Host "  Fallback: $($report.github_status_result.fallback_message)"
}
Write-Host ""

Write-Host "Missing tools:"
if ($report.missing_tools.Count -eq 0) {
    Write-Host "  NONE"
}
else {
    foreach ($tool in $report.missing_tools) {
        Write-Host "  - $tool"
    }
}
Write-Host ""

Write-Host "Blocked reasons:"
if ($report.blocked_reasons.Count -eq 0) {
    Write-Host "  NONE"
}
else {
    foreach ($reason in $report.blocked_reasons) {
        Write-Host "  - $reason"
    }
}
Write-Host ""

Write-Host "Review reasons:"
if ($report.review_reasons.Count -eq 0) {
    Write-Host "  NONE"
}
else {
    foreach ($reason in $report.review_reasons) {
        Write-Host "  - $reason"
    }
}
Write-Host ""

Write-Host "Git warnings:"
if ($report.git_warnings.Count -eq 0) {
    Write-Host "  NONE"
}
else {
    foreach ($warning in $report.git_warnings) {
        Write-Host "  - $warning"
    }
}
Write-Host ""

Write-Host "Next safe action: $nextSafeAction"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
