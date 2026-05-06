param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
$gitBranch = 'UNKNOWN'
$gitStatusClean = 'unknown'
$protectedFileDiffClean = 'unknown'
$dailyMetricsChanged = 'unknown'
$checkpointIndexChanged = 'unknown'
$routerAvailable = $false
$registryAvailable = $false
$dataContractAvailable = $false
$dashboardState = 'FAIL_BLOCKED'
$approvalRequired = 'YES'
$riskLevel = 'LOW'
$activeWorkflow = 'NONE'
$lastResult = 'UNKNOWN'
$workflowCount = 0

function Convert-ToTextBool {
    param([bool]$Value)
    if ($Value) {
        return 'true'
    }

    return 'false'
}

Write-Host 'Task name: AI_OS Stage 11C/11D Dashboard Snapshot Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, or settings-changed.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'dashboard_state: FAIL_BLOCKED'
    Write-Host "last_result: repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO DASHBOARD SNAPSHOT FILE WRITTEN.' -f [char]0x2014)
    exit 1
}

$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$routerPath = Join-Path $resolvedRepoRoot 'automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1'
$registryPath = Join-Path $resolvedRepoRoot 'docs\AI_OS\router\AIOS_WORKFLOW_REGISTRY_DRAFT.md'
$dataContractPath = Join-Path $resolvedRepoRoot 'docs\AI_OS\dashboard\AIOS_DASHBOARD_DATA_CONTRACT_DRAFT.md'

$routerAvailable = Test-Path -LiteralPath $routerPath -PathType Leaf
$registryAvailable = Test-Path -LiteralPath $registryPath -PathType Leaf
$dataContractAvailable = Test-Path -LiteralPath $dataContractPath -PathType Leaf

if ($registryAvailable) {
    $registryText = Get-Content -LiteralPath $registryPath -Raw
    $knownWorkflows = @(
        'REPO_HEALTH',
        'DAILY_START',
        'WORK_SESSION',
        'CHECKPOINT_ONLY',
        'DAILY_METRICS_DRAFT',
        'FULL_DRY_RUN_CHAIN'
    )
    $workflowCount = @($knownWorkflows | Where-Object { $registryText -match [regex]::Escape($_) }).Count
}

$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if ($gitCommand) {
    Push-Location -LiteralPath $resolvedRepoRoot
    try {
        $branchOutput = @(& git branch --show-current 2>&1)
        if ($LASTEXITCODE -eq 0 -and $branchOutput.Count -gt 0) {
            $gitBranch = [string]$branchOutput[0]
        }

        $gitStatus = @(& git status --short 2>&1)
        if ($LASTEXITCODE -eq 0) {
            $gitStatusClean = (Convert-ToTextBool -Value ($gitStatus.Count -eq 0))
        }

        $protectedDiff = @(& git diff --name-only -- README.md AGENTS.md RISK_POLICY.md SOURCE_LOG.md ERROR_LOG.md HALLUCINATION_LOG.md AAR.md DAILY_REPORT.md WHITEPAPER.md Reports\DAILY_METRICS.csv Reports\CHECKPOINT_INDEX.md 2>&1)
        if ($LASTEXITCODE -eq 0) {
            $protectedFileDiffClean = (Convert-ToTextBool -Value ($protectedDiff.Count -eq 0))
            $dailyMetricsChanged = (Convert-ToTextBool -Value ($protectedDiff -contains 'Reports/DAILY_METRICS.csv' -or $protectedDiff -contains 'Reports\DAILY_METRICS.csv'))
            $checkpointIndexChanged = (Convert-ToTextBool -Value ($protectedDiff -contains 'Reports/CHECKPOINT_INDEX.md' -or $protectedDiff -contains 'Reports\CHECKPOINT_INDEX.md'))
        }
    }
    finally {
        Pop-Location
    }
}
else {
    $lastResult = 'git command unavailable'
}

if (-not $routerAvailable -or -not $registryAvailable -or -not $dataContractAvailable) {
    $dashboardState = 'FAIL_BLOCKED'
    $lastResult = 'core dashboard files missing'
}
elseif ($gitStatusClean -eq 'false') {
    $dashboardState = 'WARN_REVIEW_REQUIRED'
    $lastResult = 'git status has untracked or modified files'
}
elseif ($gitStatusClean -eq 'true') {
    $dashboardState = 'DRY_RUN_READY'
    $lastResult = 'core files present and git status clean'
}
else {
    $dashboardState = 'WARN_REVIEW_REQUIRED'
    $lastResult = 'git status unknown'
}

Write-Host 'Dashboard text snapshot:'
Write-Host "timestamp: $timestamp"
Write-Host "repo_root: $resolvedRepoRoot"
Write-Host "git_branch: $gitBranch"
Write-Host "git_status_clean: $gitStatusClean"
Write-Host "dashboard_state: $dashboardState"
Write-Host "router_available: $(Convert-ToTextBool -Value $routerAvailable)"
Write-Host "registry_available: $(Convert-ToTextBool -Value $registryAvailable)"
Write-Host "dashboard_data_contract_available: $(Convert-ToTextBool -Value $dataContractAvailable)"
Write-Host "workflow_count: $workflowCount"
Write-Host "active_workflow: $activeWorkflow"
Write-Host "last_result: $lastResult"
Write-Host "approval_required: $approvalRequired"
Write-Host "risk_level: $riskLevel"
Write-Host "protected_files_changed: $(if ($protectedFileDiffClean -eq 'unknown') { 'unknown' } else { Convert-ToTextBool -Value ($protectedFileDiffClean -eq 'false') })"
Write-Host "protected_file_diff_clean: $protectedFileDiffClean"
Write-Host "daily_metrics_changed: $dailyMetricsChanged"
Write-Host "checkpoint_index_changed: $checkpointIndexChanged"
Write-Host ''
Write-Host 'Conceptual panel mapping:'
Write-Host "Repo Health -> dashboard_state ($dashboardState)"
Write-Host "Workflow Router -> router_available ($(Convert-ToTextBool -Value $routerAvailable))"
Write-Host "Daily Metrics -> daily_metrics_changed ($dailyMetricsChanged)"
Write-Host "Checkpoint Index -> checkpoint_index_changed ($checkpointIndexChanged)"
Write-Host "Approval Queue -> approval_required ($approvalRequired)"
Write-Host ''
Write-Host ('DRY_RUN COMPLETE {0} NO DASHBOARD SNAPSHOT FILE WRITTEN.' -f [char]0x2014)
