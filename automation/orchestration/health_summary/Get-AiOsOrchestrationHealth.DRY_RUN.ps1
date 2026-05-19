param(
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-GitText {
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

function Remove-GitWarnings {
    param([string[]]$Lines)

    return @($Lines | Where-Object { $_ -notmatch "^warning:" })
}

function Get-GitWarnings {
    param([string[]]$Lines)

    return @($Lines | Where-Object { $_ -match "^warning:" })
}

function Get-FirstCleanLine {
    param([string[]]$Lines)

    $cleanLines = @(Remove-GitWarnings -Lines $Lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($cleanLines.Count -eq 0) {
        return "UNKNOWN"
    }

    return $cleanLines[0]
}

function Test-AiOsTool {
    param(
        [Parameter(Mandatory = $true)][string]$ToolId,
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string[]]$Paths,
        [string]$MissingSeverity = "REVIEW"
    )

    $foundPath = ""
    foreach ($path in $Paths) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $foundPath = $path
            break
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($foundPath)) {
        return [pscustomobject]@{
            tool_id = $ToolId
            label = $Label
            status = "PASS"
            path = $foundPath
            missing_severity = "NONE"
        }
    }

    return [pscustomobject]@{
        tool_id = $ToolId
        label = $Label
        status = "MISSING"
        path = $Paths[0]
        missing_severity = $MissingSeverity
    }
}

function Get-ChangedPathFromStatusLine {
    param([Parameter(Mandatory = $true)][string]$Line)

    if ($Line.Length -lt 4) {
        return $Line
    }

    return $Line.Substring(3).Replace("\", "/")
}

$toolChecks = @(
    Test-AiOsTool -ToolId "clean_state_verifier" -Label "Clean-state verifier" -Paths @("automation/orchestration/clean_state_gate.ps1", "checkpoints/verify_success.ps1") -MissingSeverity "BLOCKED"
    Test-AiOsTool -ToolId "approval_runner" -Label "Approval runner" -Paths @("automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1", "automation/orchestration/approval_detection/Find-AiOsApprovalMatch.DRY_RUN.ps1") -MissingSeverity "BLOCKED"
    Test-AiOsTool -ToolId "commit_package_recommender" -Label "Commit package recommender" -Paths @("automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1") -MissingSeverity "REVIEW"
    Test-AiOsTool -ToolId "validator_chain_runner" -Label "Validator chain runner" -Paths @("automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1", "automation/orchestration/show-validator-chain.ps1") -MissingSeverity "BLOCKED"
    Test-AiOsTool -ToolId "post_push_verifier" -Label "Post-push verifier" -Paths @("automation/orchestration/post_push/Test-AiOsPostPushVerification.DRY_RUN.ps1") -MissingSeverity "REVIEW"
    Test-AiOsTool -ToolId "worker_lane_checker" -Label "Worker lane checker" -Paths @("automation/orchestration/worker_lanes/Get-AiOsWorkerLaneStatus.DRY_RUN.ps1") -MissingSeverity "REVIEW"
    Test-AiOsTool -ToolId "compliance_checker" -Label "Compliance checker" -Paths @("automation/orchestration/compliance/Test-AiOsAgentCompliance.DRY_RUN.ps1", "automation/compliance/Test-AiOsCompliance.DRY_RUN.ps1") -MissingSeverity "REVIEW"
    Test-AiOsTool -ToolId "adapter_tools" -Label "Adapter tools" -Paths @("automation/orchestration/adapters/Normalize-AiOsPacket.DRY_RUN.ps1", "automation/orchestration/adapters/Test-AiOsPacketNormalization.DRY_RUN.ps1") -MissingSeverity "REVIEW"
    Test-AiOsTool -ToolId "lock_tools" -Label "Lock tools" -Paths @("automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1", "automation/orchestration/locks/FILE_LOCK_REGISTRY.example.json") -MissingSeverity "REVIEW"
)

$branchResult = Invoke-GitText -Arguments @("branch", "--show-current")
$statusResult = Invoke-GitText -Arguments @("status", "--short")
$gitWarnings = @(
    @(
        Get-GitWarnings -Lines $branchResult.Output
        Get-GitWarnings -Lines $statusResult.Output
    ) | Sort-Object -Unique
)

$currentBranch = Get-FirstCleanLine -Lines $branchResult.Output
$statusLines = @(Remove-GitWarnings -Lines $statusResult.Output | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$dirtyFiles = @($statusLines | Where-Object { -not $_.StartsWith("?? ") } | ForEach-Object { Get-ChangedPathFromStatusLine -Line $_ })
$untrackedFiles = @($statusLines | Where-Object { $_.StartsWith("?? ") } | ForEach-Object { Get-ChangedPathFromStatusLine -Line $_ })
$repoState = if ($statusLines.Count -eq 0) { "clean" } else { "dirty" }

$missingTools = @($toolChecks | Where-Object { $_.status -eq "MISSING" })
$risks = @()

foreach ($tool in $missingTools) {
    $risks += [pscustomobject]@{
        severity = $tool.missing_severity
        risk = "$($tool.label) is missing."
        tool_id = $tool.tool_id
    }
}

if ($repoState -ne "clean") {
    $risks += [pscustomobject]@{
        severity = "REVIEW"
        risk = "Repository has dirty or untracked files."
        tool_id = "repo_status"
    }
}

if ($currentBranch -eq "UNKNOWN") {
    $risks += [pscustomobject]@{
        severity = "BLOCKED"
        risk = "Current git branch could not be detected."
        tool_id = "repo_status"
    }
}

$resultStatus = "HEALTHY"
if (@($risks | Where-Object { $_.severity -eq "BLOCKED" }).Count -gt 0) {
    $resultStatus = "BLOCKED"
} elseif ($risks.Count -gt 0) {
    $resultStatus = "REVIEW"
}

$nextSafeAction = "Orchestration health is clean. Continue with DRY_RUN planning or validation."
if ($resultStatus -eq "REVIEW") {
    $nextSafeAction = "Review missing tools and dirty repo status before APPLY, commit, push, or handoff work."
} elseif ($resultStatus -eq "BLOCKED") {
    $nextSafeAction = "Stop and resolve BLOCKED health risks before APPLY, commit, push, or handoff work."
}

$result = [pscustomobject]@{
    system = "AI_OS"
    task = "Show AI_OS orchestration health summary"
    mode = "DRY_RUN"
    result = $resultStatus
    summary = [pscustomobject]@{
        tool_count = $toolChecks.Count
        present_count = @($toolChecks | Where-Object { $_.status -eq "PASS" }).Count
        missing_count = $missingTools.Count
        risk_count = $risks.Count
    }
    tools = $toolChecks
    missing_tools = @($missingTools | ForEach-Object { $_.tool_id })
    repo_status = [pscustomobject]@{
        branch = $currentBranch
        state = $repoState
        dirty_count = $dirtyFiles.Count
        untracked_count = $untrackedFiles.Count
        dirty_files = $dirtyFiles
        untracked_files = $untrackedFiles
    }
    risks = $risks
    git_warnings = $gitWarnings
    safety = [pscustomobject]@{
        writes_performed = 0
        commits_performed = 0
        pushes_performed = 0
        dispatcher_edits = "NO"
        runtime_integration = "NO"
        dashboard_edits = "NO"
    }
    validator_friendly = $true
    next_safe_action = $nextSafeAction
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Orchestration Health"
Write-Host "Mode: DRY_RUN"
Write-Host "Result: $resultStatus"
Write-Host "Branch: $currentBranch"
Write-Host "Repo status: $repoState"
Write-Host ""
Write-Host "Tool summary:"
Write-Host "  Present: $($result.summary.present_count)"
Write-Host "  Missing: $($result.summary.missing_count)"
Write-Host "  Risks: $($result.summary.risk_count)"
Write-Host ""

Write-Host "Tools:"
foreach ($tool in $toolChecks) {
    Write-Host "  - $($tool.label): $($tool.status)"
    Write-Host "    Path: $($tool.path)"
}
Write-Host ""

Write-Host "Missing tools:"
if ($missingTools.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($tool in $missingTools) {
        Write-Host "  - $($tool.tool_id)"
    }
}
Write-Host ""

Write-Host "Repo files:"
Write-Host "  Dirty tracked files: $($dirtyFiles.Count)"
Write-Host "  Untracked files: $($untrackedFiles.Count)"
Write-Host ""

Write-Host "Risks:"
if ($risks.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($risk in $risks) {
        Write-Host "  - [$($risk.severity)] $($risk.risk)"
    }
}
Write-Host ""

Write-Host "Git warnings:"
if ($gitWarnings.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($warning in $gitWarnings) {
        Write-Host "  - $warning"
    }
}
Write-Host ""

Write-Host "Validator note: no files were changed by this DRY_RUN check."
Write-Host "Next safe action: $nextSafeAction"

